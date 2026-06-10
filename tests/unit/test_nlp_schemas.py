"""Unit tests for nlp.schemas (Pydantic AnnotatedMessage + DateRange).

Cover round-trip via ``model_dump(mode="json")`` since that is exactly how
the annotate node writes ``last_annotation`` to ConversationState.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from nlp.schemas import AnnotatedMessage, DateRange


ZURICH = ZoneInfo("Europe/Zurich")


def test_date_range_minimal_fields() -> None:
    start = datetime(2026, 6, 15, 14, 0, tzinfo=ZURICH)
    end = start + timedelta(hours=1)
    rng = DateRange(
        start_datetime=start,
        end_datetime=end,
        original_text="at 2pm on June 15",
        specificity="exact_time",
    )
    assert rng.is_flexible is False
    assert rng.specificity == "exact_time"


def test_date_range_rejects_unknown_specificity() -> None:
    start = datetime(2026, 6, 15, 14, 0, tzinfo=ZURICH)
    with pytest.raises(ValidationError):
        DateRange(
            start_datetime=start,
            end_datetime=start + timedelta(hours=1),
            original_text="x",
            specificity="not_a_real_value",  # type: ignore[arg-type]
        )


def test_annotated_message_defaults_are_empty_not_none() -> None:
    am = AnnotatedMessage(raw_text="hello")
    assert am.topic is None
    assert am.contact_medium is None
    assert am.datetime_ranges == []
    assert am.entities_raw == {}
    assert am.intent == "schedule"
    assert am.confidence == 1.0


def test_annotated_message_round_trip_via_model_dump_json() -> None:
    start = datetime(2026, 6, 15, 14, 0, tzinfo=ZURICH)
    rng = DateRange(
        start_datetime=start,
        end_datetime=start + timedelta(hours=1),
        original_text="at 2pm",
        specificity="exact_time",
    )
    am = AnnotatedMessage(
        raw_text="June 15 at 2pm please",
        topic="investing",
        contact_medium="branch",
        datetime_ranges=[rng],
        entities_raw={"compound": False, "topic_matches": []},
    )
    dumped = am.model_dump(mode="json")
    # Must be JSON-serialisable for LangGraph state storage.
    encoded = json.dumps(dumped)
    decoded = json.loads(encoded)
    restored = AnnotatedMessage(**decoded)
    assert restored.topic == "investing"
    assert restored.contact_medium == "branch"
    assert len(restored.datetime_ranges) == 1
    assert restored.datetime_ranges[0].specificity == "exact_time"
    # Start datetime survives the round trip with its timezone.
    assert restored.datetime_ranges[0].start_datetime == start


def test_specificity_literal_accepts_all_five_values() -> None:
    start = datetime(2026, 6, 15, tzinfo=ZURICH)
    end = start + timedelta(days=1)
    for spec in ("exact_time", "day_specific", "day_vague", "multi_day_vague", "compound"):
        DateRange(
            start_datetime=start,
            end_datetime=end,
            original_text="x",
            specificity=spec,  # type: ignore[arg-type]
        )
