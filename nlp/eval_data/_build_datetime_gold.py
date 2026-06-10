"""One-shot builder for the datetime intrinsic-eval gold set.

Samples stratified rows from ``evaluation/phrase_bank/temporal_expressions.json``
(en_native) and ``evaluation/phrase_bank/swiss_variants.json`` (en_de/fr/it),
filters to entries whose surface text contains an actual datetime expression,
stratifies by ``(difficulty_tag × language_variant)``, and writes a JSON file
with ``verified_*`` fields left null for human verification.

Run::

    python -m nlp.eval_data._build_datetime_gold

Deterministic via fixed seed. Re-running overwrites ``datetime_gold.json``
with the same rows (modulo any data churn in the phrase bank).

Intentionally does NOT auto-derive ``verified_specificity`` from surface
regex — doing so would test the Arm 1 parser against the same regex set it
uses for derivation, which is not an honest evaluation.
"""

from __future__ import annotations

import json
import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

SEED = 42
TARGET_PER_CELL = 30   # rows per (bucket × language_variant) cell
EN_NATIVE_BUCKETS = ("specific date", "relative", "vague", "compound")
SWISS_VARIANTS = ("en_de", "en_fr", "en_it")

ROOT = Path(__file__).resolve().parents[2]
PHRASE_BANK = ROOT / "evaluation" / "phrase_bank" / "temporal_expressions.json"
SWISS_BANK = ROOT / "evaluation" / "phrase_bank" / "swiss_variants.json"
OUT_FILE = ROOT / "nlp" / "eval_data" / "datetime_gold.json"


# Filter regexes — drop entries with no datetime token in the surface text.
# This is the *inclusion* filter, NOT the specificity-derivation rule. The
# parser's specificity derivation lives in nlp/datetime_parsers/arm1_dateparser.py.
_HAS_TIME = re.compile(
    r"\b\d{1,2}(:\d{2})?\s*(am|pm)\b"
    r"|\b\d{1,2}:\d{2}\b"
    r"|\b\d{1,2}\s*(o'?clock|uhr|h)\b"
    r"|\b(noon|midnight|midday)\b",
    re.IGNORECASE,
)
_HAS_MULTIDAY = re.compile(
    r"\b(next|this|last|coming)\s+(week|month|fortnight)\b"
    r"|\b(soon|sometime|whenever|anytime|later|sooner)\b"
    r"|\b(within|in)\s+(a|the)\s+(week|month)\b",
    re.IGNORECASE,
)
_HAS_RELATIVE_DAY = re.compile(
    r"\b(today|tomorrow|tonight|day\s+after\s+tomorrow|yesterday)\b"
    r"|\b(this|next|last|coming)\s+(mon|tues|wednes|thurs|fri|satur|sun)day\b"
    r"|\bin\s+\d+\s+days?\b",
    re.IGNORECASE,
)
_HAS_ABSOLUTE_DATE = re.compile(
    r"\b(january|february|march|april|may|june|july|august|september|october"
    r"|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\b"
    r"|\b\d{1,2}[./-]\d{1,2}([./-]\d{2,4})?\b"
    r"|\b\d{1,2}(st|nd|rd|th)\b"
    r"|\b\d{4}-\d{2}-\d{2}\b",
    re.IGNORECASE,
)


def has_datetime_surface(text: str) -> bool:
    """True iff text contains at least one datetime-like token."""
    return any(
        rx.search(text)
        for rx in (_HAS_TIME, _HAS_MULTIDAY, _HAS_RELATIVE_DAY, _HAS_ABSOLUTE_DATE)
    )


def normalise_bucket(tag: str | None) -> str | None:
    """Map raw difficulty_tag to the four buckets in scope for Arm 1."""
    if tag in EN_NATIVE_BUCKETS:
        return tag
    return None  # unsupported / deadline-driven / negative / open-ended → drop


