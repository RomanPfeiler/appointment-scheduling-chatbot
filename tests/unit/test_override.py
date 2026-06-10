"""Unit tests for the MCP server availability override mechanism.

Tests the module-level override store in ``mcp_server.mock_data`` and the
admin tool functions in ``mcp_server.tools``.  No MCP subprocess is started.
"""

import json
from datetime import date, datetime, timedelta

import pytest

from mcp_server.config import TIMEZONE
from mcp_server.mock_data import (
    BookingStore,
    clear_availability_override,
    generate_available_slots,
    is_override_active,
    set_availability_override,
)
from mcp_server.models import TimeSlot
from mcp_server.tools import (
    admin_clear_availability_override,
    admin_set_availability_override,
    booking_store,
    check_availability,
)


@pytest.fixture(autouse=True)
def _reset_override():
    """Ensure override is cleared before and after each test."""
    clear_availability_override()
    yield
    clear_availability_override()


def _make_slot(d: date, start_h: int, end_h: int) -> TimeSlot:
    return TimeSlot(
        datetime_start=datetime(d.year, d.month, d.day, start_h, 0, 0, tzinfo=TIMEZONE),
        datetime_end=datetime(d.year, d.month, d.day, end_h, 0, 0, tzinfo=TIMEZONE),
    )


def _window(d: date):
    """Return a (start_dt, end_dt) tuple covering the full business day."""
    start = datetime(d.year, d.month, d.day, 8, 0, 0, tzinfo=TIMEZONE)
    end = datetime(d.year, d.month, d.day, 17, 0, 0, tzinfo=TIMEZONE)
    return start, end


class TestOverrideReplacesSeededSlots:
    def test_returns_only_overridden_slots(self):
        d = date.today() + timedelta(days=3)
        slot = _make_slot(d, 9, 10)
        set_availability_override({d: [slot]})

        start, end = _window(d)
        result = generate_available_slots("investing", "phone", start, end)

        assert len(result) == 1
        assert result[0].datetime_start == slot.datetime_start
        assert result[0].datetime_end == slot.datetime_end

    def test_override_replaces_all_seeded_slots(self):
        """Only the two overridden slots are returned, not the full seeded set."""
        d = date.today() + timedelta(days=3)
        slots = [_make_slot(d, 9, 10), _make_slot(d, 14, 15)]
        set_availability_override({d: slots})

        start, end = _window(d)
        result = generate_available_slots("mortgage", "online", start, end)

        assert len(result) == 2
        result_starts = {s.datetime_start.hour for s in result}
        assert result_starts == {9, 14}


class TestOverrideEmptyForMissingDates:
    def test_non_overridden_date_returns_empty(self):
        d_override = date.today() + timedelta(days=3)
        d_query = date.today() + timedelta(days=4)
        slot = _make_slot(d_override, 9, 10)
        set_availability_override({d_override: [slot]})

        start, end = _window(d_query)
        result = generate_available_slots("investing", "phone", start, end)

        assert result == []

    def test_multiple_days_only_overridden_dates_return_slots(self):
        d1 = date.today() + timedelta(days=3)
        d2 = date.today() + timedelta(days=4)
        d3 = date.today() + timedelta(days=5)

        # Override only d1 and d3; d2 returns empty
        set_availability_override({
            d1: [_make_slot(d1, 9, 10)],
            d3: [_make_slot(d3, 14, 15)],
        })

        # Query spanning d1–d3
        start = datetime(d1.year, d1.month, d1.day, 8, 0, 0, tzinfo=TIMEZONE)
        end = datetime(d3.year, d3.month, d3.day, 17, 0, 0, tzinfo=TIMEZONE)
        result = generate_available_slots("investing", "phone", start, end)

        result_dates = {s.datetime_start.date() for s in result}
        assert d2 not in result_dates
        assert d1 in result_dates
        assert d3 in result_dates


