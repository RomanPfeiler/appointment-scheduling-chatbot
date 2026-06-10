"""Async bridge between the LangGraph orchestrator and the MCP server."""

import asyncio
import json
import logging
import os
import random
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Simulated latency (used by call_tool_with_metrics — see Section 9 of
# architecture/EVALUATION_FRAMEWORK.md). Only check_availability cares
# about window width; other tools pay the base overhead only.
# ----------------------------------------------------------------------


def _days_queried(arguments: dict) -> int:
    """Compute the day-count of a check_availability window.

    Returns 1 when start/end are missing or unparseable, since the latency
    model still charges the base overhead in that case.
    """
    start = arguments.get("start_datetime")
    end = arguments.get("end_datetime")
    if not start or not end:
        return 1
    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end)
    except (TypeError, ValueError):
        return 1
    delta = end_dt.date() - start_dt.date()
    return max(1, delta.days + 1)


def _compute_simulated_latency_ms(tool_name: str, arguments: dict, model: dict) -> float:
    """Apply the latency model from EVALUATION_FRAMEWORK.md Section 9a.

    ``model`` is a dict with keys ``base_overhead_ms``, ``per_day_cost_ms``,
    ``jitter_sigma_ms``. Window width matters only for ``check_availability``.
    Negative results are clipped to 0.
    """
    base = float(model.get("base_overhead_ms", 0.0))
    per_day = float(model.get("per_day_cost_ms", 0.0))
    sigma = float(model.get("jitter_sigma_ms", 0.0))

    days = _days_queried(arguments) if tool_name == "check_availability" else 0
    jitter = random.gauss(0.0, sigma) if sigma > 0 else 0.0
    return max(0.0, base + per_day * days + jitter)


