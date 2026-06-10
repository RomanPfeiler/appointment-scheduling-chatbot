"""Arm 2 entity extractor — deterministic tag-parser proven on mocked LLM output.

The model is never invoked: ``parse_entity_tags`` is exercised on hand-written
tagged strings, and ``extract`` is tested with ``local_llm.generate``
monkeypatched. Pins the string→``(topic, medium, raw)`` logic and the edge cases
without the GGUF.
"""

from __future__ import annotations

from nlp import local_llm
from nlp.entity_extractors.arm2_local_llm import (
    LocalLLMEntityExtractor,
    parse_entity_tags,
)


def test_both_slots_filled():
    topic, medium, raw = parse_entity_tags(
        "<topic>mortgage</topic><medium>online</medium>"
    )
    assert topic == "mortgage"
    assert medium == "online"
    assert raw["local_llm_raw"] == "<topic>mortgage</topic><medium>online</medium>"
    assert "model" in raw


def test_none_values_map_to_python_none():
    topic, medium, _ = parse_entity_tags("<topic>none</topic><medium>none</medium>")
    assert topic is None
    assert medium is None


def test_missing_medium_tag_yields_none_medium():
    topic, medium, _ = parse_entity_tags("<topic>pension</topic>")
    assert topic == "pension"
    assert medium is None


def test_out_of_enum_value_maps_to_none_defensively():
    # GBNF prevents this in production; the parser must still be defensive.
    topic, medium, _ = parse_entity_tags("<topic>banana</topic><medium>phone</medium>")
    assert topic is None
    assert medium == "phone"


def test_case_insensitive_values():
    topic, medium, _ = parse_entity_tags("<topic>INVESTING</topic><medium>Branch</medium>")
    assert topic == "investing"
    assert medium == "branch"


def test_extract_uses_generate(monkeypatch):
    captured: dict[str, object] = {}

    def fake_generate(prompt, gbnf, *, system=None, max_tokens=64, key=None):
        captured["prompt"] = prompt
        return "<topic>investing</topic><medium>phone</medium>"

    monkeypatch.setattr(local_llm, "generate", fake_generate)
    topic, medium, _ = LocalLLMEntityExtractor().extract("I want to invest, call me")
    assert (topic, medium) == ("investing", "phone")
    assert captured["prompt"] == "I want to invest, call me"


def test_extract_skips_llm_on_empty_text(monkeypatch):
    called = {"n": 0}

    def fake_generate(*a, **k):
        called["n"] += 1
        return "<topic>none</topic><medium>none</medium>"

    monkeypatch.setattr(local_llm, "generate", fake_generate)
    assert LocalLLMEntityExtractor().extract("  ") == (None, None, {})
    assert called["n"] == 0
