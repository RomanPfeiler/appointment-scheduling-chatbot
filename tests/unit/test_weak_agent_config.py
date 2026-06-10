"""Unit tests for the weak-agent-model experiment plumbing (ARCHITECTURE §8 2026-06-10).

Covers:
- ``_resolve_agent_config`` guard rails (weak stages require an explicit agent
  model, non-weak stages reject one; per-family thinking-budget defaults).
- ``agent_node`` actually carries the configured ``thinking_budget`` into the
  Gemini ``GenerateContentConfig`` (the 2026-03-22 doc/code-discrepancy lesson:
  a documented thinking intent must be implemented + asserted in the call path).
- ``call_gemini`` extracts ``thoughts_token_count`` and the answering model's
  ``model_version`` so records are self-verifying.
- ``_verify_agent_config`` measurement-bug tripwire (wrong model / thought
  tokens under thinking-off abort the run).
- New optional schema fields default cleanly so historical records validate.
- ``_active_api_model`` records the pinned NLP-extraction model for api arms.
"""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from google.genai import types

from evaluation.runner import (
    AgentConfigMismatchError,
    _active_api_model,
    _resolve_agent_config,
    _verify_agent_config,
    stage_to_flags,
)
from evaluation.schemas import ConversationRecord, LLMCallRecord, RunConfig, TurnRecord
from orchestrator.providers.base import LLMResult
from orchestrator.providers.gemini import call_gemini

_DEFAULT = "gemini-2.5-flash"
_WEAK = "gemini-2.5-flash-lite"


# ---------------------------------------------------------------------------
# _resolve_agent_config
# ---------------------------------------------------------------------------


def test_weak_stage_requires_explicit_agent_model() -> None:
    with pytest.raises(ValueError, match="requires an explicit --agent-model"):
        _resolve_agent_config("weak_baseline", None, None)


def test_weak_stage_rejects_the_default_model() -> None:
    # Passing the strong default explicitly is still a refusal — a weak stage
    # run on the strong model would corrupt the stage label's meaning.
    with pytest.raises(ValueError, match="requires an explicit --agent-model"):
        _resolve_agent_config("weak_baseline", _DEFAULT, None)


def test_weak_stage_resolves_model_and_thinking_off() -> None:
    model, budget = _resolve_agent_config("weak_nlp_arm3", _WEAK, None)
    assert model == _WEAK
    assert budget == 0  # weak family default: thinking off


def test_weak_stage_allows_explicit_budget_override() -> None:
    _, budget = _resolve_agent_config("weak_baseline", _WEAK, -1)
    assert budget == -1


def test_non_weak_stage_rejects_foreign_agent_model() -> None:
    with pytest.raises(ValueError, match="only valid for weak_"):
        _resolve_agent_config("baseline", _WEAK, None)


def test_non_weak_stage_defaults_to_dynamic_thinking() -> None:
    model, budget = _resolve_agent_config("baseline", None, None)
    assert model == _DEFAULT
    assert budget == -1  # the standing anchor config (§8 2026-03-22 correction)


def test_non_weak_stage_accepts_the_default_model_explicitly() -> None:
    model, budget = _resolve_agent_config("expansion", _DEFAULT, None)
    assert model == _DEFAULT
    assert budget == -1


# ---------------------------------------------------------------------------
# agent_node carries the thinking budget into the Gemini call
# ---------------------------------------------------------------------------


def _fake_gemini_result() -> LLMResult:
    return LLMResult(
        has_tool_call=False,
        tool_name=None,
        tool_args=None,
        text_response="ok",
        raw_response=SimpleNamespace(candidates=[]),
        provider="gemini",
        model_used=_WEAK,
    )


