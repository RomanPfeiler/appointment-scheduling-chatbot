"""
server.py — FastMCP server wiring layer.

Exposes the tools from tools.py over the MCP stdio transport.
All business logic lives in tools.py; this file is purely declaration.

Run directly:
    python -m mcp_server.server

Or via MCP inspector:
    mcp dev mcp_server/server.py
"""

from mcp.server.fastmcp import FastMCP

import mcp_server.tools as _tools

mcp = FastMCP("appointment-scheduler")


@mcp.tool()
def get_current_datetime() -> dict:
    """Return the current date and time in the Europe/Zurich timezone.

    Call this before checking availability whenever the user provides a relative
    time expression (e.g., 'next Wednesday', 'in three days', 'tomorrow morning').
    Use the returned date as the anchor for all date arithmetic.

    Returns a dict with:
      - datetime: ISO 8601 string with TZ offset (e.g. "2026-05-25T14:30:00+02:00")
      - date:     ISO 8601 date string (e.g. "2026-05-25")
      - weekday:  day name (e.g. "Monday")
      - week_number: ISO week number (int)
    """
    return _tools.get_current_datetime()


@mcp.tool()
def get_appointment_topics() -> list[dict]:
    """Return all available appointment topics.

    Use the returned topic_id values when calling get_appointment_contact_medium
    or check_availability.

    Returns a list of objects with topic_id and topic_name.
    """
    return _tools.get_appointment_topics()


@mcp.tool()
def get_appointment_contact_medium(topic_id: str) -> list[dict] | dict:
    """Return the contact media available for a given topic.

    Not all media are available for all topics:
    - Mortgage has no phone option (requires document review).
    - Pension has no branch option (handled remotely).

    Args:
        topic_id: A topic_id returned by get_appointment_topics.

    Returns a list of objects with contact_medium_id and contact_medium_name,
    or an error dict if topic_id is invalid.
    """
    return _tools.get_appointment_contact_medium(topic_id)


@mcp.tool()
def check_availability(
    topic_id: str,
    contact_medium_id: str,
    start_datetime: str,
    end_datetime: str,
) -> list[dict] | dict:
    """Return available 60-minute appointment slots within the requested window.

    Slots are generated dynamically relative to today. Weekends, fully-booked
    days, and slots within the next 24 hours are excluded automatically.

    If the requested range exceeds 3 days, only the first 3 days are checked.

    Args:
        topic_id: A topic_id from get_appointment_topics.
        contact_medium_id: A contact_medium_id from get_appointment_contact_medium.
        start_datetime: ISO 8601 string. Timezone defaults to Europe/Zurich if omitted.
        end_datetime:   ISO 8601 string. Timezone defaults to Europe/Zurich if omitted.

    Returns a list of {datetime_start, datetime_end} dicts (ISO 8601 strings),
    or an error dict on invalid input.
    """
    return _tools.check_availability(
        topic_id, contact_medium_id, start_datetime, end_datetime
    )


@mcp.tool()
def book_appointment(
    topic_id: str,
    contact_medium_id: str,
    datetime_start: str,
    datetime_end: str,
) -> dict:
    """Book an appointment slot returned by check_availability.

    The slot must exist in the generated availability and must not already be
    taken. Use the exact datetime_start / datetime_end values from
    check_availability to guarantee a match.

    Args:
        topic_id:           A topic_id from get_appointment_topics.
        contact_medium_id:  A contact_medium_id from get_appointment_contact_medium.
        datetime_start:     ISO 8601 string matching a slot from check_availability.
        datetime_end:       ISO 8601 string matching a slot from check_availability.

    Returns {"status": "success", "booking_id": "BK-XXXXXX", "details": {...}}
    or {"status": "error", "message": "..."}.
    """
    return _tools.book_appointment(
        topic_id, contact_medium_id, datetime_start, datetime_end
    )


@mcp.tool()
def reset_bookings() -> dict:
    """Clear all bookings from the in-memory store.

    Intended for testing and evaluation resets. Has no effect on slot
    generation (availability patterns are date-seeded and remain stable).

    Returns {"status": "reset"}.
    """
    return _tools.reset_bookings()


@mcp.tool()
def admin_set_availability_override(override_json: str) -> dict:
    """Set a fixed availability profile for the current evaluation scenario run.

    Parses override_json (a JSON object mapping ISO date strings to lists of
    "HH:MM-HH:MM" slot strings, all times in Europe/Zurich) and activates the
    override. While active, check_availability returns only the overridden slots;
    dates absent from the dict return empty.

    Intended for the evaluation runner only — not for production use.

    Args:
        override_json: JSON string, e.g. '{"2026-05-26": ["09:00-10:00"]}'

    Returns {"status": "ok", "dates_set": N} or an error dict.
    """
    return _tools.admin_set_availability_override(override_json)


@mcp.tool()
def admin_clear_availability_override() -> dict:
    """Deactivate the availability override and revert to seeded slot generation.

    Call this between evaluation scenario runs to ensure isolation.

    Returns {"status": "cleared"}.
    """
    return _tools.admin_clear_availability_override()


@mcp.tool()
def admin_set_clock_override(reference_date: str) -> dict:
    """Pin get_current_datetime() to the scenario's reference_date.

    Call this per evaluation scenario run (alongside the availability override) so
    the agent's get_current_datetime() shares the scenario's pinned clock
    (EVALUATION_FRAMEWORK §3a) — making scenario execution date-independent even
    when the run day differs from the suite anchor.

    Args:
        reference_date: ISO date string, e.g. "2026-06-01".

    Returns {"status": "ok", "clock": "<iso>"} or an error dict.
    """
    return _tools.admin_set_clock_override(reference_date)


@mcp.tool()
def admin_clear_clock_override() -> dict:
    """Revert get_current_datetime() to the real wall clock.

    Call this between evaluation scenario runs to ensure isolation.

    Returns {"status": "cleared"}.
    """
    return _tools.admin_clear_clock_override()


if __name__ == "__main__":
    mcp.run()
