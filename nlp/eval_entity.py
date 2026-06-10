"""Intrinsic eval CLI for the entity extractor.

Run::

    python -m nlp.eval_entity --arm spacy
    python -m nlp.eval_entity --arm spacy --gold path/to/entity_gold.jsonl

Reads ``nlp/eval_data/entity_gold.jsonl`` and exercises the named arm on
every row. Reports per-class precision/recall/F1 for topic and contact_medium,
split by ``row_kind`` (canonical vs paraphrase vs control) so the report's
headline finding — "spaCy matches LLMs on canonical phrasings, LLMs win on
paraphrases" — is read directly from the result table.

Anti-bleed gate: refuses to run if ``paraphrase_coverage < 0.30`` over the
labelled subset (IMPROVEMENT_PLAN §6). Same computation as
``_combine_entity_gold.py``.

Writes a JSON results file under ``nlp/eval_data/results/entity_{arm}_{ts}.json``.

The 90% verification gate kicks in for headline metrics. Below it, results
are marked PRELIMINARY.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from collections import defaultdict
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

from nlp.factory import build_entity_extractor

DEFAULT_GOLD = Path("nlp/eval_data/entity_gold.jsonl")
DEFAULT_RESULTS_DIR = Path("nlp/eval_data/results")
VERIFICATION_THRESHOLD = 0.90
ANTIBLEED_THRESHOLD = 0.30


def _load_jsonl(p: Path) -> list[dict[str, Any]]:
    with p.open(encoding="utf-8") as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def _gold_label(row: dict[str, Any], field: str) -> str:
    """Return the gold label for ``field`` — verified value if present,
    else the Claude-proposed value.

    Field-name mapping: the gold file uses ``contact_medium_proposed`` /
    ``verified_medium`` for the contact medium slot (legacy field naming),
    while the Protocol's tuple uses just ``medium``. Map both forms here.
    """
    if field == "medium":
        verified = row.get("verified_medium")
        if verified is not None:
            return verified
        return row.get("contact_medium_proposed") or "none"
    # field == "topic"
    verified = row.get("verified_topic")
    if verified is not None:
        return verified
    return row.get("topic_proposed") or "none"


def _confusion(rows: list[dict[str, Any]], arm, field: str, labels: list[str]) -> dict:
    """Run the extractor on every row and build a confusion table for ``field``."""
    counts: dict[tuple[str, str], int] = defaultdict(int)  # (gold, predicted) -> n
    for row in rows:
        topic, medium, _ = arm.extract(row["utterance"])
        pred = topic if field == "topic" else medium
        gold = _gold_label(row, "topic" if field == "topic" else "medium")
        if pred is None:
            pred = "none"
        counts[(gold, pred)] += 1
    matrix = {g: {p: counts.get((g, p), 0) for p in labels} for g in labels}
    return matrix


def _prf1(matrix: dict[str, dict[str, int]], cls: str) -> tuple[float, float, float]:
    tp = matrix[cls][cls]
    fp = sum(matrix[g][cls] for g in matrix if g != cls)
    fn = sum(matrix[cls][p] for p in matrix[cls] if p != cls)
    p = tp / (tp + fp) if (tp + fp) else 0.0
    r = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * p * r / (p + r) if (p + r) else 0.0
    return p, r, f1


def _anti_bleed(rows: list[dict[str, Any]]) -> tuple[float, int, int]:
    labelled = [
        r for r in rows
        if (r.get("topic_proposed", "none") != "none"
            or r.get("contact_medium_proposed", "none") != "none")
    ]
    paraphrase = 0
    for r in labelled:
        subs = r.get("synonym_substrings_present", {})
        topic_labelled = r.get("topic_proposed", "none") != "none"
        medium_labelled = r.get("contact_medium_proposed", "none") != "none"
        topic_para = topic_labelled and not (subs.get("topic") or [])
        medium_para = medium_labelled and not (subs.get("medium") or [])
        if topic_para or medium_para:
            paraphrase += 1
    coverage = paraphrase / max(1, len(labelled))
    return coverage, paraphrase, len(labelled)


def _print_matrix(matrix: dict[str, dict[str, int]], field: str, labels: list[str]) -> None:
    print(f"\nConfusion matrix — {field} (rows=gold, cols=predicted):")
    header = "      " + "  ".join(f"{p:>10}" for p in labels)
    print(header)
    for g in labels:
        row = f"  {g:4}  " + "  ".join(f"{matrix[g][p]:>10}" for p in labels)
        print(row)


def main() -> None:
    parser_arg = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser_arg.add_argument(
        "--arm",
        required=True,
        choices=["spacy", "local_llm", "api_llm"],
        help="Entity arm to evaluate.",
    )
    parser_arg.add_argument(
        "--gold",
        type=Path,
        default=DEFAULT_GOLD,
        help=f"Path to entity gold JSONL (default {DEFAULT_GOLD}).",
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

    rows = _load_jsonl(args.gold)

    # Anti-bleed gate
    bleed_coverage, n_para, n_labelled = _anti_bleed(rows)
    print(f"=== Entity intrinsic eval — arm: {args.arm} ===")
    print(f"Gold file:           {args.gold}")
    print(f"Total rows:          {len(rows)}")
    print(f"Labelled rows:       {n_labelled}")
    print(f"Paraphrase coverage: {bleed_coverage:.3f} ({n_para}/{n_labelled})")
    if bleed_coverage < ANTIBLEED_THRESHOLD:
        print(
            f"\nREFUSING TO RUN: paraphrase_coverage {bleed_coverage:.3f} < "
            f"{ANTIBLEED_THRESHOLD}. Anti-bleed (IMPROVEMENT_PLAN §6) failed."
        )
        raise SystemExit(2)

    # Verification gate
    n_verified = sum(1 for r in rows if r.get("verified"))
    verification_rate = n_verified / len(rows) if rows else 0
    print(f"Verified rows:       {n_verified}/{len(rows)} ({verification_rate * 100:.1f}%)")
    if verification_rate < VERIFICATION_THRESHOLD and not args.allow_unverified:
        print(
            f"\nREFUSING TO RUN: verification rate {verification_rate * 100:.1f}% "
            f"< {VERIFICATION_THRESHOLD * 100:.0f}% threshold. "
            "Pass --allow-unverified to produce PRELIMINARY results."
        )
        raise SystemExit(2)
    preliminary = verification_rate < VERIFICATION_THRESHOLD
    if preliminary:
        print("STATUS:              PRELIMINARY (below verification threshold)")
    print()

    extractor = build_entity_extractor(args.arm)

    # The eval scores topic and medium in separate passes over the same
    # utterances (overall + per row_kind), so each utterance is extracted several
    # times. The arms are deterministic, so memoize per utterance — one real
    # extraction per unique text — and time only the cache misses (the true
    # per-call wall-clock, ~ms for spaCy, ~seconds for the LLM arms). Timed at the
    # arm boundary so no arm client is imported here.
    call_ms: list[float] = []
    _raw_extract = extractor.extract

    @lru_cache(maxsize=None)
    def _memo_extract(text: str):
        t0 = time.perf_counter()
        result = _raw_extract(text)
        call_ms.append((time.perf_counter() - t0) * 1000.0)
        return result

    extractor.extract = _memo_extract  # type: ignore[method-assign]

    topic_labels = ["investing", "mortgage", "pension", "none"]
    medium_labels = ["branch", "online", "phone", "none"]

    # Overall confusion matrices
    print("-" * 70)
    print("Overall (all rows)")
    print("-" * 70)
    topic_cm = _confusion(rows, extractor, "topic", topic_labels)
    medium_cm = _confusion(rows, extractor, "medium", medium_labels)
    _print_matrix(topic_cm, "topic", topic_labels)
    _print_matrix(medium_cm, "medium", medium_labels)

    print("\nPer-class P/R/F1:")
    for cls in topic_labels:
        p, r, f1 = _prf1(topic_cm, cls)
        print(f"  topic={cls:10} P={p:.3f}  R={r:.3f}  F1={f1:.3f}")
    for cls in medium_labels:
        p, r, f1 = _prf1(medium_cm, cls)
        print(f"  medium={cls:10} P={p:.3f}  R={r:.3f}  F1={f1:.3f}")

    # Split by row_kind — the report's headline split
    by_kind: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        by_kind[row.get("row_kind", "?")].append(row)

    print("\n" + "-" * 70)
    print("By row_kind (canonical vs paraphrase vs control)")
    print("-" * 70)
    kind_results: dict[str, Any] = {}
    for kind in [
        "canonical_topic_only",
        "paraphrase_topic_only",
        "canonical_medium_only",
        "paraphrase_medium_only",
        "canonical_both",
        "control_none_none",
    ]:
        subset = by_kind.get(kind, [])
        if not subset:
            continue
        tcm = _confusion(subset, extractor, "topic", topic_labels)
        mcm = _confusion(subset, extractor, "medium", medium_labels)
        print(f"\n{kind} (n={len(subset)}):")
        for cls in topic_labels:
            if cls == "none":
                continue
            p, r, f1 = _prf1(tcm, cls)
            if p > 0 or r > 0:
                print(f"  topic={cls:10} P={p:.3f}  R={r:.3f}  F1={f1:.3f}")
        for cls in medium_labels:
            if cls == "none":
                continue
            p, r, f1 = _prf1(mcm, cls)
            if p > 0 or r > 0:
                print(f"  medium={cls:10} P={p:.3f}  R={r:.3f}  F1={f1:.3f}")
        # `none` precision tells us the false-positive story for controls
        np, nr, nf1 = _prf1(tcm, "none")
        if kind == "control_none_none":
            print(f"  topic=none      P={np:.3f}  R={nr:.3f}  F1={nf1:.3f}   "
                  f"(controls: low R = many false positives)")
        kind_results[kind] = {
            "n": len(subset),
            "topic_confusion": tcm,
            "medium_confusion": mcm,
        }

    # Write JSON
    args.results_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = args.results_dir / f"entity_{args.arm}_{ts}.json"
    out = {
        "arm": args.arm,
        "gold_file": str(args.gold),
        "anti_bleed": {
            "coverage": bleed_coverage,
            "n_paraphrase": n_para,
            "n_labelled": n_labelled,
            "threshold": ANTIBLEED_THRESHOLD,
        },
        "verification_rate": verification_rate,
        "preliminary": preliminary,
        "n_total": len(rows),
        "overall_topic_confusion": topic_cm,
        "overall_medium_confusion": medium_cm,
        "by_row_kind": kind_results,
        "inference_timing_ms": {
            "unique_calls": len(call_ms),
            "mean": statistics.fmean(call_ms) if call_ms else 0.0,
            "median": statistics.median(call_ms) if call_ms else 0.0,
            "total": sum(call_ms),
        },
    }
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResults: {out_path}")

    if call_ms:
        print(
            f"Per-call wall-clock ({args.arm}): {len(call_ms)} unique utterances, "
            f"mean {statistics.fmean(call_ms) / 1000:.2f}s, "
            f"median {statistics.median(call_ms) / 1000:.2f}s/call."
        )


if __name__ == "__main__":
    main()
