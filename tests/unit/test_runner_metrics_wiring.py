"""Unit tests for evaluation/runner.py — enrich_record() wiring.

Verifies that enrich_record() correctly calls extract_grounding_facts()
and compute_derived_metrics(), attaches their results to a copy of the
record, and overwrites the on-disk JSON.  All tests use synthetic fixtures
with no LLM calls and no subprocess.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from evaluation import storage
from evaluation.runner import enrich_record
from evaluation.schemas import (
    AvailabilityOverride,
    ConversationRecord,
    RunConfig,
    TurnRecord,
    ToolCallRecord,
)
from evaluation.storage import RunPaths, now_utc


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

_RUN_CONFIG = RunConfig(
    llm_provider="gemini",
    llm_model="gemini-2.5-flash",
    llm_temperature=0.7,
)

# A fixed datetime well in the future so it is always after "today+lead_time"
_SLOT_START = "2026-06-10T09:00:00+02:00"
_SLOT_END = "2026-06-10T10:00:00+02:00"


@pytest.fixture
def temp_runs_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect storage.runs_root() into tmp_path so writes are hermetic."""
    runs = tmp_path / "runs"
    reports = tmp_path / "reports"
    runs.mkdir()
    reports.mkdir()
    monkeypatch.setattr(storage, "runs_root", lambda: runs)
    monkeypatch.setattr(storage, "reports_root", lambda: reports)
    return tmp_path


@pytest.fixture
def minimal_record() -> ConversationRecord:
    """A ConversationRecord with two turns exercising grounding and availability."""
    turn1 = TurnRecord(
        turn_index=1,
        timestamp=datetime(2026, 6, 10, 8, 0, 0, tzinfo=timezone.utc),
        user_message="I'd like to book an investing appointment.",
        agent_response="I can help with Investing. Which contact method do you prefer?",
        tool_calls=[
            ToolCallRecord(
                tool_name="get_appointment_topics",
                parameters={},
                response=[{"topic_id": "investing", "topic_name": "Investing"}],
                success=True,
            )
        ],
    )
    turn2 = TurnRecord(
        turn_index=2,
        timestamp=datetime(2026, 6, 10, 8, 1, 0, tzinfo=timezone.utc),
        user_message="Phone please, how about 2026-06-10 at 9 AM?",
        agent_response=f"I found a slot at {_SLOT_START}. Shall I confirm?",
        tool_calls=[
            ToolCallRecord(
                tool_name="check_availability",
                parameters={
                    "topic_id": "investing",
                    "contact_medium_id": "phone",
                    "start_datetime": _SLOT_START,
                    "end_datetime": _SLOT_END,
                },
                response=[
                    {"datetime_start": _SLOT_START, "datetime_end": _SLOT_END}
                ],
                success=True,
            )
        ],
    )
    return ConversationRecord(
        scenario_id="t1_test_000",
        tier=1,
        stage="baseline",
        persona_profile="cooperative",
        run_index=1,
        run_id="20260610_080000__baseline__abc1234__smoke",
        timestamp_start=datetime(2026, 6, 10, 8, 0, 0, tzinfo=timezone.utc),
        timestamp_end=datetime(2026, 6, 10, 8, 2, 0, tzinfo=timezone.utc),
        git_commit="abc1234",
        config=_RUN_CONFIG,
        turns=[turn1, turn2],
        termination_reason="booked",
        derived=None,
        grounding_facts=[],
    )


