"""Shared filesystem paths for the mining package.

Centralised so every mining script writes to the same locations and the
EVALUATION_FRAMEWORK.md §7c layout stays the single source of truth.
"""

from __future__ import annotations

from pathlib import Path

# evaluation/mining/paths.py -> .../evaluation/
EVAL_ROOT: Path = Path(__file__).resolve().parent.parent

DATASETS_DIR: Path = EVAL_ROOT / "datasets"
MINED_DIR: Path = DATASETS_DIR / "mined"
PHRASE_BANK_DIR: Path = EVAL_ROOT / "phrase_bank"

SGD_RAW_JSONL: Path = MINED_DIR / "sgd_temporal_raw.jsonl"
MULTIWOZ_RAW_JSONL: Path = MINED_DIR / "multiwoz_temporal_raw.jsonl"

PHRASE_BANK_JSON: Path = PHRASE_BANK_DIR / "temporal_expressions.json"
UNCLASSIFIED_JSON: Path = PHRASE_BANK_DIR / "_unclassified.json"
PHRASE_BANK_SUMMARY_MD: Path = PHRASE_BANK_DIR / "SUMMARY.md"
BUCKET_LOG_MD: Path = PHRASE_BANK_DIR / "bucket_log.md"


def ensure_dirs() -> None:
    """Create the output directories if missing (idempotent)."""
    for d in (DATASETS_DIR, MINED_DIR, PHRASE_BANK_DIR):
        d.mkdir(parents=True, exist_ok=True)
