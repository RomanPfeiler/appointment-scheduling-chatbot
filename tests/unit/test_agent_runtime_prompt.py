"""Unit tests for the per-turn runtime-context block injected by
`orchestrator.nodes.agent._build_system_prompt`.

The block must:
- Contain today's date in YYYY-MM-DD form.
- Name the current Zurich offset (`+01:00` in winter / `+02:00` in summer).
- Use CEST/CET labels matching the offset.
- Prepend the static prompt rather than replace it.
"""

from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

from orchestrator.nodes.agent import (
    SYSTEM_PROMPT,
    _build_system_prompt,
    _reference_now_from_config,
)


_ZURICH = ZoneInfo("Europe/Zurich")


def test_runtime_block_includes_today_isodate() -> None:
    now = datetime(2026, 6, 15, 10, 30, tzinfo=_ZURICH)  # mid-June -> CEST
    prompt = _build_system_prompt(now=now)
    assert "2026-06-15" in prompt


def test_runtime_block_uses_cest_offset_in_summer() -> None:
    now = datetime(2026, 6, 15, 10, 30, tzinfo=_ZURICH)
    prompt = _build_system_prompt(now=now)
    assert "+02:00" in prompt
    assert "CEST" in prompt
    assert "CET (" not in prompt  # don't accidentally say BOTH labels in the same line


def test_runtime_block_uses_cet_offset_in_winter() -> None:
    now = datetime(2026, 1, 15, 10, 30, tzinfo=_ZURICH)
    prompt = _build_system_prompt(now=now)
    assert "+01:00" in prompt
    assert "CET" in prompt


def test_runtime_block_prepends_static_prompt() -> None:
    prompt = _build_system_prompt()
    # The static system prompt is preserved verbatim at the end.
    assert SYSTEM_PROMPT in prompt
    # And the runtime block comes BEFORE the static prompt.
    assert prompt.index("RUNTIME CONTEXT") < prompt.index(SYSTEM_PROMPT)


def test_runtime_block_mentions_zurich_explicitly() -> None:
    prompt = _build_system_prompt()
    assert "Europe/Zurich" in prompt


def test_static_prompt_no_longer_hardcodes_plus_01_00() -> None:
    """The plain-text +01:00 example was removed (it biased Gemini in summer)."""
    # The static prompt should NOT contain a bare "+01:00" example string —
    # any offset reference is now in the runtime block (where it's correct
    # for the current date). Tolerate the runtime block which legitimately
    # mentions both offsets; check the static-only file.
    from pathlib import Path
    static_path = (
        Path(__file__).resolve().parent.parent.parent
        / "orchestrator" / "prompts" / "appointment_assistant.md"
    )
    text = static_path.read_text(encoding="utf-8")
    # The example "2025-03-20T08:00:00+01:00" used to live in the prompt and
    # biased Gemini to always use +01:00 — make sure it's gone.
    assert "2025-03-20T08:00:00+01:00" not in text


# ─── reference_date injection (EVALUATION_FRAMEWORK §3a) ──────────────────


def test_reference_now_built_from_config_reference_date() -> None:
    """The runner-injected reference_date becomes the agent's 'today' at midday Zurich."""
    now = _reference_now_from_config({"configurable": {"reference_date": "2026-06-01"}})
    assert now == datetime(2026, 6, 1, 12, 0, tzinfo=_ZURICH)
    # And it flows into the prompt as today's date.
    assert "2026-06-01" in _build_system_prompt(now=now)


def test_reference_now_none_without_config() -> None:
    """Production path sets no reference_date → wall clock (None) → prompt unchanged."""
    assert _reference_now_from_config({}) is None
    assert _reference_now_from_config({"configurable": {}}) is None


def test_reference_now_none_on_unparseable_value() -> None:
    assert _reference_now_from_config({"configurable": {"reference_date": "not-a-date"}}) is None


# ─── NLP HINTS injection (IMPROVEMENT_PLAN §7a) ───────────────────────────


def test_baseline_no_annotation_does_not_emit_nlp_hints() -> None:
    """When annotation is None (baseline), the prompt must not contain
    "NLP HINTS" — guards against accidental injection that would change
    baseline behavior."""
    now = datetime(2026, 6, 15, 10, 30, tzinfo=_ZURICH)
    prompt = _build_system_prompt(now=now, annotation=None)
    assert "NLP HINTS" not in prompt


def test_empty_annotation_dict_does_not_emit_nlp_hints() -> None:
    """An annotation dict with no actionable content (no topic, medium,
    or datetime_ranges) emits no block."""
    now = datetime(2026, 6, 15, 10, 30, tzinfo=_ZURICH)
    empty_annotation = {
        "raw_text": "hello",
        "topic": None,
        "contact_medium": None,
        "datetime_ranges": [],
        "entities_raw": {},
    }
    prompt = _build_system_prompt(now=now, annotation=empty_annotation)
    assert "NLP HINTS" not in prompt


def test_annotation_with_topic_emits_nlp_hints_block() -> None:
    now = datetime(2026, 6, 15, 10, 30, tzinfo=_ZURICH)
    annotation = {
        "raw_text": "mortgage please",
        "topic": "mortgage",
        "contact_medium": None,
        "datetime_ranges": [],
        "entities_raw": {},
    }
    prompt = _build_system_prompt(now=now, annotation=annotation)
    assert "NLP HINTS" in prompt
    assert "topic: mortgage" in prompt


def test_annotation_with_specificity_includes_per_value_guidance() -> None:
    now = datetime(2026, 6, 15, 10, 30, tzinfo=_ZURICH)
    annotation = {
        "raw_text": "next week",
        "topic": None,
        "contact_medium": None,
        "datetime_ranges": [
            {
                "start_datetime": "2026-06-22T00:00:00+02:00",
                "end_datetime": "2026-06-26T23:59:00+02:00",
                "is_flexible": True,
                "original_text": "next week",
                "specificity": "multi_day_vague",
            }
        ],
        "entities_raw": {},
    }
    prompt = _build_system_prompt(now=now, annotation=annotation)
    assert "multi_day_vague" in prompt
    assert "3-day max window" in prompt
