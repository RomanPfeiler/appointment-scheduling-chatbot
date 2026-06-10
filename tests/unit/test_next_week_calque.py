"""Unit tests for the "next week <weekday>" calque resolver (generator).

dateparser/search_dates mis-read the Swiss-variant calques ("next week
Tuesday", "the Tuesday of next week") — dropping the weekday and returning the
start of next week (today+7 = Monday) or None (random fallback). The
deterministic resolver fixes this so the override lands on the day the agent
actually queries. Added 2026-06-06.
"""

from __future__ import annotations

import json

import pytest

from evaluation.scenarios.generator import (
    REFERENCE_DATETIME,
    _parse_phrasing_alignment,
    _resolve_next_week_weekday,
)
from evaluation.scenarios.paths import SCENARIOS_DIR, TIER_OUTPUT_FILES

REF = REFERENCE_DATETIME  # Monday 2026-06-01


@pytest.mark.parametrize(
    "phrase, offset, slot",
    [
        ("next week Tuesday at 14 o'clock", "today+8", "14:00-15:00"),
        ("the Tuesday of next week at 15h", "today+8", "15:00-16:00"),
        ("the Tuesday of next week at 14", "today+8", "14:00-15:00"),
        ("next week Monday", "today+7", "09:00-10:00"),  # next week's Monday, default slot
        ("next week Friday at 11am", "today+11", "11:00-12:00"),
    ],
)
def test_next_week_weekday_resolves_to_following_week(phrase, offset, slot):
    assert _resolve_next_week_weekday(phrase, REF) == (offset, slot)


@pytest.mark.parametrize(
    "phrase",
    [
        "next Tuesday at 2pm",   # "next <weekday>" is this-coming, not next-week
        "tomorrow at 10am",
        "this Friday afternoon",
        "in three days",
        "sometime next week",    # no weekday named
    ],
)
def test_non_calque_phrasings_fall_through(phrase):
    assert _resolve_next_week_weekday(phrase, REF) is None


def test_parse_phrasing_alignment_uses_calque_resolver_first():
    # The calque path short-circuits dateparser (which returned today+7 / None).
    assert _parse_phrasing_alignment("next week Tuesday at 14 o'clock", REF) == (
        "today+8",
        "14:00-15:00",
    )


def test_committed_calque_scenarios_are_aligned():
    """Every committed alignment-tier calque scenario targets the resolver's day."""
    for tier in (1, 2, 3, 5):
        data = json.loads(
            (SCENARIOS_DIR / TIER_OUTPUT_FILES[tier]).read_text(encoding="utf-8")
        )
        for s in data:
            resolved = _resolve_next_week_weekday(s["frozen_phrasing"], REF)
            if resolved is None or not s["booking_reachable"]:
                continue
            ew = s["expected_datetime_window"]
            assert ew is not None, f"{s['scenario_id']}: calque needs an expected window"
            assert ew["start_offset"].split("T")[0] == resolved[0], (
                f"{s['scenario_id']}: expected window day {ew['start_offset']} "
                f"!= resolver {resolved[0]}"
            )
