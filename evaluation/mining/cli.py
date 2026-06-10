"""CLI entry point for phrase-bank mining + tagging + summarisation.

Usage::

    python -m evaluation.mining.cli mine --source sgd
    python -m evaluation.mining.cli mine --source multiwoz
    python -m evaluation.mining.cli mine --source all
    python -m evaluation.mining.cli tag
    python -m evaluation.mining.cli summarize
    python -m evaluation.mining.cli all      # mine sgd + multiwoz, tag, summarize

The CLI is a thin orchestrator over :mod:`evaluation.mining.sgd`,
:mod:`evaluation.mining.multiwoz`, :mod:`evaluation.mining.tagging`, and
:mod:`evaluation.mining.summarize`. Each step writes its outputs to the
paths defined in :mod:`evaluation.mining.paths`.
"""

from __future__ import annotations

import argparse
import logging
import sys

from . import domain_filter, multiwoz, sgd, summarize, tagging


def _setup_logging(verbosity: int) -> None:
    level = logging.WARNING if verbosity == 0 else logging.INFO if verbosity == 1 else logging.DEBUG
    logging.basicConfig(level=level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")


def _cmd_mine(args: argparse.Namespace) -> int:
    source = args.source
    if source in ("sgd", "all"):
        out = sgd.mine()
        print(f"[mine sgd] wrote {out}")
    if source in ("multiwoz", "all"):
        out = multiwoz.mine()
        print(f"[mine multiwoz] wrote {out}")
    return 0


def _cmd_tag(args: argparse.Namespace) -> int:
    tagged_path, unclassified_path = tagging.tag()
    print(f"[tag] tagged -> {tagged_path}")
    print(f"[tag] unclassified -> {unclassified_path}")
    return 0


def _cmd_summarize(args: argparse.Namespace) -> int:
    out = summarize.summarize()
    print(f"[summarize] wrote {out}")
    return 0


def _cmd_filter(args: argparse.Namespace) -> int:
    result = domain_filter.apply_to_phrase_bank()
    print(
        f"[filter] {result.total_before} -> {result.total_after} "
        f"(dropped {result.dropped}: {result.dropped_by_keyword} by keyword, "
        f"{result.dropped_by_source} by source)"
    )
    return 0


def _cmd_all(args: argparse.Namespace) -> int:
    args.source = "all"
    _cmd_mine(args)
    _cmd_tag(args)
    _cmd_filter(args)
    _cmd_summarize(args)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="evaluation.mining",
        description="Mine, tag, and summarise the evaluation phrase bank.",
    )
    p.add_argument("-v", "--verbose", action="count", default=1, help="-v info, -vv debug")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_mine = sub.add_parser("mine", help="Extract temporal expressions from a dataset")
    p_mine.add_argument(
        "--source",
        choices=("sgd", "multiwoz", "all"),
        default="all",
        help="Which dataset to mine (default: all)",
    )
    p_mine.set_defaults(func=_cmd_mine)

    p_tag = sub.add_parser("tag", help="Tag mined expressions by difficulty bucket")
    p_tag.set_defaults(func=_cmd_tag)

    p_sum = sub.add_parser("summarize", help="Write phrase_bank/SUMMARY.md")
    p_sum.set_defaults(func=_cmd_summarize)

    p_filter = sub.add_parser(
        "filter",
        help="Drop out-of-domain entries (restaurants, hotels, events, ...) from temporal_expressions.json",
    )
    p_filter.set_defaults(func=_cmd_filter)

    p_all = sub.add_parser("all", help="mine (all sources) -> tag -> filter -> summarize")
    p_all.set_defaults(func=_cmd_all)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _setup_logging(args.verbose)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
