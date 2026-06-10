"""Arm 3 entity extractor — deterministic mapping proven on mocked Gemini output.

Gemini is never called: ``parse_entity_response`` is exercised on hand-written
decoded JSON dicts, and ``extract`` is tested with ``api_llm.generate_json``
monkeypatched. Pins the dict→``(topic, medium, raw)`` logic and the edge cases
without an API key — the JSON analogue of ``test_arm2_entity.py``.
"""

from __future__ import annotations

from nlp import api_llm
from nlp.entity_extractors.arm3_api_llm import (
    ApiLLMEntityExtractor,
    parse_entity_response,
)


def test_both_slots_filled():
    topic, medium, raw = parse_entity_response(
        {"topic": "mortgage", "contact_medium": "online"}
    )
    assert topic == "mortgage"
    assert medium == "online"
    assert "mortgage" in raw["api_llm_raw"]
    assert "model" in raw


def test_none_values_map_to_python_none():
    topic, medium, _ = parse_entity_response(
        {"topic": "none", "contact_medium": "none"}
    )
    assert topic is None
    assert medium is None


def test_missing_medium_key_yields_none_medium():
    topic, medium, _ = parse_entity_response({"topic": "pension"})
    assert topic == "pension"
    assert medium is None


def test_out_of_enum_value_maps_to_none_defensively():
    # The JSON schema prevents this in production; the parser must still be defensive.
    topic, medium, _ = parse_entity_response(
        {"topic": "banana", "contact_medium": "phone"}
    )
    assert topic is None
    assert medium == "phone"


def test_case_insensitive_values():
    topic, medium, _ = parse_entity_response(
        {"topic": "INVESTING", "contact_medium": "Branch"}
    )
    assert topic == "investing"
    assert medium == "branch"


def test_extract_uses_generate_json(monkeypatch):
    captured: dict[str, object] = {}

    def fake_generate_json(prompt, **kwargs):
        captured["prompt"] = prompt
        return {"topic": "investing", "contact_medium": "phone"}

    monkeypatch.setattr(api_llm, "generate_json", fake_generate_json)
    topic, medium, _ = ApiLLMEntityExtractor().extract("I want to invest, call me")
    assert (topic, medium) == ("investing", "phone")
    assert captured["prompt"] == "I want to invest, call me"


def test_extract_maps_paraphrase_to_canonical(monkeypatch):
    # The model's job is to map a paraphrase the synonym dict does not cover onto
    # the closest canonical class; the extractor passes that mapping through.
    monkeypatch.setattr(
        api_llm, "generate_json",
        lambda *a, **k: {"topic": "pension", "contact_medium": "online"},
    )
    topic, medium, _ = ApiLLMEntityExtractor().extract(
        "I'd like a webcam chat about my golden years fund"
    )
    assert (topic, medium) == ("pension", "online")


def test_extract_skips_api_on_empty_text(monkeypatch):
    called = {"n": 0}

    def fake_generate_json(*a, **k):
        called["n"] += 1
        return {"topic": "none", "contact_medium": "none"}

    monkeypatch.setattr(api_llm, "generate_json", fake_generate_json)
    assert ApiLLMEntityExtractor().extract("  ") == (None, None, {})
    assert called["n"] == 0


def test_extract_tolerates_empty_response(monkeypatch):
    # generate_json returns {} on an empty/non-JSON Gemini response → both slots
    # None, no crash.
    monkeypatch.setattr(api_llm, "generate_json", lambda *a, **k: {})
    topic, medium, _ = ApiLLMEntityExtractor().extract("what are your hours?")
    assert (topic, medium) == (None, None)
