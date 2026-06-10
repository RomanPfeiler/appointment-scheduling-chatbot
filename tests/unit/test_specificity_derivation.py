"""Direct unit tests for the surface-flag decision tree in
``nlp.datetime_parsers.arm1_dateparser._derive_specificity``.

One test per branch of the decision tree, plus a few tricky cases.
"""

from __future__ import annotations

import pytest

from nlp.datetime_parsers.arm1_dateparser import _derive_specificity


@pytest.mark.parametrize(
    "text",
    [
        "March 14 at 2pm",
        "tomorrow at 14:30",
        "next Monday at 9 o'clock",
        "April 3rd at noon",
        "Friday at 14h",
    ],
)
def test_exact_time_when_date_and_time(text: str) -> None:
    assert _derive_specificity(text) == "exact_time"


@pytest.mark.parametrize(
    "text",
    [
        "March 14",
        "April 3rd",
        "14.03",
        "2026-03-14",
        "January 7th",
    ],
)
def test_day_specific_when_date_no_time(text: str) -> None:
    assert _derive_specificity(text) == "day_specific"


@pytest.mark.parametrize(
    "text",
    [
        "tomorrow",
        "next Monday",
        "this Friday",
        "tonight",
        "in 3 days",
    ],
)
def test_day_vague_when_relative_no_time(text: str) -> None:
    assert _derive_specificity(text) == "day_vague"


@pytest.mark.parametrize(
    "text",
    [
        "next week",
        "this month",
        "sometime soon",
        "whenever",
        "within a week",
    ],
)
def test_multi_day_vague_when_multi_no_time(text: str) -> None:
    assert _derive_specificity(text) == "multi_day_vague"


def test_multi_day_dominates_when_no_time() -> None:
    """`next week Monday` → multi_day_vague wins (multi present, no time)."""
    # `next week` matches HAS_MULTI_DAY; `next Monday` matches HAS_RELATIVE_DAY.
    # Per the decision tree, HAS_MULTI_DAY and not HAS_EXPLICIT_TIME wins first.
    assert _derive_specificity("next week Monday") == "multi_day_vague"


def test_default_is_day_vague_for_ambiguous() -> None:
    """Conservative fallback when no flag matches."""
    assert _derive_specificity("xyz") == "day_vague"
    assert _derive_specificity("") == "day_vague"