async def _invoke_agent_node(monkeypatch, configurable: dict) -> types.GenerateContentConfig:
    """Run agent_node with a mocked provider; return the captured gen_config."""
    from orchestrator.nodes import agent as agent_module

    captured: dict = {}

    def fake_call_gemini(client, model, contents, config):
        captured["gen_config"] = config
        captured["model"] = model
        return _fake_gemini_result()

    monkeypatch.setattr(agent_module, "call_gemini", fake_call_gemini)
    state = {"messages": [], "turn_count": 0, "tool_result": None, "last_annotation": None}
    config = {"configurable": {"gemini_client": object(), **configurable}}
    await agent_module.agent_node(state, config)
    return captured["gen_config"]


async def test_agent_node_passes_configured_thinking_budget(monkeypatch) -> None:
    gen_config = await _invoke_agent_node(monkeypatch, {"thinking_budget": 0})
    assert gen_config.thinking_config.thinking_budget == 0


async def test_agent_node_defaults_to_dynamic_thinking(monkeypatch) -> None:
    # No thinking_budget in configurable → -1, byte-identical to every anchor run.
    gen_config = await _invoke_agent_node(monkeypatch, {})
    assert gen_config.thinking_config.thinking_budget == -1


# ---------------------------------------------------------------------------
# call_gemini: thoughts tokens + answering model version
# ---------------------------------------------------------------------------


def _fake_response(*, model_version: str | None, thoughts: int | None):
    part = SimpleNamespace(function_call=None, text="hello", thought=False)
    return SimpleNamespace(
        candidates=[
            SimpleNamespace(
                content=SimpleNamespace(parts=[part], role="model"),
                finish_reason="STOP",
            )
        ],
        usage_metadata=SimpleNamespace(
            prompt_token_count=11,
            candidates_token_count=7,
            thoughts_token_count=thoughts,
        ),
        model_version=model_version,
    )


def _client_returning(response):
    return SimpleNamespace(
        models=SimpleNamespace(generate_content=lambda **kwargs: response)
    )


def test_call_gemini_extracts_thoughts_tokens_and_model_version() -> None:
    response = _fake_response(model_version="gemini-2.5-flash-lite", thoughts=123)
    result = call_gemini(
        _client_returning(response), _WEAK, [], types.GenerateContentConfig()
    )
    assert result.thoughts_tokens == 123
    assert result.model_used == "gemini-2.5-flash-lite"


def test_call_gemini_handles_missing_thoughts_and_version() -> None:
    # Non-thinking model: no thoughts count, no model_version → fall back to the
    # requested id, thoughts None (never raises).
    response = _fake_response(model_version=None, thoughts=None)
    result = call_gemini(
        _client_returning(response), _WEAK, [], types.GenerateContentConfig()
    )
    assert result.thoughts_tokens is None
    assert result.model_used == _WEAK


# ---------------------------------------------------------------------------
# _verify_agent_config tripwire
# ---------------------------------------------------------------------------


def _record_with_call(call: LLMCallRecord, run_config: RunConfig) -> ConversationRecord:
    return ConversationRecord(
        scenario_id="t1_test_001",
        tier=1,
        stage="weak_baseline",
        run_id="test_run",
        timestamp_start=datetime.now(timezone.utc),
        git_commit="deadbeef",
        config=run_config,
        turns=[
            TurnRecord(
                turn_index=1,
                timestamp=datetime.now(timezone.utc),
                llm_calls=[call],
            )
        ],
    )


def _weak_run_config(**overrides) -> RunConfig:
    kwargs = dict(
        llm_provider="gemini",
        llm_model=_WEAK,
        llm_temperature=0.7,
        simulator_model=_DEFAULT,
        agent_thinking_budget=0,
    )
    kwargs.update(overrides)
    return RunConfig(**kwargs)


def _gemini_call(**overrides) -> LLMCallRecord:
    kwargs = dict(
        provider="gemini",
        model=_WEAK,
        prompt_message_count=1,
        response_type="text",
        thoughts_tokens=None,
    )
    kwargs.update(overrides)
    return LLMCallRecord(**kwargs)


def test_verify_passes_on_matching_record() -> None:
    rc = _weak_run_config()
    _verify_agent_config(_record_with_call(_gemini_call(), rc), rc)  # no raise


