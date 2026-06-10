"""Paths, atomic writes, directory scaffolding for evaluation artifacts.

Responsibilities:
- Resolve paths under ``evaluation/runs/<stage>/<run_id>/`` and the ad-hoc
  variant under ``evaluation/runs/adhoc/<run_id>/``.
- Build a ``run_id`` from a timestamp + stage + short git commit.
- Provide atomic JSON writes so a crash during write never leaves a
  half-written record on disk.
- Capture git_commit / git_dirty for provenance.

Layout (matches EVALUATION_FRAMEWORK.md Section 7c + adds ``runs/adhoc/``):

    evaluation/runs/<stage>/<run_id>/
        manifest.json
        records/<scenario_id>__rep<k>.json
        transcripts/<scenario_id>__rep<k>.md
        judge/<scenario_id>__rep<k>.json
        metrics/summary.json
        metrics/summary.md
    evaluation/runs/adhoc/<run_id>/
        manifest.json
        records/conversation.json
        transcripts/conversation.md
"""

from __future__ import annotations

import json
import logging
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from evaluation.schemas import ConversationRecord, RunManifest

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Project root + base paths
# ---------------------------------------------------------------------------


def project_root() -> Path:
    """Return the project root (parent of the ``evaluation/`` package)."""
    return Path(__file__).resolve().parent.parent


def evaluation_root() -> Path:
    """Return the ``evaluation/`` directory."""
    return project_root() / "evaluation"


def runs_root() -> Path:
    """Return ``evaluation/runs/``."""
    return evaluation_root() / "runs"


def reports_root() -> Path:
    """Return ``evaluation/reports/``."""
    return evaluation_root() / "reports"


# ---------------------------------------------------------------------------
# Run-id construction
# ---------------------------------------------------------------------------


def now_utc() -> datetime:
    """Single source of truth for timestamps written into records."""
    return datetime.now(timezone.utc)


def timestamp_for_id(dt: datetime | None = None) -> str:
    """Format a datetime as ``YYYYMMDD_HHMMSS`` for use in directory names."""
    dt = dt or now_utc()
    return dt.strftime("%Y%m%d_%H%M%S")


def short_commit(commit: str) -> str:
    return commit[:7] if commit else "nogit"


def build_run_id(
    stage: str,
    commit: str | None = None,
    extra: str | None = None,
    timestamp: datetime | None = None,
) -> str:
    """Build a run_id of shape ``<YYYYMMDD_HHMMSS>__<stage>__<commit>[__<extra>]``.

    ``extra`` is used by ad-hoc runs to embed a short session identifier so
    parallel sessions don't collide on the same second.
    """
    commit = commit or get_git_commit()
    parts = [timestamp_for_id(timestamp), stage, short_commit(commit)]
    if extra:
        parts.append(extra)
    return "__".join(parts)


# ---------------------------------------------------------------------------
# Git provenance
# ---------------------------------------------------------------------------


def get_git_commit() -> str:
    """Return the current ``HEAD`` short-ish commit, or ``"nogit"`` if unavailable.

    Resilient — never raises. Used for provenance only.
    """
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root(),
            capture_output=True,
            text=True,
            check=False,
            timeout=2,
        )
        if result.returncode == 0:
            return result.stdout.strip() or "nogit"
    except Exception as exc:  # pragma: no cover — defensive
        logger.debug("get_git_commit failed: %s", exc)
    return "nogit"


