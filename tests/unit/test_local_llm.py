"""Tests for nlp/local_llm.py scaffolding.

Covers the model-agnostic registry, env-var model selection, the timing buffer
contract, and (when llama_cpp is installed) that the production GBNF grammars
actually compile — proving the tag grammars are valid before any model runs.
"""

from __future__ import annotations

import pytest

from nlp import local_llm


def test_registry_has_both_pilot_models():
    assert set(local_llm.MODELS) == {"qwen2.5-3b", "llama-3.2-3b"}
    qwen = local_llm.MODELS["qwen2.5-3b"]
    assert qwen.repo_id == "Qwen/Qwen2.5-3B-Instruct-GGUF"
    assert qwen.filename == "qwen2.5-3b-instruct-q4_k_m.gguf"
    assert qwen.revision  # a pinned commit, not a moving ref
    llama = local_llm.MODELS["llama-3.2-3b"]
    assert llama.repo_id == "bartowski/Llama-3.2-3B-Instruct-GGUF"
    assert llama.filename == "Llama-3.2-3B-Instruct-Q4_K_M.gguf"
    assert llama.revision


def test_active_model_key_default(monkeypatch):
    # Default is the pilot-chosen model (Llama), so a plain nlp_arm2 run
    # reproduces the shipped Arm 2 (ARCHITECTURE Decision Log 2026-06-03/04).
    monkeypatch.delenv("LOCAL_LLM_MODEL", raising=False)
    assert local_llm.active_model_key() == "llama-3.2-3b"
    assert local_llm.active_model_spec().repo_id == "bartowski/Llama-3.2-3B-Instruct-GGUF"


def test_active_model_key_from_env(monkeypatch):
    # The rejected pilot candidate (Qwen) stays selectable for the comparison.
    monkeypatch.setenv("LOCAL_LLM_MODEL", "qwen2.5-3b")
    assert local_llm.active_model_key() == "qwen2.5-3b"
    assert local_llm.active_model_spec().repo_id == "Qwen/Qwen2.5-3B-Instruct-GGUF"


def test_active_model_key_invalid_raises(monkeypatch):
    monkeypatch.setenv("LOCAL_LLM_MODEL", "gpt-9000")
    with pytest.raises(ValueError, match="unknown LOCAL_LLM_MODEL"):
        local_llm.active_model_key()


def test_timing_summary_empty_after_reset():
    local_llm.reset_timings()
    summary = local_llm.timing_summary()
    assert summary["count"] == 0.0
    assert set(summary) == {"count", "mean_ms", "median_ms", "total_ms"}


def test_production_grammars_compile():
    pytest.importorskip("llama_cpp")
    from nlp.datetime_parsers.arm2_local_llm import GBNF_DATETIME
    from nlp.entity_extractors.arm2_local_llm import GBNF_ENTITY

    # from_string raises on invalid GBNF — compiling proves the tag grammars
    # are well-formed before any model is loaded.
    assert local_llm.compile_grammar(GBNF_DATETIME) is not None
    assert local_llm.compile_grammar(GBNF_ENTITY) is not None
