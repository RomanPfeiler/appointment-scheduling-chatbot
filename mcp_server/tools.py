"""
tools.py — Pure business logic functions exposed as MCP tools.

Each function maps 1-to-1 with a tool in the MCP contract (architecture.md §5).
All inputs arrive as plain strings (MCP wire format); outputs are plain dicts
suitable for JSON serialisation. No exceptions propagate — errors always return
{"status": "error", "message": "..."}.
"""

import json
from datetime import date, datetime, timedelta

from mcp_server.config import MAX_AVAILABILITY_WINDOW_DAYS, TIMEZONE
from mcp_server.mock_data import BookingStore, clear_availability_override
from mcp_server.mock_data import generate_available_slots, set_availability_override
from mcp_server.mock_data import is_override_active
from mcp_server.mock_data import (
    clear_clock_override,
    get_clock_override,
    set_clock_override,
)
from mcp_server.mock_data import get_contact_media as _get_contact_media
from mcp_server.mock_data import get_topics as _get_topics
from mcp_server.models import TimeSlot

# Single shared BookingStore for the lifetime of this server process.
booking_store = BookingStore()


# ---------------------------------------------------------------------------
# Datetime parsing helper
# ---------------------------------------------------------------------------


def _parse_dt(value: str) -> datetime:
    """Parse an ISO 8601 datetime string and return a timezone-aware datetime.

    If the string carries no UTC offset or tzinfo, Europe/Zurich is assumed.
    Raises ValueError for unparseable input.
    """
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TIMEZONE)
    return dt


# ---------------------------------------------------------------------------
# MCP tool functions
# ---------------------------------------------------------------------------


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
    # During an evaluation scenario run the clock is pinned to the scenario's
    # reference_date (EVALUATION_FRAMEWORK §3a) so the agent's date arithmetic
    # shares one clock with the availability override; production returns real now.
    now = get_clock_override() or datetime.now(tz=TIMEZONE)
    return {
        "datetime": now.isoformat(),
        "date": now.date().isoformat(),
        "weekday": now.strftime("%A"),
        "week_number": now.isocalendar()[1],
    }


def get_appointment_topics() -> list[dict]:
    """Return all available appointment topics.

    Use the returned topic_id values when calling get_appointment_contact_medium
    or check_availability.

    Returns a list of objects with topic_id and topic_name.
    """
    topics = _get_topics()
    return [t.model_dump() for t in topics]


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
    try:
        media = _get_contact_media(topic_id)
        return [m.model_dump() for m in media]
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}


def check_availability(
    topic_id: str,
    contact_medium_id: str,
    start_datetime: str,
    end_datetime: str,
) -> list[dict] | dict:
    """Return available 60-minute appointment slots within the requested window.

    Slots are generated dynamically relative to today. Weekends, fully-booked
    days, and slots within the next 24 hours are excluded automatically.

    If the requested range exceeds MAX_AVAILABILITY_WINDOW_DAYS, only the first
    3 days are checked (the orchestrator should chunk larger windows).

    Args:
        topic_id: A topic_id from get_appointment_topics.
        contact_medium_id: A contact_medium_id from get_appointment_contact_medium.
        start_datetime: ISO 8601 string. Timezone defaults to Europe/Zurich if omitted.
        end_datetime:   ISO 8601 string. Timezone defaults to Europe/Zurich if omitted.

    Returns a list of {datetime_start, datetime_end} dicts (ISO 8601 strings),
    or an error dict on invalid input.
    """
    # --- Parse datetimes ---
    try:
        start_dt = _parse_dt(start_datetime)
        end_dt = _parse_dt(end_datetime)
    except (ValueError, TypeError) as exc:
        return {"status": "error", "message": f"Invalid datetime format: {exc}"}

    # --- Basic range validation ---
    if start_dt >= end_dt:
        return {
            "status": "error",
            "message": "start_datetime must be before end_datetime.",
        }

    # Skip the wall-clock past-window guard while a scenario override is active:
    # the evaluation runner pins scenario dates to a fixed reference_date that may
    # be in the past relative to the real clock, and the override path already
    # bypasses lead-time/past filtering in generate_available_slots
    # (EVALUATION_FRAMEWORK §3a). In production (no override) the guard stands.
    if not is_override_active():
        now = datetime.now(tz=TIMEZONE)
        if end_dt <= now:
            return {
                "status": "error",
                "message": "end_datetime is in the past. Please provide a future date range.",
            }

    # --- Safety cap: max window per call ---
    max_end = start_dt + timedelta(days=MAX_AVAILABILITY_WINDOW_DAYS)
    if end_dt > max_end:
        end_dt = max_end

    # --- Generate slots ---
    try:
        slots = generate_available_slots(
            topic_id=topic_id,
            contact_medium_id=contact_medium_id,
            start_dt=start_dt,
            end_dt=end_dt,
            store=booking_store,
        )
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}

    return [slot.to_iso() for slot in slots]


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
    # --- Parse datetimes ---
    try:
        dt_start = _parse_dt(datetime_start)
        dt_end = _parse_dt(datetime_end)
    except (ValueError, TypeError) as exc:
        return {"status": "error", "message": f"Invalid datetime format: {exc}"}

    # --- Build TimeSlot (also validates start < end via Pydantic) ---
    try:
        slot = TimeSlot(datetime_start=dt_start, datetime_end=dt_end)
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}

    # --- Attempt booking ---
    try:
        result = booking_store.book(
            topic_id=topic_id,
            contact_medium_id=contact_medium_id,
            slot=slot,
        )
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}

    return {
        "status": "success",
        "booking_id": result.booking_id,
        "details": {
            "topic_name": result.topic_name,
            "contact_medium_name": result.contact_medium_name,
            "datetime_start": result.datetime_start.isoformat(),
            "datetime_end": result.datetime_end.isoformat(),
        },
    }


