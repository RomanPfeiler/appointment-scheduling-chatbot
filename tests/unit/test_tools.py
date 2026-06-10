"""
tests/test_tools.py — Unit tests for mcp_server/tools.py.

Tests exercise the business logic functions directly, with no MCP protocol
involved. The module-level BookingStore is reset before and after each test
via the autouse fixture to prevent state leakage between tests.
"""

from datetime import date, datetime, timedelta

import pytest

import mcp_server.tools as tools
from mcp_server.config import LEAD_TIME_HOURS, SCHEDULING_HORIZON_DAYS, TIMEZONE


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(autouse=True)
def reset_store():
    """Reset the shared BookingStore around every test."""
    tools.reset_bookings()
    yield
    tools.reset_bookings()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _find_available_slot(
    topic_id: str = "investing",
    contact_medium_id: str = "online",
) -> dict:
    """Scan forward in 3-day chunks until a free slot is found.

    Returns the first available slot dict {datetime_start, datetime_end}.
    Raises RuntimeError if nothing is found within the scheduling horizon.
    """
    now = datetime.now(tz=TIMEZONE)
    start = now + timedelta(hours=LEAD_TIME_HOURS + 48)

    for _ in range(SCHEDULING_HORIZON_DAYS // 3 + 1):
        end = start + timedelta(days=3)
        result = tools.check_availability(
            topic_id, contact_medium_id,
            start.isoformat(), end.isoformat(),
        )
        if isinstance(result, list) and result:
            return result[0]
        start = end

    raise RuntimeError(
        "No available slot found in scheduling horizon — check mock_data seeding."
    )


def _future_window(days_ahead: int = 2, width_days: int = 3) -> tuple[str, str]:
    """ISO strings for a window starting well past lead time."""
    now = datetime.now(tz=TIMEZONE)
    start = now + timedelta(hours=LEAD_TIME_HOURS + 24, days=days_ahead)
    end = start + timedelta(days=width_days)
    return start.isoformat(), end.isoformat()


def _next_weekend_window() -> tuple[str, str]:
    """ISO strings covering exactly Saturday 00:00 – Sunday 24:00 (next week),
    guaranteed to be past lead time."""
    now = datetime.now(tz=TIMEZONE)
    days_until_saturday = (5 - now.weekday()) % 7 or 7
    saturday = (now + timedelta(days=days_until_saturday)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    # Ensure past lead time
    if saturday < now + timedelta(hours=LEAD_TIME_HOURS):
        saturday += timedelta(weeks=1)
    sunday_end = saturday + timedelta(days=2)
    return saturday.isoformat(), sunday_end.isoformat()


# ---------------------------------------------------------------------------
# get_appointment_topics
# ---------------------------------------------------------------------------


class TestGetAppointmentTopics:
    def test_returns_exactly_three_topics(self):
        result = tools.get_appointment_topics()
        assert len(result) == 3

    def test_each_item_has_required_keys(self):
        result = tools.get_appointment_topics()
        for topic in result:
            assert "topic_id" in topic
            assert "topic_name" in topic

    def test_known_topic_ids_are_present(self):
        result = tools.get_appointment_topics()
        ids = {t["topic_id"] for t in result}
        assert ids == {"investing", "mortgage", "pension"}

    def test_returns_list(self):
        assert isinstance(tools.get_appointment_topics(), list)


# ---------------------------------------------------------------------------
# get_appointment_contact_medium
# ---------------------------------------------------------------------------


class TestGetAppointmentContactMedium:
    def test_investing_returns_three_media(self):
        result = tools.get_appointment_contact_medium("investing")
        assert isinstance(result, list)
        assert len(result) == 3

    def test_investing_has_all_three_types(self):
        result = tools.get_appointment_contact_medium("investing")
        ids = {m["contact_medium_id"] for m in result}
        assert ids == {"branch", "online", "phone"}

    def test_mortgage_returns_two_media(self):
        result = tools.get_appointment_contact_medium("mortgage")
        assert isinstance(result, list)
        assert len(result) == 2

    def test_mortgage_has_no_phone(self):
        result = tools.get_appointment_contact_medium("mortgage")
        ids = {m["contact_medium_id"] for m in result}
        assert "phone" not in ids

    def test_pension_returns_two_media(self):
        result = tools.get_appointment_contact_medium("pension")
        assert isinstance(result, list)
        assert len(result) == 2

    def test_pension_has_no_branch(self):
        result = tools.get_appointment_contact_medium("pension")
        ids = {m["contact_medium_id"] for m in result}
        assert "branch" not in ids

    def test_each_item_has_required_keys(self):
        result = tools.get_appointment_contact_medium("investing")
        for medium in result:
            assert "contact_medium_id" in medium
            assert "contact_medium_name" in medium

    def test_invalid_topic_returns_error_dict(self):
        result = tools.get_appointment_contact_medium("invalid_topic")
        assert isinstance(result, dict)
        assert result["status"] == "error"
        assert "message" in result


# ---------------------------------------------------------------------------
# check_availability
# ---------------------------------------------------------------------------


class TestCheckAvailability:
    def test_valid_request_returns_list(self):
        start, end = _future_window()
        result = tools.check_availability("investing", "online", start, end)
        assert isinstance(result, list)

    def test_slots_have_required_keys(self):
        start, end = _future_window()
        result = tools.check_availability("investing", "online", start, end)
        for slot in result:
            assert "datetime_start" in slot
            assert "datetime_end" in slot

    def test_slots_are_iso_strings(self):
        start, end = _future_window()
        result = tools.check_availability("investing", "online", start, end)
        for slot in result:
            # Must be parseable as ISO 8601
            datetime.fromisoformat(slot["datetime_start"])
            datetime.fromisoformat(slot["datetime_end"])

    def test_weekend_only_window_returns_empty_list(self):
        start, end = _next_weekend_window()
        result = tools.check_availability("investing", "online", start, end)
        assert isinstance(result, list)
        assert result == []

    def test_past_end_datetime_returns_error(self):
        now = datetime.now(tz=TIMEZONE)
        start = (now - timedelta(days=3)).isoformat()
        end = (now - timedelta(hours=1)).isoformat()
        result = tools.check_availability("investing", "online", start, end)
        assert isinstance(result, dict)
        assert result["status"] == "error"

    def test_start_after_end_returns_error(self):
        now = datetime.now(tz=TIMEZONE)
        start = (now + timedelta(days=3)).isoformat()
        end = (now + timedelta(days=1)).isoformat()
        result = tools.check_availability("investing", "online", start, end)
        assert isinstance(result, dict)
        assert result["status"] == "error"

    def test_invalid_topic_returns_error(self):
        start, end = _future_window()
        result = tools.check_availability("nonexistent", "online", start, end)
        assert isinstance(result, dict)
        assert result["status"] == "error"

    def test_medium_not_valid_for_topic_returns_error(self):
        # Mortgage has no phone
        start, end = _future_window()
        result = tools.check_availability("mortgage", "phone", start, end)
        assert isinstance(result, dict)
        assert result["status"] == "error"

    def test_unparseable_datetime_returns_error(self):
        result = tools.check_availability("investing", "online", "not-a-date", "also-not")
        assert isinstance(result, dict)
        assert result["status"] == "error"

    def test_naive_datetime_string_accepted(self):
        """Offset-naive strings should default to Europe/Zurich without error."""
        now = datetime.now(tz=TIMEZONE)
        start = (now + timedelta(hours=LEAD_TIME_HOURS + 48)).replace(tzinfo=None)
        end = start + timedelta(days=3)
        result = tools.check_availability(
            "investing", "online",
            start.isoformat(), end.isoformat(),
        )
        assert isinstance(result, list)

    def test_window_exceeding_max_is_capped(self):
        """Requesting 10 days should silently cap to MAX_AVAILABILITY_WINDOW_DAYS."""
        now = datetime.now(tz=TIMEZONE)
        start = now + timedelta(hours=LEAD_TIME_HOURS + 48)
        end = start + timedelta(days=10)
        result = tools.check_availability(
            "investing", "online",
            start.isoformat(), end.isoformat(),
        )
        assert isinstance(result, list)
        if result:
            cap = start + timedelta(days=3)
            for slot in result:
                slot_end = datetime.fromisoformat(slot["datetime_end"])
                assert slot_end <= cap + timedelta(hours=1)  # allow end-of-day slot


# ---------------------------------------------------------------------------
# book_appointment
# ---------------------------------------------------------------------------


class TestBookAppointment:
    def test_booking_returns_success_status(self):
        slot = _find_available_slot()
        result = tools.book_appointment(
            "investing", "online",
            slot["datetime_start"], slot["datetime_end"],
        )
        assert result["status"] == "success"

    def test_booking_returns_booking_id(self):
        slot = _find_available_slot()
        result = tools.book_appointment(
            "investing", "online",
            slot["datetime_start"], slot["datetime_end"],
        )
        assert "booking_id" in result
        assert result["booking_id"].startswith("BK-")

    def test_booking_result_contains_details(self):
        slot = _find_available_slot()
        result = tools.book_appointment(
            "investing", "online",
            slot["datetime_start"], slot["datetime_end"],
        )
        details = result["details"]
        assert "topic_name" in details
        assert "contact_medium_name" in details
        assert "datetime_start" in details
        assert "datetime_end" in details

    def test_double_booking_returns_error(self):
        slot = _find_available_slot()
        first = tools.book_appointment(
            "investing", "online",
            slot["datetime_start"], slot["datetime_end"],
        )
        assert first["status"] == "success"

        second = tools.book_appointment(
            "investing", "online",
            slot["datetime_start"], slot["datetime_end"],
        )
        assert second["status"] == "error"
        assert "message" in second

    def test_booked_slot_absent_from_subsequent_availability(self):
        slot = _find_available_slot()
        tools.book_appointment(
            "investing", "online",
            slot["datetime_start"], slot["datetime_end"],
        )
        # Re-query the same narrow 1-hour window
        result = tools.check_availability(
            "investing", "online",
            slot["datetime_start"], slot["datetime_end"],
        )
        assert isinstance(result, list)
        assert not any(s["datetime_start"] == slot["datetime_start"] for s in result)

    def test_invalid_topic_returns_error(self):
        slot = _find_available_slot()
        result = tools.book_appointment(
            "bad_topic", "online",
            slot["datetime_start"], slot["datetime_end"],
        )
        assert result["status"] == "error"

    def test_medium_not_valid_for_topic_returns_error(self):
        slot = _find_available_slot()
        result = tools.book_appointment(
            "mortgage", "phone",
            slot["datetime_start"], slot["datetime_end"],
        )
        assert result["status"] == "error"

    def test_invalid_datetime_returns_error(self):
        result = tools.book_appointment("investing", "online", "bad", "also-bad")
        assert result["status"] == "error"


# ---------------------------------------------------------------------------
# reset_bookings
# ---------------------------------------------------------------------------


class TestResetBookings:
    def test_returns_reset_status(self):
        result = tools.reset_bookings()
        assert result == {"status": "reset"}

    def test_slot_is_rebookable_after_reset(self):
        slot = _find_available_slot()
        first = tools.book_appointment(
            "investing", "online",
            slot["datetime_start"], slot["datetime_end"],
        )
        assert first["status"] == "success"

        tools.reset_bookings()

        second = tools.book_appointment(
            "investing", "online",
            slot["datetime_start"], slot["datetime_end"],
        )
        assert second["status"] == "success"

    def test_reset_after_no_bookings_is_idempotent(self):
        result = tools.reset_bookings()
        assert result == {"status": "reset"}
        result2 = tools.reset_bookings()
        assert result2 == {"status": "reset"}


# ---------------------------------------------------------------------------
# get_current_datetime
# ---------------------------------------------------------------------------


class TestGetCurrentDatetime:
    def test_returns_required_keys(self):
        result = tools.get_current_datetime()
        assert set(result.keys()) == {"datetime", "date", "weekday", "week_number"}

    def test_datetime_is_valid_iso(self):
        result = tools.get_current_datetime()
        dt = datetime.fromisoformat(result["datetime"])
        assert dt.tzinfo is not None

    def test_date_is_valid_iso(self):
        result = tools.get_current_datetime()
        date.fromisoformat(result["date"])

    def test_weekday_is_nonempty_string(self):
        result = tools.get_current_datetime()
        assert isinstance(result["weekday"], str) and len(result["weekday"]) > 0

    def test_week_number_is_valid_int(self):
        result = tools.get_current_datetime()
        assert isinstance(result["week_number"], int)
        assert 1 <= result["week_number"] <= 53

    def test_date_matches_datetime(self):
        result = tools.get_current_datetime()
        dt = datetime.fromisoformat(result["datetime"])
        assert result["date"] == dt.date().isoformat()
