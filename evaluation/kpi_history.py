"""Append-only writer for ``evaluation/reports/kpi_history.csv``.

This is the project's "track difference over time" mechanism per
EVALUATION_FRAMEWORK.md Section 7d — one row per scenario-run, tagged with
``git_commit`` + ``change_note``, so KPI deltas are attributable to specific
changes.

Ad-hoc Chainlit runs do **not** append to this file (they would pollute
trend analysis with single-conversation noise). Use ``evaluation/runs/adhoc/``
listings for those.
"""

from __future__ import annotations

import csv
import io
import logging
import os
from pathlib import Path

from evaluation.schemas import KPIHistoryRow
from evaluation.storage import reports_root

logger = logging.getLogger(__name__)


def kpi_history_path() -> Path:
    return reports_root() / "kpi_history.csv"


def ensure_kpi_history_exists() -> Path:
    """Create ``kpi_history.csv`` with its header row if it doesn't exist yet,
    or **migrate** an existing file whose header is missing columns the current
    :class:`KPIHistoryRow` schema requires (new columns are appended; old rows
    are padded with blanks for the new columns).

    Returns the path. Safe to call repeatedly.
    """
    path = kpi_history_path()
    expected_header = list(KPIHistoryRow.csv_header())

    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(expected_header)
        return path

    # File exists — check whether the header is stale (missing newer columns).
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        try:
            current_header = next(reader)
        except StopIteration:
            current_header = []
        rows = list(reader)

    if current_header == expected_header:
        return path  # already up to date

    # Migrate: pad each old row with blanks for any missing trailing columns,
    # and rewrite the file with the expected header.
    missing_cols = [c for c in expected_header if c not in current_header]
    if missing_cols:
        logger.info(
            "Migrating kpi_history.csv header: adding columns %s", missing_cols
        )
        # Map each row to a dict keyed by old header, then re-emit using the
        # expected header (missing columns become blank). Drop empty rows
        # (e.g. stray trailing newlines) defensively.
        old_dicts = []
        for row in rows:
            if not any(cell.strip() for cell in row):
                continue  # skip blank rows
            # Pad the row up to len(current_header) if it's short; extras get dropped.
            padded = row + [""] * max(0, len(current_header) - len(row))
            old_dicts.append(dict(zip(current_header, padded[: len(current_header)])))

        # Write through csv module with newline="" so DictWriter's '\r\n'
        # terminator isn't doubled by Windows text-mode translation.
        tmp = path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8", newline="") as fout:
            writer = csv.DictWriter(fout, fieldnames=expected_header)
            writer.writeheader()
            for d in old_dicts:
                writer.writerow({col: d.get(col, "") for col in expected_header})
        os.replace(tmp, path)
    return path


def append_row(row: KPIHistoryRow) -> Path:
    """Append a single :class:`KPIHistoryRow` to the history file.

    Uses ``csv``'s append mode, which is atomic enough for the single-writer
    pattern (one runner per evaluation pass). Returns the path written to.
    Ensures the header is up to date before appending.
    """
    path = ensure_kpi_history_exists()
    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row.to_csv_row())
    logger.info("Appended KPI history row for run_id=%s", row.run_id)
    return path


def update_judge_means(
    run_id: str,
    mean_temporal: float | None,
    mean_negotiation: float | None,
    mean_efficiency: float | None,
    mean_recovery: float | None,
    mean_customer_experience: float | None = None,
) -> bool:
    """Update ``judge_mean_*`` fields in kpi_history.csv for an existing run_id row.

    Performs a read-modify-write of the entire file atomically (write to ``.tmp``
    sibling, then ``os.replace``). If ``run_id`` is not found, logs a warning and
    returns ``False``. Returns ``True`` on success.

    ``mean_customer_experience`` is optional for backwards compatibility with
    callers that pre-date the §8a dimension-5 addition.

    Thread-safety: safe for the single-writer pattern (one judge process at a time).
    """
    path = kpi_history_path()
    if not path.exists():
        logger.warning(
            "update_judge_means: kpi_history.csv not found — cannot update run_id=%s",
            run_id,
        )
        return False

    # Migrate the header first if it's stale (adds missing columns to old rows).
    ensure_kpi_history_exists()

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(KPIHistoryRow.csv_header())
        rows = list(reader)

    # Strip any orphaned `None` key (DictReader leftover when a row had more
    # cells than the header had — happens if a row was appended by a newer
    # runner version before the header was migrated). Then pad missing columns.
    for row in rows:
        row.pop(None, None)
        for col in fieldnames:
            row.setdefault(col, "")

    def _fmt(v: float | None) -> str:
        return "" if v is None else str(v)

    updated = False
    for row in rows:
        if row.get("run_id") == run_id:
            row["judge_mean_temporal"] = _fmt(mean_temporal)
            row["judge_mean_negotiation"] = _fmt(mean_negotiation)
            row["judge_mean_efficiency"] = _fmt(mean_efficiency)
            row["judge_mean_recovery"] = _fmt(mean_recovery)
            if "judge_mean_customer_experience" in fieldnames:
                row["judge_mean_customer_experience"] = _fmt(mean_customer_experience)
            updated = True
            # update the LAST matching row (handles duplicates by writing to the
            # last one); do not break so all duplicates get updated

    if not updated:
        logger.warning(
            "update_judge_means: run_id=%s not found in kpi_history.csv", run_id
        )
        return False

    # Write through csv module with newline="" so DictWriter's '\r\n'
    # terminator isn't doubled by Windows text-mode translation.
    tmp = path.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as fout:
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    os.replace(tmp, path)

    logger.info("Updated judge means for run_id=%s in kpi_history.csv", run_id)
    return True


__all__ = [
    "kpi_history_path",
    "ensure_kpi_history_exists",
    "append_row",
    "update_judge_means",
]
