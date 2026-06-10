"""Unit tests for the phrase-bank domain filter (evaluation/mining/domain_filter.py).

The filter drops entries whose text contains an out-of-domain keyword
(movie / restaurant / hotel / event / weather / ...) or whose source_service
matches a known out-of-domain prefix (Restaurants_, Hotels_, Events_, ...).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from evaluation.mining import domain_filter


def test_filter_drops_movie_phrase() -> None:
    entries = [
        {"expression_text": "I haven't seen a good movie in some time."},
        {"expression_text": "Book me next Tuesday at 9am."},
    ]
    kept, result = domain_filter.filter_entries(entries)
    assert len(kept) == 1
    assert kept[0]["expression_text"].startswith("Book me")
    assert result.total_before == 2
    assert result.total_after == 1
    assert result.dropped == 1
    assert result.dropped_by_keyword == 1
    assert result.dropped_by_source == 0


def test_filter_drops_hotel_source_service() -> None:
    entries = [
        {"expression_text": "next Tuesday at 9am", "source_service": "Hotels_1"},
        {"expression_text": "next Wednesday morning", "source_service": "Banks_1"},
    ]
    kept, result = domain_filter.filter_entries(entries)
    assert len(kept) == 1
    assert kept[0]["source_service"] == "Banks_1"
    assert result.dropped_by_source == 1
    assert result.dropped_by_keyword == 0


def test_filter_drops_event_in_keyword() -> None:
    entries = [
        {"expression_text": "Is there any Blues event in Phoenix next Wednesday?"},
        {"expression_text": "I'd like an appointment next Wednesday."},
    ]
    kept, result = domain_filter.filter_entries(entries)
    assert len(kept) == 1
    assert "Blues event" not in kept[0]["expression_text"]


def test_filter_preserves_in_domain_phrasings() -> None:
    entries = [
        {"expression_text": "next Tuesday at 9am", "source_service": "Banks_2"},
        {"expression_text": "sometime next week", "source_service": "Services_3"},
        {"expression_text": "tomorrow morning at 10", "source_service": None},
    ]
    kept, result = domain_filter.filter_entries(entries)
    assert len(kept) == 3
    assert result.dropped == 0


def test_filter_keyword_is_case_insensitive() -> None:
    entries = [
        {"expression_text": "Need a TABLE FOR two next Friday."},
        {"expression_text": "Book this appointment for next Friday."},
    ]
    kept, result = domain_filter.filter_entries(entries)
    assert len(kept) == 1


def test_apply_to_phrase_bank_writes_backup(tmp_path: Path) -> None:
    bank = tmp_path / "temporal_expressions.json"
    log = tmp_path / "bucket_log.md"
    entries = [
        {"expression_text": "I haven't seen a good movie in some time."},
        {"expression_text": "Book me next Tuesday at 9am."},
    ]
    bank.write_text(json.dumps(entries), encoding="utf-8")

    result = domain_filter.apply_to_phrase_bank(
        bank_path=bank, bucket_log_path=log
    )
    # The backup should exist with original entries.
    backup = bank.with_name("temporal_expressions_pre_filter.json")
    assert backup.exists()
    assert json.loads(backup.read_text(encoding="utf-8")) == entries
    # The bank itself should be filtered.
    new = json.loads(bank.read_text(encoding="utf-8"))
    assert len(new) == 1
    assert new[0]["expression_text"].startswith("Book me")
    # The bucket log got appended.
    assert log.exists()
    text = log.read_text(encoding="utf-8")
    assert "out-of-domain filter pass" in text
    assert "Entries before: 2" in text
    assert "Entries after: 1" in text

    assert result.dropped == 1
    assert result.examples  # at least one example recorded


def test_apply_to_phrase_bank_does_not_overwrite_existing_backup(tmp_path: Path) -> None:
    """Second run mustn't clobber the first backup."""
    bank = tmp_path / "temporal_expressions.json"
    log = tmp_path / "bucket_log.md"
    entries = [
        {"expression_text": "Book me next Tuesday at 9am."},
        {"expression_text": "I'd like a movie tonight."},
    ]
    bank.write_text(json.dumps(entries), encoding="utf-8")
    domain_filter.apply_to_phrase_bank(bank_path=bank, bucket_log_path=log)
    backup = bank.with_name("temporal_expressions_pre_filter.json")
    first_backup_mtime = backup.stat().st_mtime_ns
    first_backup_content = backup.read_text(encoding="utf-8")

    # Second run.
    domain_filter.apply_to_phrase_bank(bank_path=bank, bucket_log_path=log)
    assert backup.stat().st_mtime_ns == first_backup_mtime
    assert backup.read_text(encoding="utf-8") == first_backup_content
