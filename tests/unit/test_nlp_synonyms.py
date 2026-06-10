"""Unit tests for nlp.synonyms — the canonical lists feeding the spaCy arm.

These tests are sanity checks: matcher ambiguity, casing, and the presence
of the three required ids in each dict.
"""

from __future__ import annotations

from nlp.synonyms import (
    SYNONYMS_MEDIUM,
    SYNONYMS_TOPIC,
    all_medium_synonyms,
    all_topic_synonyms,
)


def test_topic_dict_has_three_required_ids() -> None:
    assert set(SYNONYMS_TOPIC) == {"investing", "mortgage", "pension"}


def test_medium_dict_has_three_required_ids() -> None:
    assert set(SYNONYMS_MEDIUM) == {"branch", "online", "phone"}


def test_every_synonym_is_lowercase() -> None:
    for syns in SYNONYMS_TOPIC.values():
        for s in syns:
            assert s == s.lower(), f"non-lowercase topic synonym: {s!r}"
    for syns in SYNONYMS_MEDIUM.values():
        for s in syns:
            assert s == s.lower(), f"non-lowercase medium synonym: {s!r}"


def test_no_empty_synonyms() -> None:
    for syns in SYNONYMS_TOPIC.values():
        for s in syns:
            assert s.strip(), "empty topic synonym"
    for syns in SYNONYMS_MEDIUM.values():
        for s in syns:
            assert s.strip(), "empty medium synonym"


def test_topic_and_medium_synonym_sets_do_not_overlap() -> None:
    """A literal that appears in both classes would create matcher ambiguity."""
    overlap = all_topic_synonyms() & all_medium_synonyms()
    assert overlap == set(), f"topic/medium overlap: {overlap}"


def test_per_topic_synonyms_disjoint() -> None:
    """Within the topic dict, each surface form maps to exactly one topic."""
    seen: dict[str, str] = {}
    for topic_id, syns in SYNONYMS_TOPIC.items():
        for s in syns:
            assert s not in seen, f"{s!r} appears in both {seen[s]} and {topic_id}"
            seen[s] = topic_id


def test_per_medium_synonyms_disjoint() -> None:
    """Within the medium dict, each surface form maps to exactly one medium."""
    seen: dict[str, str] = {}
    for medium_id, syns in SYNONYMS_MEDIUM.items():
        for s in syns:
            assert s not in seen, f"{s!r} appears in both {seen[s]} and {medium_id}"
            seen[s] = medium_id
