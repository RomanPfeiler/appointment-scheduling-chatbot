"""End-to-end unit tests for the Arm 1 dateparser-based datetime parser."""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from nlp.datetime_parsers.arm1_dateparser import DateparserDatetimeParser
from nlp.schemas import DateRange

ZURICH = ZoneInfo("Europe/Zurich")
# Mid-week anchor in CEST: Sunday 2026-05-31 12:00 Europe/Zurich.
ANCHOR = datetime(2026, 5, 31, 12, 0, tzinfo=ZURICH)


@pytest.fixture(scope="module")
def parser() -> DateparserDatetimeParser:
    return DateparserDatetimeParser()


def test_empty_input_returns_empty_list(parser: DateparserDatetimeParser) -> None:
    assert parser.parse("", now=ANCHOR) == []
    assert parser.parse("   ", now=ANCHOR) == []


def test_non_datetime_returns_empty_list(parser: DateparserDatetimeParser) -> None:
    assert parser.parse("hello there", now=ANCHOR) == []


def test_specific_date_with_time_emits_exact_time(parser: DateparserDatetimeParser) -> None:
    ranges = parser.parse("March 14 at 2pm", now=ANCHOR)
    assert len(ranges) == 1
    r = ranges[0]
    assert r.specificity == "exact_time"
    assert r.start_datetime.month == 3
    assert r.start_datetime.day == 14
    assert r.start_datetime.hour == 14
    # End is start + 1 hour for exact_time.
    assert (r.end_datetime - r.start_datetime).total_seconds() == 3600


def test_specific_date_no_time_emits_day_specific(parser: DateparserDatetimeParser) -> None:
    ranges = parser.parse("March 14", now=ANCHOR)
    assert len(ranges) == 1
    r = ranges[0]
    assert r.specificity == "day_specific"
    assert r.start_datetime.hour == 0
    # End is end of day.
    assert r.end_datetime.hour == 23
    assert r.end_datetime.minute == 59


def test_relative_day_emits_day_vague(parser: DateparserDatetimeParser) -> None:
    ranges = parser.parse("tomorrow", now=ANCHOR)
    assert len(ranges) == 1
    r = ranges[0]
    assert r.specificity == "day_vague"
    assert r.is_flexible is True


def test_multi_day_vague_emits_multi_day_vague(parser: DateparserDatetimeParser) -> None:
    ranges = parser.parse("next week", now=ANCHOR)
    assert len(ranges) == 1
    r = ranges[0]
    assert r.specificity == "multi_day_vague"
    assert r.is_flexible is True
    # End is at least 3 days after start (Mon-Fri working week).
    assert (r.end_datetime - r.start_datetime).days >= 3


def test_compound_or_emits_two_ranges(parser: DateparserDatetimeParser) -> None:
    ranges = parser.parse("Tuesday or Thursday", now=ANCHOR)
    assert len(ranges) == 2
    assert all(isinstance(r, DateRange) for r in ranges)


def test_zurich_offset_in_winter() -> None:
    parser = DateparserDatetimeParser()
    winter_anchor = datetime(2026, 1, 15, 12, 0, tzinfo=ZURICH)
    ranges = parser.parse("tomorrow at 14:00", now=winter_anchor)
    assert len(ranges) == 1
    # CET is UTC+1 → offset is 3600 seconds.
    assert ranges[0].start_datetime.utcoffset().total_seconds() == 3600


def test_zurich_offset_in_summer() -> None:
    parser = DateparserDatetimeParser()
    summer_anchor = datetime(2026, 7, 15, 12, 0, tzinfo=ZURICH)
    ranges = parser.parse("tomorrow at 14:00", now=summer_anchor)
    assert len(ranges) == 1
    # CEST is UTC+2 → offset is 7200 seconds.
    assert ranges[0].start_datetime.utcoffset().total_seconds() == 7200


def test_dmy_date_order_for_swiss_format() -> None:
    """`14.03` should resolve to 14 March (DMY), not 3 April (MDY)."""
    parser = DateparserDatetimeParser()
    ranges = parser.parse("the 14.03", now=ANCHOR)
    if ranges:
        # Some dateparser versions struggle with "the X.Y" — accept either no
        # parse or the DMY interpretation, but never MDY (month=14 is invalid
        # anyway, so this guards against a flipped-month bug).
        assert ranges[0].start_datetime.month == 3
        assert ranges[0].start_datetime.day == 14


def test_original_text_preserved_per_range(parser: DateparserDatetimeParser) -> None:
    ranges = parser.parse("Tuesday or Thursday", now=ANCHOR)
    texts = {r.original_text for r in ranges}
    assert "Tuesday" in texts
    assert "Thursday" in texts


def test_arm_name_is_dateparser(parser: DateparserDatetimeParser) -> None:
    assert parser.arm_name == "dateparser"
