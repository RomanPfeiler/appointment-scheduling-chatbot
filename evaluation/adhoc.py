"""Always-on ad-hoc Chainlit recording — manual sessions produce records too.

Why always-on:
- Manual chat sessions are the user's primary tool for poking at the agent
  during development; having an inspectable JSON record + markdown transcript
  on disk makes after-the-fact analysis trivial.
- Cost is negligible (one ConversationRecorder per session, no extra LLM
  calls), and the layout matches what the runner will produce — so analysis
  tools written here transfer to scenario runs.

The Chainlit integration is split out so ``app.py`` only sees three small
function calls. A CLI (``python -m evaluation.adhoc list|gc``) is provided
for inspecting + cleaning up runs.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Iterable

from evaluation.recorder import ConversationRecorder
from evaluation.schemas import RunConfig, RunManifest
from evaluation.storage import (
    RunPaths,
    build_run_id,
    get_git_commit,
    get_git_dirty,
    list_adhoc_runs,
    load_manifest,
    load_record,
    now_utc,
    write_manifest,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Chainlit integration helpers
# ---------------------------------------------------------------------------


def make_session_recorder(
    *,
    session_id: str,
    provider: str,
    model: str,
    temperature: float,
    max_tokens: int | None = None,
    change_note: str | None = None,
) -> ConversationRecorder:
    """Build a ConversationRecorder for one Chainlit chat session.

    Writes the manifest immediately with ``status='in_progress'`` so the
    artifact exists even if the session crashes before the first turn.
    """
    short_session = (session_id or "anon").replace("-", "")[:8] or "anon"
    config = RunConfig(
        llm_provider=provider,
        llm_model=model,
        llm_temperature=temperature,
        llm_max_tokens=max_tokens,
    )
    run_id = build_run_id(stage="adhoc", extra=short_session)
    paths = RunPaths(run_id=run_id, stage="adhoc")
    paths.ensure_dirs()

    manifest = RunManifest(
        run_id=run_id,
        stage="adhoc",
        timestamp_start=now_utc(),
        git_commit=get_git_commit(),
        git_dirty=get_git_dirty(),
        change_note=change_note,
        config=config,
        scenario_count=1,
        rep_count=1,
    )
    write_manifest(paths, manifest)

    recorder = ConversationRecorder(
        scenario_id="adhoc",
        tier="adhoc",
        stage="adhoc",
        persona_profile="adhoc",
        run_index=1,
        run_id=run_id,
        paths=paths,
        config=config,
        change_note=change_note,
        manifest=manifest,
    )
    logger.info("Ad-hoc recorder created for session %s → %s", short_session, paths.run_dir)
    return recorder


# ---------------------------------------------------------------------------
# CLI: list / gc
# ---------------------------------------------------------------------------


def _format_table(rows: Iterable[list[str]], headers: list[str]) -> str:
    rows_list = [headers, *rows]
    widths = [max(len(r[c]) for r in rows_list) for c in range(len(headers))]
    out: list[str] = []
    for i, row in enumerate(rows_list):
        out.append("  ".join(cell.ljust(widths[c]) for c, cell in enumerate(row)))
        if i == 0:
            out.append("  ".join("-" * w for w in widths))
    return "\n".join(out)


def cmd_list(args: argparse.Namespace) -> int:
    """Print the N most recent ad-hoc runs as a table."""
    runs = list_adhoc_runs(limit=args.limit)
    if not runs:
        print("No ad-hoc runs found under evaluation/runs/adhoc/.")
        return 0

    rows: list[list[str]] = []
    for run_dir in runs:
        manifest_path = run_dir / "manifest.json"
        record_path = run_dir / "records" / "conversation.json"
        status = "?"
        turns = "?"
        booked = "?"
        if manifest_path.exists():
            try:
                manifest = load_manifest(manifest_path)
                status = manifest.status
            except Exception as exc:
                status = f"err:{exc.__class__.__name__}"
        if record_path.exists():
            try:
                record = load_record(record_path)
                turns = str(len(record.turns))
                if record.derived is not None:
                    booked = "yes" if record.derived.booked else "no"
            except Exception as exc:
                turns = f"err:{exc.__class__.__name__}"
        rows.append([run_dir.name, status, turns, booked])

    print(_format_table(rows, ["run_id", "status", "turns", "booked"]))
    return 0


def cmd_gc(args: argparse.Namespace) -> int:
    """Mark stale ``in_progress`` ad-hoc manifests as ``crashed``.

    Lets the user see at a glance which sessions never finalized cleanly
    (Chainlit crashes, browser closes that didn't fire on_chat_end, etc.).
    Does NOT delete any data — the records and transcripts stay where they
    were written.
    """
    runs = list_adhoc_runs()
    touched = 0
    for run_dir in runs:
        manifest_path = run_dir / "manifest.json"
        if not manifest_path.exists():
            continue
        try:
            manifest = load_manifest(manifest_path)
        except Exception as exc:
            print(f"skip (parse error): {run_dir.name}  ({exc})")
            continue
        if manifest.status == "in_progress":
            manifest.status = "crashed"
            paths = RunPaths(run_id=manifest.run_id, stage="adhoc")
            # Use load → modify → write to keep the manifest file format consistent.
            write_manifest(paths, manifest)
            touched += 1
            print(f"marked crashed: {run_dir.name}")
    print(f"Done. {touched} manifest(s) marked crashed.")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    """Print the markdown transcript of a specific run to stdout."""
    run_dir = Path(args.run_id)
    if not run_dir.is_absolute():
        # Resolve relative to adhoc/ for convenience.
        from evaluation.storage import runs_root

        candidate = runs_root() / "adhoc" / args.run_id
        if candidate.exists():
            run_dir = candidate
    transcript_path = run_dir / "transcripts" / "conversation.md"
    if not transcript_path.exists():
        print(f"No transcript found at {transcript_path}", file=sys.stderr)
        return 1
    print(transcript_path.read_text(encoding="utf-8"))
    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.adhoc",
        description="Inspect and maintain ad-hoc Chainlit conversation records.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="List recent ad-hoc runs.")
    p_list.add_argument("--limit", type=int, default=10)
    p_list.set_defaults(func=cmd_list)

    p_gc = sub.add_parser("gc", help="Mark stale in_progress manifests as crashed.")
    p_gc.set_defaults(func=cmd_gc)

    p_show = sub.add_parser("show", help="Print a run's markdown transcript.")
    p_show.add_argument("run_id", help="Run id (or absolute path to the run dir).")
    p_show.set_defaults(func=cmd_show)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())


__all__ = ["make_session_recorder", "main"]
