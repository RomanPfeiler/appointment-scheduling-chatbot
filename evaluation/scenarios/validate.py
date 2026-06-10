"""Standalone validator for committed scenario JSON files.

Replays the per-tier invariants enforced by `generator._assert_scenario_invariants`
against every scenario in the committed tier files. Exits non-zero on any
violation. CI / pytest call this to catch generator regressions.

Usage::

    python -m evaluation.scenarios.validate           # all tiers
    python -m evaluation.scenarios.validate --tier 1  # only Tier 1
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

from evaluation.schemas import Scenario

from .generator import _assert_scenario_invariants
from .paths import SCENARIOS_DIR, TIER_OUTPUT_FILES

log = logging.getLogger(__name__)


def validate_tier(tier: int) -> list[str]:
    """Return a list of human-readable violation messages for ``tier``."""
    path = SCENARIOS_DIR / TIER_OUTPUT_FILES[tier]
    if not path.exists():
        return [f"Tier {tier}: file missing — {path}"]

    raw = json.loads(path.read_text(encoding="utf-8"))
    violations: list[str] = []
    for entry in raw:
        try:
            scenario = Scenario.model_validate(entry)
        except Exception as exc:  # noqa: BLE001
            violations.append(
                f"{entry.get('scenario_id', '<no-id>')}: schema validation failed: {exc}"
            )
            continue
        try:
            _assert_scenario_invariants(scenario)
        except ValueError as exc:
            violations.append(str(exc))
    return violations


def validate_all(tiers: list[int] | None = None) -> dict[int, list[str]]:
    """Run validation for the given tiers (or all if None)."""
    tiers = tiers or sorted(TIER_OUTPUT_FILES.keys())
    return {tier: validate_tier(tier) for tier in tiers}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.scenarios.validate",
        description="Validate committed scenario JSON files against per-tier invariants.",
    )
    parser.add_argument(
        "--tier", type=int, choices=sorted(TIER_OUTPUT_FILES.keys()), default=None,
        help="Validate only this tier (default: all).",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    tiers = [args.tier] if args.tier is not None else None
    results = validate_all(tiers)

    total_violations = 0
    for tier, violations in results.items():
        if not violations:
            print(f"Tier {tier}: OK")
            continue
        total_violations += len(violations)
        print(f"Tier {tier}: {len(violations)} violation(s):")
        for v in violations:
            print(f"  - {v}")

    if total_violations:
        print(f"\nFAILED: {total_violations} total violation(s).", file=sys.stderr)
        return 1
    print("\nAll scenarios pass invariants.")
    return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = ["validate_tier", "validate_all", "main"]