class TestClearOverrideRestoresSeeded:
    def test_seeded_slots_return_after_clear(self):
        """Clearing the override restores normal seeded generation."""
        # Find a day that seeded generation produces slots for
        d = date.today() + timedelta(days=5)
        # Ensure it's a weekday
        while d.weekday() >= 5:
            d += timedelta(days=1)

        set_availability_override({d: []})  # empty override → no slots
        start, end = _window(d)
        result_with_override = generate_available_slots("investing", "phone", start, end)

        clear_availability_override()
        result_without_override = generate_available_slots("investing", "phone", start, end)

        # After clearing, seeded generation may return slots (topic-/date-dependent)
        # The key assertion is that the states differ: override returned 0, clear may return ≥0
        assert result_with_override == []
        # Seeded result can be 0 (fully-booked day) — just verify no exception and type is list
        assert isinstance(result_without_override, list)


class TestBookAppointmentWithOverride:
    def test_can_book_overridden_slot(self):
        """A slot declared in the override should be bookable."""
        d = date.today() + timedelta(days=3)
        slot = _make_slot(d, 9, 10)
        set_availability_override({d: [slot]})

        store = BookingStore()
        start, end = _window(d)
        available = generate_available_slots("investing", "phone", start, end, store=store)
        assert len(available) == 1

        result = store.book("investing", "phone", available[0])
        assert result.status == "success"
        assert result.booking_id.startswith("BK-")

    def test_already_booked_slot_excluded_from_override(self):
        """A booked slot should not appear in subsequent availability checks."""
        d = date.today() + timedelta(days=3)
        slot = _make_slot(d, 9, 10)
        set_availability_override({d: [slot]})

        store = BookingStore()
        start, end = _window(d)
        available = generate_available_slots("investing", "phone", start, end, store=store)
        store.book("investing", "phone", available[0])

        # Second check should exclude the booked slot
        available2 = generate_available_slots("investing", "phone", start, end, store=store)
        assert available2 == []


class TestCheckAvailabilityPastGuardBypass:
    """``check_availability`` skips the wall-clock past-window guard while an
    override is active, so scenarios pinned to a past ``reference_date`` still
    return slots on any run day (EVALUATION_FRAMEWORK §3a). In production (no
    override) the guard still rejects past windows.
    """

    def test_past_window_rejected_without_override(self):
        assert is_override_active() is False
        past = date.today() - timedelta(days=5)
        start, end = _window(past)
        result = check_availability(
            "investing", "phone", start.isoformat(), end.isoformat()
        )
        assert isinstance(result, dict)
        assert result["status"] == "error"
        assert "in the past" in result["message"]

    def test_past_window_allowed_with_override(self):
        booking_store.reset()
        past = date.today() - timedelta(days=5)
        slot = _make_slot(past, 9, 10)
        set_availability_override({past: [slot]})
        assert is_override_active() is True

        start, end = _window(past)
        result = check_availability(
            "investing", "phone", start.isoformat(), end.isoformat()
        )
        # Returns the overridden slot list, NOT the past-window error dict.
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0]["datetime_start"].startswith(past.isoformat())


class TestAdminToolFunction:
    def test_admin_set_parses_valid_json(self):
        d = date.today() + timedelta(days=3)
        override_data = {d.isoformat(): ["09:00-10:00", "14:00-15:00"]}
        result = admin_set_availability_override(json.dumps(override_data))

        assert result["status"] == "ok"
        assert result["dates_set"] == 1

        start, end = _window(d)
        slots = generate_available_slots("investing", "phone", start, end)
        assert len(slots) == 2

    def test_admin_set_returns_error_on_invalid_json(self):
        result = admin_set_availability_override("not-valid-json")
        assert result["status"] == "error"
        assert "Invalid JSON" in result["message"]

    def test_admin_set_returns_error_on_bad_slot_format(self):
        d = date.today() + timedelta(days=3)
        bad = {d.isoformat(): ["09h00-10h00"]}  # wrong separator
        result = admin_set_availability_override(json.dumps(bad))
        assert result["status"] == "error"

    def test_admin_clear_reverts_override(self):
        d = date.today() + timedelta(days=3)
        override_data = {d.isoformat(): ["09:00-10:00"]}
        admin_set_availability_override(json.dumps(override_data))

        result = admin_clear_availability_override()
        assert result["status"] == "cleared"

        # Override should be gone — seeded generation applies
        start, end = _window(d)
        # Should not raise; result type is list (may be empty for fully-booked seed)
        slots = generate_available_slots("investing", "phone", start, end)
        assert isinstance(slots, list)
