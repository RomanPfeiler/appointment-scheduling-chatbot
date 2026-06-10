"""
paired_analysis.py — Paired statistics for stage-vs-stage comparison.

Implements the EVALUATION_FRAMEWORK §10 statistics:
- Wilcoxon signed-rank (continuous KPIs)
- McNemar's exact binomial (binary outcomes: booked, faithful)
- Bootstrap 95% CIs on headline KPIs (mean / median / proportion)

Stdlib-only (no scipy). Pairs records by (scenario_id, run_index); excludes
pairs where either side has termination_reason == "error" or derived == None.

Usage:
    python -m evaluation.paired_analysis \
        --baseline-run 20260525_130220__baseline__a00c977__representative \
        --candidate-run 20260531_163412__nlp_arm1__a00c977__representative \
        --output evaluation/runs/_logs/nlp_arm1_vs_baseline_paired.json
"""

from __future__ import annotations

import argparse
import json
import math
import random
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, median, stdev
from typing import Any

EVAL_ROOT = Path(__file__).resolve().parent
RUNS_ROOT = EVAL_ROOT / "runs"


# ──────────────────────────────────────────────────────────────────────────
# Record loading
# ──────────────────────────────────────────────────────────────────────────

def _run_dir(run_id: str) -> Path:
    """Locate the run directory by scanning stage subfolders."""
    for stage_dir in RUNS_ROOT.iterdir():
        if not stage_dir.is_dir():
            continue
        candidate = stage_dir / run_id
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError(f"Run id {run_id!r} not found under {RUNS_ROOT}")


def load_records(run_id: str) -> dict[tuple[str, int], dict[str, Any]]:
    """Load all records for a run, keyed by (scenario_id, run_index)."""
    run_dir = _run_dir(run_id)
    records_dir = run_dir / "records"
    out: dict[tuple[str, int], dict[str, Any]] = {}
    for f in sorted(records_dir.glob("*.json")):
        with f.open(encoding="utf-8") as fh:
            rec = json.load(fh)
        key = (rec["scenario_id"], rec["run_index"])
        out[key] = rec
    return out


def is_valid_record(rec: dict[str, Any]) -> bool:
    """A record contributes to paired stats iff it terminated non-error and has derived."""
    return (
        rec.get("termination_reason") != "error"
        and isinstance(rec.get("derived"), dict)
    )


# ──────────────────────────────────────────────────────────────────────────
# Stdlib paired statistics
# ──────────────────────────────────────────────────────────────────────────

