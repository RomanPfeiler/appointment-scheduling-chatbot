"""Unit tests for evaluation/judge.py and the update_judge_means() helper.

All tests mock the Gemini API — no real network calls are made.

Covers:
- ScenarioJudge._score_once returns a valid JudgeScoreSet on success.
- ScenarioJudge.score calls the LLM exactly JUDGE_REPS times.
- Graceful degradation: one failing rep is skipped, rest succeed.
- Full failure: all reps fail → empty list (not exception).
- Recovery quality is scored for Tier 4 but not for Tier 1.
- update_judge_means() updates an existing row in kpi_history.csv.
- update_judge_means() returns False for a missing run_id.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from evaluation.judge import (
    JUDGE_REPS,
    JUDGE_TEMPERATURE,
    JUDGE_MODEL_DEFAULT,
    JudgeError,
    ScenarioJudge,
    _CUSTOMER_EXPERIENCE_NOT_SCORED,
    _CUSTOMER_EXPERIENCE_RUBRIC,
    _NEGOTIATION_NOT_SCORED,
    _NEGOTIATION_RUBRIC,
    _PROMPT_PATH,
    _RECOVERY_RUBRIC,
    _RECOVERY_NOT_SCORED,
)
from evaluation.kpi_history import update_judge_means, kpi_history_path
from evaluation.schemas import (
    ConversationRecord,
    JudgeScoreSet,
    KPIHistoryRow,
    RunConfig,
)


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


def _minimal_config() -> RunConfig:
    return RunConfig(
        llm_provider="gemini",
        llm_model="gemini-2.5-flash",
        llm_temperature=0.7,
    )


def _minimal_record(tier: int | str = 1) -> ConversationRecord:
    return ConversationRecord(
        scenario_id=f"t{tier}_test_001",
        tier=tier,
        stage="baseline",
        persona_profile="cooperative",
        run_index=1,
        run_id="20260525_120000__baseline__abc1234",
        timestamp_start=datetime(2026, 5, 25, 12, 0, 0, tzinfo=timezone.utc),
        git_commit="abc1234",
        config=_minimal_config(),
        frozen_phrasing="next Tuesday morning",
    )


def _valid_judge_payload(recovery: int | None = None) -> dict:
    return {
        "temporal_understanding": 4,
        "negotiation_effectiveness": 3,
        "conversational_efficiency": 4,
        "recovery_quality": recovery,
        "justifications": {
            "temporal_understanding": "Agent queried correct window.",
            "negotiation_effectiveness": "Proposed one alternative.",
            "conversational_efficiency": "Asked contact medium twice.",
            "recovery_quality": None,
        },
        "overall_notes": None,
    }


def _mock_response(payload: dict) -> MagicMock:
    """Build a minimal Gemini response mock returning JSON text."""
    part = MagicMock()
    part.thought = False
    part.text = json.dumps(payload)
    candidate = MagicMock()
    candidate.content.parts = [part]
    response = MagicMock()
    response.candidates = [candidate]
    return response


def _make_judge(mock_client: MagicMock, judge_reps: int | None = None) -> ScenarioJudge:
    """Create a ScenarioJudge with the real prompt template and a mock client.

    ``judge_reps`` defaults to the module's ``JUDGE_REPS`` (the public alias for
    ``JUDGE_REPS_DEFAULT``). Pass an explicit value when a test depends on
    multi-rep behaviour (e.g. skip-failed-rep, within-record variance).
    """
    template = _PROMPT_PATH.read_text(encoding="utf-8")
    return ScenarioJudge(
        gemini_client=mock_client,
        model=JUDGE_MODEL_DEFAULT,
        temperature=JUDGE_TEMPERATURE,
        prompt_template=template,
        judge_reps=judge_reps if judge_reps is not None else JUDGE_REPS,
    )


# ---------------------------------------------------------------------------
# Test 1: _score_once returns a valid JudgeScoreSet
# ---------------------------------------------------------------------------


def test_score_once_returns_valid_score_set() -> None:
    record = _minimal_record(tier=1)
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _mock_response(
        _valid_judge_payload(recovery=None)
    )
    judge = _make_judge(mock_client)

    result = judge._score_once(record, "transcript text", "description", rep_index=1)

    assert isinstance(result, JudgeScoreSet)
    assert 1 <= result.temporal_understanding <= 5
    assert 1 <= result.negotiation_effectiveness <= 5
    assert 1 <= result.conversational_efficiency <= 5
    assert result.recovery_quality is None  # tier 1 → no recovery
    assert result.rep_index == 1
    assert result.judge_model == JUDGE_MODEL_DEFAULT


# ---------------------------------------------------------------------------
# Test 2: score() calls the LLM exactly JUDGE_REPS times
# ---------------------------------------------------------------------------


def test_score_calls_llm_three_times() -> None:
    record = _minimal_record(tier=1)
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _mock_response(
        _valid_judge_payload()
    )
    judge = _make_judge(mock_client)

    results = judge.score(record, "transcript", "description")

    assert mock_client.models.generate_content.call_count == JUDGE_REPS
    assert len(results) == JUDGE_REPS


# ---------------------------------------------------------------------------
# Test 3: score() skips a failed rep and returns the rest
# ---------------------------------------------------------------------------


def test_score_skips_failed_rep_and_continues() -> None:
    record = _minimal_record(tier=1)
    mock_client = MagicMock()
    good_response = _mock_response(_valid_judge_payload())
    # Second call raises; first and third succeed
    mock_client.models.generate_content.side_effect = [
        good_response,
        Exception("API error"),
        good_response,
    ]
    # Explicit reps=3 — this test exercises multi-rep failure tolerance,
    # which the default (reps=1) cannot demonstrate.
    judge = _make_judge(mock_client, judge_reps=3)

    results = judge.score(record, "transcript", "description")

    assert len(results) == 2
    assert all(isinstance(r, JudgeScoreSet) for r in results)
    assert mock_client.models.generate_content.call_count == 3


# ---------------------------------------------------------------------------
# Test 4: score() returns empty list when all reps fail
# ---------------------------------------------------------------------------


def test_score_returns_empty_list_when_all_fail() -> None:
    record = _minimal_record(tier=1)
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("always fails")
    judge = _make_judge(mock_client)

    results = judge.score(record, "transcript", "description")

    assert results == []
    assert mock_client.models.generate_content.call_count == JUDGE_REPS


# ---------------------------------------------------------------------------
# Test 5: Recovery Quality IS scored for Tier 4
# ---------------------------------------------------------------------------


def test_recovery_quality_scored_for_tier4() -> None:
    record = _minimal_record(tier=4)
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _mock_response(
        _valid_judge_payload(recovery=3)
    )
    judge = _make_judge(mock_client)

    result = judge._score_once(record, "transcript", "description", rep_index=1)

    # Check the score value
    assert result.recovery_quality == 3

    # Check that the Recovery rubric (not the "Not scored" note) was in the prompt
    call_args = mock_client.models.generate_content.call_args
    prompt_content = call_args[1]["contents"][0].parts[0].text
    assert "Recovery Quality" in prompt_content
    assert "Not scored for this tier" not in prompt_content


# ---------------------------------------------------------------------------
# Test 6: Recovery Quality is NOT scored for Tier 1
# ---------------------------------------------------------------------------


def test_recovery_quality_not_scored_for_tier1() -> None:
    record = _minimal_record(tier=1)
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value = _mock_response(
        _valid_judge_payload(recovery=None)
    )
    judge = _make_judge(mock_client)

    result = judge._score_once(record, "transcript", "description", rep_index=1)

    assert result.recovery_quality is None

    call_args = mock_client.models.generate_content.call_args
    prompt_content = call_args[1]["contents"][0].parts[0].text
    assert "Not scored for this tier" in prompt_content


# ---------------------------------------------------------------------------
# Tier 7 — Negotiation Effectiveness and Customer Experience are SKIPPED
# ---------------------------------------------------------------------------


def test_negotiation_and_customer_skipped_for_tier7() -> None:
    """Tier 7 prompt must contain the 'Not scored' notes for Negotiation and
    Customer Experience (refusal is the correct behaviour; the standard
    rubrics would systematically underscore the agent)."""
    record = _minimal_record(tier=7)
    mock_client = MagicMock()
    # Judge correctly emits nulls for the skipped dimensions.
    payload = _valid_judge_payload()
    payload["negotiation_effectiveness"] = None
    payload["customer_experience"] = None
    payload["justifications"]["negotiation_effectiveness"] = None
    payload["justifications"]["customer_experience"] = None
    mock_client.models.generate_content.return_value = _mock_response(payload)
    judge = _make_judge(mock_client)

    result = judge._score_once(record, "transcript", "description", rep_index=1)

    # Skipped dimensions came back as None.
    assert result.negotiation_effectiveness is None
    assert result.customer_experience is None
    # Always-scored dimensions present.
    assert result.temporal_understanding is not None
    assert result.conversational_efficiency is not None

    # Prompt contained the "Not scored" notes for both skipped dimensions.
    call_args = mock_client.models.generate_content.call_args
    prompt_content = call_args[1]["contents"][0].parts[0].text
    assert "Tier 7 is out-of-scope by design" in prompt_content
    # The full Negotiation rubric must NOT be in the prompt.
    assert "Proposed close alternatives in the same turn" not in prompt_content
    # The full Customer Experience rubric must NOT be in the prompt.
    assert "you'd happily recommend this bank" not in prompt_content


def test_negotiation_and_customer_scored_for_tiers_1_to_6() -> None:
    """Non-Tier-7 scenarios still get the full Negotiation and CX rubrics."""
    for tier in (1, 2, 3, 4, 5, 6):
        record = _minimal_record(tier=tier)
        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _mock_response(
            _valid_judge_payload()
        )
        judge = _make_judge(mock_client)
        judge._score_once(record, "transcript", "description", rep_index=1)

        call_args = mock_client.models.generate_content.call_args
        prompt_content = call_args[1]["contents"][0].parts[0].text
        assert "Proposed close alternatives in the same turn" in prompt_content, (
            f"Tier {tier}: Negotiation rubric should be present"
        )
        assert "you'd happily recommend this bank" in prompt_content, (
            f"Tier {tier}: Customer Experience rubric should be present"
        )


def test_compute_summary_excludes_none_negotiation_from_mean(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A Tier 7 score with negotiation=None must not drag the mean down."""
    from evaluation.judge import JudgeRunner
    from evaluation.schemas import JudgeScoreSet

    scores = [
        # Two Tiers 1–6 scores
        JudgeScoreSet(
            rep_index=1, judge_model="x", judge_temperature=0.3,
            temporal_understanding=5, negotiation_effectiveness=4,
            conversational_efficiency=5, customer_experience=5,
            recovery_quality=None,
        ),
        JudgeScoreSet(
            rep_index=1, judge_model="x", judge_temperature=0.3,
            temporal_understanding=5, negotiation_effectiveness=4,
            conversational_efficiency=5, customer_experience=5,
            recovery_quality=None,
        ),
        # One Tier 7 score with negotiation/customer skipped
        JudgeScoreSet(
            rep_index=1, judge_model="x", judge_temperature=0.3,
            temporal_understanding=5, negotiation_effectiveness=None,
            conversational_efficiency=5, customer_experience=None,
            recovery_quality=None,
        ),
    ]
    summary = JudgeRunner._compute_summary(
        run_id="r", stage="baseline", judge_model="x",
        judge_temperature=0.3, judge_reps=1,
        all_scores=scores, record_count=3, failed_count=0,
    )
    # Mean of negotiation should be 4.0 (from the two Tiers 1–6 scores), not (4+4+0)/3.
    assert summary.mean_negotiation == 4.0
    assert summary.mean_customer_experience == 5.0
    # Temporal (always scored) averages all three.
    assert summary.mean_temporal == 5.0


