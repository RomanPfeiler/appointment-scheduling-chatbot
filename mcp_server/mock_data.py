"""
mock_data.py — Dynamic slot generation and in-memory booking store.

Slot availability is generated relative to the current date so that demos
and tests never go stale. Randomness is seeded by (date + topic_id) so the
same inputs always produce the same availability pattern (reproducible eval).

An admin override mechanism allows the evaluation runner to inject a fixed
availability profile before each scenario run (see EVALUATION_FRAMEWORK.md §3a).
When active, ``generate_available_slots`` returns only the overridden slots;
all non-overridden dates return empty. Clear the override between scenarios
via ``clear_availability_override()``.
"""

import hashlib
import json
import secrets
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Optional

from mcp_server.config import (
    BUSINESS_HOURS_END,
    BUSINESS_HOURS_START,
    DEFAULT_SLOT_DURATION_MINUTES,
    LEAD_TIME_HOURS,
    TIMEZONE,
)
from mcp_server.models import BookingResult, ContactMedium, TimeSlot, Topic

# ---------------------------------------------------------------------------
# Reference data — loaded once at import time
# ---------------------------------------------------------------------------

_DATA_PATH = Path(__file__).parent / "data" / "reference_data.json"

with _DATA_PATH.open(encoding="utf-8") as _f:
    _REF: dict = json.load(_f)

_TOPICS: list[Topic] = [Topic(**t) for t in _REF["topics"]]
_TOPIC_IDS: set[str] = {t.topic_id for t in _TOPICS}

_CONTACT_MEDIA: dict[str, list[ContactMedium]] = {
    topic_id: [ContactMedium(**cm) for cm in media]
    for topic_id, media in _REF["contact_media"].items()
}


# ---------------------------------------------------------------------------
# Admin override store (process-lifetime, set via MCP admin tools)
# ---------------------------------------------------------------------------

_override_active: bool = False
_override_slots_by_date: dict[date, list[TimeSlot]] = {}


def set_availability_override(slots_by_date: dict[date, list[TimeSlot]]) -> None:
    """Activate a fixed availability profile for evaluation scenarios.

    While active, ``generate_available_slots`` returns only the slots in
    *slots_by_date* for the queried date range; any date absent from the
    dict returns empty (fully booked). The lead-time filter is bypassed so
    scenario timing is deterministic regardless of when the runner starts.

    Call ``clear_availability_override`` between scenarios to restore the
    default seeded-random generation.
    """
    global _override_active, _override_slots_by_date
    _override_active = True
    _override_slots_by_date = dict(slots_by_date)


def clear_availability_override() -> None:
    """Deactivate the override and revert to seeded slot generation."""
    global _override_active, _override_slots_by_date
    _override_active = False
    _override_slots_by_date = {}


# ---------------------------------------------------------------------------
# Scenario clock override (EVALUATION_FRAMEWORK.md §3a / §14)
#
# ``get_current_datetime`` returns the real wall clock by default. During an
# evaluation scenario run the runner pins it to the scenario's ``reference_date``
# so the agent's date arithmetic shares ONE clock with the availability override
# and the simulator. Without this, the agent calls ``get_current_datetime``,
# anchors on the real run-day, and queries days the override never populated —
# the alignment broke whenever the run day differed from the suite anchor
# (observed 2026-06-06: run-day 06-06 vs anchor 06-01). Closing it makes scenario
# execution truly date-independent. Clear between scenarios via
# ``clear_clock_override()``.
# ---------------------------------------------------------------------------
_clock_override: datetime | None = None


def set_clock_override(now: datetime) -> None:
    """Pin ``get_current_datetime`` to ``now`` for the current scenario run."""
    global _clock_override
    _clock_override = now


def clear_clock_override() -> None:
    """Revert ``get_current_datetime`` to the real wall clock."""
    global _clock_override
    _clock_override = None


def get_clock_override() -> "datetime | None":
    """Return the pinned scenario clock, or ``None`` when on the real clock."""
    return _clock_override


def is_override_active() -> bool:
    """Return whether a scenario availability override is currently active.

    The evaluation runner sets an override per scenario and resolves all
    scenario dates against a pinned ``reference_date`` (EVALUATION_FRAMEWORK §3a),
    which may legitimately be in the past relative to the real wall clock. Callers
    (``check_availability``) use this to skip wall-clock past-window guards while an
    override is active, so scenario outcomes are date-independent on any run day.
    """
    return _override_active


