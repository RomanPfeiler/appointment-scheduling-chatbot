"""Arm 1 — datetime parser using the ``dateparser`` library + surface heuristics.

Implements the algorithm in ``architecture/IMPROVEMENT_PLAN.md`` §7 + §7a.
The library handles relative resolution; the surface regex set derives the
``specificity`` enrichment that informs the agent's window-sizing.

Specificity is derived from the surface text, *not* from
``dateparser._result.period`` (internal, undocumented, fragile across
library versions). The regex set is transparent and testable in isolation
— each branch of the decision tree gets a unit test.

The five legal specificity values are declared in ``nlp.schemas``. This arm
emits four of them at the per-``DateRange`` level: ``exact_time``,
``day_specific``, ``day_vague``, ``multi_day_vague``. The fifth value
(``compound``) is reserved for higher-level flagging; the annotate node sets
``AnnotatedMessage.entities_raw["compound"] = True`` when this arm returns
≥2 ``DateRange`` objects from a single utterance.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import dateparser
from dateparser.search import search_dates

from nlp.datetime_parsers.resolution import (
    DATEPARSER_SETTINGS,
    HAS_ABSOLUTE_DATE as _HAS_ABSOLUTE_DATE,
    HAS_EXPLICIT_TIME as _HAS_EXPLICIT_TIME,
    HAS_MULTI_DAY as _HAS_MULTI_DAY,
    HAS_RELATIVE_DAY as _HAS_RELATIVE_DAY,
)
from nlp.datetime_parsers.windows import (
    compute_end_datetime,
    is_flexible_for,
    snap_start,
)
from nlp.schemas import DateRange, Specificity

ZURICH = ZoneInfo("Europe/Zurich")


# ─── Surface-text regex set ───────────────────────────────────────────────
# The four surface signals are the shared, arm-neutral constants in
# ``nlp.datetime_parsers.resolution`` (re-bound to the private names this arm
# has always used). They are the canonical home; the one-shot eval-data builder
# ``nlp/eval_data/_build_datetime_gold.py`` keeps its own copies to stay
# import-cycle-free, and a unit test asserts the two agree.

# Compound separator — "or"/"oder"/"ou" surrounded by whitespace.
_COMPOUND_SEP = re.compile(r"\s+(?:or|oder|ou)\s+", re.IGNORECASE)

# dateparser defaults (TIMEZONE, DMY order, future-preferring) are the shared
# ``DATEPARSER_SETTINGS`` in ``nlp.datetime_parsers.resolution`` so every arm uses
# the identical engine configuration.


def _derive_specificity(text: str) -> Specificity:
    """Apply the surface-flag decision tree from IMPROVEMENT_PLAN §7a.

    First match wins. Conservative default ``day_vague`` for ambiguous input.
    """
    has_time = bool(_HAS_EXPLICIT_TIME.search(text))
    has_multi = bool(_HAS_MULTI_DAY.search(text))
    has_rel = bool(_HAS_RELATIVE_DAY.search(text))
    has_abs = bool(_HAS_ABSOLUTE_DATE.search(text))

    if has_multi and not has_time:
        return "multi_day_vague"
    if has_time and (has_abs or has_rel):
        return "exact_time"
    if has_abs and not has_time:
        return "day_specific"
    if has_rel and not has_time:
        return "day_vague"
    return "day_vague"


def _split_compound(text: str) -> list[str]:
    """Split on "or"/"oder"/"ou". Returns ≥1 stripped non-empty candidates."""
    parts = _COMPOUND_SEP.split(text)
    return [p.strip() for p in parts if p.strip()]


class DateparserDatetimeParser:
    """Arm 1 datetime parser.

    Stateless — safe to construct once per session and reuse across turns.
    The annotate node holds a single instance via ``config["configurable"]``.

    Two-stage strategy:
      1. ``dateparser.search.search_dates(text)`` — finds date-like substrings
         in free text. Handles sentences ("Please tell me what events are
         scheduled for March 9th." → finds "March 9th") and natural compound
         expressions ("Tuesday or Thursday at 2pm" → finds both).
      2. Fallback: ``dateparser.parse(candidate)`` per "or"/"oder"/"ou"-split
         candidate. Picks up bare relative/vague phrases that ``search_dates``
         misses ("next week", "tomorrow"). Plain ``parse`` resolves these
         where ``search_dates`` returns None.
    """

    arm_name: str = "dateparser"

    def parse(self, text: str, *, now: datetime) -> list[DateRange]:
        if not text or not text.strip():
            return []

        settings: dict[str, Any] = {**DATEPARSER_SETTINGS, "RELATIVE_BASE": now}

        # ── Stage 1: search_dates over the full utterance ─────────────────
        try:
            found = search_dates(text, settings=settings)
        except Exception:
            found = None

        if found:
            ranges: list[DateRange] = []
            for matched_text, parsed_dt in found:
                rng = self._build_range(matched_text, parsed_dt)
                if rng is not None:
                    ranges.append(rng)
            if ranges:
                return ranges

        # ── Stage 2: fallback to parse() per "or"-split candidate ─────────
        ranges = []
        for candidate in _split_compound(text):
            parsed = dateparser.parse(candidate, settings=settings)
            if parsed is None:
                continue
            rng = self._build_range(candidate, parsed)
            if rng is not None:
                ranges.append(rng)
        return ranges

    def _build_range(self, matched_text: str, parsed: datetime) -> DateRange | None:
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=ZURICH)
        else:
            parsed = parsed.astimezone(ZURICH)

        spec = _derive_specificity(matched_text)
        # Window sizing is the shared specificity→window policy (windows.py),
        # so every arm sizes windows identically (IMPROVEMENT_PLAN §7a).
        start = snap_start(parsed, spec)
        end = compute_end_datetime(start, spec)
        is_flexible = is_flexible_for(spec)

        return DateRange(
            start_datetime=start,
            end_datetime=end,
            is_flexible=is_flexible,
            original_text=matched_text,
            specificity=spec,
        )
