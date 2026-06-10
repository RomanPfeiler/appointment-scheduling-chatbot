"""Arm 2 datetime parser — deterministic tag-parser proven on mocked LLM output.

The model is never invoked here: ``parse_datetime_tags`` is exercised directly
on hand-written tagged strings (with real ``dateparser`` resolution), and the
``parse`` method is tested with ``local_llm.generate`` monkeypatched. This pins
the string→``DateRange`` logic and every edge case without the GGUF.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from nlp import local_llm
from nlp.datetime_parsers.arm2_local_llm import (
    LocalLLMDatetimeParser,
    parse_datetime_tags,
)

ZURICH = ZoneInfo("Europe/Zurich")
ANCHOR = datetime(2026, 6, 1, 12, 0, tzinfo=ZURICH)  # Monday


def test_exact_time_single_range():
    raw = "<dt><expr>next Tuesday at 14:00</expr><spec>exact_time</spec></dt>"
    ranges = parse_datetime_tags(raw, now=ANCHOR)
    assert len(ranges) == 1
    r = ranges[0]
    assert r.specificity == "exact_time"
    assert r.is_flexible is False
    assert r.original_text == "next Tuesday at 14:00"
    assert (r.start_datetime.hour, r.start_datetime.minute) == (14, 0)  # time kept
    assert r.end_datetime == r.start_datetime + timedelta(hours=1)
    assert r.start_datetime.tzinfo is not None  # tz-aware


def test_none_sentinel_yields_empty():
    assert parse_datetime_tags("<none/>", now=ANCHOR) == []


def test_empty_input_yields_empty():
    assert parse_datetime_tags("", now=ANCHOR) == []


def test_compound_two_ranges_snapped_to_midnight():
    raw = (
        "<dt><expr>Tuesday</expr><spec>day_vague</spec></dt>"
        "<dt><expr>Thursday</expr><spec>day_vague</spec></dt>"
    )
    ranges = parse_datetime_tags(raw, now=ANCHOR)
    assert len(ranges) == 2
    for r in ranges:
        assert r.specificity == "day_vague"
        assert r.is_flexible is True
        assert (r.start_datetime.hour, r.start_datetime.minute) == (0, 0)  # snapped


def test_unresolvable_expr_is_skipped_not_committed():
    # Recognition "succeeded" (a <dt> block) but dateparser can't resolve it →
    # skip the item rather than emit a wrong DateRange.
    raw = "<dt><expr>xyzzy qwerty</expr><spec>day_vague</spec></dt>"
    assert parse_datetime_tags(raw, now=ANCHOR) == []


def test_out_of_enum_spec_is_skipped():
    raw = "<dt><expr>tomorrow</expr><spec>not_a_spec</spec></dt>"
    assert parse_datetime_tags(raw, now=ANCHOR) == []


def test_day_specific_snaps_and_ends_end_of_day():
    raw = "<dt><expr>14 March</expr><spec>day_specific</spec></dt>"
    ranges = parse_datetime_tags(raw, now=ANCHOR)
    assert len(ranges) == 1
    r = ranges[0]
    assert r.specificity == "day_specific"
    assert r.is_flexible is False
    assert (r.start_datetime.hour, r.start_datetime.minute) == (0, 0)
    assert (r.end_datetime.hour, r.end_datetime.minute) == (23, 59)


def test_multi_day_vague_five_day_span():
    raw = "<dt><expr>next week</expr><spec>multi_day_vague</spec></dt>"
    ranges = parse_datetime_tags(raw, now=ANCHOR)
    assert len(ranges) == 1
    r = ranges[0]
    assert r.specificity == "multi_day_vague"
    assert r.is_flexible is True
    assert (r.end_datetime - r.start_datetime).days == 4


def test_parse_method_uses_generate(monkeypatch):
    captured: dict[str, object] = {}

    def fake_generate(prompt, gbnf, *, system=None, max_tokens=256, key=None):
        captured["prompt"] = prompt
        captured["system"] = system
        return "<dt><expr>tomorrow</expr><spec>day_vague</spec></dt>"

    monkeypatch.setattr(local_llm, "generate", fake_generate)
    ranges = LocalLLMDatetimeParser().parse("can I come tomorrow?", now=ANCHOR)
    assert len(ranges) == 1 and ranges[0].specificity == "day_vague"
    assert "Current date:" in captured["prompt"]  # now passed for linguistic context


def test_last_diagnostics_separates_recognition_and_resolution(monkeypatch):
    parser = LocalLLMDatetimeParser()

    # recognized AND resolved
    monkeypatch.setattr(
        local_llm, "generate",
        lambda *a, **k: "<dt><expr>tomorrow</expr><spec>day_vague</spec></dt>",
    )
    parser.parse("tomorrow?", now=ANCHOR)
    d = parser.last_diagnostics()
    assert d["recognized"] == ["tomorrow"] and d["resolved"] == ["tomorrow"]
    assert d["unresolved"] == []

    # recognized but UNRESOLVABLE → a resolution failure, not a recognition one
    monkeypatch.setattr(
        local_llm, "generate",
        lambda *a, **k: "<dt><expr>xyzzy qwerty</expr><spec>day_vague</spec></dt>",
    )
    parser.parse("hmm", now=ANCHOR)
    d = parser.last_diagnostics()
    assert d["recognized"] == ["xyzzy qwerty"] and d["resolved"] == []
    assert d["unresolved"] == ["xyzzy qwerty"]

    # <none/> → a recognition failure (nothing recognized at all)
    monkeypatch.setattr(local_llm, "generate", lambda *a, **k: "<none/>")
    parser.parse("I like turtles", now=ANCHOR)
    d = parser.last_diagnostics()
    assert d["recognized"] == [] and d["resolved"] == [] and d["unresolved"] == []


def test_parse_method_skips_llm_on_empty_text(monkeypatch):
    called = {"n": 0}

    def fake_generate(*a, **k):
        called["n"] += 1
        return "<none/>"

    monkeypatch.setattr(local_llm, "generate", fake_generate)
    assert LocalLLMDatetimeParser().parse("   ", now=ANCHOR) == []
    assert called["n"] == 0  # no model call for empty input
