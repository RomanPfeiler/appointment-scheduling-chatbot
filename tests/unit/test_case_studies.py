"""Unit tests for evaluation.case_studies pick + render logic."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from evaluation import storage
from evaluation.case_studies import (
    JUDGE_DIMENSIONS,
    pick_low_judgments,
    pick_tier_failures,
    render_run_block,
)
from evaluation.schemas import (
    ConversationRecord,
    DerivedMetrics,
    JudgeScoreSet,
    RunConfig,
    TurnRecord,
)


_TEST_CONFIG = RunConfig(
    llm_provider="gemini",
    llm_model="gemini-2.5-flash",
    llm_temperature=0.7,
)


# ---------------------------------------------------------------------------
# Test helpers — build minimal but schema-valid records
# ---------------------------------------------------------------------------


def _make_record(
    *,
    scenario_id: str,
    tier: int = 1,
    run_index: int = 1,
    termination: str = "max_turns",
    persona: str = "cooperative",
    judge: JudgeScoreSet | None = None,
    derived: DerivedMetrics | None = None,
    turns: int = 12,
    avail_calls: int = 12,
) -> ConversationRecord:
    derived_obj = derived or DerivedMetrics(
        total_turn_count=turns,
        total_mcp_calls=avail_calls,
        availability_calls=avail_calls,
        booked=(termination == "booked"),
    )
    turn_objs = [
        TurnRecord(turn_index=i + 1, timestamp=datetime(2026, 5, 25, 12, i, tzinfo=timezone.utc))
        for i in range(turns)
    ]
    return ConversationRecord(
        scenario_id=scenario_id,
        tier=tier,
        stage="baseline",
        persona_profile=persona,
        run_index=run_index,
        run_id="rid",
        timestamp_start=datetime(2026, 5, 25, tzinfo=timezone.utc),
        git_commit="a00c977a6ec1",
        config=_TEST_CONFIG,
        turns=turn_objs,
        judge_scores=[judge] if judge else [],
        derived=derived_obj,
        termination_reason=termination,
    )


def _judge(
    *,
    temporal: int = 4,
    negotiation: int | None = 4,
    efficiency: int = 4,
    customer: int | None = 4,
    recovery: int | None = None,
    justifications: dict[str, str] | None = None,
) -> JudgeScoreSet:
    return JudgeScoreSet(
        rep_index=1,
        judge_model="gemini-2.5-flash",
        judge_temperature=0.3,
        temporal_understanding=temporal,
        negotiation_effectiveness=negotiation,
        conversational_efficiency=efficiency,
        customer_experience=customer,
        recovery_quality=recovery,
        justifications=justifications or {},
    )


# ---------------------------------------------------------------------------
# pick_tier_failures
# ---------------------------------------------------------------------------


def test_pick_tier_failures_prefers_stable_fails() -> None:
    """3-rep failures rank above 1-rep failures of the same tier."""
    records = []
    # scenario A: 3 reps all failing
    for rep in (1, 2, 3):
        records.append(_make_record(scenario_id="t1_a", tier=1, run_index=rep))
    # scenario B: 1 failing rep
    records.append(_make_record(scenario_id="t1_b", tier=1, run_index=1))
    # scenario C: 2 failing reps
    records.append(_make_record(scenario_id="t1_c", tier=1, run_index=1))
    records.append(_make_record(scenario_id="t1_c", tier=1, run_index=2))

    picks = pick_tier_failures(records, tier=1, k=2)

    assert [p[0].scenario_id for p in picks] == ["t1_a", "t1_c"]
    assert [p[1] for p in picks] == [3, 2]
    # The picked rep is always the lowest run_index
    assert all(p[0].run_index == 1 for p in picks)


def test_pick_tier_failures_excludes_booked_and_refusal_accepted() -> None:
    records = [
        _make_record(scenario_id="t1_a", tier=1, termination="booked"),
        _make_record(scenario_id="t1_b", tier=1, termination="refusal_accepted"),
        _make_record(scenario_id="t1_c", tier=1, termination="max_turns"),
    ]
    picks = pick_tier_failures(records, tier=1, k=2)
    assert [p[0].scenario_id for p in picks] == ["t1_c"]


def test_pick_tier_failures_tier_7_inverts_correctness() -> None:
    """For Tier 7, refusal_accepted is the CORRECT outcome — booked is a failure."""
    records = [
        _make_record(scenario_id="t7_a", tier=7, termination="refusal_accepted"),
        _make_record(scenario_id="t7_b", tier=7, termination="booked"),
        _make_record(scenario_id="t7_c", tier=7, termination="max_turns"),
    ]
    picks = pick_tier_failures(records, tier=7, k=3)
    assert sorted(p[0].scenario_id for p in picks) == ["t7_b", "t7_c"]


def test_pick_tier_failures_other_tier_ignored() -> None:
    records = [
        _make_record(scenario_id="t1_x", tier=1, termination="max_turns"),
        _make_record(scenario_id="t2_x", tier=2, termination="max_turns"),
    ]
    picks_t1 = pick_tier_failures(records, tier=1, k=2)
    assert [p[0].scenario_id for p in picks_t1] == ["t1_x"]


def test_pick_tier_failures_returns_empty_when_no_failures() -> None:
    records = [
        _make_record(scenario_id="t1_a", tier=1, termination="booked"),
    ]
    assert pick_tier_failures(records, tier=1, k=2) == []


# ---------------------------------------------------------------------------
# pick_low_judgments
# ---------------------------------------------------------------------------


def test_pick_low_judgments_returns_lowest_first() -> None:
    records = [
        _make_record(scenario_id="a", judge=_judge(temporal=2)),
        _make_record(scenario_id="b", judge=_judge(temporal=1)),
        _make_record(scenario_id="c", judge=_judge(temporal=2)),
    ]
    picks = pick_low_judgments(records, "temporal_understanding", k=2)
    scores = [p[2] for p in picks]
    assert scores == [1, 2]


def test_pick_low_judgments_excludes_error_termination() -> None:
    """Error-path records score 1 trivially — they shouldn't crowd real findings."""
    records = [
        _make_record(scenario_id="err", judge=_judge(temporal=1), termination="error"),
        _make_record(scenario_id="real", judge=_judge(temporal=2)),
    ]
    picks = pick_low_judgments(records, "temporal_understanding", k=2)
    assert [p[0].scenario_id for p in picks] == ["real"]