def test_verify_allows_version_suffix() -> None:
    rc = _weak_run_config()
    call = _gemini_call(model=_WEAK + "-001")
    _verify_agent_config(_record_with_call(call, rc), rc)  # no raise


def test_verify_rejects_wrong_model_family() -> None:
    # The strong model answering a weak run — exactly the "manifest records a
    # different model than the one that answered" measurement bug.
    rc = _weak_run_config()
    call = _gemini_call(model=_DEFAULT)
    with pytest.raises(AgentConfigMismatchError, match="answered by"):
        _verify_agent_config(_record_with_call(call, rc), rc)


def test_verify_rejects_lite_answering_a_strong_run() -> None:
    # Reverse direction: prefix matching must not let the -lite suffix pass.
    rc = _weak_run_config(llm_model=_DEFAULT, agent_thinking_budget=-1)
    call = _gemini_call(model=_WEAK)
    with pytest.raises(AgentConfigMismatchError, match="answered by"):
        _verify_agent_config(_record_with_call(call, rc), rc)


def test_verify_rejects_thoughts_under_thinking_off() -> None:
    rc = _weak_run_config()
    call = _gemini_call(thoughts_tokens=42)
    with pytest.raises(AgentConfigMismatchError, match="thought tokens"):
        _verify_agent_config(_record_with_call(call, rc), rc)


def test_verify_allows_thoughts_under_dynamic_thinking() -> None:
    rc = _weak_run_config(llm_model=_DEFAULT, agent_thinking_budget=-1)
    call = _gemini_call(model=_DEFAULT, thoughts_tokens=42)
    _verify_agent_config(_record_with_call(call, rc), rc)  # no raise


def test_verify_skips_non_gemini_calls() -> None:
    rc = _weak_run_config()
    call = _gemini_call(provider="claude", model="claude-sonnet-4-20250514")
    _verify_agent_config(_record_with_call(call, rc), rc)  # no raise


# ---------------------------------------------------------------------------
# Schema: additive optional fields keep old records valid
# ---------------------------------------------------------------------------


def test_run_config_new_fields_default_none() -> None:
    rc = RunConfig(llm_provider="gemini", llm_model=_DEFAULT, llm_temperature=0.7)
    assert rc.simulator_model is None
    assert rc.agent_thinking_budget is None
    assert rc.nlp_api_model is None


def test_llm_call_record_thoughts_tokens_defaults_none() -> None:
    call = LLMCallRecord(provider="gemini", prompt_message_count=1, response_type="text")
    assert call.thoughts_tokens is None


def test_run_config_round_trips_new_fields() -> None:
    rc = _weak_run_config(nlp_api_model=_DEFAULT)
    restored = RunConfig.model_validate(rc.model_dump())
    assert restored.simulator_model == _DEFAULT
    assert restored.agent_thinking_budget == 0
    assert restored.nlp_api_model == _DEFAULT


# ---------------------------------------------------------------------------
# _active_api_model (pinned NLP-extraction model, recorded for api arms)
# ---------------------------------------------------------------------------


def test_active_api_model_none_when_no_api_arm() -> None:
    assert _active_api_model(stage_to_flags("baseline")) is None
    assert _active_api_model(stage_to_flags("nlp_arm1")) is None
    assert _active_api_model(stage_to_flags("weak_expansion")) is None


def test_active_api_model_records_pinned_default(monkeypatch) -> None:
    monkeypatch.delenv("NLP_API_MODEL", raising=False)
    assert _active_api_model(stage_to_flags("nlp_arm3")) == _DEFAULT
    assert _active_api_model(stage_to_flags("weak_nlp_arm3_expansion")) == _DEFAULT


def test_active_api_model_respects_env_override(monkeypatch) -> None:
    monkeypatch.setenv("NLP_API_MODEL", "gemini-x")
    assert _active_api_model(stage_to_flags("nlp_arm3")) == "gemini-x"
