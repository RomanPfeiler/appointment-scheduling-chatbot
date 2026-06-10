"""Arm 3 datetime parser — deterministic build logic proven on mocked Gemini output.

Gemini is never called: ``build_ranges`` is exercised directly on hand-written
``[{expr, specificity}]`` lists (with real ``dateparser`` resolution via the shared
neutral resolver), and ``parse`` is tested with ``api_llm.generate_json``
monkeypatched. This pins the JSON→``DateRange`` logic and every edge case without an
API key — the JSON analogue of ``test_arm2_datetime.py``.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from nlp import api_llm
from nlp.datetime_parsers.arm3_api_llm import ApiLLMDatetimeParser, build_ranges

ZURICH = ZoneInfo("Europe/Zurich")
ANCHOR = datetime(2026, 6, 1, 12, 0, tzinfo=ZURICH)  # Monday


def test_exact_time_single_range():
    exprs = [{"expr": "next Tuesday at 14:00", "specificity": "exact_time"}]
    ranges = build_ranges(exprs, now=ANCHOR)
    assert len(ranges) == 1
    r = ranges[0]
    assert r.specificity == "exact_time"
    assert r.is_flexible is False
    assert r.original_text == "next Tuesday at 14:00"
    assert (r.start_datetime.hour, r.start_datetime.minute) == (14, 0)  # time kept
    assert r.end_datetime == r.start_datetime + timedelta(hours=1)
    assert r.start_datetime.tzinfo is not None  # tz-aware


def test_no_expressions_yields_empty():
    assert build_ranges([], now=ANCHOR) == []


def test_compound_two_ranges_snapped_to_midnight():
    exprs = [
        {"expr": "Tuesday", "specificity": "day_vague"},
        {"expr": "Thursday", "specificity": "day_vague"},
    ]
    ranges = build_ranges(exprs, now=ANCHOR)
    assert len(ranges) == 2
    for r in ranges:
        assert r.specificity == "day_vague"
        assert r.is_flexible is True
        assert (r.start_datetime.hour, r.start_datetime.minute) == (0, 0)  # snapped


def test_unresolvable_expr_is_skipped_not_committed():
    # Recognition "succeeded" but dateparser can't resolve it → skip, don't emit a
    # wrong DateRange.
    exprs = [{"expr": "xyzzy qwerty", "specificity": "day_vague"}]
    assert build_ranges(exprs, now=ANCHOR) == []


def test_out_of_enum_spec_is_skipped():
    exprs = [{"expr": "tomorrow", "specificity": "not_a_spec"}]
    assert build_ranges(exprs, now=ANCHOR) == []


def test_day_specific_snaps_and_ends_end_of_day():
    exprs = [{"expr": "14 March", "specificity": "day_specific"}]
    ranges = build_ranges(exprs, now=ANCHOR)
    assert len(ranges) == 1
    r = ranges[0]
    assert r.specificity == "day_specific"
    assert r.is_flexible is False
    assert (r.start_datetime.hour, r.start_datetime.minute) == (0, 0)
    assert (r.end_datetime.hour, r.end_datetime.minute) == (23, 59)


def test_multi_day_vague_five_day_span():
    exprs = [{"expr": "next week", "specificity": "multi_day_vague"}]
    ranges = build_ranges(exprs, now=ANCHOR)
    assert len(ranges) == 1
    r = ranges[0]
    assert r.specificity == "multi_day_vague"
    assert r.is_flexible is True
    assert (r.end_datetime - r.start_datetime).days == 4


def test_parse_method_uses_generate_json(monkeypatch):
    captured: dict[str, object] = {}

    def fake_generate_json(prompt, **kwargs):
        captured["prompt"] = prompt
        captured["system"] = kwargs.get("system")
        return {"expressions": [{"expr": "tomorrow", "specificity": "day_vague"}]}

    monkeypatch.setattr(api_llm, "generate_json", fake_generate_json)
    ranges = ApiLLMDatetimeParser().parse("can I come tomorrow?", now=ANCHOR)
    assert len(ranges) == 1 and ranges[0].specificity == "day_vague"
    assert "Current date:" in captured["prompt"]  # now passed for linguistic context


def test_parse_method_skips_api_on_empty_text(monkeypatch):
    called = {"n": 0}

    def fake_generate_json(*a, **k):
        called["n"] += 1
        return {"expressions": []}

    monkeypatch.setattr(api_llm, "generate_json", fake_generate_json)
    assert ApiLLMDatetimeParser().parse("   ", now=ANCHOR) == []
    assert called["n"] == 0  # no API call for empty input


def test_parse_tolerates_empty_or_malformed_response(monkeypatch):
    # generate_json returns {} on an empty/non-JSON Gemini response → no ranges,
    # no crash.
    monkeypatch.setattr(api_llm, "generate_json", lambda *a, **k: {})
    assert ApiLLMDatetimeParser().parse("sometime next week?", now=ANCHOR) == []


def test_last_diagnostics_separates_recognition_and_resolution(monkeypatch):
    parser = ApiLLMDatetimeParser()

    # recognized AND resolved
    monkeypatch.setattr(
        api_llm, "generate_json",
        lambda *a, **k: {"expressions": [{"expr": "tomorrow", "specificity": "day_vague"}]},
    )
    parser.parse("tomorrow?", now=ANCHOR)
    d = parser.last_diagnostics()
    assert d["recognized"] == ["tomorrow"] and d["resolved"] == ["tomorrow"]
    assert d["unresolved"] == []

    # recognized but UNRESOLVABLE → a resolution failure, not a recognition one
    monkeypatch.setattr(
        api_llm, "generate_json",
        lambda *a, **k: {"expressions": [{"expr": "xyzzy qwerty", "specificity": "day_vague"}]},
    )
    parser.parse("hmm", now=ANCHOR)
    d = parser.last_diagnostics()
    assert d["recognized"] == ["xyzzy qwerty"] and d["resolved"] == []
    assert d["unresolved"] == ["xyzzy qwerty"]

    # no expressions → a recognition failure (nothing recognized at all)
    monkeypatch.setattr(api_llm, "generate_json", lambda *a, **k: {"expressions": []})
    parser.parse("I like turtles", now=ANCHOR)
    d = parser.last_diagnostics()
    assert d["recognized"] == [] and d["resolved"] == [] and d["unresolved"] == []