# ---------------------------------------------------------------------------
# Test 7: update_judge_means() updates an existing row
# ---------------------------------------------------------------------------


def test_update_judge_means_updates_existing_row(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    csv_file = tmp_path / "kpi_history.csv"

    # Write a pre-existing row with null judge fields
    row = KPIHistoryRow(
        run_id="run_abc123",
        stage="baseline",
        timestamp=datetime(2026, 5, 25, 12, 0, 0, tzinfo=timezone.utc),
        git_commit="abc1234",
        scenario_count=10,
        rep_count=3,
    )
    with csv_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(KPIHistoryRow.csv_header())
        writer.writerow(row.to_csv_row())

    monkeypatch.setattr(
        "evaluation.kpi_history.kpi_history_path", lambda: csv_file
    )

    result = update_judge_means(
        run_id="run_abc123",
        mean_temporal=4.1,
        mean_negotiation=3.8,
        mean_efficiency=4.5,
        mean_recovery=3.2,
    )

    assert result is True

    with csv_file.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 1
    assert rows[0]["run_id"] == "run_abc123"
    assert rows[0]["judge_mean_temporal"] == "4.1"
    assert rows[0]["judge_mean_negotiation"] == "3.8"
    assert rows[0]["judge_mean_efficiency"] == "4.5"
    assert rows[0]["judge_mean_recovery"] == "3.2"


# ---------------------------------------------------------------------------
# Test 8: update_judge_means() returns False for missing run_id
# ---------------------------------------------------------------------------


def test_update_judge_means_returns_false_for_missing_run_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    csv_file = tmp_path / "kpi_history.csv"

    # Write a row for a DIFFERENT run_id
    row = KPIHistoryRow(
        run_id="run_present",
        stage="baseline",
        timestamp=datetime(2026, 5, 25, 12, 0, 0, tzinfo=timezone.utc),
        git_commit="abc1234",
    )
    with csv_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(KPIHistoryRow.csv_header())
        writer.writerow(row.to_csv_row())

    monkeypatch.setattr(
        "evaluation.kpi_history.kpi_history_path", lambda: csv_file
    )

    result = update_judge_means(
        run_id="run_MISSING",
        mean_temporal=4.0,
        mean_negotiation=4.0,
        mean_efficiency=4.0,
        mean_recovery=None,
    )

    assert result is False

    # CSV should be unchanged
    with csv_file.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    assert len(rows) == 1
    assert rows[0]["run_id"] == "run_present"
    assert rows[0]["judge_mean_temporal"] == ""  # unchanged