def _phi(z: float) -> float:
    """Standard-normal CDF via erf (stdlib)."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def wilcoxon_signed_rank(diffs: list[float]) -> dict[str, Any]:
    """Two-sided Wilcoxon signed-rank with normal approximation + tie correction.

    Returns p-value, W+, n_nonzero, z. Drops zero differences (Wilcoxon convention).
    Uses average ranks for ties.
    """
    nonzero = [d for d in diffs if d != 0.0]
    n = len(nonzero)
    if n == 0:
        return {"n": 0, "w_plus": 0.0, "z": 0.0, "p_value": 1.0}

    abs_diffs = sorted(((abs(d), 1 if d > 0 else -1) for d in nonzero), key=lambda x: x[0])

    # Average-rank assignment (1-indexed) with tie correction sum.
    ranks: list[float] = [0.0] * n
    i = 0
    tie_term = 0.0  # sum of (t**3 - t) over tie groups
    while i < n:
        j = i
        while j + 1 < n and abs_diffs[j + 1][0] == abs_diffs[i][0]:
            j += 1
        avg_rank = (i + 1 + j + 1) / 2.0
        for k in range(i, j + 1):
            ranks[k] = avg_rank
        t = j - i + 1
        if t > 1:
            tie_term += t**3 - t
        i = j + 1

    w_plus = sum(r for r, (_, s) in zip(ranks, abs_diffs) if s > 0)
    w_minus = sum(r for r, (_, s) in zip(ranks, abs_diffs) if s < 0)
    w = min(w_plus, w_minus)

    mu = n * (n + 1) / 4.0
    sigma2 = n * (n + 1) * (2 * n + 1) / 24.0 - tie_term / 48.0
    sigma = math.sqrt(sigma2) if sigma2 > 0 else 0.0
    if sigma == 0.0:
        return {"n": n, "w_plus": w_plus, "w_minus": w_minus, "z": 0.0, "p_value": 1.0}

    # Continuity correction
    z = (w - mu + 0.5) / sigma if w < mu else (w - mu - 0.5) / sigma
    p = 2.0 * min(_phi(z), 1.0 - _phi(z))
    return {
        "n": n,
        "w_plus": w_plus,
        "w_minus": w_minus,
        "z": z,
        "p_value": p,
    }


def mcnemar_exact(b: int, c: int) -> dict[str, Any]:
    """McNemar's exact two-sided test on discordant pairs.

    b = pairs where baseline=1, candidate=0 ("baseline-only success")
    c = pairs where baseline=0, candidate=1 ("candidate-only success")
    Concordant pairs do not enter the test.

    Returns the two-sided p-value from a Binomial(b+c, 0.5) null.
    """
    n = b + c
    if n == 0:
        return {"b_baseline_only": 0, "c_candidate_only": 0, "p_value": 1.0}
    k = min(b, c)
    # Two-sided exact: 2 * sum_{i=0..k} C(n,i) * 0.5**n, capped at 1.
    cum = sum(math.comb(n, i) for i in range(k + 1)) * (0.5 ** n)
    p = min(1.0, 2.0 * cum)
    return {
        "b_baseline_only": b,
        "c_candidate_only": c,
        "n_discordant": n,
        "p_value": p,
    }


def bootstrap_ci(
    values: list[float],
    statistic: str,
    n_boot: int = 5000,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Percentile bootstrap 95% CI on mean, median, or proportion. Returns (point, lo, hi)."""
    if not values:
        return (float("nan"), float("nan"), float("nan"))
    rng = random.Random(seed)
    n = len(values)

    def _stat(xs: list[float]) -> float:
        if statistic == "mean":
            return mean(xs)
        if statistic == "median":
            return median(xs)
        if statistic == "proportion":
            return sum(xs) / len(xs)
        raise ValueError(statistic)

    point = _stat(values)
    samples: list[float] = []
    for _ in range(n_boot):
        resample = [values[rng.randrange(n)] for _ in range(n)]
        samples.append(_stat(resample))
    samples.sort()
    lo = samples[int(0.025 * n_boot)]
    hi = samples[int(0.975 * n_boot)]
    return (point, lo, hi)


def paired_diff_ci(
    baseline_vals: list[float],
    candidate_vals: list[float],
    statistic: str,
    n_boot: int = 5000,
    seed: int = 42,
) -> tuple[float, float, float]:
    """Bootstrap 95% CI on the paired difference (candidate − baseline)."""
    assert len(baseline_vals) == len(candidate_vals)
    rng = random.Random(seed)
    n = len(baseline_vals)
    if n == 0:
        return (float("nan"), float("nan"), float("nan"))

    def _stat(b: list[float], c: list[float]) -> float:
        if statistic == "mean":
            return mean(c) - mean(b)
        if statistic == "median":
            return median(c) - median(b)
        if statistic == "proportion":
            return sum(c) / len(c) - sum(b) / len(b)
        raise ValueError(statistic)

    point = _stat(baseline_vals, candidate_vals)
    samples: list[float] = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        bs = [baseline_vals[i] for i in idx]
        cs = [candidate_vals[i] for i in idx]
        samples.append(_stat(bs, cs))
    samples.sort()
    lo = samples[int(0.025 * n_boot)]
    hi = samples[int(0.975 * n_boot)]
    return (point, lo, hi)


# ──────────────────────────────────────────────────────────────────────────
# Metric extraction
# ──────────────────────────────────────────────────────────────────────────

