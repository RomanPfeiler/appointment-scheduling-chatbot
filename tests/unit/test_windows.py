"""Standalone tests for the shared specificity→window policy.

These exercise ``nlp/datetime_parsers/windows.py`` **independently of both
arms** via directly constructed inputs — every ``specificity`` value plus the
edge cases (start on the hour, start mid-hour, each window span, tz-aware
contract). The arm tests cover wiring; these pin the policy itself.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest

from nlp.datetime_parsers.windows import (
    compute_end_datetime,
    is_flexible_for,
    snap_start,
)

ZURICH = ZoneInfo("Europe/Zurich")

# A mid-hour start and an on-the-hour start, both tz-aware.
MID_HOUR = datetime(2026, 6, 1, 14, 30, 15, 500, tzinfo=ZURICH)
ON_HOUR = datetime(2026, 6, 1, 10, 0, 0, 0, tzinfo=ZURICH)
DAY_LEVEL = ("day_specific", "day_vague", "multi_day_vague")


# ── is_flexible_for ────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "spec,expected",
    [
        ("exact_time", False),
        ("day_specific", False),
        ("day_vague", True),
        ("multi_day_vague", True),
        ("compound", False),
    ],
)
def test_is_flexible_for(spec, expected):
    assert is_flexible_for(spec) is expected


# ── snap_start ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize("spec", DAY_LEVEL)
@pytest.mark.parametrize("start", [MID_HOUR, ON_HOUR])
def test_snap_start_day_level_goes_to_midnight(spec, start):
    snapped = snap_start(start, spec)
    assert (snapped.hour, snapped.minute, snapped.second, snapped.microsecond) == (0, 0, 0, 0)
    assert snapped.date() == start.date()
    assert snapped.tzinfo is start.tzinfo  # timezone preserved


@pytest.mark.parametrize("spec", ["exact_time", "compound"])
@pytest.mark.parametrize("start", [MID_HOUR, ON_HOUR])
def test_snap_start_non_day_level_unchanged(spec, start):
    assert snap_start(start, spec) == start


def test_snap_start_rejects_naive():
    with pytest.raises(ValueError, match="timezone-aware"):
        snap_start(datetime(2026, 6, 1, 9, 0), "day_specific")


# ── compute_end_datetime ───────────────────────────────────────────────────

def test_end_exact_time_is_one_hour():
    assert compute_end_datetime(MID_HOUR, "exact_time") == MID_HOUR + timedelta(hours=1)


@pytest.mark.parametrize("spec", ["day_specific", "day_vague"])
def test_end_day_level_is_end_of_same_day(spec):
    start = snap_start(MID_HOUR, spec)  # midnight
    end = compute_end_datetime(start, spec)
    assert (end.hour, end.minute, end.second) == (23, 59, 0)
    assert end.date() == start.date()


def test_end_multi_day_vague_is_five_day_span():
    start = snap_start(MID_HOUR, "multi_day_vague")  # midnight day 0
    end = compute_end_datetime(start, "multi_day_vague")
    assert end == start + timedelta(days=4, hours=23, minutes=59)
    assert (end - start).days == 4  # days 0..4 inclusive → 5-day span


def test_end_compound_falls_back_to_one_hour():
    assert compute_end_datetime(ON_HOUR, "compound") == ON_HOUR + timedelta(hours=1)


def test_end_preserves_timezone():
    assert compute_end_datetime(MID_HOUR, "exact_time").tzinfo is MID_HOUR.tzinfo


def test_end_rejects_naive():
    with pytest.raises(ValueError, match="timezone-aware"):
        compute_end_datetime(datetime(2026, 6, 1, 9, 0), "exact_time")


def test_start_strictly_before_end_for_all_specificities():
    for spec in ("exact_time", "day_specific", "day_vague", "multi_day_vague", "compound"):
        start = snap_start(MID_HOUR, spec)
        assert start < compute_end_datetime(start, spec)