class MCPBridge:
    """Wraps the MCP stdio client with explicit connect/disconnect lifecycle.

    Unlike a plain ``async with`` block, this class lets the caller open the
    connection once (e.g. at Chainlit session start) and reuse it across many
    tool calls before closing it at session end.
    """

    def __init__(self, server_script_path: str) -> None:
        """Initialise the bridge.

        Args:
            server_script_path: Filesystem path to ``mcp_server/server.py``.
        """
        self._server_script_path = server_script_path
        self._stdio_context = None
        self._session_context = None
        self._session: ClientSession | None = None

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """Open the MCP stdio transport and initialise a ClientSession.

        Safe to await from any async context.  Logs a warning and returns
        immediately if already connected.
        """
        if self.is_connected:
            logger.warning("MCPBridge.connect() called while already connected — ignoring.")
            return

        # Derive the project root from the server script path so that the
        # subprocess can import `mcp_server` as a package.
        # e.g. "mcp_server/server.py" -> absolute project root two levels up.
        server_abs = Path(os.path.abspath(self._server_script_path))
        project_root = str(server_abs.parent.parent)

        # Run as a module (-m mcp_server.server) so Python adds project_root to
        # sys.path automatically — running as a plain script would add the
        # mcp_server/ subdirectory instead, breaking `import mcp_server.tools`.
        # sys.executable ensures we use the active conda env, not a system Python.
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_server.server"],
            cwd=project_root,
        )

        # Manually enter the async context managers so the connection stays
        # open beyond a single ``async with`` block.
        self._stdio_context = stdio_client(server_params)
        read_stream, write_stream = await self._stdio_context.__aenter__()

        self._session_context = ClientSession(read_stream, write_stream)
        self._session = await self._session_context.__aenter__()
        await self._session.initialize()

        logger.info("MCPBridge connected to %s", self._server_script_path)

    async def disconnect(self) -> None:
        """Cleanly close the session and the stdio transport."""
        if self._session_context is not None:
            await self._session_context.__aexit__(None, None, None)
            self._session_context = None
            self._session = None

        if self._stdio_context is not None:
            await self._stdio_context.__aexit__(None, None, None)
            self._stdio_context = None

        logger.info("MCPBridge disconnected.")

    @property
    def is_connected(self) -> bool:
        """Return ``True`` if a live ClientSession exists."""
        return self._session is not None

    # ------------------------------------------------------------------
    # Tool calls
    # ------------------------------------------------------------------

    async def call_tool(self, tool_name: str, arguments: dict) -> dict | list:
        """Call an MCP tool and return the parsed result.

        Args:
            tool_name: Name of the MCP tool (e.g. ``"get_appointment_topics"``).
            arguments: Keyword arguments forwarded to the tool.

        Returns:
            Parsed JSON from the tool's TextContent response(s).  FastMCP
            creates one ``TextContent`` block per list element when a tool
            returns a list, so all blocks are parsed and collected.  If the
            response contains a single block the parsed value is returned
            directly (typically a dict); multiple blocks are returned as a
            list.
            On any error, returns ``{"status": "error", "message": "<reason>"}``.

        Raises:
            RuntimeError: If called before :meth:`connect`.
        """
        if not self.is_connected:
            raise RuntimeError("MCPBridge is not connected. Call connect() first.")

        try:
            result = await self._session.call_tool(tool_name, arguments)
            # result.content is a list of Content objects.  FastMCP creates
            # one TextContent per element when a tool returns a list, so we
            # must parse ALL blocks — not just [0].
            parsed = [
                json.loads(block.text)
                for block in result.content
                if hasattr(block, "text")
            ]
            if len(parsed) == 1:
                return parsed[0]
            return parsed
        except Exception as exc:
            logger.error("MCPBridge.call_tool(%s) failed: %s", tool_name, exc)
            return {"status": "error", "message": str(exc)}

    async def call_tool_with_metrics(
        self,
        tool_name: str,
        arguments: dict,
        *,
        latency_model: dict | None = None,
        simulate_latency: bool = False,
    ) -> dict:
        """Call an MCP tool and return both the result and timing metrics.

        Wraps :meth:`call_tool`. Used by the executor when conversation
        recording is active so the evaluation record captures realistic
        latency information without disturbing the original ``call_tool``
        contract.

        Args:
            tool_name: Name of the MCP tool.
            arguments: Forwarded to the tool.
            latency_model: Optional dict shaped like ``LatencyModel``:
                ``{base_overhead_ms, per_day_cost_ms, jitter_sigma_ms}``.
                When ``simulate_latency`` is True, the simulated value is
                computed from this and asyncio.sleep()'d before the call.
            simulate_latency: When True, inject simulated latency BEFORE the
                real call so the agent experiences wall-clock cost similar
                to a production server. Defaults to False so production
                Chainlit sessions stay fast.

        Returns:
            ``{"response": <parsed>, "actual_latency_ms": float,
                "simulated_latency_ms": float | None, "success": bool}``
        """
        sim_ms: float | None = None
        if simulate_latency and latency_model is not None:
            sim_ms = _compute_simulated_latency_ms(tool_name, arguments, latency_model)
            if sim_ms > 0:
                await asyncio.sleep(sim_ms / 1000.0)

        started = time.perf_counter()
        response = await self.call_tool(tool_name, arguments)
        actual_ms = (time.perf_counter() - started) * 1000.0

        success = True
        if isinstance(response, dict) and response.get("status") == "error":
            success = False

        return {
            "response": response,
            "actual_latency_ms": actual_ms,
            "simulated_latency_ms": sim_ms,
            "success": success,
        }

    # ------------------------------------------------------------------
    # Debugging helpers
    # ------------------------------------------------------------------

    async def list_tools(self) -> list[str]:
        """Return the names of all tools registered on the MCP server.

        Useful for smoke-testing the connection.
        """
        if not self.is_connected:
            raise RuntimeError("MCPBridge is not connected. Call connect() first.")

        response = await self._session.list_tools()
        return [tool.name for tool in response.tools]