def _ladder_fire_turns(rec: dict[str, Any]) -> int:
    """Ladder-fire-rate **proxy**: count of turns where ``check_availability``
    was recorded ≥2 times (i.e. the executor's widening ladder ran after an
    empty first call).

    Derived from raw ``turns[].tool_calls`` so it is computable for BOTH the
    expansion-only anchor (whose ``derived`` predates the ladder fields) and any
    new run — the apples-to-apples requirement for the paired comparison.

    ⚠ This is a proxy, biased **low**: a ladder step served from the per-session
    availability cache issues no MCP call, so it leaves no ``ToolCallRecord``
    (``orchestrator/nodes/execute.py`` short-circuits cache-covered windows). It
    also cannot distinguish an executor ladder step from the agent independently
    re-calling ``check_availability`` within the same turn. The cache confound is
    symmetric across the two expansion-on arms being compared, so the *directional*
    difference (does Arm 3 make the ladder fire less?) stays informative even
    though absolute counts are understated. Runs that carry the clean
    ``TurnRecord.ladder_steps`` signal (post 2026-06-08) can be scored exactly.
    """
    turns = rec.get("turns") or []
    count = 0
    for turn in turns:
        avail = sum(
            1 for tc in (turn.get("tool_calls") or [])
            if tc.get("tool_name") == "check_availability"
        )
        if avail >= 2:
            count += 1
    return count


_CONTINUOUS_METRICS = {
    "turn_count": lambda r: r["derived"]["total_turn_count"],
    "efficiency_ratio": lambda r: r["derived"].get("efficiency_ratio"),
    "simulated_latency_ms": lambda r: r["derived"]["total_simulated_latency_ms"],
    "parse_accuracy": lambda r: r["derived"].get("parse_accuracy_score"),
    "dead_end_turns": lambda r: r["derived"]["dead_end_turn_count"],
    "unsupported_facts": lambda r: r["derived"]["unsupported_facts_count"],
    # check_availability call volume — the cost/efficiency side of the
    # expansion comparison (more ladder firing → more availability calls).
    "availability_calls": lambda r: r["derived"]["availability_calls"],
    # Ladder-fire-rate proxy (see _ladder_fire_turns docstring for the caveat).
    "ladder_fire_turns": _ladder_fire_turns,
}

_BINARY_METRICS = {
    "booked": lambda r: 1 if r["derived"]["booked"] else 0,
    "faithful": lambda r: 1 if r["derived"]["faithful"] else 0,
    "refusal_accepted": lambda r: 1 if r.get("termination_reason") == "refusal_accepted" else 0,
}


_JUDGE_DIMS = [
    "temporal_understanding",
    "negotiation_effectiveness",
    "conversational_efficiency",
    "customer_experience",
    "recovery_quality",
]


def _judge_score(rec: dict[str, Any], dim: str) -> float | None:
    """Mean of judge_scores[*][dim] for this record (None if all None / no scores)."""
    js = rec.get("judge_scores") or []
    vals = [s.get(dim) for s in js if isinstance(s.get(dim), int)]
    if not vals:
        return None
    return mean(vals)


# ──────────────────────────────────────────────────────────────────────────
# Top-level comparison
# ──────────────────────────────────────────────────────────────────────────

def _split_by_tier(
    pairs: list[tuple[dict[str, Any], dict[str, Any]]],
) -> dict[int, list[tuple[dict[str, Any], dict[str, Any]]]]:
    by_tier: dict[int, list[tuple[dict[str, Any], dict[str, Any]]]] = defaultdict(list)
    for b, c in pairs:
        tier = b.get("tier")
        if isinstance(tier, int):
            by_tier[tier].append((b, c))
    return dict(sorted(by_tier.items()))


