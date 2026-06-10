"""Combine entity_with_label.jsonl + entity_controls.jsonl into entity_gold.jsonl.

Runs the anti-bleed audit (IMPROVEMENT_PLAN §6) and refuses to write if the
paraphrase coverage is too low. The audit metric:

    paraphrase_coverage = 1 - (#labelled rows containing any synonym substring
                                  / #labelled rows with a topic OR medium label)

Threshold: ≥ 0.30. The expected value with our 150-row authored set is ≈ 0.40
(60 paraphrase + 60 canonical_both / 150 = 0.40 contain no synonym → wait,
actually: 60 paraphrase rows contain NO synonym substring for their labelled
class, so paraphrase_coverage on the 150 labelled set is 60/150 = 0.40).

Run::

    python -m nlp.eval_data._combine_entity_gold
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2] / "nlp" / "eval_data"
WITH_LABEL = ROOT / "entity_with_label.jsonl"
CONTROLS = ROOT / "entity_controls.jsonl"
OUT = ROOT / "entity_gold.jsonl"

ANTIBLEED_THRESHOLD = 0.30


def _load_jsonl(p: Path) -> list[dict[str, Any]]:
    with p.open(encoding="utf-8") as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def anti_bleed_audit(rows: list[dict[str, Any]]) -> tuple[float, int, int]:
    """Return (paraphrase_coverage, n_paraphrase_or_clean, n_labelled).

    A row counts as "paraphrase-or-clean for its labelled class" when:
    - proposed topic ≠ none AND no topic-synonym substring is present, OR
    - proposed medium ≠ none AND no medium-synonym substring is present, OR
    - the row has a label and no synonyms at all
    """
    labelled = [
        r
        for r in rows
        if r.get("topic_proposed", "none") != "none"
        or r.get("contact_medium_proposed", "none") != "none"
    ]
    paraphrase_count = 0
    for r in labelled:
        subs = r.get("synonym_substrings_present", {})
        topic_subs = subs.get("topic") or []
        medium_subs = subs.get("medium") or []
        topic_labelled = r.get("topic_proposed", "none") != "none"
        medium_labelled = r.get("contact_medium_proposed", "none") != "none"
        # Paraphrase if at least one labelled class has no corresponding synonym
        topic_paraphrase = topic_labelled and not topic_subs
        medium_paraphrase = medium_labelled and not medium_subs
        if topic_paraphrase or medium_paraphrase:
            paraphrase_count += 1
    coverage = paraphrase_count / max(1, len(labelled))
    return coverage, paraphrase_count, len(labelled)


def main() -> None:
    with_label = _load_jsonl(WITH_LABEL)
    controls = _load_jsonl(CONTROLS)
    all_rows = with_label + controls

    coverage, n_paraphrase, n_labelled = anti_bleed_audit(all_rows)
    print(
        f"anti-bleed audit: paraphrase_coverage = "
        f"{coverage:.3f} ({n_paraphrase}/{n_labelled} labelled rows are paraphrase)"
    )
    if coverage < ANTIBLEED_THRESHOLD:
        raise SystemExit(
            f"FAIL: paraphrase_coverage {coverage:.3f} < {ANTIBLEED_THRESHOLD}. "
            "Add more paraphrase rows or remove canonical bias before committing."
        )

    with OUT.open("w", encoding="utf-8") as f:
        for row in all_rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # Final distribution print
    by_kind: dict[str, int] = {}
    by_topic: dict[str, int] = {}
    by_medium: dict[str, int] = {}
    for r in all_rows:
        by_kind[r["row_kind"]] = by_kind.get(r["row_kind"], 0) + 1
        by_topic[r.get("topic_proposed", "none")] = (
            by_topic.get(r.get("topic_proposed", "none"), 0) + 1
        )
        by_medium[r.get("contact_medium_proposed", "none")] = (
            by_medium.get(r.get("contact_medium_proposed", "none"), 0) + 1
        )

    print(f"wrote {OUT} -- {len(all_rows)} rows")
    print(f"  by_row_kind: {by_kind}")
    print(f"  by_topic_proposed: {by_topic}")
    print(f"  by_medium_proposed: {by_medium}")


if __name__ == "__main__":
    main()
