"""Execute node: calls the MCP server via MCPBridge and returns the tool result.

When ``config["configurable"]["expansion_policy_enabled"]`` is set, ``check_availability``
calls go through a deterministic executor-side expansion policy (``orchestrator/expansion.py``):
a session availability cache short-circuits known ranges, and an empty result triggers a
bounded widening ladder so the agent gets nearby slots in the same turn instead of looping.
With the flag off (the default — baseline and the NLP arms), this node is byte-identical to
its pre-expansion behaviour.
"""

import logging
from datetime import datetime, timezone

from langchain_core.runnables import RunnableConfig

from mcp_server.config import TIMEZONE
from orchestrator.expansion import (
    AvailabilityCache,
    build_ladder,
    days_in_window,
    parse_iso,
    run_expansion,
)
from orchestrator.mcp_bridge import MCPBridge
from orchestrator.nodes.agent import _reference_now_from_config
from orchestrator.state import ConversationState

logger = logging.getLogger(__name__)


async def execute_node(state: ConversationState, config: RunnableConfig) -> dict:
    """Execute the pending MCP tool call and store the result in state.

    Reads ``pending_tool_call`` from state, calls the MCP server via the bridge
    supplied in ``config["configurable"]["mcp_bridge"]``, and returns a state
    update that:
    - Clears ``pending_tool_call`` (tool has been executed).
    - Sets ``tool_result`` so the agent node can build a function_response on
      the next iteration.

    If ``config["configurable"]["recorder"]`` is present, the tool call is
    recorded into the evaluation ConversationRecord with both actual and
    (optionally) simulated latency.
    """
    mcp_bridge: MCPBridge = config["configurable"]["mcp_bridge"]
    recorder = config["configurable"].get("recorder")
    simulate_latency: bool = config["configurable"].get("simulate_latency", False)
    latency_model = config["configurable"].get("latency_model")
    expansion_on: bool = bool(config["configurable"].get("expansion_policy_enabled", False))
    cache: AvailabilityCache | None = config["configurable"].get("availability_cache")
    tool_call = state["pending_tool_call"]

    # Safety check — should never happen given the conditional edge logic.
    if tool_call is None:
        logger.warning("execute_node called with no pending_tool_call — skipping.")
        return {}

    # --- Expansion policy path (opt-in) ---
    # Only check_availability is widened; everything else (and the whole baseline)
    # uses the unchanged code path below.
    if expansion_on and cache is not None and tool_call["name"] == "check_availability":
        return await _execute_check_availability_expanded(
            config,
            mcp_bridge=mcp_bridge,
            recorder=recorder,
            simulate_latency=simulate_latency,
            latency_model=latency_model,
            cache=cache,
            tool_call=tool_call,
        )

    logger.info("Executing tool: %s with args: %s", tool_call["name"], tool_call["args"])

    metrics = await mcp_bridge.call_tool_with_metrics(
        tool_call["name"],
        tool_call["args"],
        latency_model=latency_model,
        simulate_latency=simulate_latency,
    )
    result = metrics["response"]

    logger.info("Tool result: %s", result)

    debug_record = {
        "node": "execute_node",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "mcp_tool_call",
        "details": {
            "tool_name": tool_call["name"],
            "parameters": tool_call["args"],
            "response": result,
            "success": metrics["success"],
            "actual_latency_ms": metrics["actual_latency_ms"],
            "simulated_latency_ms": metrics["simulated_latency_ms"],
        },
    }

    if recorder is not None:
        recorder.record_tool_call(
            tool_name=tool_call["name"],
            parameters=tool_call["args"],
            response=result,
            simulated_latency_ms=metrics["simulated_latency_ms"],
            actual_latency_ms=metrics["actual_latency_ms"],
            success=metrics["success"],
            error_message=(result.get("message") if isinstance(result, dict) and not metrics["success"] else None),
        )

    # Per-key cache invalidation on a successful booking — regardless of the
    # expansion flag's current value (2026-06-10): the cache object outlives a
    # mid-session toggle (it is created once per chat/scenario), so a booking
    # made while the policy is OFF must still drop that day, or re-enabling the
    # policy could serve the just-booked slot from stale cache. With no cache
    # supplied (baseline runner path) this is a no-op and the path is unchanged.
    if cache is not None and tool_call["name"] == "book_appointment" and metrics["success"]:
        _invalidate_booked_day(cache, tool_call["args"])

    return {
        "pending_tool_call": None,  # clear — tool has been executed
        "tool_result": {
            "name": tool_call["name"],
            "response": result,
        },
        "debug_log": [debug_record],
    }