def _continuous_block(
    pairs: list[tuple[dict[str, Any], dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for name, extractor in _CONTINUOUS_METRICS.items():
        b_vals: list[float] = []
        c_vals: list[float] = []
        for b, c in pairs:
            bv = extractor(b)
            cv = extractor(c)
            if bv is None or cv is None:
                continue
            b_vals.append(float(bv))
            c_vals.append(float(cv))
        if not b_vals:
            out[name] = {"n_pairs": 0}
            continue
        diffs = [cv - bv for bv, cv in zip(b_vals, c_vals)]
        wil = wilcoxon_signed_rank(diffs)
        mean_b, mean_b_lo, mean_b_hi = bootstrap_ci(b_vals, "mean")
        mean_c, mean_c_lo, mean_c_hi = bootstrap_ci(c_vals, "mean")
        med_b, med_b_lo, med_b_hi = bootstrap_ci(b_vals, "median")
        med_c, med_c_lo, med_c_hi = bootstrap_ci(c_vals, "median")
        diff_mean, diff_lo, diff_hi = paired_diff_ci(b_vals, c_vals, "mean")
        out[name] = {
            "n_pairs": len(b_vals),
            "baseline_mean": mean_b,
            "baseline_mean_ci": [mean_b_lo, mean_b_hi],
            "candidate_mean": mean_c,
            "candidate_mean_ci": [mean_c_lo, mean_c_hi],
            "baseline_median": med_b,
            "baseline_median_ci": [med_b_lo, med_b_hi],
            "candidate_median": med_c,
            "candidate_median_ci": [med_c_lo, med_c_hi],
            "delta_mean": diff_mean,
            "delta_mean_ci": [diff_lo, diff_hi],
            "wilcoxon": wil,
        }
    return out


def _binary_block(
    pairs: list[tuple[dict[str, Any], dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for name, extractor in _BINARY_METRICS.items():
        b_vals: list[float] = []
        c_vals: list[float] = []
        b_b = 0  # baseline=1, candidate=0
        c_c = 0  # baseline=0, candidate=1
        for b, c in pairs:
            bv = extractor(b)
            cv = extractor(c)
            b_vals.append(bv)
            c_vals.append(cv)
            if bv == 1 and cv == 0:
                b_b += 1
            elif bv == 0 and cv == 1:
                c_c += 1
        if not b_vals:
            out[name] = {"n_pairs": 0}
            continue
        mn = mcnemar_exact(b_b, c_c)
        prop_b, prop_b_lo, prop_b_hi = bootstrap_ci(b_vals, "proportion")
        prop_c, prop_c_lo, prop_c_hi = bootstrap_ci(c_vals, "proportion")
        diff, diff_lo, diff_hi = paired_diff_ci(b_vals, c_vals, "proportion")
        out[name] = {
            "n_pairs": len(b_vals),
            "baseline_rate": prop_b,
            "baseline_rate_ci": [prop_b_lo, prop_b_hi],
            "candidate_rate": prop_c,
            "candidate_rate_ci": [prop_c_lo, prop_c_hi],
            "delta_rate": diff,
            "delta_rate_ci": [diff_lo, diff_hi],
            "mcnemar": mn,
        }
    return out


def _judge_block(
    pairs: list[tuple[dict[str, Any], dict[str, Any]]],
) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for dim in _JUDGE_DIMS:
        b_vals: list[float] = []
        c_vals: list[float] = []
        for b, c in pairs:
            bv = _judge_score(b, dim)
            cv = _judge_score(c, dim)
            if bv is None or cv is None:
                continue
            b_vals.append(bv)
            c_vals.append(cv)
        if not b_vals:
            out[dim] = {"n_pairs": 0}
            continue
        diffs = [cv - bv for bv, cv in zip(b_vals, c_vals)]
        wil = wilcoxon_signed_rank(diffs)
        mean_b, mean_b_lo, mean_b_hi = bootstrap_ci(b_vals, "mean")
        mean_c, mean_c_lo, mean_c_hi = bootstrap_ci(c_vals, "mean")
        diff_mean, diff_lo, diff_hi = paired_diff_ci(b_vals, c_vals, "mean")
        out[dim] = {
            "n_pairs": len(b_vals),
            "baseline_mean": mean_b,
            "baseline_mean_ci": [mean_b_lo, mean_b_hi],
            "candidate_mean": mean_c,
            "candidate_mean_ci": [mean_c_lo, mean_c_hi],
            "delta_mean": diff_mean,
            "delta_mean_ci": [diff_lo, diff_hi],
            "wilcoxon": wil,
        }
    return out


def compare(
    baseline_run: str,
    candidate_run: str,
) -> dict[str, Any]:
    """Run the full paired comparison."""
    base = load_records(baseline_run)
    cand = load_records(candidate_run)

    common_keys = sorted(set(base.keys()) & set(cand.keys()))

    # Pairing diagnostics
    baseline_only = sorted(set(base.keys()) - set(cand.keys()))
    candidate_only = sorted(set(cand.keys()) - set(base.keys()))

    excluded_pairs: list[dict[str, Any]] = []
    valid_pairs: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for key in common_keys:
        b = base[key]
        c = cand[key]
        if not is_valid_record(b) or not is_valid_record(c):
            excluded_pairs.append(
                {
                    "scenario_id": key[0],
                    "rep": key[1],
                    "baseline_termination": b.get("termination_reason"),
                    "candidate_termination": c.get("termination_reason"),
                    "baseline_has_derived": isinstance(b.get("derived"), dict),
                    "candidate_has_derived": isinstance(c.get("derived"), dict),
                }
            )
            continue
        valid_pairs.append((b, c))

    by_tier = _split_by_tier(valid_pairs)

    report: dict[str, Any] = {
        "baseline_run": baseline_run,
        "candidate_run": candidate_run,
        "pairing": {
            "baseline_records": len(base),
            "candidate_records": len(cand),
            "common_keys": len(common_keys),
            "valid_pairs": len(valid_pairs),
            "excluded_pair_count": len(excluded_pairs),
            "baseline_only_keys": len(baseline_only),
            "candidate_only_keys": len(candidate_only),
        },
        "excluded_pairs": excluded_pairs,
        "overall": {
            "continuous": _continuous_block(valid_pairs),
            "binary": _binary_block(valid_pairs),
            "judge": _judge_block(valid_pairs),
        },
        "per_tier": {
            f"tier_{t}": {
                "n_pairs": len(tps),
                "continuous": _continuous_block(tps),
                "binary": _binary_block(tps),
                "judge": _judge_block(tps),
            }
            for t, tps in by_tier.items()
        },
    }
    return report


# ──────────────────────────────────────────────────────────────────────────
# Markdown rendering
# ──────────────────────────────────────────────────────────────────────────

def _fmt(x: float | None, nd: int = 2) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    return f"{x:.{nd}f}"


def _fmt_pct(x: float, nd: int = 1) -> str:
    if math.isnan(x):
        return "—"
    return f"{x*100:.{nd}f}%"


def _stars(p: float) -> str:
    if math.isnan(p):
        return ""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return ""


def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    pa = report["pairing"]
    lines.append(f"# Paired comparison — `{report['candidate_run']}` vs `{report['baseline_run']}`")
    lines.append("")
    lines.append(
        f"**Pairing:** {pa['valid_pairs']} valid pairs out of {pa['common_keys']} matched scenario-runs "
        f"(excluded {pa['excluded_pair_count']} pairs where either side had `termination=error` or missing derived metrics). "
        f"Baseline-only keys: {pa['baseline_only_keys']}, candidate-only: {pa['candidate_only_keys']}."
    )
    lines.append("")

    def _section(label: str, block: dict[str, Any]) -> None:
        lines.append(f"## {label}")
        lines.append("")
        lines.append("### Continuous KPIs (Wilcoxon signed-rank, mean CI from paired bootstrap)")
        lines.append("")
        lines.append(
            "| Metric | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |"
        )
        lines.append("|---|---:|---:|---:|---:|---:|")
        for name, blk in block["continuous"].items():
            if blk.get("n_pairs", 0) == 0:
                lines.append(f"| {name} | 0 | — | — | — | — |")
                continue
            bm = blk["baseline_mean"]
            bm_lo, bm_hi = blk["baseline_mean_ci"]
            cm = blk["candidate_mean"]
            cm_lo, cm_hi = blk["candidate_mean_ci"]
            dm = blk["delta_mean"]
            dm_lo, dm_hi = blk["delta_mean_ci"]
            p = blk["wilcoxon"]["p_value"]
            lines.append(
                f"| {name} | {blk['n_pairs']} | "
                f"{_fmt(bm)} [{_fmt(bm_lo)}, {_fmt(bm_hi)}] | "
                f"{_fmt(cm)} [{_fmt(cm_lo)}, {_fmt(cm_hi)}] | "
                f"{_fmt(dm)} [{_fmt(dm_lo)}, {_fmt(dm_hi)}] | "
                f"{_fmt(p, 4)}{_stars(p)} |"
            )
        lines.append("")
        lines.append("### Binary KPIs (McNemar exact, proportion CIs from paired bootstrap)")
        lines.append("")
        lines.append(
            "| Metric | n | baseline rate [95% CI] | candidate rate [95% CI] | Δrate [95% CI] | b/c discordant | p (McNemar) |"
        )
        lines.append("|---|---:|---:|---:|---:|---:|---:|")
        for name, blk in block["binary"].items():
            if blk.get("n_pairs", 0) == 0:
                lines.append(f"| {name} | 0 | — | — | — | — | — |")
                continue
            br = blk["baseline_rate"]
            br_lo, br_hi = blk["baseline_rate_ci"]
            cr = blk["candidate_rate"]
            cr_lo, cr_hi = blk["candidate_rate_ci"]
            dr = blk["delta_rate"]
            dr_lo, dr_hi = blk["delta_rate_ci"]
            mn = blk["mcnemar"]
            p = mn["p_value"]
            lines.append(
                f"| {name} | {blk['n_pairs']} | "
                f"{_fmt_pct(br)} [{_fmt_pct(br_lo)}, {_fmt_pct(br_hi)}] | "
                f"{_fmt_pct(cr)} [{_fmt_pct(cr_lo)}, {_fmt_pct(cr_hi)}] | "
                f"{_fmt_pct(dr)} [{_fmt_pct(dr_lo)}, {_fmt_pct(dr_hi)}] | "
                f"{mn['b_baseline_only']}/{mn['c_candidate_only']} | "
                f"{_fmt(p, 4)}{_stars(p)} |"
            )
        lines.append("")
        lines.append("### Judge dimensions (Wilcoxon signed-rank on per-record means)")
        lines.append("")
        lines.append(
            "| Dim | n | baseline mean [95% CI] | candidate mean [95% CI] | Δmean [95% CI] | p (Wilcoxon) |"
        )
        lines.append("|---|---:|---:|---:|---:|---:|")
        for name, blk in block["judge"].items():
            if blk.get("n_pairs", 0) == 0:
                lines.append(f"| {name} | 0 | — | — | — | — |")
                continue
            bm = blk["baseline_mean"]
            bm_lo, bm_hi = blk["baseline_mean_ci"]
            cm = blk["candidate_mean"]
            cm_lo, cm_hi = blk["candidate_mean_ci"]
            dm = blk["delta_mean"]
            dm_lo, dm_hi = blk["delta_mean_ci"]
            p = blk["wilcoxon"]["p_value"]
            lines.append(
                f"| {name} | {blk['n_pairs']} | "
                f"{_fmt(bm)} [{_fmt(bm_lo)}, {_fmt(bm_hi)}] | "
                f"{_fmt(cm)} [{_fmt(cm_lo)}, {_fmt(cm_hi)}] | "
                f"{_fmt(dm)} [{_fmt(dm_lo)}, {_fmt(dm_hi)}] | "
                f"{_fmt(p, 4)}{_stars(p)} |"
            )
        lines.append("")

    _section("Overall (all tiers)", report["overall"])
    for tname, tblock in report["per_tier"].items():
        n = tblock["n_pairs"]
        _section(f"Tier {tname.split('_')[1]} (n={n})", tblock)
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Paired statistics for two evaluation runs (EVALUATION_FRAMEWORK §10)."
    )
    parser.add_argument("--baseline-run", required=True, help="Baseline run_id (anchor).")
    parser.add_argument("--candidate-run", required=True, help="Candidate run_id (e.g. nlp_arm1).")
    parser.add_argument(
        "--output-json",
        type=Path,
        default=None,
        help="Path to write the full JSON report. If omitted, prints to stdout.",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=None,
        help="Path to write a markdown rendering of the report.",
    )
    args = parser.parse_args(argv)

    report = compare(args.baseline_run, args.candidate_run)

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        with args.output_json.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Wrote JSON report → {args.output_json}", file=sys.stderr)
    else:
        json.dump(report, sys.stdout, indent=2)

    if args.output_md:
        args.output_md.parent.mkdir(parents=True, exist_ok=True)
        with args.output_md.open("w", encoding="utf-8") as f:
            f.write(render_markdown(report))
        print(f"Wrote Markdown report → {args.output_md}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
