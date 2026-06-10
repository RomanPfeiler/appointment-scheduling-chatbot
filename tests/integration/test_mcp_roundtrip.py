"""
tests/integration/test_mcp_roundtrip.py — Integration tests for the MCP wire protocol.

Spawns the FastMCP server as a subprocess via MCPBridge and exercises each tool
over the stdio transport. Catches:
- FastMCP serialisation regressions (e.g. list-of-dicts → single TextContent vs many)
- mcp[cli] version drift
- MCPBridge connect/disconnect lifecycle bugs
- Error-dict contract violations (tools must return dicts, never raise across the wire)

Slow tests — marked @pytest.mark.integration so they can be skipped during fast
local iteration: pytest -m "not integration".
"""

from contextlib import asynccontextmanager
from datetime import datetime, timedelta

import pytest

from mcp_server.config import LEAD_TIME_HOURS, SCHEDULING_HORIZON_DAYS, TIMEZONE
from orchestrator.mcp_bridge import MCPBridge

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Bridge helper
# ---------------------------------------------------------------------------
#
# We deliberately do NOT use a pytest_asyncio fixture for the bridge. anyio's
# stdio_client must be entered and exited from the same asyncio task, and
# pytest-asyncio yield fixtures sometimes run teardown in a different task —
# producing "Attempted to exit cancel scope in a different task" errors.
# An asynccontextmanager invoked inside each test body keeps both lifecycle
# events in the same task.