# ---------------------------------------------------------------------------
# Reference data accessors
# ---------------------------------------------------------------------------


def get_topics() -> list[Topic]:
    """Return all available appointment topics."""
    return list(_TOPICS)


def get_contact_media(topic_id: str) -> list[ContactMedium]:
    """Return contact media available for *topic_id*.

    Raises ValueError if topic_id is not recognised.
    """
    if topic_id not in _TOPIC_IDS:
        raise ValueError(
            f"Unknown topic_id '{topic_id}'. "
            f"Valid values: {sorted(_TOPIC_IDS)}"
        )
    return list(_CONTACT_MEDIA[topic_id])


# ---------------------------------------------------------------------------
# Slot generation helpers
# ---------------------------------------------------------------------------


def _day_seed(day: date, topic_id: str) -> int:
    """Deterministic integer seed from a date + topic_id pair."""
    key = f"{day.isoformat()}:{topic_id}"
    digest = hashlib.md5(key.encode()).hexdigest()  # noqa: S324 — not crypto
    return int(digest[:8], 16)


def _slots_for_day(day: date, topic_id: str) -> list[TimeSlot]:
    """Generate all candidate 60-min slots for *day*, then remove some
    deterministically to simulate realistic booking patterns:

      seed % 10 in {0, 1, 2}  → fully booked   (30 %)
      seed % 10 in {3, 4, 5, 6} → 2–4 slots      (40 %)
      seed % 10 in {7, 8, 9}  → mostly open     (30 %)
    """
    # Build every possible slot within business hours
    all_slots: list[TimeSlot] = []
    hour = BUSINESS_HOURS_START
    while hour + DEFAULT_SLOT_DURATION_MINUTES // 60 <= BUSINESS_HOURS_END:
        slot_start = datetime(
            day.year, day.month, day.day, hour, 0, 0, tzinfo=TIMEZONE
        )
        slot_end = slot_start + timedelta(minutes=DEFAULT_SLOT_DURATION_MINUTES)
        all_slots.append(TimeSlot(datetime_start=slot_start, datetime_end=slot_end))
        hour += DEFAULT_SLOT_DURATION_MINUTES // 60

    total = len(all_slots)  # e.g. 9 slots for 08:00–17:00
    seed = _day_seed(day, topic_id)
    bucket = seed % 10

    if bucket <= 2:
        # Fully booked
        return []
    elif bucket <= 6:
        # Keep 2–4 slots, chosen deterministically
        keep_count = 2 + (seed % 3)          # 2, 3, or 4
        keep_count = min(keep_count, total)
        step = max(1, total // keep_count)
        return [all_slots[i * step % total] for i in range(keep_count)]
    else:
        # Mostly open — remove 1 or 2 slots
        remove_count = 1 + (seed % 2)
        remove_indices = {(seed * (i + 1)) % total for i in range(remove_count)}
        return [s for i, s in enumerate(all_slots) if i not in remove_indices]


# ---------------------------------------------------------------------------
# Public slot generation
# ---------------------------------------------------------------------------


def generate_available_slots(
    topic_id: str,
    contact_medium_id: str,
    start_dt: datetime,
    end_dt: datetime,
    store: Optional["BookingStore"] = None,
) -> list[TimeSlot]:
    """Return available TimeSlots within [start_dt, end_dt].

    Rules applied in order:
    1. Weekends are skipped entirely.
    2. A deterministic per-day pattern removes some slots to simulate demand.
    3. Slots that start before now + LEAD_TIME_HOURS are excluded.
    4. Slots already booked in *store* (if supplied) are excluded.

    All returned datetimes are timezone-aware (Europe/Zurich).
    """
    # Validate inputs against reference data
    if topic_id not in _TOPIC_IDS:
        raise ValueError(f"Unknown topic_id '{topic_id}'.")
    valid_media_ids = {cm.contact_medium_id for cm in _CONTACT_MEDIA[topic_id]}
    if contact_medium_id not in valid_media_ids:
        raise ValueError(
            f"Contact medium '{contact_medium_id}' not available for topic '{topic_id}'."
        )

    # --- Override mode: return only the injected slots, bypass seeded generation ---
    # Lead-time and past-time filters are skipped so scenario timing is deterministic.
    if _override_active:
        available: list[TimeSlot] = []
        current_day = start_dt.date()
        end_day = end_dt.date()
        while current_day <= end_day:
            for slot in _override_slots_by_date.get(current_day, []):
                if slot.datetime_start >= start_dt and slot.datetime_end <= end_dt:
                    if store is None or not store.is_booked(slot):
                        available.append(slot)
            current_day += timedelta(days=1)
        return available

    earliest = datetime.now(tz=TIMEZONE) + timedelta(hours=LEAD_TIME_HOURS)

    available = []
    current_day = start_dt.date()
    end_day = end_dt.date()

    while current_day <= end_day:
        # Skip weekends (Monday=0 … Sunday=6)
        if current_day.weekday() < 5:
            day_slots = _slots_for_day(current_day, topic_id)
            for slot in day_slots:
                # Must be within the requested window
                if slot.datetime_start < start_dt or slot.datetime_end > end_dt:
                    continue
                # Enforce lead time
                if slot.datetime_start < earliest:
                    continue
                # Exclude already-booked slots
                if store is not None and store.is_booked(slot):
                    continue
                available.append(slot)

        current_day += timedelta(days=1)

    return available


# ---------------------------------------------------------------------------
# In-memory booking store
# ---------------------------------------------------------------------------


class BookingStore:
    """Thread-unsafe in-memory store for booked appointments.

    Designed so a database backend can replace it later without changing the
    public interface.
    """

    def __init__(self) -> None:
        self._bookings: dict[str, BookingResult] = {}
        # Secondary index: (start_iso, end_iso) → booking_id for fast lookup
        self._slot_index: dict[tuple[str, str], str] = {}

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def book(
        self,
        topic_id: str,
        contact_medium_id: str,
        slot: TimeSlot,
    ) -> BookingResult:
        """Attempt to book *slot* for the given topic and medium.

        Returns a BookingResult with status "success" or raises ValueError
        if the slot is unavailable or already taken.
        """
        # Verify topic / medium
        if topic_id not in _TOPIC_IDS:
            raise ValueError(f"Unknown topic_id '{topic_id}'.")
        media_map = {cm.contact_medium_id: cm for cm in _CONTACT_MEDIA[topic_id]}
        if contact_medium_id not in media_map:
            raise ValueError(
                f"Contact medium '{contact_medium_id}' not available for '{topic_id}'."
            )

        # Check slot is already booked
        if self.is_booked(slot):
            raise ValueError(
                f"Slot {slot.datetime_start.isoformat()} is already booked."
            )

        # Verify the slot exists in the generated availability (no phantom slots)
        window_start = slot.datetime_start
        window_end = slot.datetime_end
        available = generate_available_slots(
            topic_id, contact_medium_id, window_start, window_end, store=None
        )
        if not any(
            s.datetime_start == slot.datetime_start and s.datetime_end == slot.datetime_end
            for s in available
        ):
            raise ValueError(
                f"Slot {slot.datetime_start.isoformat()} is not available "
                f"(fully booked day or outside business hours)."
            )

        # Generate booking
        booking_id = "BK-" + secrets.token_hex(3).upper()
        topic = next(t for t in _TOPICS if t.topic_id == topic_id)
        medium = media_map[contact_medium_id]

        result = BookingResult(
            status="success",
            booking_id=booking_id,
            topic_name=topic.topic_name,
            contact_medium_name=medium.contact_medium_name,
            datetime_start=slot.datetime_start,
            datetime_end=slot.datetime_end,
        )

        self._bookings[booking_id] = result
        self._slot_index[self._slot_key(slot)] = booking_id
        return result

    def is_booked(self, slot: TimeSlot) -> bool:
        """Return True if *slot* has already been booked."""
        return self._slot_key(slot) in self._slot_index

    def reset(self) -> None:
        """Clear all bookings (used by the reset_bookings MCP tool)."""
        self._bookings.clear()
        self._slot_index.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _slot_key(slot: TimeSlot) -> tuple[str, str]:
        return (slot.datetime_start.isoformat(), slot.datetime_end.isoformat())
