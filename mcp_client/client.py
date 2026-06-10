"""
mcp_client/client.py — Async MCP client for the appointment scheduler server.

Connects to mcp_server.server via stdio transport (server runs as a subprocess).
Designed to be used as an async context manager by the LangGraph executor node.

Usage:
    async with AppointmentMCPClient() as client:
        topics = await client.call_tool("get_appointment_topics", {})
"""

import asyncio
import json
import sys
from contextlib import AsyncExitStack
from datetime import datetime, timedelta
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from mcp.types import TextContent

from mcp_server.config import LEAD_TIME_HOURS, TIMEZONE


class AppointmentMCPClient:
    """Async MCP client that spawns the appointment scheduler server as a subprocess.

    Manages connection lifecycle via AsyncExitStack so both the stdio transport
    and the ClientSession are cleaned up correctly on exit.
    """

    def __init__(self) -> None:
        self._stack = AsyncExitStack()
        self._session: ClientSession | None = None

    # ------------------------------------------------------------------
    # Connection lifecycle
    # ------------------------------------------------------------------

    async def connect(self) -> None:
        """Spawn the MCP server subprocess and initialise the session.

        Uses sys.executable so the server runs under the same interpreter
        and environment as the client — no PATH resolution issues.
        """
        params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "mcp_server.server"],
        )
        read_stream, write_stream = await self._stack.enter_async_context(
            stdio_client(params)
        )
        self._session = await self._stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await self._session.initialize()

    async def close(self) -> None:
        """Shut down the session and the server subprocess cleanly."""
        await self._stack.aclose()
        self._session = None

    # ------------------------------------------------------------------
    # Async context manager
    # ------------------------------------------------------------------

    async def __aenter__(self) -> "AppointmentMCPClient":
        await self.connect()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def list_tools(self) -> list[dict]:
        """Return the tools registered on the server.

        Returns a list of dicts with keys: name, description, inputSchema.
        """
        self._require_session()
        result = await self._session.list_tools()  # type: ignore[union-attr]
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema,
            }
            for tool in result.tools
        ]

    async def call_tool(self, tool_name: str, arguments: dict) -> Any:
        """Call a server tool and return the parsed Python object.

        The MCP server serialises return values as JSON text inside a
        TextContent block. This method parses that JSON automatically so
        callers always receive native Python dicts / lists.

        Raises:
            RuntimeError: if the server signals isError=True.
            ValueError: if the response cannot be parsed as JSON.
        """
        self._require_session()
        result = await self._session.call_tool(tool_name, arguments)  # type: ignore[union-attr]

        if result.isError:
            raw = self._extract_text(result.content)
            raise RuntimeError(f"MCP tool '{tool_name}' returned an error: {raw}")

        raw_text = self._extract_text(result.content)
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"Could not parse response from '{tool_name}' as JSON: {exc}\n"
                f"Raw response: {raw_text!r}"
            ) from exc

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_session(self) -> None:
        if self._session is None:
            raise RuntimeError(
                "Not connected. Use 'async with AppointmentMCPClient() as client' "
                "or call connect() first."
            )

    @staticmethod
    def _extract_text(content: list) -> str:
        """Concatenate all TextContent blocks from a tool response."""
        parts: list[str] = []
        for item in content:
            if isinstance(item, TextContent):
                parts.append(item.text)
            elif hasattr(item, "text"):
                parts.append(str(item.text))
        return "".join(parts)


# ---------------------------------------------------------------------------
# Demo / __main__
# ---------------------------------------------------------------------------


def _next_weekday(weekday: int) -> datetime:
    """Return the next occurrence of *weekday* (0=Mon … 6=Sun) past lead time."""
    now = datetime.now(tz=TIMEZONE)
    earliest = now + timedelta(hours=LEAD_TIME_HOURS)
    candidate = earliest.replace(hour=0, minute=0, second=0, microsecond=0)
    # Advance day-by-day until we land on the target weekday
    while candidate.weekday() != weekday:
        candidate += timedelta(days=1)
    # If that day is still within lead time, skip to the following week
    if candidate < earliest:
        candidate += timedelta(weeks=1)
    return candidate


