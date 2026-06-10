"""Guard against ``exact_time`` over-labelling by the LLM datetime arms.

The shared :func:`reconcile_exact_time` downgrades a model-claimed ``exact_time``
that carries no clock token, so a bare date/day never produces an un-bookable
midnight 1-hour window (the named cause of the Arm 3 smoke regression). Tested at
the unit level and end-to-end through both LLM arms' deterministic build paths.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from nlp.datetime_parsers.arm2_local_llm import parse_datetime_tags
from nlp.datetime_parsers.arm3_api_llm import build_ranges
from nlp.datetime_parsers.resolution import has_explicit_time, reconcile_exact_time

ZURICH = ZoneInfo("Europe/Zurich")
ANCHOR = datetime(2026, 6, 1, 12, 0, tzinfo=ZURICH)  # Monday


# ─── has_explicit_time ────────────────────────────────────────────────────────
def test_has_explicit_time_detects_clock_tokens():
    assert has_explicit_time("next Tuesday at 14:00")
    assert has_explicit_time("tomorrow 2pm")
    assert has_explicit_time("at noon")
    assert has_explicit_time("9 o'clock")


def test_has_explicit_time_false_for_date_only():
    assert not has_explicit_time("14 March")
    assert not has_explicit_time("next Tuesday")
    assert not has_explicit_time("next week")


# ─── reconcile_exact_time ─────────────────────────────────────────────────────
def test_exact_time_with_clock_token_passes_through():
    assert reconcile_exact_time("next Tuesday at 14:00", "exact_time") == "exact_time"
    assert reconcile_exact_time("tomorrow 2pm", "exact_time") == "exact_time"


def test_exact_time_on_absolute_date_downgrades_to_day_specific():
    assert reconcile_exact_time("14 March", "exact_time") == "day_specific"
    assert reconcile_exact_time("20.03", "exact_time") == "day_specific"


def test_exact_time_on_relative_day_downgrades_to_day_vague():
    assert reconcile_exact_time("next Tuesday", "exact_time") == "day_vague"
    assert reconcile_exact_time("tomorrow", "exact_time") == "day_vague"


def test_exact_time_on_multi_day_downgrades_to_multi_day_vague():
    assert reconcile_exact_time("next week", "exact_time") == "multi_day_vague"


def test_exact_time_on_ambiguous_text_defaults_to_day_vague():
    assert reconcile_exact_time("whenever suits", "exact_time") == "multi_day_vague"
    assert reconcile_exact_time("qwerty", "exact_time") == "day_vague"


def test_non_exact_time_specs_pass_through_untouched():
    assert reconcile_exact_time("14 March", "day_specific") == "day_specific"
    assert reconcile_exact_time("next Tuesday", "day_vague") == "day_vague"
    assert reconcile_exact_time("next week", "multi_day_vague") == "multi_day_vague"


# ─── End-to-end through both LLM arms' build paths ────────────────────────────
def test_arm3_mislabelled_date_only_yields_day_window_not_midnight_hour():
    # The bug: "14 March" labelled exact_time → 00:00–01:00 window. The guard
    # rewrites it to a full-day window instead.
    ranges = build_ranges(
        [{"expr": "14 March", "specificity": "exact_time"}], now=ANCHOR
    )
    assert len(ranges) == 1
    r = ranges[0]
    assert r.specificity == "day_specific"
    assert (r.start_datetime.hour, r.start_datetime.minute) == (0, 0)
    assert (r.end_datetime.hour, r.end_datetime.minute) == (23, 59)


def test_arm3_genuine_exact_time_is_preserved():
    ranges = build_ranges(
        [{"expr": "next Tuesday at 14:00", "specificity": "exact_time"}], now=ANCHOR
    )
    assert len(ranges) == 1
    assert ranges[0].specificity == "exact_time"
    assert (ranges[0].start_datetime.hour, ranges[0].start_datetime.minute) == (14, 0)


def test_arm2_mislabelled_relative_day_downgrades():
    raw = "<dt><expr>next Tuesday</expr><spec>exact_time</spec></dt>"
    ranges = parse_datetime_tags(raw, now=ANCHOR)
    assert len(ranges) == 1
    r = ranges[0]
    assert r.specificity == "day_vague"
    assert (r.start_datetime.hour, r.start_datetime.minute) == (0, 0)
    assert r.is_flexible is True
