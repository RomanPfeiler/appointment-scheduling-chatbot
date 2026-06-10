"""CLI entry point for scenario generation, statistics, and validation.

Usage::

    python -m evaluation.scenarios.cli generate --seed 1234
    python -m evaluation.scenarios.cli stats
    python -m evaluation.scenarios.cli validate
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter

from evaluation.schemas import Scenario

from .generator import write_all
from .paths import SCENARIOS_DIR, TIER_OUTPUT_FILES


def _setup_logging(verbosity: int) -> None:
    level = logging.WARNING if verbosity == 0 else logging.INFO if verbosity == 1 else logging.DEBUG
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def _cmd_generate(args: argparse.Namespace) -> int:
    paths = write_all(seed=args.seed)
    for tier, p in sorted(paths.items()):
        size = p.stat().st_size
        print(f"  tier {tier}: {p.name}  ({size:,} bytes)")
    return 0


def _iter_scenario_files() -> list[tuple[int, list[dict]]]:
    out: list[tuple[int, list[dict]]] = []
    for tier, name in sorted(TIER_OUTPUT_FILES.items()):
        path = SCENARIOS_DIR / name
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        out.append((tier, data))
    return out


def _cmd_stats(args: argparse.Namespace) -> int:
    """Print per-tier / per-language / per-topic counts plus reachability."""
    total = 0
    lang_total: Counter[str] = Counter()
    topic_total: Counter[tuple[str, str]] = Counter()
    reachable_total = 0
    unreachable_total = 0

    print("\nPer-tier counts:")
    print(f"  {'Tier':>4} | {'Count':>6} | {'Reach':>6} | {'Unreach':>7} | Language mix")
    print(f"  {'----':>4} | {'-----':>6} | {'-----':>6} | {'------':>7} | -------------")
    for tier, scenarios in _iter_scenario_files():
        lang_mix: Counter[str] = Counter(s["language_variant"] for s in scenarios)
        reach = sum(1 for s in scenarios if s.get("booking_reachable", True))
        unreach = len(scenarios) - reach
        total += len(scenarios)
        reachable_total += reach
        unreachable_total += unreach
        lang_total.update(lang_mix)
        for s in scenarios:
            topic_total[(s["topic_id"], s["contact_medium_id"])] += 1

        mix_str = ", ".join(f"{k}={v}" for k, v in sorted(lang_mix.items()))
        print(f"  {tier:>4} | {len(scenarios):>6} | {reach:>6} | {unreach:>7} | {mix_str}")
    print(f"  {'----':>4} | {'-----':>6} | {'-----':>6} | {'------':>7} |")
    print(f"  {'TOT':>4} | {total:>6} | {reachable_total:>6} | {unreachable_total:>7} |")

    print("\nLanguage variant totals:")
    for variant in ("en_native", "en_de", "en_fr", "en_it"):
        print(f"  {variant:>10}: {lang_total[variant]}")

    print("\n(topic, medium) coverage:")
    for (topic, medium), count in sorted(topic_total.items()):
        print(f"  {topic:>10}/{medium:<8} {count}")

    return 0


def _cmd_validate(args: argparse.Namespace) -> int:
    """Round-trip every scenario through Scenario.model_validate."""
    errors = 0
    total = 0
    for tier, scenarios in _iter_scenario_files():
        for s_dict in scenarios:
            total += 1
            try:
                Scenario.model_validate(s_dict)
            except Exception as e:  # noqa: BLE001
                errors += 1
                print(
                    f"  FAIL tier {tier} {s_dict.get('scenario_id', '?')}: "
                    f"{type(e).__name__}: {str(e)[:160]}"
                )
    print(f"\nValidated {total} scenarios; {errors} errors")
    return 0 if errors == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="evaluation.scenarios",
        description="Generate, inspect, and validate the evaluation scenario suite.",
    )
    p.add_argument("-v", "--verbose", action="count", default=1, help="-v info, -vv debug")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_gen = sub.add_parser("generate", help="Write all 7 tier JSON files")
    p_gen.add_argument("--seed", type=int, default=1234, help="RNG seed (deterministic)")
    p_gen.set_defaults(func=_cmd_generate)

    p_stats = sub.add_parser("stats", help="Print per-tier / per-language / per-topic counts")
    p_stats.set_defaults(func=_cmd_stats)

    p_val = sub.add_parser("validate", help="Round-trip each scenario through Scenario.model_validate")
    p_val.set_defaults(func=_cmd_validate)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _setup_logging(args.verbose)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
