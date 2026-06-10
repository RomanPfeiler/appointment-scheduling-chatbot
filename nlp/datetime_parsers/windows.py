"""Shared specificity→window policy for the datetime parser arms.

These helpers encode the project's window-sizing **contract** (IMPROVEMENT_PLAN
§7a) — ``exact_time`` → tight 1-hour window, day-level → that whole day,
``multi_day_vague`` → a 5-day span — **not** any classical-NLP parsing. All
datetime arms call them on their already-resolved start so every arm sizes
windows identically; that is what keeps the cross-arm comparison about
*recognition*, not window policy.

**Explicit input contract (no implicit assumptions).** Every function takes a
**timezone-aware** ``datetime`` and a ``specificity`` enum value. A naive
datetime is a programming error and is **rejected** with a clear ``ValueError``
— callers attach the timezone explicitly *before* calling. No assumption is
made that the start sits on a clean hour, nor about which arm produced it.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from nlp.schemas import Specificity

# Day-level specificities snap to midnight; the rest keep their resolved time.
_DAY_LEVEL: frozenset[str] = frozenset(
    {"day_specific", "day_vague", "multi_day_vague"}
)
# Flexible = the agent may widen the window on an empty result.
_FLEXIBLE: frozenset[str] = frozenset({"day_vague", "multi_day_vague"})


def _require_aware(dt: datetime, arg: str) -> None:
    """Reject naive datetimes explicitly — the contract demands tz-awareness."""
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        raise ValueError(
            f"{arg} must be timezone-aware; got naive {dt!r}. "
            "Attach a timezone (e.g. Europe/Zurich) before calling windows.*()."
        )


def is_flexible_for(specificity: Specificity) -> bool:
    """True iff the window is flexible (agent may expand on a miss).

    Flexible for ``day_vague`` and ``multi_day_vague`` — matches Arm 1.
    """
    return specificity in _FLEXIBLE


def snap_start(start: datetime, specificity: Specificity) -> datetime:
    """Snap the resolved start to the policy's canonical start-of-window.

    Day-level specificities (``day_specific`` / ``day_vague`` /
    ``multi_day_vague``) snap to 00:00:00 of the same day; ``exact_time`` (and
    the reserved ``compound``) keep the resolved time unchanged. The timezone is
    preserved. ``start`` must be timezone-aware.
    """
    _require_aware(start, "start")
    if specificity in _DAY_LEVEL:
        return start.replace(hour=0, minute=0, second=0, microsecond=0)
    return start


def compute_end_datetime(start: datetime, specificity: Specificity) -> datetime:
    """End datetime for the window, per IMPROVEMENT_PLAN §7a.

    - ``exact_time`` → ``start + 1 hour``.
    - ``day_specific`` / ``day_vague`` → 23:59:00 the same day.
    - ``multi_day_vague`` → ``start + 4 days`` at 23:59 (a 5-day span; assumes a
      midnight-snapped start, which :func:`snap_start` guarantees for this
      specificity).
    - reserved ``compound`` (never sized per range) → ``start + 1 hour``
      fallback.

    ``start`` must be timezone-aware; the timezone is preserved.
    """
    _require_aware(start, "start")
    if specificity == "exact_time":
        return start + timedelta(hours=1)
    if specificity in ("day_specific", "day_vague"):
        return start.replace(hour=23, minute=59, second=0, microsecond=0)
    if specificity == "multi_day_vague":
        return start + timedelta(days=4, hours=23, minutes=59)
    return start + timedelta(hours=1)
