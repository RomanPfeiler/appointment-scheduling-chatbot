"""Unit tests for the within-record-across-reps std added to JudgeSummary.

`_within_record_std` slices the flat all_scores list into groups of
`judge_reps`, computes stdev within each group, then averages.
"""

from __future__ import annotations

from evaluation.judge import _within_record_std
from evaluation.schemas import JudgeScoreSet


def _score(
    rep_index: int,
    *,
    temporal: int = 3,
    negotiation: int = 3,
    efficiency: int = 3,
    customer: int | None = None,
    recovery: int | None = None,
) -> JudgeScoreSet:
    return JudgeScoreSet(
        rep_index=rep_index,
        judge_model="gemini-2.5-flash",
        judge_temperature=0.3,
        temporal_understanding=temporal,
        negotiation_effectiveness=negotiation,
        conversational_efficiency=efficiency,
        customer_experience=customer,
        recovery_quality=recovery,
    )


def test_reps_below_2_returns_none() -> None:
    scores = [_score(1, temporal=4), _score(1, temporal=5)]
    assert _within_record_std(scores, "temporal_understanding", judge_reps=1) is None


def test_all_zero_variance_groups_return_zero() -> None:
    # Two records, 3 reps each, all scoring 4 — within-record stdev = 0 for each.
    scores = [
        _score(1, temporal=4), _score(2, temporal=4), _score(3, temporal=4),
        _score(1, temporal=4), _score(2, temporal=4), _score(3, temporal=4),
    ]
    assert _within_record_std(scores, "temporal_understanding", judge_reps=3) == 0.0


def test_within_record_std_averaged_across_records() -> None:
    # Record A: reps [1, 2, 3] -> stdev = 1.0
    # Record B: reps [4, 4, 4] -> stdev = 0.0
    # Mean of per-record stdevs = 0.5
    scores = [
        _score(1, temporal=1), _score(2, temporal=2), _score(3, temporal=3),
        _score(1, temporal=4), _score(2, temporal=4), _score(3, temporal=4),
    ]
    result = _within_record_std(scores, "temporal_understanding", judge_reps=3)
    assert result is not None
    assert abs(result - 0.5) < 1e-9


def test_recovery_quality_none_values_skipped() -> None:
    # 2 reps per record. Record A has recovery=[None, None] (Tier 1, not scored)
    # Record B has recovery=[2, 4] -> stdev = sqrt(2) ≈ 1.414
    # Result must be just the Record B stdev (Record A contributes no values).
    scores = [
        _score(1, recovery=None), _score(2, recovery=None),
        _score(1, recovery=2), _score(2, recovery=4),
    ]
    result = _within_record_std(scores, "recovery_quality", judge_reps=2)
    assert result is not None
    # stdev of [2, 4] = sqrt(((2-3)^2 + (4-3)^2) / (2-1)) = sqrt(2)
    assert abs(result - 1.4142135623730951) < 1e-9


def test_empty_scores_returns_none() -> None:
    assert _within_record_std([], "temporal_understanding", judge_reps=3) is None


def test_partial_last_group_handled() -> None:
    # 5 scores with reps=3 means one full group [0:3] and a partial group [3:5]
    # of size 2 — the partial group is still valid (need >=2 values for stdev).
    scores = [
        _score(1, temporal=1), _score(2, temporal=3), _score(3, temporal=5),  # stdev = 2.0
        _score(1, temporal=2), _score(2, temporal=4),                          # stdev ≈ 1.414
    ]
    result = _within_record_std(scores, "temporal_understanding", judge_reps=3)
    assert result is not None
    # Mean of 2.0 and sqrt(2)
    import math
    expected = (2.0 + math.sqrt(2)) / 2.0
    assert abs(result - expected) < 1e-9