@pytest.fixture
def minimal_scenario_dict() -> dict:
    """A minimal Tier 1 scenario dict compatible with Scenario.model_validate."""
    return {
        "scenario_id": "t1_test_000",
        "tier": 1,
        "description": "Direct match — test fixture",
        "topic_id": "investing",
        "contact_medium_id": "phone",
        "availability_override": {
            "slots_by_offset": {"today+2": ["09:00-10:00"]},
            "notes": "",
        },
        "simulator_goal": "Book a phone meeting about investing at 9am.",
        "persona_profile": "cooperative",
        "frozen_phrasing": "Can I get a phone meeting next Tuesday at 9?",
        "language_variant": "en_native",
        "expected_datetime_window": None,
        "optimal_availability_calls": 1,
        "expected_turn_range": [4, 5],
        "booking_reachable": True,
        "notes": "test fixture",
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_enrich_attaches_grounding_facts(
    minimal_record: ConversationRecord,
    minimal_scenario_dict: dict,
    temp_runs_root: Path,
) -> None:
    paths = RunPaths(run_id=minimal_record.run_id, stage="baseline")
    paths.ensure_dirs()

    result = enrich_record(minimal_record, minimal_scenario_dict, paths)

    assert isinstance(result.grounding_facts, list)
    assert len(result.grounding_facts) > 0, "Expected at least one grounding fact"


def test_enrich_attaches_derived_metrics(
    minimal_record: ConversationRecord,
    minimal_scenario_dict: dict,
    temp_runs_root: Path,
) -> None:
    paths = RunPaths(run_id=minimal_record.run_id, stage="baseline")
    paths.ensure_dirs()

    result = enrich_record(minimal_record, minimal_scenario_dict, paths)

    assert result.derived is not None, "DerivedMetrics should be attached"


def test_enrich_derived_has_availability_calls(
    minimal_record: ConversationRecord,
    minimal_scenario_dict: dict,
    temp_runs_root: Path,
) -> None:
    paths = RunPaths(run_id=minimal_record.run_id, stage="baseline")
    paths.ensure_dirs()

    result = enrich_record(minimal_record, minimal_scenario_dict, paths)

    assert result.derived is not None
    assert result.derived.availability_calls == 1


def test_enrich_derived_efficiency_ratio(
    minimal_record: ConversationRecord,
    minimal_scenario_dict: dict,
    temp_runs_root: Path,
) -> None:
    """1 actual call / 1 optimal call = 1.0."""
    paths = RunPaths(run_id=minimal_record.run_id, stage="baseline")
    paths.ensure_dirs()

    result = enrich_record(minimal_record, minimal_scenario_dict, paths)

    assert result.derived is not None
    assert result.derived.efficiency_ratio == pytest.approx(1.0)


def test_enrich_overwrites_disk_record(
    minimal_record: ConversationRecord,
    minimal_scenario_dict: dict,
    temp_runs_root: Path,
) -> None:
    """enrich_record() must overwrite the on-disk JSON with derived metrics."""
    paths = RunPaths(run_id=minimal_record.run_id, stage="baseline")
    paths.ensure_dirs()

    result = enrich_record(minimal_record, minimal_scenario_dict, paths)

    record_path = paths.record_path(minimal_record.scenario_id, rep=minimal_record.run_index)
    assert record_path.exists(), f"Record file not found at {record_path}"

    on_disk = ConversationRecord.model_validate_json(record_path.read_text(encoding="utf-8"))
    assert on_disk.derived is not None, "On-disk record should have derived metrics"
    assert (
        on_disk.derived.availability_calls == result.derived.availability_calls
    ), "On-disk derived metrics should match returned record"


def test_enrich_does_not_mutate_input(
    minimal_record: ConversationRecord,
    minimal_scenario_dict: dict,
    temp_runs_root: Path,
) -> None:
    """enrich_record() returns a new record; original should be unchanged."""
    paths = RunPaths(run_id=minimal_record.run_id, stage="baseline")
    paths.ensure_dirs()

    original_derived = minimal_record.derived
    original_grounding = list(minimal_record.grounding_facts)

    enrich_record(minimal_record, minimal_scenario_dict, paths)

    assert minimal_record.derived is original_derived, "Input record must not be mutated"
    assert minimal_record.grounding_facts == original_grounding


def test_enrich_raises_on_invalid_scenario(
    minimal_record: ConversationRecord,
    temp_runs_root: Path,
) -> None:
    """enrich_record() raises ValidationError if the scenario dict is malformed.

    The caller (ScenarioRunner.run_once) wraps this in try/except to avoid
    aborting the whole run — this test documents that the function raises rather
    than silently returning a partial result.
    """
    from pydantic import ValidationError

    paths = RunPaths(run_id=minimal_record.run_id, stage="baseline")
    paths.ensure_dirs()

    bad_scenario = {"scenario_id": "bad", "tier": 1}  # missing required fields

    with pytest.raises(ValidationError):
        enrich_record(minimal_record, bad_scenario, paths)
