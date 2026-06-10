"""
tests/test_mock_data.py — Tests for mcp_server/mock_data.py.

Covers: timezone awareness, business hours, weekends, lead time,
deterministic reproducibility, realistic booking patterns, and BookingStore.
"""

from datetime import datetime, timedelta

import pytest

from mcp_server.config import (
    BUSINESS_HOURS_END,
    BUSINESS_HOURS_START,
    LEAD_TIME_HOURS,
    SCHEDULING_HORIZON_DAYS,
    TIMEZONE,
)
from mcp_server.mock_data import (
    BookingStore,
    generate_available_slots,
    get_contact_media,
    get_topics,
)
from mcp_server.models import TimeSlot


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def store() -> BookingStore:
    """Fresh BookingStore for each test."""
    return BookingStore()


@pytest.fixture
def wide_window() -> tuple[datetime, datetime]:
    """A 7-day window starting 48 h past lead time — broad enough to guarantee slots."""
    now = datetime.now(tz=TIMEZONE)
    start = now + timedelta(hours=LEAD_TIME_HOURS + 48)
    end = start + timedelta(days=7)
    return start, end


@pytest.fixture
def slots(wide_window: tuple[datetime, datetime]) -> list[TimeSlot]:
    """Available slots for investing/online over the wide window."""
    start, end = wide_window
    return generate_available_slots("investing", "online", start, end)


