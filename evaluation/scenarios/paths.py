"""Filesystem paths shared by the scenario generation package."""

from __future__ import annotations

from pathlib import Path

# evaluation/scenarios/paths.py -> .../evaluation/
EVAL_ROOT: Path = Path(__file__).resolve().parent.parent
SCENARIOS_DIR: Path = EVAL_ROOT / "scenarios"
PHRASE_BANK_JSON: Path = EVAL_ROOT / "phrase_bank" / "temporal_expressions.json"
SWISS_VARIANTS_JSON: Path = EVAL_ROOT / "phrase_bank" / "swiss_variants.json"
# Hand-curated banking-specific out-of-scope phrasings for Tier 7 (per
# EVALUATION_FRAMEWORK.md §5a; added 2026-05-25 alongside the phrase-bank
# domain filter so Tier 7 has a clean, in-domain source).
BANKING_UNSUPPORTED_JSON: Path = EVAL_ROOT / "phrase_bank" / "banking_unsupported.json"
REFERENCE_DATA_JSON: Path = (
    EVAL_ROOT.parent / "mcp_server" / "data" / "reference_data.json"
)

# Per-tier output files (must match the names referenced in
# EVALUATION_FRAMEWORK.md §7c and ARCHITECTURE.md §4)
TIER_OUTPUT_FILES: dict[int, str] = {
    1: "tier1_direct_match.json",
    2: "tier2_near_miss.json",
    3: "tier3_day_shift.json",
    4: "tier4_broad_window.json",
    5: "tier5_multi_round.json",
    6: "tier6_other.json",
    7: "tier7_out_of_scope.json",
}