def get_git_dirty() -> bool:
    """Return True if the working tree has uncommitted changes."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_root(),
            capture_output=True,
            text=True,
            check=False,
            timeout=2,
        )
        if result.returncode == 0:
            return bool(result.stdout.strip())
    except Exception as exc:  # pragma: no cover
        logger.debug("get_git_dirty failed: %s", exc)
    return False


# ---------------------------------------------------------------------------
# Run-directory paths
# ---------------------------------------------------------------------------


class RunPaths:
    """Resolved filesystem paths for one run.

    Use :meth:`ensure_dirs` once at run start; thereafter the path properties
    are safe to write to.
    """

    def __init__(self, run_id: str, stage: str) -> None:
        self.run_id = run_id
        self.stage = stage
        if stage == "adhoc":
            self.run_dir = runs_root() / "adhoc" / run_id
        else:
            self.run_dir = runs_root() / stage / run_id

    # --- Top-level files ---
    @property
    def manifest(self) -> Path:
        return self.run_dir / "manifest.json"

    # --- Subdirectories ---
    @property
    def records_dir(self) -> Path:
        return self.run_dir / "records"

    @property
    def transcripts_dir(self) -> Path:
        return self.run_dir / "transcripts"

    @property
    def judge_dir(self) -> Path:
        return self.run_dir / "judge"

    @property
    def metrics_dir(self) -> Path:
        return self.run_dir / "metrics"

    # --- Per-scenario file helpers ---
    def record_path(self, scenario_id: str, rep: int = 1) -> Path:
        return self.records_dir / f"{scenario_id}__rep{rep}.json"

    def transcript_path(self, scenario_id: str, rep: int = 1) -> Path:
        return self.transcripts_dir / f"{scenario_id}__rep{rep}.md"

    def judge_path(self, scenario_id: str, rep: int = 1) -> Path:
        return self.judge_dir / f"{scenario_id}__rep{rep}.json"

    # --- Ad-hoc helpers (single record per run) ---
    @property
    def adhoc_record(self) -> Path:
        return self.records_dir / "conversation.json"

    @property
    def adhoc_transcript(self) -> Path:
        return self.transcripts_dir / "conversation.md"

    # --- Directory setup ---
    def ensure_dirs(self) -> None:
        for d in (self.records_dir, self.transcripts_dir, self.judge_dir, self.metrics_dir):
            d.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Atomic writes
# ---------------------------------------------------------------------------


def atomic_write_text(path: Path, content: str, encoding: str = "utf-8") -> None:
    """Write ``content`` to ``path`` atomically.

    Writes to a sibling ``<name>.tmp`` then ``os.replace`` swaps it in.
    Prevents readers from seeing a partially-written file if the process
    crashes mid-write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding=encoding)
    os.replace(tmp, path)


def write_json(path: Path, payload: dict | list) -> None:
    """Write JSON atomically with stable, human-readable formatting."""
    atomic_write_text(path, json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n")


def write_manifest(paths: RunPaths, manifest: RunManifest) -> None:
    """Serialise + atomically write the manifest for a run."""
    write_json(paths.manifest, manifest.model_dump(mode="json"))


def write_record(paths: RunPaths, record: ConversationRecord, scenario_id: str | None = None, rep: int = 1) -> Path:
    """Write a ConversationRecord to disk and return the path.

    For ad-hoc runs (``stage == "adhoc"``) the file is always
    ``records/conversation.json``. For scenario runs the filename derives from
    ``scenario_id`` + ``rep``.
    """
    paths.ensure_dirs()
    if paths.stage == "adhoc":
        out = paths.adhoc_record
    else:
        sid = scenario_id or record.scenario_id
        out = paths.record_path(sid, rep)
    write_json(out, record.model_dump(mode="json"))
    return out


def write_transcript(paths: RunPaths, transcript: str, scenario_id: str | None = None, rep: int = 1) -> Path:
    """Write a rendered markdown transcript to disk and return the path."""
    paths.ensure_dirs()
    if paths.stage == "adhoc":
        out = paths.adhoc_transcript
    else:
        sid = scenario_id or "conversation"
        out = paths.transcript_path(sid, rep)
    atomic_write_text(out, transcript)
    return out


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_record(path: Path) -> ConversationRecord:
    """Load + validate a JSON record."""
    return ConversationRecord.model_validate_json(path.read_text(encoding="utf-8"))


def load_manifest(path: Path) -> RunManifest:
    """Load + validate a manifest."""
    return RunManifest.model_validate_json(path.read_text(encoding="utf-8"))


def list_adhoc_runs(limit: int | None = None) -> list[Path]:
    """Return ad-hoc run directories, newest first.

    Returns at most ``limit`` paths; pass ``None`` for unbounded.
    """
    base = runs_root() / "adhoc"
    if not base.exists():
        return []
    dirs = sorted((p for p in base.iterdir() if p.is_dir()), reverse=True)
    if limit is not None:
        dirs = dirs[:limit]
    return dirs


__all__ = [
    "project_root",
    "evaluation_root",
    "runs_root",
    "reports_root",
    "now_utc",
    "timestamp_for_id",
    "short_commit",
    "build_run_id",
    "get_git_commit",
    "get_git_dirty",
    "RunPaths",
    "atomic_write_text",
    "write_json",
    "write_manifest",
    "write_record",
    "write_transcript",
    "load_record",
    "load_manifest",
    "list_adhoc_runs",
]
