"""Unit tests for nlp.factory — arm dispatch.

Arm 1 (dateparser/spacy), Arm 2 (local_llm), and Arm 3 (api_llm) all construct.
Arm 2 construction must be lazy — building it must NOT load the GGUF; Arm 3
construction must be lazy too — building it must NOT create the Gemini client or
require an API key (both load on first parse/extract).
"""

from __future__ import annotations

import pytest

from nlp import api_llm, local_llm
from nlp.factory import build_datetime_parser, build_entity_extractor


def test_datetime_arm1_constructs() -> None:
    p = build_datetime_parser("dateparser")
    assert p.arm_name == "dateparser"


def test_entity_arm1_constructs() -> None:
    e = build_entity_extractor("spacy")
    assert e.arm_name == "spacy"


def test_datetime_arm2_constructs_without_loading_model() -> None:
    before = dict(local_llm._INSTANCES)
    p = build_datetime_parser("local_llm")
    assert p.arm_name == "local_llm"
    # Lazy: construction must not load a GGUF (model cache unchanged).
    assert local_llm._INSTANCES == before


def test_datetime_arm3_constructs_without_client_or_key() -> None:
    before = api_llm._CLIENT
    p = build_datetime_parser("api_llm")
    assert p.arm_name == "api_llm"
    # Lazy: construction must not create the Gemini client (it builds on first parse).
    assert api_llm._CLIENT is before


def test_entity_arm2_constructs_without_loading_model() -> None:
    before = dict(local_llm._INSTANCES)
    e = build_entity_extractor("local_llm")
    assert e.arm_name == "local_llm"
    # Lazy: construction must not load a GGUF (model cache unchanged).
    assert local_llm._INSTANCES == before


def test_entity_arm3_constructs_without_client_or_key() -> None:
    before = api_llm._CLIENT
    e = build_entity_extractor("api_llm")
    assert e.arm_name == "api_llm"
    # Lazy: construction must not create the Gemini client (it builds on first extract).
    assert api_llm._CLIENT is before


def test_unknown_datetime_arm_raises_value_error() -> None:
    with pytest.raises(ValueError, match="unknown datetime arm"):
        build_datetime_parser("not_a_real_arm")


def test_unknown_entity_arm_raises_value_error() -> None:
    with pytest.raises(ValueError, match="unknown entity arm"):
        build_entity_extractor("not_a_real_arm")