def load_candidates() -> list[dict[str, Any]]:
    """Load both phrase banks; assign language_variant; filter to datetime rows."""
    out: list[dict[str, Any]] = []

    with PHRASE_BANK.open(encoding="utf-8") as f:
        for r in json.load(f):
            bucket = normalise_bucket(r.get("difficulty_tag"))
            if bucket is None:
                continue
            if not has_datetime_surface(r["expression_text"]):
                continue
            out.append(
                {
                    "expression_id": r["expression_id"],
                    "expression_text": r["expression_text"],
                    "difficulty_bucket": bucket,
                    "language_variant": "en_native",
                    "source_dataset": r.get("source_dataset"),
                    "source_service": r.get("source_service"),
                    "normalized_meaning_dialog_level": r.get("normalized_meaning"),
                }
            )

    with SWISS_BANK.open(encoding="utf-8") as f:
        for r in json.load(f):
            bucket = normalise_bucket(r.get("difficulty_tag"))
            if bucket is None:
                continue
            if not has_datetime_surface(r["expression_text"]):
                continue
            out.append(
                {
                    "expression_id": r["expression_id"],
                    "expression_text": r["expression_text"],
                    "difficulty_bucket": bucket,
                    "language_variant": r.get("language_variant", "en_native"),
                    "source_dataset": r.get("source_dataset"),
                    "source_service": r.get("source_service"),
                    "normalized_meaning_dialog_level": r.get("normalized_meaning"),
                }
            )
    return out


def stratified_sample(
    candidates: list[dict[str, Any]],
    target_per_cell: int,
    seed: int,
) -> list[dict[str, Any]]:
    """Sample up to ``target_per_cell`` per (bucket × language_variant) cell."""
    rng = random.Random(seed)
    by_cell: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in candidates:
        by_cell[(r["difficulty_bucket"], r["language_variant"])].append(r)

    sampled: list[dict[str, Any]] = []
    for cell, rows in sorted(by_cell.items()):
        rng.shuffle(rows)
        sampled.extend(rows[:target_per_cell])
    return sampled


def add_verification_template(row: dict[str, Any]) -> dict[str, Any]:
    """Append empty ``verified_*`` fields for human review."""
    row["verified_specificity"] = None       # one of: exact_time | day_specific |
                                              #         day_vague | multi_day_vague |
                                              #         compound | not_a_datetime
    row["verified_date_iso"] = None           # "YYYY-MM-DD" or null
    row["verified_time_iso"] = None           # "HH:MM" or null
    row["verified_range_end_date_iso"] = None # for multi_day_vague / compound
    row["verified_compound_count"] = None     # 1 for single, ≥2 for compound
    row["verification_notes"] = None
    row["verified"] = False                   # human flips to true after review
    return row


def main() -> None:
    candidates = load_candidates()
    sampled = stratified_sample(candidates, TARGET_PER_CELL, SEED)
    sampled = [add_verification_template(r) for r in sampled]

    # Cell distribution for the summary block
    counts: dict[tuple[str, str], int] = defaultdict(int)
    for r in sampled:
        counts[(r["difficulty_bucket"], r["language_variant"])] += 1

    meta = {
        "schema_version": "1.0",
        "seed": SEED,
        "target_per_cell": TARGET_PER_CELL,
        "buckets_in_scope": list(EN_NATIVE_BUCKETS),
        "language_variants_in_scope": ["en_native", *SWISS_VARIANTS],
        "anchor_datetime_for_eval": "2026-05-31T12:00:00+02:00",
        "candidate_pool_total": len(candidates),
        "sampled_total": len(sampled),
        "per_cell_counts": {f"{b}|{v}": n for (b, v), n in sorted(counts.items())},
        "verification_fields": [
            "verified_specificity",
            "verified_date_iso",
            "verified_time_iso",
            "verified_range_end_date_iso",
            "verified_compound_count",
            "verification_notes",
            "verified",
        ],
        "notes": (
            "Auto-derivation of verified_* fields is intentionally NOT performed "
            "because the Arm 1 parser uses the same surface regex set for its "
            "specificity derivation — auto-deriving gold would test the parser "
            "against itself. Human verification required before any intrinsic "
            "eval result is reported."
        ),
    }

    payload = {"_meta": meta, "rows": sampled}
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUT_FILE.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"wrote {OUT_FILE} — {len(sampled)} rows across {len(counts)} cells")
    print("per-cell counts:")
    for (b, v), n in sorted(counts.items()):
        print(f"  {b:14} × {v:10} → {n:2d}")


if __name__ == "__main__":
    main()