def test_pick_low_judgments_distinct_scenarios() -> None:
    """Same scenario across reps appears at most once in the picks."""
    records = [
        _make_record(scenario_id="a", run_index=1, judge=_judge(temporal=1)),
        _make_record(scenario_id="a", run_index=2, judge=_judge(temporal=1)),
        _make_record(scenario_id="b", run_index=1, judge=_judge(temporal=2)),
    ]
    picks = pick_low_judgments(records, "temporal_understanding", k=2)
    sids = [p[0].scenario_id for p in picks]
    assert sids == ["a", "b"]
    assert len(set(sids)) == 2


def test_pick_low_judgments_skips_none_scores() -> None:
    """Tier-7 negotiation is None — should be skipped, not counted as 0."""
    records = [
        _make_record(
            scenario_id="t7", tier=7, termination="refusal_accepted",
            judge=_judge(negotiation=None),
        ),
        _make_record(scenario_id="t6", tier=6, judge=_judge(negotiation=2)),
    ]
    picks = pick_low_judgments(records, "negotiation_effectiveness", k=2)
    assert [p[0].scenario_id for p in picks] == ["t6"]


def test_pick_low_judgments_excludes_scores_above_2() -> None:
    records = [
        _make_record(scenario_id="a", judge=_judge(temporal=3)),
        _make_record(scenario_id="b", judge=_judge(temporal=4)),
    ]
    assert pick_low_judgments(records, "temporal_understanding", k=2) == []


