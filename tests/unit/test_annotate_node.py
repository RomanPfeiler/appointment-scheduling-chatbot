"""Unit tests for orchestrator.nodes.annotate.annotate_node.

Covers:
- Baseline pass-through (all flags off → ``{}``)
- Flag-on with the Arm 1 parser/extractor populating ``last_annotation``
- Arm 2 (local_llm) runs through the factory with the LLM mocked
- Empty user message returns ``{}`` cleanly
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from google.genai import types

from nlp.factory import build_datetime_parser, build_entity_extractor
from orchestrator.nodes.annotate import annotate_node
from orchestrator.state import default_state

ZURICH = ZoneInfo("Europe/Zurich")


def _user_message(text: str) -> types.Content:
    return types.Content(role="user", parts=[types.Part.from_text(text=text)])


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


def test_pass_through_when_all_flags_off() -> None:
    state = default_state()
    state["messages"] = [_user_message("I'd like to book next Tuesday at 2pm.")]
    out = _run(annotate_node(state, {"configurable": {}}))
    assert out == {}


def test_populates_last_annotation_when_flags_on() -> None:
    state = default_state()
    state["messages"] = [_user_message("I'd like to discuss a mortgage at the branch.")]
    config = {
        "configurable": {
            "nlp_datetime_enabled": True,
            "nlp_entity_enabled": True,
            "datetime_arm": "dateparser",
            "entity_arm": "spacy",
            "_dt_parser": build_datetime_parser("dateparser"),
            "_ent_extractor": build_entity_extractor("spacy"),
        }
    }
    out = _run(annotate_node(state, config))
    ann = out["last_annotation"]
    assert ann["raw_text"] == "I'd like to discuss a mortgage at the branch."
    assert ann["topic"] == "mortgage"
    assert ann["contact_medium"] == "branch"


def test_empty_user_message_returns_empty(monkeypatch) -> None:
    state = default_state()
    state["messages"] = []  # no user message yet
    config = {
        "configurable": {
            "nlp_datetime_enabled": True,
            "nlp_entity_enabled": True,
            "datetime_arm": "dateparser",
            "entity_arm": "spacy",
        }
    }
    out = _run(annotate_node(state, config))
    assert out == {}


def test_compound_flag_set_when_two_ranges() -> None:
    """Cleaner compound input — dateparser struggles when free-text noise
    surrounds the date tokens (e.g. "Could we do Tuesday or Thursday?"
    parses only "Thursday"). Use a tighter input here; the noisy case is a
    real Arm 1 limitation called out in the report."""
    state = default_state()
    state["messages"] = [_user_message("Tuesday or Thursday")]
    config = {
        "configurable": {
            "nlp_datetime_enabled": True,
            "nlp_entity_enabled": False,
            "datetime_arm": "dateparser",
            "_dt_parser": build_datetime_parser("dateparser"),
        }
    }
    out = _run(annotate_node(state, config))
    ann = out["last_annotation"]
    assert len(ann["datetime_ranges"]) == 2
    assert ann["entities_raw"]["compound"] is True


def test_arm2_runs_through_factory_with_mocked_llm(monkeypatch) -> None:
    # Arm 2 is implemented now; selecting it through annotate populates
    # last_annotation. Mock the LLM so this unit test never loads the GGUF.
    from nlp import local_llm

    monkeypatch.setattr(
        local_llm,
        "generate",
        lambda *a, **k: "<dt><expr>next Tuesday</expr><spec>day_vague</spec></dt>",
    )
    state = default_state()
    state["messages"] = [_user_message("can we meet next Tuesday?")]
    config = {
        "configurable": {
            "nlp_datetime_enabled": True,
            "datetime_arm": "local_llm",  # arm 2
        }
    }
    out = _run(annotate_node(state, config))
    ann = out["last_annotation"]
    assert len(ann["datetime_ranges"]) == 1
    assert ann["datetime_ranges"][0]["specificity"] == "day_vague"


class _RecordingParser:
    """Stub datetime parser that records the ``now`` it was given."""

    arm_name = "recording"

    def __init__(self) -> None:
        self.seen_now: datetime | None = None

    def parse(self, text: str, *, now: datetime):
        self.seen_now = now
        return []


def test_uses_reference_date_as_now_when_present() -> None:
    """In a pinned run the parser's relative base is the scenario reference_date
    (noon Europe/Zurich), not the wall clock — never wall-clock during a run."""
    parser = _RecordingParser()
    state = default_state()
    state["messages"] = [_user_message("can we meet next Tuesday?")]
    config = {
        "configurable": {
            "nlp_datetime_enabled": True,
            "datetime_arm": "recording",
            "_dt_parser": parser,
            "reference_date": "2026-06-01",
        }
    }
    _run(annotate_node(state, config))
    assert parser.seen_now == datetime(2026, 6, 1, 12, 0, tzinfo=ZURICH)


def test_falls_back_to_wall_clock_when_no_reference_date() -> None:
    """Interactive chat (no reference_date) → the parser's base is the wall clock."""
    parser = _RecordingParser()
    state = default_state()
    state["messages"] = [_user_message("can we meet tomorrow?")]
    config = {
        "configurable": {
            "nlp_datetime_enabled": True,
            "datetime_arm": "recording",
            "_dt_parser": parser,
        }
    }
    _run(annotate_node(state, config))
    assert parser.seen_now is not None
    assert parser.seen_now.tzinfo is not None
    assert abs(parser.seen_now - datetime.now(ZURICH)) < timedelta(minutes=1)


def test_debug_record_emitted_when_active() -> None:
    state = default_state()
    state["messages"] = [_user_message("tomorrow at 2pm")]
    config = {
        "configurable": {
            "nlp_datetime_enabled": True,
            "nlp_entity_enabled": False,
            "datetime_arm": "dateparser",
            "_dt_parser": build_datetime_parser("dateparser"),
        }
    }
    out = _run(annotate_node(state, config))
    assert "debug_log" in out
    assert len(out["debug_log"]) == 1
    assert out["debug_log"][0]["node"] == "annotate_node"
