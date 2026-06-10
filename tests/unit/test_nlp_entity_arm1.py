"""End-to-end unit tests for the Arm 1 spaCy entity extractor.

These do not require the trained ``en_core_web_sm`` model — the constructor
falls back to a blank English pipeline. The ``LOWER`` attribute matching
does not need the trained model.
"""

from __future__ import annotations

import pytest

from nlp.entity_extractors.arm1_spacy import SpacyEntityExtractor


@pytest.fixture(scope="module")
def extractor() -> SpacyEntityExtractor:
    return SpacyEntityExtractor()


def test_empty_input_returns_none_none_empty(extractor: SpacyEntityExtractor) -> None:
    topic, medium, raw = extractor.extract("")
    assert topic is None
    assert medium is None
    assert raw == {}


def test_canonical_investing_match(extractor: SpacyEntityExtractor) -> None:
    topic, medium, raw = extractor.extract("I'd like to talk about investing.")
    assert topic == "investing"
    assert medium is None
    assert raw["topic_matches"]


def test_canonical_mortgage_match(extractor: SpacyEntityExtractor) -> None:
    topic, _, _ = extractor.extract("I'd like to discuss a mortgage.")
    assert topic == "mortgage"


def test_canonical_pension_match(extractor: SpacyEntityExtractor) -> None:
    topic, _, _ = extractor.extract("I'd like to talk about my pension.")
    assert topic == "pension"


def test_canonical_branch_match(extractor: SpacyEntityExtractor) -> None:
    _, medium, _ = extractor.extract("Can I come to the branch?")
    assert medium == "branch"


def test_canonical_online_match(extractor: SpacyEntityExtractor) -> None:
    _, medium, _ = extractor.extract("Let's do a video call.")
    assert medium == "online"


def test_canonical_phone_match(extractor: SpacyEntityExtractor) -> None:
    _, medium, _ = extractor.extract("Could you call me?")
    assert medium == "phone"


def test_no_topic_no_medium_when_neutral(extractor: SpacyEntityExtractor) -> None:
    topic, medium, _ = extractor.extract("Thanks for the help.")
    assert topic is None
    assert medium is None


def test_multi_token_phrase_matches(extractor: SpacyEntityExtractor) -> None:
    """`home loan` is a two-token phrase — PhraseMatcher must match it."""
    topic, _, _ = extractor.extract("Can I book a meeting about a home loan?")
    assert topic == "mortgage"


def test_case_insensitive_matching(extractor: SpacyEntityExtractor) -> None:
    topic, medium, _ = extractor.extract("MORTGAGE advice at the BRANCH please.")
    assert topic == "mortgage"
    assert medium == "branch"


def test_paraphrase_does_not_match(extractor: SpacyEntityExtractor) -> None:
    """`grow my money` is the paraphrase test — spaCy should NOT match."""
    topic, medium, _ = extractor.extract("I want to grow my money.")
    assert topic is None
    assert medium is None


def test_both_topic_and_medium_extracted(extractor: SpacyEntityExtractor) -> None:
    topic, medium, _ = extractor.extract(
        "I'd like to discuss a mortgage at the branch."
    )
    assert topic == "mortgage"
    assert medium == "branch"


def test_arm_name_is_spacy(extractor: SpacyEntityExtractor) -> None:
    assert extractor.arm_name == "spacy"


def test_longest_match_wins_for_overlapping_synonyms(
    extractor: SpacyEntityExtractor,
) -> None:
    """In "investment portfolio", "invest", "investment", "portfolio" all match
    investing. The longest token-span match wins."""
    topic, _, raw = extractor.extract("Can I schedule a meeting about my investment portfolio?")
    assert topic == "investing"
    # Several matches should be present.
    assert len(raw["topic_matches"]) >= 2