def reset_bookings() -> dict:
    """Clear all bookings from the in-memory store.

    Intended for testing and evaluation resets. Has no effect on slot
    generation (availability patterns are date-seeded and remain stable).

    Returns {"status": "reset"}.
    """
    booking_store.reset()
    return {"status": "reset"}


# ---------------------------------------------------------------------------
# Admin tools — evaluation runner use only
# ---------------------------------------------------------------------------


def admin_set_availability_override(override_json: str) -> dict:
    """Set a fixed availability profile for the current scenario run.

    Parses *override_json* (a JSON object mapping ISO date strings to lists of
    ``"HH:MM-HH:MM"`` slot strings, all times in Europe/Zurich) and activates
    the override in ``mock_data``.  While active, ``check_availability`` returns
    only the overridden slots; dates absent from the dict return empty.

    Intended for the evaluation runner — not for production use.

    Args:
        override_json: JSON string, e.g.
            ``'{"2026-05-26": ["09:00-10:00", "15:00-16:00"]}'``

    Returns ``{"status": "ok", "dates_set": N}`` or an error dict.
    """
    try:
        data: dict[str, list[str]] = json.loads(override_json)
    except Exception as exc:
        return {"status": "error", "message": f"Invalid JSON: {exc}"}

    slots_by_date: dict[date, list[TimeSlot]] = {}
    for date_str, slot_strs in data.items():
        try:
            d = date.fromisoformat(date_str)
        except ValueError as exc:
            return {"status": "error", "message": f"Invalid date '{date_str}': {exc}"}

        slots: list[TimeSlot] = []
        for slot_str in slot_strs:
            try:
                start_part, end_part = slot_str.split("-", 1)
                sh, sm = map(int, start_part.strip().split(":"))
                eh, em = map(int, end_part.strip().split(":"))
                slot_start = datetime(d.year, d.month, d.day, sh, sm, 0, tzinfo=TIMEZONE)
                slot_end = datetime(d.year, d.month, d.day, eh, em, 0, tzinfo=TIMEZONE)
                slots.append(TimeSlot(datetime_start=slot_start, datetime_end=slot_end))
            except Exception as exc:
                return {"status": "error", "message": f"Invalid slot '{slot_str}': {exc}"}

        slots_by_date[d] = slots

    set_availability_override(slots_by_date)
    return {"status": "ok", "dates_set": len(slots_by_date)}


def admin_clear_availability_override() -> dict:
    """Deactivate the availability override and revert to seeded slot generation.

    Call this between scenario runs to ensure isolation.

    Returns ``{"status": "cleared"}``.
    """
    clear_availability_override()
    return {"status": "cleared"}


def admin_set_clock_override(reference_date: str) -> dict:
    """Pin ``get_current_datetime`` to noon Europe/Zurich on ``reference_date``.

    Mirrors the availability override: the runner calls this per scenario so the
    agent's ``get_current_datetime`` shares the scenario's pinned clock
    (EVALUATION_FRAMEWORK §3a), making scenario execution date-independent even
    when the run day differs from the suite anchor.

    Args:
        reference_date: ISO date string, e.g. ``"2026-06-01"``.

    Returns ``{"status": "ok", "clock": "<iso>"}`` or an error dict.
    """
    try:
        d = date.fromisoformat(reference_date)
    except (ValueError, TypeError) as exc:
        return {"status": "error", "message": f"bad reference_date {reference_date!r}: {exc}"}
    now = datetime(d.year, d.month, d.day, 12, 0, tzinfo=TIMEZONE)
    set_clock_override(now)
    return {"status": "ok", "clock": now.isoformat()}


def admin_clear_clock_override() -> dict:
    """Revert ``get_current_datetime`` to the real wall clock.

    Returns ``{"status": "cleared"}``.
    """
    clear_clock_override()
    return {"status": "cleared"}
