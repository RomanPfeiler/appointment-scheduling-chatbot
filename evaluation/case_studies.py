"""case_studies.py — Per-run case-study block generator.

Pulls representative failed and low-judgment scenarios from a completed
evaluation run and emits a markdown block ready to paste (or ``--prepend``)
into ``project_presentation/progress/case_studies.md``.

Two deterministic pick functions:

- :func:`pick_tier_failures` — top ``k`` scenarios per tier with
  ``termination_reason`` outside ``{booked, refusal_accepted}``, preferring
  stable-fail scenarios (same scenario_id failing across multiple reps).
  Tier 7 inverts the rule: anything ≠ ``refusal_accepted`` counts as failure.

- :func:`pick_low_judgments` — up to ``k`` records per judge dimension whose
  score is ≤ 2, distinct ``scenario_id``, ascending score then tier then id.
  Records with ``termination_reason == "error"`` are excluded (they score 1
  trivially because the agent never spoke).

Usage::

    python -m evaluation.case_studies render \\
        --run-id 20260525_130220__baseline__a00c977__representative \\
        --stage baseline \\
        [--out project_presentation/progress/case_studies.md --prepend] \\
        [--date 2026-05-25]
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date as date_cls
from pathlib import Path

from evaluation.schemas import ConversationRecord, JudgeScoreSet
from evaluation.storage import RunPaths, load_record, now_utc

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

JUDGE_DIMENSIONS: list[tuple[str, str]] = [
    ("temporal_understanding", "Temporal"),
    ("negotiation_effectiveness", "Negotiation"),
    ("conversational_efficiency", "Efficiency"),
    ("customer_experience", "Customer Experience"),
    ("recovery_quality", "Recovery"),
]

# A "failure" for tiers 1–6 means the conversation didn't book and wasn't a
# correct refusal. For tier 7 the correct outcome is a refusal, so anything
# else (including a stray booking) is a failure.
_NON_FAILURE_T1_T6: frozenset[str] = frozenset({"booked", "refusal_accepted"})
_NON_FAILURE_T7: frozenset[str] = frozenset({"refusal_accepted"})


# ---------------------------------------------------------------------------
# Pick functions
# ---------------------------------------------------------------------------


def _is_failure(record: ConversationRecord) -> bool:
    """Tier-aware failure predicate.

    Tier 7's correct outcome is a polite refusal (``refusal_accepted``), so
    a booking or max_turns there IS a failure. For all other tiers the
    correct outcomes are ``booked`` or ``refusal_accepted``.
    """
    tier = record.tier
    try:
        tier_int = int(tier)
    except (TypeError, ValueError):
        tier_int = -1
    non_failure = _NON_FAILURE_T7 if tier_int == 7 else _NON_FAILURE_T1_T6
    return record.termination_reason not in non_failure


def pick_tier_failures(
    records: list[ConversationRecord],
    tier: int,
    k: int = 2,
) -> list[tuple[ConversationRecord, int]]:
    """Return up to ``k`` ``(record, failed_reps_count)`` tuples for ``tier``.

    Ranking: stable-fail first (most reps of the same scenario failing),
    then ``scenario_id`` ascending for determinism. Each picked scenario
    contributes its first failed rep (lowest ``run_index``).
    """
    tier_records = [r for r in records if _matches_tier(r, tier)]
    failed = [r for r in tier_records if _is_failure(r)]

    by_scenario: dict[str, list[ConversationRecord]] = defaultdict(list)
    for r in failed:
        by_scenario[r.scenario_id].append(r)

    ranked = sorted(
        by_scenario.items(),
        key=lambda kv: (-len(kv[1]), kv[0]),
    )

    picks: list[tuple[ConversationRecord, int]] = []
    for scenario_id, reps in ranked[:k]:
        reps_sorted = sorted(reps, key=lambda r: r.run_index)
        picks.append((reps_sorted[0], len(reps)))
    return picks


def pick_low_judgments(
    records: list[ConversationRecord],
    dimension: str,
    k: int = 2,
) -> list[tuple[ConversationRecord, JudgeScoreSet, int]]:
    """Return up to ``k`` ``(record, score_set, score)`` tuples scored ≤ 2.

    Excludes ``termination_reason == "error"`` records (they score 1 trivially
    because the agent never produced any conversation content). Picks
    distinct ``scenario_id``, breaking ties by ascending score, then tier,
    then scenario_id.
    """
    candidates: list[tuple[int, ConversationRecord, JudgeScoreSet]] = []
    for r in records:
        if r.termination_reason == "error":
            continue
        for js in r.judge_scores:
            value = getattr(js, dimension)
            if value is not None and value <= 2:
                candidates.append((int(value), r, js))

    candidates.sort(
        key=lambda triple: (triple[0], _tier_sort_key(triple[1].tier), triple[1].scenario_id),
    )

    picks: list[tuple[ConversationRecord, JudgeScoreSet, int]] = []
    seen_scenarios: set[str] = set()
    for score, record, score_set in candidates:
        if record.scenario_id in seen_scenarios:
            continue
        seen_scenarios.add(record.scenario_id)
        picks.append((record, score_set, score))
        if len(picks) >= k:
            break
    return picks


def _matches_tier(record: ConversationRecord, tier: int) -> bool:
    try:
        return int(record.tier) == tier
    except (TypeError, ValueError):
        return False


def _tier_sort_key(tier: int | str) -> int:
    try:
        return int(tier)
    except (TypeError, ValueError):
        return 999


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _RenderContext:
    run_id: str
    stage: str
    section_date: str
    git_short: str


def _judge_summary_str(js: JudgeScoreSet | None) -> str:
    """Render T/N/E/CX/R as ``a / b / c / d / e`` with ``—`` for ``None``."""
    if js is None:
        return "— / — / — / — / —"

    def fmt(v: int | None) -> str:
        return "—" if v is None else str(v)

    return (
        f"{fmt(js.temporal_understanding)} / "
        f"{fmt(js.negotiation_effectiveness)} / "
        f"{fmt(js.conversational_efficiency)} / "
        f"{fmt(js.customer_experience)} / "
        f"{fmt(js.recovery_quality)}"
    )


def _first_judge_score(record: ConversationRecord) -> JudgeScoreSet | None:
    return record.judge_scores[0] if record.judge_scores else None


def _transcript_relpath(ctx: _RenderContext, scenario_id: str, rep: int) -> str:
    """Build the relative path from ``project_presentation/progress/`` to a
    transcript file. The case-studies file lives at
    ``project_presentation/progress/case_studies.md``; transcripts live at
    ``evaluation/runs/<stage>/<run_id>/transcripts/<sid>__rep<k>.md`` —
    relative path requires ``../../``.
    """
    return (
        f"../../evaluation/runs/{ctx.stage}/{ctx.run_id}/transcripts/"
        f"{scenario_id}__rep{rep}.md"
    )


def _fact_line(record: ConversationRecord, n_failed_reps: int) -> str:
    derived = record.derived
    avail_calls = derived.availability_calls if derived else "?"
    turns_n = derived.total_turn_count if derived else len(record.turns)
    stable_mark = ""
    if n_failed_reps >= 2:
        stable_mark = f" · STABLE-FAIL {n_failed_reps}/3"
    return (
        f"{record.termination_reason} · {record.persona_profile or '?'} · "
        f"{turns_n} turns · {avail_calls} avail-calls{stable_mark}"
    )


def _bullet_for_failure(
    ctx: _RenderContext,
    record: ConversationRecord,
    n_failed_reps: int,
) -> str:
    link = _transcript_relpath(ctx, record.scenario_id, record.run_index)
    facts = _fact_line(record, n_failed_reps)
    judge_line = _judge_summary_str(_first_judge_score(record))
    return (
        f"- **T{record.tier} · [`{record.scenario_id}__rep{record.run_index}`]({link})** — {facts}\n"
        f"  Pattern: _annotate after reading transcript_\n"
        f"  Judge T/N/E/CX/R: {judge_line}"
    )


def _bullet_for_low_judgment(
    ctx: _RenderContext,
    record: ConversationRecord,
    score_set: JudgeScoreSet,
    score: int,
    dim_attr: str,
    dim_label: str,
) -> str:
    link = _transcript_relpath(ctx, record.scenario_id, record.run_index)
    rationale = (score_set.justifications or {}).get(dim_attr, "").strip()
    if not rationale:
        rationale = "(no justification recorded)"
    facts = _fact_line(record, 0)
    return (
        f"- **{dim_label} {score}/5 · [`{record.scenario_id}__rep{record.run_index}`]({link})** — T{record.tier} · {facts}\n"
        f"  Judge: _{rationale}_"
    )


def render_run_block(
    run_id: str,
    stage: str,
    *,
    section_date: str | None = None,
    note: str | None = None,
    failures_per_tier: int = 2,
    low_judgments_per_dim: int = 2,
) -> str:
    """Produce the markdown case-study block for one run.

    Args:
        run_id: directory name under ``evaluation/runs/<stage>/``.
        stage: stage subdirectory (``baseline``/``nlp``/etc.).
        section_date: ``YYYY-MM-DD`` for the header; defaults to today UTC.
        note: optional one-line note rendered under the header.
        failures_per_tier: how many failed scenarios to pick per tier.
        low_judgments_per_dim: how many low-score records to pick per
            judge dimension.

    Returns:
        Markdown block (no trailing newline). Starts with ``### `` heading.
    """
    paths = RunPaths(run_id, stage)
    if not paths.records_dir.exists():
        raise FileNotFoundError(f"records dir missing: {paths.records_dir}")

    record_paths = sorted(paths.records_dir.glob("*.json"))
    if not record_paths:
        raise ValueError(f"no records under {paths.records_dir}")
    records = [load_record(p) for p in record_paths]

    git_short = _extract_git_short(run_id, records)
    section_date = section_date or now_utc().date().isoformat()
    ctx = _RenderContext(
        run_id=run_id, stage=stage, section_date=section_date, git_short=git_short
    )

    by_tier: dict[int, list[ConversationRecord]] = defaultdict(list)
    for r in records:
        key = _tier_sort_key(r.tier)
        if 1 <= key <= 7:
            by_tier[key].append(r)

    # --- Header + intro ---
    lines: list[str] = []
    lines.append(
        f"### {section_date} — {stage} — `{git_short}` — run_id `{run_id}`"
    )
    lines.append("")
    lines.append(
        f"> Sample: {len(records)} records · "
        f"See [`results_snapshots.md`](results_snapshots.md) for KPIs."
    )
    if note:
        lines.append("")
        lines.append(f"> Note: {note}")
    lines.append("")

    # --- Tier failures ---
    lines.append("#### Failed cases — 2 per tier (stable-fail preferred)")
    lines.append("")
    for tier in sorted(by_tier):
        picks = pick_tier_failures(records, tier, k=failures_per_tier)
        if not picks:
            continue
        for record, n_failed in picks:
            lines.append(_bullet_for_failure(ctx, record, n_failed))
    lines.append("")

    # --- Low-judgment exemplars ---
    lines.append(
        "#### Low-judgment exemplars — ≤ 2 per dimension "
        "(score ≤ 2, excluding `termination=error`)"
    )
    lines.append("")
    for dim_attr, dim_label in JUDGE_DIMENSIONS:
        picks = pick_low_judgments(records, dim_attr, k=low_judgments_per_dim)
        if not picks:
            lines.append(f"- **{dim_label}**: no records with score ≤ 2.")
            continue
        for record, score_set, score in picks:
            lines.append(
                _bullet_for_low_judgment(
                    ctx, record, score_set, score, dim_attr, dim_label
                )
            )

    return "\n".join(lines)


def _extract_git_short(run_id: str, records: list[ConversationRecord]) -> str:
    """Best-effort short git commit (first 7 chars).

    Run IDs follow the pattern ``YYYYMMDD_HHMMSS__<stage>__<git>__<extra>``;
    falls back to the record's ``git_commit`` if the run_id is non-canonical.
    """
    parts = run_id.split("__")
    if len(parts) >= 3 and len(parts[2]) >= 7:
        return parts[2][:7]
    if records and records[0].git_commit:
        return records[0].git_commit[:7]
    return "unknown"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _prepend_to_file(path: Path, block: str) -> None:
    """Insert ``block`` after the first ``## `` line in ``path``.

    If no ``## `` heading is present, appends with a separating blank line.
    """
    existing = path.read_text(encoding="utf-8") if path.exists() else ""
    if not existing:
        path.write_text(block + "\n", encoding="utf-8")
        return

    lines = existing.splitlines()
    insert_at = None
    for idx, line in enumerate(lines):
        if line.startswith("## "):
            insert_at = idx + 1
            break

    if insert_at is None:
        new_text = existing.rstrip() + "\n\n" + block + "\n"
    else:
        head = "\n".join(lines[:insert_at])
        tail = "\n".join(lines[insert_at:])
        new_text = head + "\n\n" + block + "\n\n" + tail
        if not new_text.endswith("\n"):
            new_text += "\n"

    path.write_text(new_text, encoding="utf-8")


def _cmd_render(args: argparse.Namespace) -> int:
    try:
        block = render_run_block(
            run_id=args.run_id,
            stage=args.stage,
            section_date=args.date,
            note=args.note,
            failures_per_tier=args.failures_per_tier,
            low_judgments_per_dim=args.low_per_dim,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.out:
        out_path = Path(args.out)
        if args.prepend:
            _prepend_to_file(out_path, block)
        else:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(block + "\n", encoding="utf-8")
        print(f"wrote {out_path}", file=sys.stderr)
    else:
        sys.stdout.write(block + "\n")
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.case_studies",
        description="Render the per-run case-study markdown block.",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    render_p = sub.add_parser("render", help="Render a run's case-study block.")
    render_p.add_argument("--run-id", required=True, help="Run ID directory name.")
    render_p.add_argument(
        "--stage",
        required=True,
        choices=["baseline", "nlp", "planner", "robustness"],
        help="Evaluation stage subdirectory.",
    )
    render_p.add_argument(
        "--date",
        default=None,
        help="Section date YYYY-MM-DD (defaults to today UTC).",
    )
    render_p.add_argument(
        "--note",
        default=None,
        help="Optional one-line note rendered under the header.",
    )
    render_p.add_argument(
        "--failures-per-tier",
        type=int,
        default=2,
        help="Picks per tier (default 2).",
    )
    render_p.add_argument(
        "--low-per-dim",
        type=int,
        default=2,
        help="Low-judgment picks per dimension (default 2).",
    )
    render_p.add_argument(
        "--out",
        default=None,
        help="Output file (default: stdout).",
    )
    render_p.add_argument(
        "--prepend",
        action="store_true",
        default=False,
        help="When used with --out, insert block after the first '## ' heading.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "render":
        return _cmd_render(args)
    parser.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "JUDGE_DIMENSIONS",
    "pick_tier_failures",
    "pick_low_judgments",
    "render_run_block",
]