@asynccontextmanager
async def connected_bridge():
    b = MCPBridge(server_script_path="mcp_server/server.py")
    await b.connect()
    try:
        await b.call_tool("reset_bookings", {})
        yield b
    finally:
        await b.disconnect()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _find_available_slot(bridge: MCPBridge) -> dict:
    """Walk forward in 3-day chunks until check_availability returns a slot."""
    now = datetime.now(tz=TIMEZONE)
    start = now + timedelta(hours=LEAD_TIME_HOURS + 48)

    for _ in range(SCHEDULING_HORIZON_DAYS // 3 + 1):
        end = start + timedelta(days=3)
        result = await bridge.call_tool(
            "check_availability",
            {
                "topic_id": "investing",
                "contact_medium_id": "online",
                "start_datetime": start.isoformat(),
                "end_datetime": end.isoformat(),
            },
        )
        if isinstance(result, list) and result:
            return result[0]
        start = end

    raise RuntimeError("No slot found over scheduling horizon — check mock_data seeding.")


# ---------------------------------------------------------------------------
# Tool discovery
# ---------------------------------------------------------------------------


async def test_list_tools_returns_all_five():
    async with connected_bridge() as bridge:
        names = await bridge.list_tools()
    assert {
        "get_appointment_topics",
        "get_appointment_contact_medium",
        "check_availability",
        "book_appointment",
        "reset_bookings",
    } <= set(names)


# ---------------------------------------------------------------------------
# get_appointment_topics
# ---------------------------------------------------------------------------


async def test_get_topics_roundtrip():
    """A list-returning tool must come back as a Python list of dicts."""
    async with connected_bridge() as bridge:
        result = await bridge.call_tool("get_appointment_topics", {})
    assert isinstance(result, list)
    assert len(result) == 3
    assert all("topic_id" in t and "topic_name" in t for t in result)


# ---------------------------------------------------------------------------
# get_appointment_contact_medium
# ---------------------------------------------------------------------------


async def test_get_contact_medium_valid_topic():
    async with connected_bridge() as bridge:
        result = await bridge.call_tool(
            "get_appointment_contact_medium", {"topic_id": "investing"}
        )
    assert isinstance(result, list)
    ids = {m["contact_medium_id"] for m in result}
    assert ids == {"branch", "online", "phone"}


async def test_get_contact_medium_invalid_topic_returns_error_dict():
    """MCP tools MUST return error dicts, never raise across the wire."""
    async with connected_bridge() as bridge:
        result = await bridge.call_tool(
            "get_appointment_contact_medium", {"topic_id": "nonexistent"}
        )
    assert isinstance(result, dict)
    assert result.get("status") == "error"
    assert "message" in result


# ---------------------------------------------------------------------------
# check_availability
# ---------------------------------------------------------------------------


async def test_check_availability_returns_list():
    now = datetime.now(tz=TIMEZONE)
    start = (now + timedelta(hours=LEAD_TIME_HOURS + 48)).isoformat()
    end = (now + timedelta(hours=LEAD_TIME_HOURS + 48, days=3)).isoformat()
    async with connected_bridge() as bridge:
        result = await bridge.call_tool(
            "check_availability",
            {
                "topic_id": "investing",
                "contact_medium_id": "online",
                "start_datetime": start,
                "end_datetime": end,
            },
        )
    assert isinstance(result, list)


async def test_check_availability_invalid_input_returns_error_dict():
    async with connected_bridge() as bridge:
        result = await bridge.call_tool(
            "check_availability",
            {
                "topic_id": "investing",
                "contact_medium_id": "online",
                "start_datetime": "not-a-date",
                "end_datetime": "also-not",
            },
        )
    assert isinstance(result, dict)
    assert result["status"] == "error"


# ---------------------------------------------------------------------------
# Full booking sequence
# ---------------------------------------------------------------------------


async def test_full_booking_sequence():
    """End-to-end: topics -> media -> availability -> book -> re-check.

    Mirrors the demo in mcp_client/client.py. Asserts the wire protocol survives
    a realistic multi-call session and that the booking store mutates correctly.
    """
    async with connected_bridge() as bridge:
        topics = await bridge.call_tool("get_appointment_topics", {})
        assert any(t["topic_id"] == "investing" for t in topics)

        media = await bridge.call_tool(
            "get_appointment_contact_medium", {"topic_id": "investing"}
        )
        assert any(m["contact_medium_id"] == "online" for m in media)

        slot = await _find_available_slot(bridge)

        booking = await bridge.call_tool(
            "book_appointment",
            {
                "topic_id": "investing",
                "contact_medium_id": "online",
                "datetime_start": slot["datetime_start"],
                "datetime_end": slot["datetime_end"],
            },
        )
        assert booking["status"] == "success"
        assert booking["booking_id"].startswith("BK-")
        assert booking["details"]["topic_name"] == "Investing"
        assert booking["details"]["contact_medium_name"] == "Online Meeting"

        # The booked slot must disappear from the same 1-hour window.
        recheck = await bridge.call_tool(
            "check_availability",
            {
                "topic_id": "investing",
                "contact_medium_id": "online",
                "start_datetime": slot["datetime_start"],
                "end_datetime": slot["datetime_end"],
            },
        )
        assert isinstance(recheck, list)
        assert not any(s["datetime_start"] == slot["datetime_start"] for s in recheck)


async def test_double_booking_returns_error():
    async with connected_bridge() as bridge:
        slot = await _find_available_slot(bridge)
        args = {
            "topic_id": "investing",
            "contact_medium_id": "online",
            "datetime_start": slot["datetime_start"],
            "datetime_end": slot["datetime_end"],
        }

        first = await bridge.call_tool("book_appointment", args)
        assert first["status"] == "success"

        second = await bridge.call_tool("book_appointment", args)
        assert second["status"] == "error"
        assert "message" in second


# ---------------------------------------------------------------------------
# reset_bookings
# ---------------------------------------------------------------------------


async def test_reset_bookings_clears_state():
    """After reset, the same slot is bookable again."""
    async with connected_bridge() as bridge:
        slot = await _find_available_slot(bridge)
        args = {
            "topic_id": "investing",
            "contact_medium_id": "online",
            "datetime_start": slot["datetime_start"],
            "datetime_end": slot["datetime_end"],
        }

        first = await bridge.call_tool("book_appointment", args)
        assert first["status"] == "success"

        reset = await bridge.call_tool("reset_bookings", {})
        assert reset["status"] == "reset"

        second = await bridge.call_tool("book_appointment", args)
        assert second["status"] == "success"
        assert second["booking_id"] != first["booking_id"]


# ---------------------------------------------------------------------------
# Bridge lifecycle
# ---------------------------------------------------------------------------


async def test_call_tool_without_connect_raises():
    """The bridge must refuse calls before connect()."""
    b = MCPBridge(server_script_path="mcp_server/server.py")
    assert not b.is_connected
    with pytest.raises(RuntimeError):
        await b.call_tool("get_appointment_topics", {})
