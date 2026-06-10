"""Intrinsic eval CLI for the datetime parser.

Run::

    python -m nlp.eval_datetime --arm dateparser
    python -m nlp.eval_datetime --arm dateparser --gold path/to/datetime_gold.json

Reads ``nlp/eval_data/datetime_gold.json`` and exercises the named arm on
every row. Reports per ``(difficulty_bucket × language_variant)`` cell:

- **parse_rate**: fraction of rows for which the parser returned ≥1
  DateRange. Headline coverage metric.
- **specificity_distribution**: counts of emitted specificity values.
  Descriptive — shows how the parser classifies each bucket.
- **compound_rate** (compound bucket only): fraction of rows that yielded
  ≥2 ranges. Headline compound-detection metric.

Two distinct gold-independent quality signals (neither is accuracy-vs-gold;
true accuracy waits for human-verified labels):

- **specificity_plausibility%**: fraction of emitted ranges whose ``specificity``
  label is in the plausible set for the row's ``difficulty_bucket``. A
  *specificity-classification* soft proxy (this is what the column historically
  labelled "plausible%" actually computed — renamed here to say what it is).
- **domain_plausibility%**: a *well-formedness / domain-sanity* check on the
  resolved range — NOT a specificity check and NOT accuracy-vs-gold. A range is
  domain-plausible when its start is tz-aware Europe/Zurich, ``start < end``, the
  window falls inside the scheduling horizon (``end ≥ now+LEAD_TIME_HOURS`` and
  ``start ≤ now+SCHEDULING_HORIZON_DAYS``), and — for ``exact_time`` only — the
  start clock time is within business hours ``[BUSINESS_HOURS_START,
  BUSINESS_HOURS_END)``. Business hours are conditioned on ``exact_time`` because
  day-level specificities snap the start to midnight by the shared window policy,
  so a literal start∈[08:00,17:00) check would wrongly fail every day-level range.
  Constants come from ``mcp_server/config.py``. This matters more for the LLM
  arms, where a resolved date can be *parseable-but-implausible*.

For recognition-vs-resolution failure analysis, the per-row log records the
emitted expression (``original_text``) and the resolved datetime for every range,
plus — for arms that expose ``last_diagnostics()`` (the local-LLM arm) — the raw
model output and any recognized-but-unresolved expressions.

Writes a JSON results file under ``nlp/eval_data/results/datetime_{arm}_{ts}.json``.

The 90% verification gate kicks in for headline accuracy metrics. With
verified rows below 90% we emit a clear PRELIMINARY banner so no result is
mistaken for the headline number.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from mcp_server.config import (
    BUSINESS_HOURS_END,
    BUSINESS_HOURS_START,
    LEAD_TIME_HOURS,
    SCHEDULING_HORIZON_DAYS,
    TIMEZONE,
)
from nlp.factory import build_datetime_parser

ZURICH = ZoneInfo("Europe/Zurich")
ANCHOR = datetime(2026, 5, 31, 12, 0, tzinfo=ZURICH)
DEFAULT_GOLD = Path("nlp/eval_data/datetime_gold.json")
DEFAULT_RESULTS_DIR = Path("nlp/eval_data/results")
VERIFICATION_THRESHOLD = 0.90

# Bucket → plausible specificity values. A specificity emission in the set
# is treated as a "reasonable" parse of that bucket; anything outside is a
# gross misclassification.
_PLAUSIBLE_SPECIFICITY = {
    "specific date": {"exact_time", "day_specific"},
    "relative": {"exact_time", "day_vague", "day_specific"},
    "vague": {"day_vague", "multi_day_vague", "exact_time"},
    "compound": {"exact_time", "day_specific", "day_vague"},
}


def _is_domain_plausible(rng: Any, now: datetime) -> bool:
    """Gold-independent domain-sanity check on a resolved range.

    See the module docstring for the full definition. Business hours bind only
    ``exact_time`` (day-level starts are midnight-snapped by the window policy).
    """
    start = rng.start_datetime
    end = rng.end_datetime
    if start.tzinfo is None or start.utcoffset() is None:
        return False
    if not start < end:
        return False
    # Inside the bookable horizon — checked via end ≥ lead cutoff and
    # start ≤ horizon, which avoids the midnight-snap vs lead-time artifact.
    if end < now + timedelta(hours=LEAD_TIME_HOURS):
        return False
    if start > now + timedelta(days=SCHEDULING_HORIZON_DAYS):
        return False
    if rng.specificity == "exact_time":
        local_hour = start.astimezone(TIMEZONE).hour
        if not (BUSINESS_HOURS_START <= local_hour < BUSINESS_HOURS_END):
            return False
    return True


def _score_row(row: dict, parser_output: list, bucket: str, now: datetime) -> dict[str, Any]:
    """Compute per-row scores. Returns a dict the aggregator merges."""
    n_ranges = len(parser_output)
    spec_plausible = _PLAUSIBLE_SPECIFICITY.get(bucket, set())
    return {
        "parsed_any": 1 if n_ranges >= 1 else 0,
        "n_ranges": n_ranges,
        "specificities": [r.specificity for r in parser_output],
        "spec_plausible_count": sum(
            1 for r in parser_output if r.specificity in spec_plausible
        ),
        "domain_plausible_count": sum(
            1 for r in parser_output if _is_domain_plausible(r, now)
        ),
        "compound_ok": int(n_ranges >= 2) if bucket == "compound" else None,
    }


def main() -> None:
    parser_arg = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser_arg.add_argument(
        "--arm",
        required=True,
        choices=["dateparser", "local_llm", "api_llm"],
        help="Datetime arm to evaluate.",
    )
    parser_arg.add_argument(
        "--gold",
        type=Path,
        default=DEFAULT_GOLD,
        help=f"Path to datetime gold JSON (default {DEFAULT_GOLD}).",
    )
    parser_arg.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help=f"Directory to write results JSON (default {DEFAULT_RESULTS_DIR}).",
    )
    parser_arg.add_argument(
        "--allow-unverified",
        action="store_true",
        default=False,
        help=(
            "Run even when verification coverage is below "
            f"{VERIFICATION_THRESHOLD * 100:.0f}%. Results are marked PRELIMINARY."
        ),
    )
    args = parser_arg.parse_args()

    with args.gold.open(encoding="utf-8") as f:
        payload = json.load(f)
    rows = payload["rows"]

    # Verification gate
    n_verified = sum(1 for r in rows if r.get("verified"))
    verification_rate = n_verified / len(rows) if rows else 0
    if verification_rate < VERIFICATION_THRESHOLD and not args.allow_unverified:
        print(
            f"REFUSING TO RUN: verification rate {verification_rate * 100:.1f}% "
            f"< {VERIFICATION_THRESHOLD * 100:.0f}% threshold. "
            "Pass --allow-unverified to produce PRELIMINARY results."
        )
        raise SystemExit(2)
    preliminary = verification_rate < VERIFICATION_THRESHOLD

    print(f"=== Datetime intrinsic eval — arm: {args.arm} ===")
    print(f"Gold file:        {args.gold}")
    print(f"Anchor datetime:  {ANCHOR.isoformat()}")
    print(f"Total rows:       {len(rows)}")
    print(f"Verified rows:    {n_verified}/{len(rows)} ({verification_rate * 100:.1f}%)")
    if preliminary:
        print("STATUS:           PRELIMINARY (below verification threshold)")
    print()

    dt_parser = build_datetime_parser(args.arm)
    # Per-parse wall-clock, timed at the arm boundary (arm-agnostic — ~ms for the
    # classical arm, ~seconds for the LLM arms). Avoids importing any arm's client.
    call_ms: list[float] = []

    cells: dict[tuple[str, str], dict[str, Any]] = defaultdict(
        lambda: {
            "n": 0,
            "parsed_any": 0,
            "spec_plausible": 0,
            "domain_plausible": 0,
            "spec_counts": defaultdict(int),
            "n_ranges_counts": defaultdict(int),
            "compound_with_two_or_more": 0,
        }
    )

    # Per-row log for recognition-vs-resolution failure analysis: the emitted
    # expression + resolved datetime for every range, plus the raw model output
    # and unresolved expressions for arms that expose last_diagnostics().
    per_row: list[dict[str, Any]] = []
    diag_fn = getattr(dt_parser, "last_diagnostics", None)

    failures: list[dict[str, Any]] = []
    for row in rows:
        bucket = row["difficulty_bucket"]
        variant = row["language_variant"]
        text = row["expression_text"]
        t0 = time.perf_counter()
        try:
            output = dt_parser.parse(text, now=ANCHOR)
        except Exception as exc:
            output = []
            failures.append(
                {"expression_id": row["expression_id"], "text": text, "error": str(exc)}
            )
        call_ms.append((time.perf_counter() - t0) * 1000.0)
        score = _score_row(row, output, bucket, ANCHOR)
        cell = cells[(bucket, variant)]
        cell["n"] += 1
        cell["parsed_any"] += score["parsed_any"]
        cell["spec_plausible"] += score["spec_plausible_count"]
        cell["domain_plausible"] += score["domain_plausible_count"]
        for spec in score["specificities"]:
            cell["spec_counts"][spec] += 1
        cell["n_ranges_counts"][score["n_ranges"]] += 1
        if bucket == "compound" and score["compound_ok"] == 1:
            cell["compound_with_two_or_more"] += 1

        row_log: dict[str, Any] = {
            "expression_id": row["expression_id"],
            "bucket": bucket,
            "variant": variant,
            "text": text,
            "parsed_any": score["parsed_any"],
            "ranges": [
                {
                    "expr": r.original_text,
                    "resolved": r.start_datetime.isoformat(),
                    "specificity": r.specificity,
                    "domain_plausible": _is_domain_plausible(r, ANCHOR),
                }
                for r in output
            ],
        }
        if callable(diag_fn):
            diag = diag_fn()
            if diag is not None:
                row_log["model_raw"] = diag.get("raw", "")
                row_log["recognized"] = diag.get("recognized", [])
                row_log["unresolved"] = diag.get("unresolved", [])
        per_row.append(row_log)

    # Aggregate totals
    total_n = sum(c["n"] for c in cells.values())
    total_parsed = sum(c["parsed_any"] for c in cells.values())
    total_spec_plausible = sum(c["spec_plausible"] for c in cells.values())
    total_domain_plausible = sum(c["domain_plausible"] for c in cells.values())
    total_ranges = sum(
        n * count
        for c in cells.values()
        for n, count in c["n_ranges_counts"].items()
    )

    # Print per-cell results
    print(f"{'bucket':14}  {'variant':9}  {'n':>3}  {'parse%':>6}  {'spec_pl%':>8}  "
          f"{'dom_pl%':>8}  {'spec_distribution'}")
    for (bucket, variant), c in sorted(cells.items()):
        cell_ranges = total_ranges_for_cell(c)
        parse_pct = (c["parsed_any"] / c["n"] * 100) if c["n"] else 0
        spec_pl_pct = (c["spec_plausible"] / cell_ranges * 100) if cell_ranges else 0
        dom_pl_pct = (c["domain_plausible"] / cell_ranges * 100) if cell_ranges else 0
        spec_summary = ", ".join(f"{k}={v}" for k, v in sorted(c["spec_counts"].items()))
        print(
            f"{bucket:14}  {variant:9}  {c['n']:3d}  {parse_pct:5.1f}%  "
            f"{spec_pl_pct:7.1f}%  {dom_pl_pct:7.1f}%   {spec_summary}"
        )
        if bucket == "compound":
            ok = c["compound_with_two_or_more"]
            print(f"{'':14}  {'':9}       compound>=2: {ok}/{c['n']} = "
                  f"{(ok / c['n'] * 100) if c['n'] else 0:.1f}%")

    print()
    print(
        f"TOTAL: n={total_n}  parsed_any={total_parsed} "
        f"({total_parsed / total_n * 100:.1f}%)  "
        f"spec_plausible={total_spec_plausible}/{total_ranges} "
        f"({(total_spec_plausible / total_ranges * 100) if total_ranges else 0:.1f}%)  "
        f"domain_plausible={total_domain_plausible}/{total_ranges} "
        f"({(total_domain_plausible / total_ranges * 100) if total_ranges else 0:.1f}%)"
    )
    if failures:
        print(f"\nParser-raised exceptions: {len(failures)}")
        for fail in failures[:5]:
            print(f"  {fail['expression_id']}: {fail['text']!r} -> {fail['error']}")

    # Write JSON
    args.results_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = args.results_dir / f"datetime_{args.arm}_{ts}.json"
    out = {
        "arm": args.arm,
        "gold_file": str(args.gold),
        "anchor": ANCHOR.isoformat(),
        "verification_rate": verification_rate,
        "preliminary": preliminary,
        "total_rows": total_n,
        "total_parsed_any": total_parsed,
        "total_ranges_emitted": total_ranges,
        "total_spec_plausible_ranges": total_spec_plausible,
        "total_domain_plausible_ranges": total_domain_plausible,
        "cells": {
            f"{b}|{v}": {
                "n": c["n"],
                "parsed_any": c["parsed_any"],
                "parse_rate": c["parsed_any"] / c["n"] if c["n"] else 0,
                "spec_counts": dict(c["spec_counts"]),
                "n_ranges_counts": {str(k): v for k, v in c["n_ranges_counts"].items()},
                "spec_plausible_count": c["spec_plausible"],
                "domain_plausible_count": c["domain_plausible"],
                "compound_with_two_or_more": c["compound_with_two_or_more"],
            }
            for (b, v), c in sorted(cells.items())
        },
        "per_row": per_row,
        "inference_timing_ms": {
            "count": len(call_ms),
            "mean": statistics.fmean(call_ms) if call_ms else 0.0,
            "median": statistics.median(call_ms) if call_ms else 0.0,
            "total": sum(call_ms),
        },
        "failures": failures,
    }
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResults: {out_path}")

    if call_ms:
        print(
            f"Per-call wall-clock ({args.arm}): {len(call_ms)} calls, "
            f"mean {statistics.fmean(call_ms) / 1000:.2f}s, "
            f"median {statistics.median(call_ms) / 1000:.2f}s/call."
        )


def total_ranges_for_cell(c: dict[str, Any]) -> int:
    return sum(n * count for n, count in c["n_ranges_counts"].items())


if __name__ == "__main__":
    main()
