"""Unit tests for evaluation/schemas.py — round-trip validation + defaults.

Covers:
- Minimal ConversationRecord round-trips through JSON.
- Optional fields default cleanly (no required field surprises).
- Ad-hoc tier value (``"adhoc"``) is accepted alongside ints 1..7.
- JudgeScoreSet enforces the 1..5 range.
- KPIHistoryRow CSV serialisation produces a row matching the header order.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from evaluation.schemas import (
    SCHEMA_VERSION,
    ConversationRecord,
    DerivedMetrics,
    JudgeScoreSet,
    KPIHistoryRow,
    LatencyModel,
    LLMCallRecord,
    RunConfig,
    RunManifest,
    ToolCallRecord,
    TurnRecord,
)


def _minimal_config() -> RunConfig:
    return RunConfig(
        llm_provider="gemini",
        llm_model="gemini-2.5-flash",
        llm_temperature=0.7,
    )


def _minimal_record(**overrides) -> ConversationRecord:
    defaults = dict(
        scenario_id="adhoc",
        tier="adhoc",
        stage="adhoc",
        persona_profile="adhoc",
        run_index=1,
        run_id="20260524_120000__adhoc__abcd123__ses12345",
        timestamp_start=datetime(2026, 5, 24, 12, 0, 0, tzinfo=timezone.utc),
        git_commit="abcd123",
        config=_minimal_config(),
    )
    defaults.update(overrides)
    return ConversationRecord(**defaults)


def test_minimal_record_round_trip_through_json() -> None:
    record = _minimal_record()
    payload = record.model_dump_json()
    parsed = ConversationRecord.model_validate_json(payload)
    assert parsed.scenario_id == "adhoc"
    assert parsed.schema_version == SCHEMA_VERSION
    assert parsed.config.llm_provider == "gemini"
    assert parsed.config.latency_model.base_overhead_ms == 400.0


def test_record_with_turns_and_tool_calls_round_trips() -> None:
    turn = TurnRecord(
        turn_index=1,
        timestamp=datetime(2026, 5, 24, 12, 0, 5, tzinfo=timezone.utc),
        user_message="I'd like to book a mortgage appointment.",
        agent_response="Sure — which day works for you?",
        llm_calls=[
            LLMCallRecord(
                provider="gemini",
                model="gemini-2.5-flash",
                prompt_message_count=2,
                response_type="text",
                text_preview="Sure — which day works for you?",
                latency_ms=842.3,
                input_tokens=512,
                output_tokens=24,
                temperature=0.7,
            )
        ],
        tool_calls=[
            ToolCallRecord(
                tool_name="get_appointment_topics",
                parameters={},
                response=[{"topic_id": "mortgage", "topic_name": "Mortgage"}],
                actual_latency_ms=72.4,
                success=True,
            )
        ],
        state_snapshot={"phase": "topic"},
        turn_duration_ms=915.7,
    )
    record = _minimal_record(turns=[turn])
    parsed = ConversationRecord.model_validate_json(record.model_dump_json())
    assert len(parsed.turns) == 1
    assert parsed.turns[0].tool_calls[0].tool_name == "get_appointment_topics"
    assert parsed.turns[0].llm_calls[0].input_tokens == 512


def test_integer_tier_accepted() -> None:
    record = _minimal_record(tier=3, stage="baseline", persona_profile="negotiating")
    assert record.tier == 3


def test_judge_score_set_rejects_out_of_range() -> None:
    with pytest.raises(ValidationError):
        JudgeScoreSet(
            rep_index=1,
            judge_model="gemini",
            judge_temperature=0.1,
            temporal_understanding=6,  # >5, must fail
            negotiation_effectiveness=3,
            conversational_efficiency=3,
        )


def test_kpi_history_row_csv_round_trip() -> None:
    row = KPIHistoryRow(
        run_id="20260524_120000__baseline__abcd123",
        stage="baseline",
        timestamp=datetime(2026, 5, 24, 12, 0, 0, tzinfo=timezone.utc),
        git_commit="abcd123",
        change_note="initial baseline",
        scenario_count=10,
        rep_count=3,
        booking_completion_rate=0.9,
        median_turns=5.5,
    )
    header = KPIHistoryRow.csv_header()
    row_values = row.to_csv_row()
    assert len(header) == len(row_values)
    # change_note column should be present and populated
    assert row_values[header.index("change_note")] == "initial baseline"
    # missing optional fields render as empty strings
    assert row_values[header.index("faithful_rate")] == ""


def test_run_manifest_defaults_status_in_progress() -> None:
    manifest = RunManifest(
        run_id="rid",
        stage="baseline",
        timestamp_start=datetime(2026, 5, 24, tzinfo=timezone.utc),
        git_commit="abc",
        config=_minimal_config(),
    )
    assert manifest.status == "in_progress"
    assert manifest.record_count_written == 0
    assert manifest.config.latency_model == LatencyModel()


def test_derived_metrics_defaults() -> None:
    metrics = DerivedMetrics(
        total_turn_count=4,
        total_mcp_calls=2,
        availability_calls=1,
    )
    assert metrics.faithful is True
    assert metrics.unsupported_facts_count == 0
    assert metrics.booked is False
