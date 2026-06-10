"""Unit tests for evaluation.runner.stage_to_flags."""

from __future__ import annotations

import pytest

from evaluation.runner import _active_local_model, stage_to_flags


def test_baseline_returns_all_off() -> None:
    flags = stage_to_flags("baseline")
    assert flags["nlp_datetime_enabled"] is False
    assert flags["nlp_entity_enabled"] is False
    assert flags["datetime_arm"] is None
    assert flags["entity_arm"] is None
    assert flags["nlp_llm_backend"] is None


def test_nlp_arm1_sets_dateparser_and_spacy() -> None:
    flags = stage_to_flags("nlp_arm1")
    assert flags["nlp_datetime_enabled"] is True
    assert flags["nlp_entity_enabled"] is True
    assert flags["datetime_arm"] == "dateparser"
    assert flags["entity_arm"] == "spacy"


def test_nlp_arm2_sets_local_llm() -> None:
    flags = stage_to_flags("nlp_arm2")
    assert flags["datetime_arm"] == "local_llm"
    assert flags["entity_arm"] == "local_llm"
    assert flags["nlp_llm_backend"] == "local"


def test_nlp_arm3_sets_api_llm() -> None:
    flags = stage_to_flags("nlp_arm3")
    assert flags["datetime_arm"] == "api_llm"
    assert flags["entity_arm"] == "api_llm"
    assert flags["nlp_llm_backend"] == "api"
    # Arm 3 alone must NOT turn on the executor expansion policy.
    assert flags["expansion_policy_enabled"] is False


def test_expansion_sets_only_executor_policy() -> None:
    flags = stage_to_flags("expansion")
    assert flags["expansion_policy_enabled"] is True
    # Expansion alone must keep every NLP component off.
    assert flags["nlp_datetime_enabled"] is False
    assert flags["nlp_entity_enabled"] is False
    assert flags["datetime_arm"] is None
    assert flags["entity_arm"] is None


def test_nlp_arm3_expansion_sets_both_families() -> None:
    # The combined stage composes the orthogonal flag families: Arm 3 NLP
    # (annotate-side) AND the executor expansion policy (execute-side).
    flags = stage_to_flags("nlp_arm3_expansion")
    assert flags["nlp_datetime_enabled"] is True
    assert flags["nlp_entity_enabled"] is True
    assert flags["datetime_arm"] == "api_llm"
    assert flags["entity_arm"] == "api_llm"
    assert flags["nlp_llm_backend"] == "api"
    assert flags["expansion_policy_enabled"] is True


def test_baseline_and_arms_leave_expansion_off() -> None:
    # No shared-key clobber: only the two expansion-bearing stages enable it.
    for stage in ("baseline", "nlp_arm1", "nlp_arm2", "nlp_arm3"):
        assert stage_to_flags(stage)["expansion_policy_enabled"] is False


@pytest.mark.parametrize(
    "stage", ["nlp", "planner", "robustness", "adhoc", "unknown_stage"]
)
def test_non_arm_stages_return_baseline_defaults(stage: str) -> None:
    flags = stage_to_flags(stage)
    assert flags["nlp_datetime_enabled"] is False
    assert flags["nlp_entity_enabled"] is False


@pytest.mark.parametrize(
    "weak_stage,strong_stage",
    [
        ("weak_baseline", "baseline"),
        ("weak_nlp_arm1", "nlp_arm1"),
        ("weak_nlp_arm2", "nlp_arm2"),
        ("weak_nlp_arm3", "nlp_arm3"),
        ("weak_expansion", "expansion"),
        ("weak_nlp_arm3_expansion", "nlp_arm3_expansion"),
    ],
)
def test_weak_stages_mirror_strong_flag_families(weak_stage: str, strong_stage: str) -> None:
    # ARCHITECTURE §8 2026-06-10: the weak family differs ONLY in agent model +
    # thinking budget (RunConfig), never in the NLP/expansion flags — so the
    # paired weak-vs-weak comparisons isolate the same interventions.
    assert stage_to_flags(weak_stage) == stage_to_flags(strong_stage)


def test_active_local_model_none_for_non_local_arms() -> None:
    # No local arm in play → nothing recorded, no import cost.
    assert _active_local_model(stage_to_flags("baseline")) is None
    assert _active_local_model(stage_to_flags("nlp_arm1")) is None
    assert _active_local_model(stage_to_flags("nlp_arm3")) is None


def test_active_local_model_records_model_key_for_arm2(monkeypatch) -> None:
    # nlp_arm2 → the run is self-describing about *which* GGUF produced it.
    monkeypatch.delenv("LOCAL_LLM_MODEL", raising=False)
    assert _active_local_model(stage_to_flags("nlp_arm2")) == "llama-3.2-3b"
    monkeypatch.setenv("LOCAL_LLM_MODEL", "qwen2.5-3b")
    assert _active_local_model(stage_to_flags("nlp_arm2")) == "qwen2.5-3b"
