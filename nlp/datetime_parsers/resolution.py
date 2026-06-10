"""Neutral deterministic datetime resolver — shared infrastructure for all arms.

This module holds the ``dateparser``-based **resolution** (a recognized/normalized
temporal expression → an absolute, tz-aware datetime) plus the canonical
``dateparser`` settings and the per-range ``specificity`` enum. Every datetime arm
(Arm 1 classical, Arm 2 local LLM, Arm 3 API LLM) does the **same** calendar
arithmetic through here, so the cross-arm comparison is about *recognition* — and
recognition errors (the arm) are structurally separated from resolution errors
(``dateparser``).

**Dependency rule.** Arms import from this module; this module imports nothing
arm-specific (standard library + ``dateparser`` only). No arm imports another arm's
module — the deterministic resolver is shared *infrastructure*, not an Arm-2
internal. ``windows.py`` is the sibling shared module for the *window-sizing
policy*; this module is kept separate so the pure policy helpers stay free of any
``dateparser`` dependency.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import dateparser
from dateparser.search import search_dates

ZURICH = ZoneInfo("Europe/Zurich")

# Per-``DateRange`` specificity values an arm may emit. These are four of the five
# values in ``nlp.schemas.Specificity``; the fifth (``compound``) is a
# message-level flag set by the annotate node, never a per-range value.
VALID_SPEC: frozenset[str] = frozenset(
    {"exact_time", "day_specific", "day_vague", "multi_day_vague"}
)

# ─── Surface-text specificity signals (shared across arms) ────────────────────
# Canonical home for the four surface regexes. Arm 1 imports them for its
# ``_derive_specificity`` decision tree; the LLM arms (Arm 2/3) use them in
# :func:`reconcile_exact_time` to sanity-check the model's self-reported spec.
# (The one-shot eval-data builder ``nlp/eval_data/_build_datetime_gold.py`` keeps
# its own copies to stay import-cycle-free — a unit test asserts they agree.)
HAS_EXPLICIT_TIME = re.compile(
    r"\b\d{1,2}(:\d{2})?\s*(am|pm)\b"
    r"|\b\d{1,2}:\d{2}\b"
    r"|\b\d{1,2}\s*(o'?clock|uhr|h)\b"
    r"|\b(noon|midnight|midday)\b",
    re.IGNORECASE,
)
HAS_MULTI_DAY = re.compile(
    r"\b(next|this|last|coming)\s+(week|month|fortnight)\b"
    r"|\b(soon|sometime|whenever|anytime|later|sooner)\b"
    r"|\b(within|in)\s+(a|the)\s+(week|month)\b",
    re.IGNORECASE,
)
HAS_RELATIVE_DAY = re.compile(
    r"\b(today|tomorrow|tonight|day\s+after\s+tomorrow|yesterday)\b"
    r"|\b(this|next|last|coming)\s+(mon|tues|wednes|thurs|fri|satur|sun)day\b"
    r"|\b(mon|tues|wednes|thurs|fri|satur|sun)day\b"
    r"|\bin\s+\d+\s+days?\b",
    re.IGNORECASE,
)
HAS_ABSOLUTE_DATE = re.compile(
    r"\b(january|february|march|april|may|june|july|august|september|october"
    r"|november|december|jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\b"
    r"|\b\d{1,2}[./-]\d{1,2}([./-]\d{2,4})?\b"
    r"|\b\d{1,2}(st|nd|rd|th)\b"
    r"|\b\d{4}-\d{2}-\d{2}\b",
    re.IGNORECASE,
)


def has_explicit_time(expr: str) -> bool:
    """True iff ``expr`` carries an explicit clock time (``14:00``, ``2pm``, ``noon``)."""
    return bool(HAS_EXPLICIT_TIME.search(expr))


def reconcile_exact_time(expr: str, spec: str) -> str:
    """Downgrade an LLM-claimed ``exact_time`` that has **no clock time** in the text.

    The LLM arms (Arm 2, Arm 3) self-report ``specificity``; small/zero-shot models
    over-label a bare date ("14 March") or relative day ("next Tuesday") as
    ``exact_time``. Left uncorrected, :func:`windows.compute_end_datetime` builds a
    1-hour window off the resolver's **midnight** default → an un-bookable
    00:00–01:00 slot that fails the business-hours plausibility check and empties
    ``check_availability`` → a dead-end turn (the named cause of the Arm 3 smoke
    regression). Arm 1 never hits this — it *derives* spec from this same surface
    regex — so the guard lives here and both LLM arms call it.

    Only ``exact_time`` is touched, and only when the surface text carries no clock
    token. The replacement keys off the surface form (mirrors Arm 1's decision-tree
    priority once "no time" is known): multi-day phrase → ``multi_day_vague``,
    absolute date → ``day_specific``, otherwise ``day_vague`` (conservative,
    flexible). Every other spec passes through unchanged.
    """
    if spec != "exact_time" or has_explicit_time(expr):
        return spec
    if HAS_MULTI_DAY.search(expr):
        return "multi_day_vague"
    if HAS_ABSOLUTE_DATE.search(expr):
        return "day_specific"
    return "day_vague"

# Resolution languages: the LLM arms normalize calques, but a literal localized
# token may slip through — give ``dateparser`` the Swiss variants to fall back on.
RESOLVE_LANGUAGES: list[str] = ["en", "de", "fr", "it"]

# ``dateparser`` defaults applied to every parse/resolve call (Swiss expectations).
# This is the canonical copy; Arm 1 imports it for its own two-stage strategy.
DATEPARSER_SETTINGS: dict[str, Any] = {
    "TIMEZONE": "Europe/Zurich",
    "RETURN_AS_TIMEZONE_AWARE": True,
    "DATE_ORDER": "DMY",  # Swiss expectation: 14.03 → 14 March
    "PREFER_DATES_FROM": "future",
}


def resolve_expression(expr: str, *, now: datetime) -> datetime | None:
    """Resolve a (normalized) temporal expression to a tz-aware Europe/Zurich datetime.

    ``search_dates`` runs first (it handles relative weekday phrases like
    "next Tuesday" that bare ``parse`` returns ``None`` for), then ``parse`` as a
    fallback — both with :data:`DATEPARSER_SETTINGS` and ``now`` as
    ``RELATIVE_BASE``, so the calendar arithmetic is identical across arms. The
    relative base is passed **explicitly** (eval anchor intrinsically; scenario
    ``reference_date`` in the runner) — never the wall clock.

    Returns ``None`` when neither stage can resolve the expression — a *resolution*
    failure, which the caller logs distinctly from a *recognition* failure.
    """
    settings = {**DATEPARSER_SETTINGS, "RELATIVE_BASE": now}
    resolved: datetime | None = None
    try:
        found = search_dates(expr, settings=settings, languages=RESOLVE_LANGUAGES)
    except Exception:
        found = None
    if found:
        resolved = found[0][1]  # first match's datetime (expr is a single phrase)
    if resolved is None:
        try:
            resolved = dateparser.parse(
                expr, settings=settings, languages=RESOLVE_LANGUAGES
            )
        except Exception:
            resolved = None
    if resolved is None:
        return None
    if resolved.tzinfo is None:
        return resolved.replace(tzinfo=ZURICH)
    return resolved.astimezone(ZURICH)
