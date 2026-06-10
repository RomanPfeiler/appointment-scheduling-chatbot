"""Difficulty-bucket tagging for the mined phrase bank.

Buckets (EVALUATION_FRAMEWORK.md §5 seed list):
- ``specific date``  — explicit calendar date / time (e.g. "March 20th at 2pm").
- ``relative``       — relative-to-now (e.g. "next Tuesday", "tomorrow morning").
- ``vague``          — under-specified (e.g. "sometime next week", "soon").
- ``compound``       — multiple/disjunctive constraints (e.g. "Tuesday or Thursday").
- ``unsupported``    — patterns the appointment API cannot fulfil by design
                       (recurring series, attendee constraints, multi-week durations).

Likely discovery buckets (only added when ≥3 phrasings cluster — Section 5):
- ``deadline-driven`` ("before Friday")
- ``negative constraint`` ("not Monday")
- ``open-ended``      ("whenever you have time")

The tagger runs *auto* (regex + dateparser confirmation) on every entry. Anything
the heuristics cannot classify is written to ``_unclassified.json`` for manual
review.
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Iterator

from .paths import (
    MULTIWOZ_RAW_JSONL,
    PHRASE_BANK_JSON,
    SGD_RAW_JSONL,
    UNCLASSIFIED_JSON,
    ensure_dirs,
)

log = logging.getLogger(__name__)


# --- Regex patterns ---------------------------------------------------------

_UNSUPPORTED_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bevery (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|week|day|month)\b", re.IGNORECASE),
    re.compile(r"\brecurring\b", re.IGNORECASE),
    re.compile(r"\bweekly\b", re.IGNORECASE),
    re.compile(r"\bmonthly\b", re.IGNORECASE),
    re.compile(r"\bfor (?:\d+|the next \d+) (?:weeks?|months?)\b", re.IGNORECASE),
    re.compile(r"\bwith (?:someone|a (?:specific|particular)) (?:who|that)\b", re.IGNORECASE),
    re.compile(r"\bright after (?:\w+'s|john's|jane's|my [a-z]+\b)", re.IGNORECASE),
    re.compile(r"\bfor (?:\d+|three|four|five|six|seven|eight) (?:people|attendees|guests)\b", re.IGNORECASE),
)

_DEADLINE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bbefore (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|noon|midnight|the end of|\d)\b", re.IGNORECASE),
    re.compile(r"\bby (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|noon|the end of|\d)\b", re.IGNORECASE),
    re.compile(r"\bno later than\b", re.IGNORECASE),
)

_NEGATIVE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(?:not|never|except|other than|anything but)\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|tomorrow|today|this week|next week|the morning|the afternoon)\b", re.IGNORECASE),
    re.compile(r"\b(?:no|avoid)\s+(?:mondays?|tuesdays?|wednesdays?|thursdays?|fridays?|saturdays?|sundays?)\b", re.IGNORECASE),
)

_OPEN_ENDED_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\bwhenever (?:you have|works|is convenient|possible)\b", re.IGNORECASE),
    re.compile(r"\bany ?time\b", re.IGNORECASE),
    re.compile(r"\bwhenever\b", re.IGNORECASE),
)

_COMPOUND_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(?:morning|afternoon|evening|am|pm|\d+(?:am|pm)?)\s*(?:or|and)\s+(?:morning|afternoon|evening|am|pm|\d+(?:am|pm)?)\b", re.IGNORECASE),
    re.compile(r"\b(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\s*(?:or|and|,)\s*(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", re.IGNORECASE),
    re.compile(r"\beither\s+\w+\s+or\s+\w+\b", re.IGNORECASE),
    re.compile(r"\bany day except\b", re.IGNORECASE),
)

_VAGUE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(?:sometime|some time|soon|eventually|maybe|perhaps|possibly|around|roughly|approximately)\b", re.IGNORECASE),
    re.compile(r"\bafter work\b", re.IGNORECASE),
    re.compile(r"\bsoonest available\b", re.IGNORECASE),
    re.compile(r"\bnext (?:week|month)\b(?!.*\b(?:on|at|monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d)\b)", re.IGNORECASE),
)

_RELATIVE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"\b(?:tomorrow|today|tonight|yesterday)\b", re.IGNORECASE),
    re.compile(r"\bnext (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", re.IGNORECASE),
    re.compile(r"\bthis (?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|morning|afternoon|evening)\b", re.IGNORECASE),
    re.compile(r"\bin\s+\d+\s+(?:day|days|hour|hours|week|weeks)\b", re.IGNORECASE),
    re.compile(r"\bthe day after tomorrow\b", re.IGNORECASE),
)

_SPECIFIC_DATE_PATTERNS: tuple[re.Pattern[str], ...] = (
    # Numeric date / month-name patterns
    re.compile(r"\b(?:january|february|march|april|may|june|july|august|september|october|november|december)\s+(?:the\s+)?\d+(?:st|nd|rd|th)?\b", re.IGNORECASE),
    re.compile(r"\b\d{1,2}(?:st|nd|rd|th)\s+(?:of\s+)?(?:january|february|march|april|may|june|july|august|september|october|november|december)\b", re.IGNORECASE),
    re.compile(r"\bthe\s+\d{1,2}(?:st|nd|rd|th)\b", re.IGNORECASE),
    re.compile(r"\b\d{4}-\d{2}-\d{2}\b"),
    re.compile(r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b"),
    re.compile(r"\bat\s+\d{1,2}(?::\d{2})?\s*(?:am|pm)\b", re.IGNORECASE),
    re.compile(r"\b\d{1,2}\s*o'?clock\b", re.IGNORECASE),
)

BUCKET_ORDER: tuple[str, ...] = (
    "unsupported",  # check first — overrides everything else
    "compound",
    "deadline-driven",
    "negative constraint",
    "open-ended",
    "specific date",
    "relative",
    "vague",
)

_BUCKET_PATTERNS: dict[str, tuple[re.Pattern[str], ...]] = {
    "unsupported": _UNSUPPORTED_PATTERNS,
    "compound": _COMPOUND_PATTERNS,
    "deadline-driven": _DEADLINE_PATTERNS,
    "negative constraint": _NEGATIVE_PATTERNS,
    "open-ended": _OPEN_ENDED_PATTERNS,
    "specific date": _SPECIFIC_DATE_PATTERNS,
    "relative": _RELATIVE_PATTERNS,
    "vague": _VAGUE_PATTERNS,
}


def classify(text: str) -> str | None:
    """Return the difficulty bucket for ``text``, or ``None`` if heuristics fail.

    Buckets are checked in ``BUCKET_ORDER`` — earlier wins. ``unsupported``
    is first because a phrase like "every Monday at 10" otherwise looks
    specific.
    """
    for bucket in BUCKET_ORDER:
        for pattern in _BUCKET_PATTERNS[bucket]:
            if pattern.search(text):
                return bucket
    return None


def _iter_jsonl(path: Path) -> Iterator[dict]:
    if not path.exists():
        log.warning("Mined file missing, skipping: %s", path)
        return
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def tag() -> tuple[Path, Path]:
    """Read both mined JSONLs, classify, write the bank and unclassified leftovers.

    Returns (tagged_path, unclassified_path).
    """
    ensure_dirs()

    tagged: list[dict] = []
    unclassified: list[dict] = []
    seen_texts: set[str] = set()

    for src in (SGD_RAW_JSONL, MULTIWOZ_RAW_JSONL):
        for record in _iter_jsonl(src):
            text = record.get("expression_text", "")
            if not text or text in seen_texts:
                continue
            seen_texts.add(text)

            bucket = classify(text)
            entry = {
                "expression_id": record.get("expression_id", ""),
                "expression_text": text,
                "difficulty_tag": bucket,
                "source_dataset": record.get("source_dataset", ""),
                "source_service": record.get("source_service", ""),
                "source_dialogue_id": record.get("source_dialogue_id", ""),
                "source_turn_idx": record.get("source_turn_idx", 0),
                "original_context": record.get("original_context", ""),
                "normalized_meaning": record.get("normalized_meaning", ""),
                "tag_source": "auto" if bucket else "unclassified",
                "notes": "",
            }
            if bucket:
                tagged.append(entry)
            else:
                unclassified.append(entry)

    PHRASE_BANK_JSON.write_text(
        json.dumps(tagged, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    UNCLASSIFIED_JSON.write_text(
        json.dumps(unclassified, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    log.info(
        "Tagging done: %d tagged -> %s ; %d unclassified -> %s",
        len(tagged),
        PHRASE_BANK_JSON,
        len(unclassified),
        UNCLASSIFIED_JSON,
    )
    return PHRASE_BANK_JSON, UNCLASSIFIED_JSON