def test_pick_low_judgments_ties_resolve_by_tier_then_id() -> None:
    """Same low score: lower tier first, then alphabetical scenario_id."""
    records = [
        _make_record(scenario_id="z", tier=3, judge=_judge(temporal=1)),
        _make_record(scenario_id="a", tier=5, judge=_judge(temporal=1)),
        _make_record(scenario_id="m", tier=3, judge=_judge(temporal=1)),
    ]
    picks = pick_low_judgments(records, "temporal_understanding", k=3)
    assert [p[0].scenario_id for p in picks] == ["m", "z", "a"]


def test_pick_low_judgments_works_for_all_five_dimensions() -> None:
    """Sanity check that the dim attribute names match JudgeScoreSet fields."""
    records = [
        _make_record(
            scenario_id="a",
            tier=3,  # tier 3 allows recovery to be scored
            judge=_judge(temporal=1, negotiation=2, efficiency=1, customer=2, recovery=1),
        )
    ]
    for dim_attr, _label in JUDGE_DIMENSIONS:
        picks = pick_low_judgments(records, dim_attr, k=1)
        assert len(picks) == 1, f"no pick for dimension {dim_attr}"


# ---------------------------------------------------------------------------
# render_run_block (integration — uses tmp filesystem)
# ---------------------------------------------------------------------------


@pytest.fixture
def temp_runs_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    runs = tmp_path / "runs"
    runs.mkdir()
    monkeypatch.setattr(storage, "runs_root", lambda: runs)
    return runs


def _write_records(runs_root: Path, run_id: str, stage: str, records: list[ConversationRecord]) -> None:
    record_dir = runs_root / stage / run_id / "records"
    record_dir.mkdir(parents=True)
    for r in records:
        path = record_dir / f"{r.scenario_id}__rep{r.run_index}.json"
        path.write_text(r.model_dump_json(), encoding="utf-8")


def test_render_run_block_has_header_and_transcript_links(temp_runs_root: Path) -> None:
    run_id = "20260525_130220__baseline__a00c977__representative"
    stage = "baseline"
    records = [
        _make_record(
            scenario_id="t1_a", tier=1, run_index=rep,
            judge=_judge(temporal=2, justifications={"temporal_understanding": "agent confused dates"}),
        )
        for rep in (1, 2, 3)
    ]
    _write_records(temp_runs_root, run_id, stage, records)

    block = render_run_block(run_id=run_id, stage=stage, section_date="2026-05-25")

    # Header
    assert block.startswith("### 2026-05-25 — baseline — `a00c977`")
    # Transcript link uses ../../evaluation/runs/<stage>/<run_id>/transcripts/
    assert (
        "../../evaluation/runs/baseline/"
        "20260525_130220__baseline__a00c977__representative/"
        "transcripts/t1_a__rep1.md"
    ) in block
    # Failure section with stable-fail marker
    assert "Failed cases" in block
    assert "STABLE-FAIL 3/3" in block
    # Low-judgment section with judge rationale embedded
    assert "Low-judgment exemplars" in block
    assert "agent confused dates" in block


def test_render_run_block_missing_dir_raises(temp_runs_root: Path) -> None:
    with pytest.raises(FileNotFoundError):
        render_run_block(run_id="no_such_run", stage="baseline")


def test_render_run_block_no_failures_emits_dim_placeholder(temp_runs_root: Path) -> None:
    """When a dim has zero qualifying records, output a 'no records' line."""
    run_id = "20260525_000000__baseline__a00c977__test"
    stage = "baseline"
    # All booked + high scores → no failures, no low-judgments
    records = [
        _make_record(
            scenario_id="t1_a", tier=1, termination="booked",
            judge=_judge(temporal=5, negotiation=5, efficiency=5, customer=5),
        )
    ]
    _write_records(temp_runs_root, run_id, stage, records)
    block = render_run_block(run_id=run_id, stage=stage, section_date="2026-05-25")
    assert "no records with score" in block
