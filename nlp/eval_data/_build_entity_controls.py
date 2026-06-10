"""Sample 50 entity-gold (none, none) controls from SGD raw.

SGD's services (dentists, salons, doctors, banking-as-event-tickets) are
*independent* of our Swiss bank topic/medium domain, so a random SGD sample
is a realistic source for negative-control utterances — measuring spaCy's
false-positive rate on natural appointment-flow language.

The sample deliberately includes "hard negatives": utterances containing a
synonym substring (e.g. "what's their phone number?" — has "phone" but means
phone number, not contact-by-phone intent). These test the matcher's
context-sensitivity.

Run::

    python -m nlp.eval_data._build_entity_controls

Deterministic via fixed seed. Output is APPENDED to the start of
``entity_gold.jsonl``; the with-label rows (authored separately) follow.
"""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Any

from nlp.synonyms import all_medium_synonyms, all_topic_synonyms

SEED = 1729
TARGET_CONTROLS = 50
TARGET_CLEAN = 30      # no synonym substring at all
TARGET_HARD = 20       # synonym substring present but used non-topically/non-medially
SGD_RAW = (
    Path(__file__).resolve().parents[2]
    / "evaluation"
    / "datasets"
    / "mined"
    / "sgd_temporal_raw.jsonl"
)
OUT_FILE = (
    Path(__file__).resolve().parents[2] / "nlp" / "eval_data" / "entity_controls.jsonl"
)


def load_sgd() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with SGD_RAW.open(encoding="utf-8") as f:
        for ln in f:
            rows.append(json.loads(ln))
    return rows


def synonym_hits(text: str, all_syns: set[str]) -> list[str]:
    """Return the synonym substrings present in ``text`` (lowercased)."""
    t = text.lower()
    return sorted({s for s in all_syns if s in t})


def _to_row(r: dict[str, Any], topic_subs: list[str], medium_subs: list[str]) -> dict[str, Any]:
    return {
        "utterance_id": r["expression_id"],
        "utterance": r["expression_text"],
        "source_dataset": r.get("source_dataset"),
        "source_service": r.get("source_service", "?"),
        "topic_proposed": "none",
        "contact_medium_proposed": "none",
        "synonym_substrings_present": {"topic": topic_subs, "medium": medium_subs},
        "is_hard_negative": bool(topic_subs or medium_subs),
        "verified_topic": None,
        "verified_medium": None,
        "verified_includes_paraphrase": None,
        "verified": False,
        "row_kind": "control_none_none",
        "verification_notes": None,
    }


def main() -> None:
    rows = load_sgd()
    rng = random.Random(SEED)

    topic_syns = all_topic_synonyms()
    medium_syns = all_medium_synonyms()

    # Pass 1: partition the entire SGD corpus into clean vs hard pools
    clean_pool: list[tuple[dict[str, Any], list[str], list[str]]] = []
    hard_pool: list[tuple[dict[str, Any], list[str], list[str]]] = []
    for r in rows:
        text = r.get("expression_text", "")
        if not text or len(text) > 200:
            continue
        topic_subs = synonym_hits(text, topic_syns)
        medium_subs = synonym_hits(text, medium_syns)
        item = (r, topic_subs, medium_subs)
        if topic_subs or medium_subs:
            hard_pool.append(item)
        else:
            clean_pool.append(item)

    # Pass 2: pull TARGET_CLEAN from clean_pool, TARGET_HARD from hard_pool
    per_service_cap = 10  # tighter cap since pools are imbalanced
    sample: list[dict[str, Any]] = []

    def pull(pool: list[tuple[dict[str, Any], list[str], list[str]]], target: int) -> None:
        rng.shuffle(pool)
        by_svc: dict[str, int] = {}
        added = 0
        for r, topic_subs, medium_subs in pool:
            svc = r.get("source_service", "?")
            if by_svc.get(svc, 0) >= per_service_cap:
                continue
            sample.append(_to_row(r, topic_subs, medium_subs))
            by_svc[svc] = by_svc.get(svc, 0) + 1
            added += 1
            if added >= target:
                return

    pull(clean_pool, TARGET_CLEAN)
    pull(hard_pool, TARGET_HARD)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUT_FILE.open("w", encoding="utf-8") as f:
        for row in sample:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # Distribution summary
    n_clean = sum(1 for r in sample if not r["is_hard_negative"])
    n_hard = sum(1 for r in sample if r["is_hard_negative"])
    by_svc: dict[str, int] = {}
    for r in sample:
        by_svc[r["source_service"]] = by_svc.get(r["source_service"], 0) + 1

    print(f"wrote {OUT_FILE} -- {len(sample)} rows")
    print(f"  clean negatives (no synonym substring): {n_clean}")
    print(f"  hard negatives (synonym substring present): {n_hard}")
    print(f"  by source_service: {by_svc}")


if __name__ == "__main__":
    main()