def _find_slot(store: BookingStore | None = None) -> TimeSlot:
    """Scan forward until a real available slot is found."""
    now = datetime.now(tz=TIMEZONE)
    start = now + timedelta(hours=LEAD_TIME_HOURS + 48)
    for _ in range(SCHEDULING_HORIZON_DAYS // 3 + 1):
        end = start + timedelta(days=3)
        found = generate_available_slots("investing", "online", start, end, store=store)
        if found:
            return found[0]
        start = end
    raise RuntimeError("No slot found — check mock_data seeding.")


# ---------------------------------------------------------------------------
# Timezone awareness
# ---------------------------------------------------------------------------


class TestTimezoneAwareness:
    def test_all_starts_are_timezone_aware(self, slots: list[TimeSlot]):
        for slot in slots:
            assert slot.datetime_start.tzinfo is not None, (
                f"datetime_start is naive: {slot.datetime_start}"
            )

    def test_all_ends_are_timezone_aware(self, slots: list[TimeSlot]):
        for slot in slots:
            assert slot.datetime_end.tzinfo is not None, (
                f"datetime_end is naive: {slot.datetime_end}"
            )

    def test_utc_offset_is_in_zurich_range(self, slots: list[TimeSlot]):
        """Europe/Zurich is UTC+1 (winter) or UTC+2 (summer)."""
        for slot in slots:
            offset = slot.datetime_start.utcoffset()
            assert offset is not None
            offset_hours = offset.total_seconds() / 3600
            assert 1 <= offset_hours <= 2, (
                f"Unexpected UTC offset {offset_hours}h for {slot.datetime_start}"
            )


# ---------------------------------------------------------------------------
# Business hours
# ---------------------------------------------------------------------------


class TestBusinessHours:
    def test_no_slot_starts_before_business_hours(self, slots: list[TimeSlot]):
        for slot in slots:
            assert slot.datetime_start.hour >= BUSINESS_HOURS_START, (
                f"Slot starts at {slot.datetime_start.hour}:00, before {BUSINESS_HOURS_START}:00"
            )

    def test_no_slot_starts_at_or_after_business_hours_end(self, slots: list[TimeSlot]):
        for slot in slots:
            assert slot.datetime_start.hour < BUSINESS_HOURS_END, (
                f"Slot starts at {slot.datetime_start.hour}:00, at or after {BUSINESS_HOURS_END}:00"
            )

    def test_no_slot_ends_after_business_hours(self, slots: list[TimeSlot]):
        for slot in slots:
            # A slot ending exactly at 17:00 is fine
            end = slot.datetime_end
            assert (end.hour < BUSINESS_HOURS_END) or (
                end.hour == BUSINESS_HOURS_END and end.minute == 0
            ), f"Slot ends at {end.hour}:{end.minute:02d}, past {BUSINESS_HOURS_END}:00"

    def test_all_slots_have_correct_duration(self, slots: list[TimeSlot]):
        for slot in slots:
            duration = (slot.datetime_end - slot.datetime_start).total_seconds() / 60
            assert duration == 60, f"Slot duration is {duration} min, expected 60"


# ---------------------------------------------------------------------------
# Weekends
# ---------------------------------------------------------------------------


class TestWeekends:
    def test_no_slots_on_saturday(self, slots: list[TimeSlot]):
        saturdays = [s for s in slots if s.datetime_start.weekday() == 5]
        assert saturdays == [], f"Found slots on Saturday: {saturdays}"

    def test_no_slots_on_sunday(self, slots: list[TimeSlot]):
        sundays = [s for s in slots if s.datetime_start.weekday() == 6]
        assert sundays == [], f"Found slots on Sunday: {sundays}"

    def test_weekend_only_window_returns_empty(self):
        now = datetime.now(tz=TIMEZONE)
        days_until_saturday = (5 - now.weekday()) % 7 or 7
        saturday = (now + timedelta(days=days_until_saturday)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        if saturday < now + timedelta(hours=LEAD_TIME_HOURS):
            saturday += timedelta(weeks=1)
        sunday_end = saturday + timedelta(days=2)
        result = generate_available_slots("investing", "online", saturday, sunday_end)
        assert result == []


# ---------------------------------------------------------------------------
# Lead time
# ---------------------------------------------------------------------------


class TestLeadTime:
    def test_no_slot_starts_before_lead_time(self):
        now = datetime.now(tz=TIMEZONE)
        start = now
        end = now + timedelta(hours=LEAD_TIME_HOURS * 2)
        slots = generate_available_slots("investing", "online", start, end)
        earliest_allowed = now + timedelta(hours=LEAD_TIME_HOURS)
        for slot in slots:
            assert slot.datetime_start >= earliest_allowed, (
                f"Slot at {slot.datetime_start} violates {LEAD_TIME_HOURS}h lead time"
            )

    def test_window_inside_lead_time_returns_empty(self):
        now = datetime.now(tz=TIMEZONE)
        end = now + timedelta(hours=LEAD_TIME_HOURS - 1)
        result = generate_available_slots("investing", "online", now, end)
        assert result == []


# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------


class TestReproducibility:
    def test_same_call_twice_returns_identical_slots(self, wide_window: tuple[datetime, datetime]):
        start, end = wide_window
        first = generate_available_slots("investing", "online", start, end)
        second = generate_available_slots("investing", "online", start, end)

        assert len(first) == len(second)
        for a, b in zip(first, second):
            assert a.datetime_start == b.datetime_start
            assert a.datetime_end == b.datetime_end

    def test_different_topics_may_differ(self, wide_window: tuple[datetime, datetime]):
        """Seeds differ by topic_id, so both topics must return valid independent lists."""
        start, end = wide_window
        investing = generate_available_slots("investing", "online", start, end)
        pension = generate_available_slots("pension", "online", start, end)
        # Both must be valid lists — patterns are allowed (but not required) to differ,
        # since two topics can legitimately share the same available days by coincidence.
        assert isinstance(investing, list)
        assert isinstance(pension, list)


# ---------------------------------------------------------------------------
# Realistic booking pattern
# ---------------------------------------------------------------------------


class TestBookingPattern:
    def test_some_days_are_fully_booked_over_horizon(self):
        """Over 21 days, ~30% of weekdays should have 0 slots."""
        now = datetime.now(tz=TIMEZONE)
        start = now + timedelta(hours=LEAD_TIME_HOURS + 48)
        end = start + timedelta(days=SCHEDULING_HORIZON_DAYS)
        slots = generate_available_slots("investing", "online", start, end)

        days_with_slots = {s.datetime_start.date() for s in slots}
        total_weekdays = sum(
            1 for i in range(SCHEDULING_HORIZON_DAYS)
            if (start + timedelta(days=i)).weekday() < 5
        )
        assert len(days_with_slots) < total_weekdays, (
            "Expected some fully-booked days, but every weekday had slots."
        )

    def test_some_slots_exist_over_wide_window(self, slots: list[TimeSlot]):
        """A 7-day window should contain at least one available slot."""
        assert len(slots) > 0, (
            "Expected available slots in a 7-day window, but got none."
        )

    def test_not_all_slots_on_same_day(self, slots: list[TimeSlot]):
        """A 7-day window should span more than one weekday."""
        if len(slots) < 2:
            pytest.skip("Too few slots to test multi-day spread.")
        days = {s.datetime_start.date() for s in slots}
        assert len(days) > 1


# ---------------------------------------------------------------------------
# BookingStore
# ---------------------------------------------------------------------------


class TestBookingStore:
    def test_book_returns_success_status(self, store: BookingStore):
        slot = _find_slot()
        result = store.book("investing", "online", slot)
        assert result.status == "success"

    def test_booking_id_has_correct_prefix(self, store: BookingStore):
        slot = _find_slot()
        result = store.book("investing", "online", slot)
        assert result.booking_id.startswith("BK-")

    def test_booking_result_has_correct_names(self, store: BookingStore):
        slot = _find_slot()
        result = store.book("investing", "online", slot)
        assert result.topic_name == "Investing"
        assert result.contact_medium_name == "Online Meeting"

    def test_booking_result_datetimes_match_slot(self, store: BookingStore):
        slot = _find_slot()
        result = store.book("investing", "online", slot)
        assert result.datetime_start == slot.datetime_start
        assert result.datetime_end == slot.datetime_end

    def test_is_booked_false_before_booking(self, store: BookingStore):
        slot = _find_slot()
        assert not store.is_booked(slot)

    def test_is_booked_true_after_booking(self, store: BookingStore):
        slot = _find_slot()
        store.book("investing", "online", slot)
        assert store.is_booked(slot)

    def test_double_booking_raises_value_error(self, store: BookingStore):
        slot = _find_slot()
        store.book("investing", "online", slot)
        with pytest.raises(ValueError, match="already booked"):
            store.book("investing", "online", slot)

    def test_booked_slot_excluded_from_generate(self, store: BookingStore):
        slot = _find_slot(store=None)
        store.book("investing", "online", slot)
        after = generate_available_slots(
            "investing", "online",
            slot.datetime_start, slot.datetime_end,
            store=store,
        )
        assert not any(s.datetime_start == slot.datetime_start for s in after)

    def test_reset_clears_bookings(self, store: BookingStore):
        slot = _find_slot()
        store.book("investing", "online", slot)
        assert store.is_booked(slot)
        store.reset()
        assert not store.is_booked(slot)

    def test_slot_rebookable_after_reset(self, store: BookingStore):
        slot = _find_slot()
        store.book("investing", "online", slot)
        store.reset()
        result = store.book("investing", "online", slot)
        assert result.status == "success"

    def test_invalid_topic_raises(self, store: BookingStore):
        slot = _find_slot()
        with pytest.raises(ValueError):
            store.book("nonexistent_topic", "online", slot)

    def test_medium_unavailable_for_topic_raises(self, store: BookingStore):
        slot = _find_slot()
        with pytest.raises(ValueError):
            store.book("mortgage", "phone", slot)  # mortgage has no phone


# ---------------------------------------------------------------------------
# Reference data accessors
# ---------------------------------------------------------------------------


class TestReferenceDataAccessors:
    def test_get_topics_returns_three(self):
        topics = get_topics()
        assert len(topics) == 3

    def test_get_topics_have_required_attributes(self):
        for topic in get_topics():
            assert hasattr(topic, "topic_id")
            assert hasattr(topic, "topic_name")

    def test_get_topics_known_ids(self):
        ids = {t.topic_id for t in get_topics()}
        assert ids == {"investing", "mortgage", "pension"}

    def test_get_contact_media_unknown_topic_raises(self):
        with pytest.raises(ValueError):
            get_contact_media("nonexistent")

    def test_mortgage_excludes_phone(self):
        ids = {m.contact_medium_id for m in get_contact_media("mortgage")}
        assert "phone" not in ids

    def test_pension_excludes_branch(self):
        ids = {m.contact_medium_id for m in get_contact_media("pension")}
        assert "branch" not in ids

    def test_investing_includes_all_three(self):
        ids = {m.contact_medium_id for m in get_contact_media("investing")}
        assert ids == {"branch", "online", "phone"}