def _invalidate_booked_day(cache: AvailabilityCache, args: dict) -> None:
    """Drop the cached availability for the (topic, medium, date) just booked."""
    booked = parse_iso(args.get("datetime_start"))
    if booked is None:
        return
    cache.invalidate(args.get("topic_id"), args.get("contact_medium_id"), booked.date())


async def _execute_check_availability_expanded(
    config: RunnableConfig,
    *,
    mcp_bridge: MCPBridge,
    recorder,
    simulate_latency: bool,
    latency_model: dict | None,
    cache: AvailabilityCache,
    tool_call: dict,
) -> dict:
    """Run check_availability through the cache + bounded expansion ladder.

    Step 0 is the agent's *exact* requested window — always the first recorded
    check_availability call so the parse-accuracy KPI (which reads the first call's
    params) still measures the agent's datetime choice, never the executor's widened
    window. The widening ladder fires only on a success + empty-list result.
    """
    args = tool_call["args"]
    topic_id = args.get("topic_id")
    medium_id = args.get("contact_medium_id")
    start_dt = parse_iso(args.get("start_datetime"))
    end_dt = parse_iso(args.get("end_datetime"))
    now = _reference_now_from_config(config) or datetime.now(TIMEZONE)

    step0: dict = {"served_from_cache": False, "mcp_call": False}

    # --- Step 0: the agent's exact window ---
    if start_dt is not None and end_dt is not None and start_dt < end_dt and cache.covers(
        topic_id, medium_id, days_in_window(start_dt, end_dt)
    ):
        # Whole window already known this session — answer from cache, no MCP call.
        result = cache.slots_in_window(topic_id, medium_id, start_dt, end_dt)
        success = True
        step0["served_from_cache"] = True
    else:
        metrics = await mcp_bridge.call_tool_with_metrics(
            "check_availability", args,
            latency_model=latency_model, simulate_latency=simulate_latency,
        )
        result = metrics["response"]
        success = metrics["success"]
        step0["mcp_call"] = True
        if recorder is not None:
            recorder.record_tool_call(
                tool_name="check_availability",
                parameters=args,
                response=result,
                simulated_latency_ms=metrics["simulated_latency_ms"],
                actual_latency_ms=metrics["actual_latency_ms"],
                success=success,
                error_message=(
                    result.get("message")
                    if isinstance(result, dict) and not success
                    else None
                ),
            )

    ladder_debug: list[dict] = []
    # --- Ladder fires only on success + empty list (never on errors) ---
    if success and isinstance(result, list) and not result and start_dt is not None:
        ladder = build_ladder(start_dt, end_dt, now=now)
        result, ladder_debug = await run_expansion(
            bridge=mcp_bridge,
            recorder=recorder,
            simulate_latency=simulate_latency,
            latency_model=latency_model,
            topic_id=topic_id,
            contact_medium_id=medium_id,
            ladder=ladder,
            cache=cache,
        )

    logger.info(
        "check_availability (expansion): step0=%s ladder_steps=%d -> %s slots",
        "cache" if step0["served_from_cache"] else "mcp",
        len(ladder_debug),
        len(result) if isinstance(result, list) else "error",
    )

    # Persist the clean per-turn ladder-fire signal into the evaluation record
    # (TurnRecord.ladder_steps). Recording only — does not affect agent behaviour.
    if recorder is not None and ladder_debug:
        recorder.record_ladder_steps(ladder_debug)

    debug_record = {
        "node": "execute_node",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": "mcp_tool_call_expanded",
        "details": {
            "tool_name": "check_availability",
            "parameters": args,
            "step0": step0,
            "ladder_steps": ladder_debug,
            "result_count": len(result) if isinstance(result, list) else None,
        },
    }

    return {
        "pending_tool_call": None,
        "tool_result": {"name": "check_availability", "response": result},
        "debug_log": [debug_record],
    }
