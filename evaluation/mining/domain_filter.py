"""Out-of-domain phrase filter for the mined phrase bank.

The SGD / MultiWOZ corpora are out-of-domain by default (restaurants, hotels,
events, travel, weather, calendar). Even after the difficulty tagger sorts
entries by date/time difficulty, many phrases reference nouns that don't
belong in a Swiss-bank appointment-booking conversation:

  "I am feeling really bored. Is there any Blues event in Phoenix next Wednesday?"
  "Please book me a table for 4 at Mayflower Seafood Restaurant on Friday."
  "Add an event titled Reservation for 5 people."

When such phrases are glued verbatim into the simulator's first message, the
simulator typically apologizes for the phrasing ("I used an odd phrase") and
substitutes an in-scope request — contaminating the evaluation. See plan §3
and `project_presentation/progress/learnings.md` (2026-05-25).

This module provides a keyword / source filter applied to the already-tagged
`temporal_expressions.json`. The filter is idempotent and writes a backup
`_pre_filter.json` once on first run so the original mined bank stays
recoverable.

Usage::

    python -m evaluation.mining.cli filter
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path

from .paths import BUCKET_LOG_MD, PHRASE_BANK_DIR, PHRASE_BANK_JSON

log = logging.getLogger(__name__)


# Out-of-domain keywords (case-insensitive, word-boundary anchored). Any phrase
# whose text matches one of these is dropped from the appointment-scheduling
# bank. Curated from the entries observed leaking into the first baseline run.
_OUT_OF_DOMAIN_KEYWORDS: tuple[str, ...] = (
    # Food / restaurants
    "restaurant", "restaurants", "dinner", "lunch", "breakfast", "brunch",
    "table for", "reservation for", "reserve a table", "seafood",
    "menu", "cuisine", "chef", "diner", "café", "cafe",
    # Hotels / travel
    "hotel", "hotels", "nights", "checkin", "check in", "check-in",
    "checkout", "check out", "check-out", "flight", "flights", "airline",
    "train ticket", "bus ticket", "taxi", "uber", "rental car",
    "boarding pass",
    # Events / entertainment / media
    "concert", "blues event", "rock event", "jazz event", "music event",
    "festival", "ticket to", "tickets to", "movie", "movies", "film",
    "cinema", "theater", "theatre", "show times", "showtime",
    "performance", "event in",
    # Weather / news / search
    "weather forecast", "weather in", "news in",
    # Calendar add-event syntax leaking from SGD `Calendar_1`
    "add an event", "add event", "create event", "event titled",
    "titled reservation", "titled meeting with",
    # Unrelated services
    "haircut", "salon", "spa", "massage", "dentist", "doctor's office",
    "babysitter",
    # Movie-search / "I'm bored" template
    "i am feeling bored", "i'm feeling bored", "feeling really bored",
    "find me a", "find one for me",
    # Multi-attendee phrasings that aren't already in `unsupported`
    "for 4 people", "for 5 people", "for 6 people", "for two people",
    "for three people",
)

# Source services known to be out-of-domain in SGD. Matching is case-sensitive
# substring on `source_service` (e.g. `"Restaurants_1"`, `"Hotels_3"`).
_OUT_OF_DOMAIN_SOURCE_SERVICES: tuple[str, ...] = (
    "Restaurants_", "Hotels_", "Travel_", "Buses_", "Flights_", "Trains_",
    "Events_", "Media_", "Movies_", "Music_", "Weather_", "RentalCars_",
    "RideSharing_", "Homes_", "RealEstate_",
)


@dataclass(slots=True)
class FilterResult:
    """Outcome of one filter pass."""

    total_before: int
    total_after: int
    dropped: int
    dropped_by_keyword: int
    dropped_by_source: int
    examples: list[str]  # up to 10 example texts that were dropped


def _matches_keyword(text: str) -> str | None:
    """Return the matching keyword if `text` contains one, else None."""
    lowered = text.lower()
    for kw in _OUT_OF_DOMAIN_KEYWORDS:
        # Use word-boundary regex for multi-word keywords too — \b on either
        # end works for ASCII-letter keywords, and avoids matching e.g.
        # "restaurant" inside "restaurantowner" but still catches "restaurants".
        if re.search(rf"\b{re.escape(kw)}\b", lowered):
            return kw
    return None


def _matches_source(source_service: str | None) -> str | None:
    if not source_service:
        return None
    for prefix in _OUT_OF_DOMAIN_SOURCE_SERVICES:
        if source_service.startswith(prefix):
            return prefix
    return None


def filter_entries(entries: list[dict]) -> tuple[list[dict], FilterResult]:
    """Apply the out-of-domain filter to a list of phrase-bank entries.

    Pure function — does not touch disk. Returns ``(kept_entries, FilterResult)``.
    """
    kept: list[dict] = []
    dropped_kw = 0
    dropped_src = 0
    examples: list[str] = []

    for entry in entries:
        text = str(entry.get("expression_text", ""))
        source = entry.get("source_service")

        kw = _matches_keyword(text)
        src = _matches_source(source)

        if kw is None and src is None:
            kept.append(entry)
            continue

        if kw is not None:
            dropped_kw += 1
        else:
            dropped_src += 1
        if len(examples) < 10:
            reason = f"keyword={kw!r}" if kw else f"source={src!r}"
            examples.append(f"[{reason}] {text!r}")

    total_before = len(entries)
    total_after = len(kept)
    return kept, FilterResult(
        total_before=total_before,
        total_after=total_after,
        dropped=total_before - total_after,
        dropped_by_keyword=dropped_kw,
        dropped_by_source=dropped_src,
        examples=examples,
    )


def apply_to_phrase_bank(
    *,
    bank_path: Path = PHRASE_BANK_JSON,
    bucket_log_path: Path = BUCKET_LOG_MD,
    backup_suffix: str = "_pre_filter.json",
) -> FilterResult:
    """Filter the on-disk phrase bank in place, creating a one-time backup.

    1. Reads ``bank_path``.
    2. If a backup (``<bank>_pre_filter.json``) does not exist yet, writes the
       current contents to that path before filtering (so this is recoverable).
    3. Applies :func:`filter_entries` and writes the filtered list back to
       ``bank_path``.
    4. Appends an entry to ``bucket_log_path`` describing the filter pass.
    """
    if not bank_path.exists():
        raise FileNotFoundError(f"Phrase bank missing: {bank_path}")

    entries = json.loads(bank_path.read_text(encoding="utf-8"))
    backup_path = bank_path.with_name(bank_path.stem + backup_suffix)
    if not backup_path.exists():
        backup_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2),
                               encoding="utf-8")
        log.info("Wrote one-time backup -> %s", backup_path)

    kept, result = filter_entries(entries)
    bank_path.write_text(json.dumps(kept, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    log.info(
        "Filter complete: %d -> %d (dropped %d; %d by keyword, %d by source)",
        result.total_before, result.total_after,
        result.dropped, result.dropped_by_keyword, result.dropped_by_source,
    )

    _append_bucket_log(bucket_log_path, result)
    return result


def _append_bucket_log(path: Path, result: FilterResult) -> None:
    """Append a domain-filter entry to bucket_log.md (creates the file if needed)."""
    from datetime import date
    PHRASE_BANK_DIR.mkdir(parents=True, exist_ok=True)
    header_needed = not path.exists()
    today = date.today().isoformat()
    lines: list[str] = []
    if header_needed:
        lines.append("# Phrase-bank bucket log\n")
        lines.append(
            "Append-only log of structural changes to the phrase bank "
            "(new buckets, filter passes, source additions). See "
            "EVALUATION_FRAMEWORK.md §5.\n\n"
        )
    lines.append(f"## {today} — out-of-domain filter pass\n\n")
    lines.append(
        f"- Entries before: {result.total_before}\n"
        f"- Entries after: {result.total_after}\n"
        f"- Dropped: {result.dropped} "
        f"({result.dropped_by_keyword} by keyword, {result.dropped_by_source} by source service)\n"
        f"- Example drops:\n"
    )
    for ex in result.examples:
        lines.append(f"  - {ex}\n")
    lines.append("\n")

    with path.open("a", encoding="utf-8") as f:
        f.writelines(lines)


__all__ = [
    "FilterResult",
    "apply_to_phrase_bank",
    "filter_entries",
]