async def _demo() -> None:
    print("=" * 60)
    print("Appointment Scheduler MCP Client — Demo")
    print("=" * 60)

    async with AppointmentMCPClient() as client:

        # ----------------------------------------------------------
        # 1. Discover available tools
        # ----------------------------------------------------------
        tools = await client.list_tools()
        print(f"\n[1] Available tools ({len(tools)}):")
        for t in tools:
            print(f"    • {t['name']}")

        # ----------------------------------------------------------
        # 2. Get appointment topics
        # ----------------------------------------------------------
        topics: list[dict] = await client.call_tool("get_appointment_topics", {})
        print(f"\n[2] Topics ({len(topics)}):")
        for t in topics:
            print(f"    • {t['topic_id']}: {t['topic_name']}")

        # ----------------------------------------------------------
        # 3. Contact media for mortgage
        # ----------------------------------------------------------
        media: list[dict] = await client.call_tool(
            "get_appointment_contact_medium", {"topic_id": "mortgage"}
        )
        print(f"\n[3] Contact media for 'mortgage' ({len(media)}):")
        for m in media:
            print(f"    • {m['contact_medium_id']}: {m['contact_medium_name']}")

        # ----------------------------------------------------------
        # 4. Check availability — next Tuesday (weekday 1)
        # ----------------------------------------------------------
        tuesday = _next_weekday(weekday=1)  # 1 = Tuesday
        window_start = tuesday.isoformat()
        window_end = (tuesday + timedelta(days=1)).isoformat()

        print(f"\n[4] Checking availability for investing/online on {tuesday.date()} …")
        slots = await client.call_tool(
            "check_availability",
            {
                "topic_id": "investing",
                "contact_medium_id": "online",
                "start_datetime": window_start,
                "end_datetime": window_end,
            },
        )

        if not slots:
            print("    No slots available on that day (fully booked). Try a different date.")
            return

        print(f"    {len(slots)} slot(s) found:")
        for s in slots[:5]:  # show at most 5
            print(f"    • {s['datetime_start']}  →  {s['datetime_end']}")
        if len(slots) > 5:
            print(f"    … and {len(slots) - 5} more")

        # ----------------------------------------------------------
        # 5. Book the first available slot
        # ----------------------------------------------------------
        first_slot = slots[0]
        print(f"\n[5] Booking slot: {first_slot['datetime_start']} …")
        booking = await client.call_tool(
            "book_appointment",
            {
                "topic_id": "investing",
                "contact_medium_id": "online",
                "datetime_start": first_slot["datetime_start"],
                "datetime_end": first_slot["datetime_end"],
            },
        )
        print(f"    Status     : {booking['status']}")
        print(f"    Booking ID : {booking['booking_id']}")
        print(f"    Topic      : {booking['details']['topic_name']}")
        print(f"    Medium     : {booking['details']['contact_medium_name']}")
        print(f"    Time       : {booking['details']['datetime_start']}")

        # ----------------------------------------------------------
        # 6. Verify the booked slot is gone
        # ----------------------------------------------------------
        print(f"\n[6] Re-checking availability for the same 1-hour window …")
        recheck = await client.call_tool(
            "check_availability",
            {
                "topic_id": "investing",
                "contact_medium_id": "online",
                "start_datetime": first_slot["datetime_start"],
                "end_datetime": first_slot["datetime_end"],
            },
        )
        booked_still_listed = any(
            s["datetime_start"] == first_slot["datetime_start"] for s in recheck
        )
        if booked_still_listed:
            print("    FAIL — booked slot is still showing as available!")
        else:
            print("    OK — booked slot no longer appears in availability.")

    print("\nDemo complete.")


if __name__ == "__main__":
    asyncio.run(_demo())
