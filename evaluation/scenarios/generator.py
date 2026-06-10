"""Scenario generator — templates × phrase bank × topic/medium × language_variant.

Produces ~500 scenarios across 7 tiers (EVALUATION_FRAMEWORK.md §3, §12). The
output is the canonical `Scenario` JSON list per tier, written to the paths in
`paths.TIER_OUTPUT_FILES`.

Templates live as code in this module because override construction is mildly
procedural (offset arithmetic, slot-window math). Re-running with the same
`--seed` is fully deterministic.
"""

from __future__ import annotations

import json
import logging
import random
import re
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import dateparser
import dateparser.search

from evaluation.schemas import (
    REFERENCE_DATE,
    AvailabilityOverride,
    ExpectedDateTimeWindow,
    LanguageVariant,
    PersonaProfile,
    Scenario,
    Tier,
)

from .paths import (
    BANKING_UNSUPPORTED_JSON,
    PHRASE_BANK_JSON,
    REFERENCE_DATA_JSON,
    SCENARIOS_DIR,
    SWISS_VARIANTS_JSON,
    TIER_OUTPUT_FILES,
)

log = logging.getLogger(__name__)

# Suite-wide scenario clock as a ``datetime`` for dateparser's ``RELATIVE_BASE``.
# Derived from the canonical ``REFERENCE_DATE`` (a Monday) so the generation-time
# anchor and the per-scenario ``reference_date`` stamped onto each Scenario are
# the *same* date — this is what makes the fixture-alignment invariant a no-op on
# the generated suite and prevents the date-drift bug (EVALUATION_FRAMEWORK §3a).
REFERENCE_DATETIME = datetime(
    REFERENCE_DATE.year, REFERENCE_DATE.month, REFERENCE_DATE.day
)


# ---------------------------------------------------------------------------
# Phrase bank loading + sampling
# ---------------------------------------------------------------------------


def _load_bank(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Phrase bank missing: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


@dataclass(slots=True)
class PhraseBanks:
    native: list[dict]
    swiss: list[dict]
    # Hand-curated banking-specific out-of-scope phrasings used for Tier 7.
    # Schema matches `temporal_expressions.json` plus `language_variant`.
    banking_unsupported: list[dict] = field(default_factory=list)

    @classmethod
    def load(cls) -> "PhraseBanks":
        banking = _load_bank(BANKING_UNSUPPORTED_JSON) if BANKING_UNSUPPORTED_JSON.exists() else []
        return cls(
            native=_load_bank(PHRASE_BANK_JSON),
            swiss=_load_bank(SWISS_VARIANTS_JSON),
            banking_unsupported=banking,
        )

    def sample(
        self,
        rng: random.Random,
        buckets: tuple[str, ...],
        variant: LanguageVariant,
    ) -> dict:
        """Sample one phrase matching the buckets + variant.

        ``en_native`` draws from the mined bank (no language_variant field —
        all entries are treated as native). The Swiss variants draw from the
        addendum filtered by ``language_variant``. Falls back to native if the
        Swiss filter yields nothing (small sample sizes can run out).

        For the ``unsupported`` bucket the banking-specific addendum
        (`banking_unsupported.json`) is preferred when present — it ensures
        Tier 7 phrases are actually about banking, not restaurant/hotel/event
        domains the mined bank inherited from SGD/MultiWOZ.
        """
        if buckets == ("unsupported",) and self.banking_unsupported:
            # Preferred source for Tier 7 — in-domain by construction.
            if variant == "en_native":
                pool = [e for e in self.banking_unsupported
                        if e.get("language_variant", "en_native") == "en_native"]
            else:
                pool = [e for e in self.banking_unsupported
                        if e.get("language_variant") == variant]
                if not pool:
                    pool = [e for e in self.banking_unsupported
                            if e.get("language_variant", "en_native") == "en_native"]
            if pool:
                return rng.choice(pool)

        if variant == "en_native":
            pool = [e for e in self.native if e.get("difficulty_tag") in buckets]
        else:
            pool = [
                e
                for e in self.swiss
                if e.get("difficulty_tag") in buckets
                and e.get("language_variant") == variant
            ]
            if not pool:
                # Fall back to native if the requested Swiss bucket × variant
                # combination is empty (the addendum is small by design).
                pool = [e for e in self.native if e.get("difficulty_tag") in buckets]
        if not pool:
            raise RuntimeError(
                f"No phrasings available for buckets={buckets} variant={variant}. "
                "Bank may need refreshing or buckets are too narrow."
            )
        return rng.choice(pool)


# ---------------------------------------------------------------------------
# Reference data (topics + media)
# ---------------------------------------------------------------------------


def _load_topic_medium_pairs() -> list[tuple[str, str]]:
    """Return all valid (topic_id, contact_medium_id) combinations."""
    data = json.loads(REFERENCE_DATA_JSON.read_text(encoding="utf-8"))
    pairs: list[tuple[str, str]] = []
    for topic in data["topics"]:
        tid = topic["topic_id"]
        for medium in data["contact_media"].get(tid, []):
            pairs.append((tid, medium["contact_medium_id"]))
    return pairs


# ---------------------------------------------------------------------------
# Override builders (one per override "shape")
# ---------------------------------------------------------------------------


_DEFAULT_DAY_SLOTS = ("09:00-10:00", "10:00-11:00", "11:00-12:00",
                      "14:00-15:00", "15:00-16:00", "16:00-17:00")


def _hours_in_range(start_h: int, end_h: int) -> tuple[str, ...]:
    """Generate 1-hour slot strings between ``start_h`` and ``end_h``."""
    return tuple(f"{h:02d}:00-{h + 1:02d}:00" for h in range(start_h, end_h))


def _override_direct_match(
    rng: random.Random, ctx: dict[str, Any]
) -> AvailabilityOverride:
    """Tier 1: requested slot AVAILABLE + 2-3 others same day."""
    day = ctx["primary_offset"]
    preferred_slot = ctx["preferred_slot"]
    other_slots = rng.sample(
        [s for s in _DEFAULT_DAY_SLOTS if s != preferred_slot], k=rng.randint(2, 3)
    )
    return AvailabilityOverride(
        slots_by_offset={day: [preferred_slot] + other_slots},
        notes="Tier 1 — preferred slot available + same-day alternatives",
    )


def _override_near_miss(
    rng: random.Random, ctx: dict[str, Any]
) -> AvailabilityOverride:
    """Tier 2: requested slot NOT available, 2-3 alternatives same day."""
    day = ctx["primary_offset"]
    preferred_slot = ctx["preferred_slot"]
    other_slots = rng.sample(
        [s for s in _DEFAULT_DAY_SLOTS if s != preferred_slot], k=rng.randint(2, 3)
    )
    return AvailabilityOverride(
        slots_by_offset={day: other_slots},
        notes="Tier 2 — preferred slot busy; same-day alternatives exist",
    )


def _override_day_shift(
    rng: random.Random, ctx: dict[str, Any]
) -> AvailabilityOverride:
    """Tier 3: requested day FULL, +1/+2 days have slots."""
    day = ctx["primary_offset"]
    base_n = int(day.removeprefix("today+"))
    next_day = f"today+{base_n + 1}"
    after_next = f"today+{base_n + 2}"
    return AvailabilityOverride(
        slots_by_offset={
            next_day: list(rng.sample(_DEFAULT_DAY_SLOTS, k=3)),
            after_next: list(rng.sample(_DEFAULT_DAY_SLOTS, k=2)),
        },
        notes="Tier 3 — primary day fully booked; alternatives on +1/+2",
    )


def _override_broad_window(
    rng: random.Random, ctx: dict[str, Any]
) -> AvailabilityOverride:
    """Tier 4: scattered availability across a 4-7 day window."""
    base_n = int(ctx["primary_offset"].removeprefix("today+"))
    window_days = rng.randint(4, 7)
    slots: dict[str, list[str]] = {}
    for d in range(base_n, base_n + window_days):
        # Roughly half the days get 1-2 slots
        if rng.random() < 0.5:
            slots[f"today+{d}"] = list(
                rng.sample(_DEFAULT_DAY_SLOTS, k=rng.randint(1, 2))
            )
    if not slots:
        # Guarantee at least one slot so the scenario isn't accidentally unreachable
        slots[f"today+{base_n + 1}"] = [rng.choice(_DEFAULT_DAY_SLOTS)]
    return AvailabilityOverride(
        slots_by_offset=slots,
        notes="Tier 4 — scattered availability in a broad window",
    )


def _override_multi_round(
    rng: random.Random, ctx: dict[str, Any]
) -> AvailabilityOverride:
    """Tier 5: initial preference unavailable; second preference available."""
    day = ctx["primary_offset"]
    base_n = int(day.removeprefix("today+"))
    second_day = f"today+{base_n + 2}"
    return AvailabilityOverride(
        slots_by_offset={
            day: [],  # explicitly empty (no preferred slot)
            second_day: list(rng.sample(_DEFAULT_DAY_SLOTS, k=2)),
            f"today+{base_n + 3}": list(rng.sample(_DEFAULT_DAY_SLOTS, k=2)),
        },
        notes="Tier 5 — primary day busy; alternatives later for negotiation",
    )


def _override_tier6(
    rng: random.Random, ctx: dict[str, Any]
) -> AvailabilityOverride:
    """Tier 6: varies by sub-template. Provide moderate scattered availability."""
    base_n = int(ctx["primary_offset"].removeprefix("today+"))
    slots: dict[str, list[str]] = {}
    for d in range(base_n, base_n + 5):
        if rng.random() < 0.6:
            slots[f"today+{d}"] = list(
                rng.sample(_DEFAULT_DAY_SLOTS, k=rng.randint(1, 3))
            )
    return AvailabilityOverride(
        slots_by_offset=slots,
        notes="Tier 6 — moderate scattered availability for deadline/negative/open-ended phrasings",
    )


def _override_unreachable(
    rng: random.Random, ctx: dict[str, Any]
) -> AvailabilityOverride:
    """`booking_reachable=False`: empty override (nothing available)."""
    return AvailabilityOverride(
        slots_by_offset={},
        notes="Unreachable — no availability in the requested horizon",
    )


def _override_tier7(
    rng: random.Random, ctx: dict[str, Any]
) -> AvailabilityOverride:
    """Tier 7: API can't fulfil the request shape; availability irrelevant."""
    return AvailabilityOverride(
        slots_by_offset={},
        notes="Tier 7 — out-of-scope; correct response is polite refusal",
    )


# ---------------------------------------------------------------------------
# Tier templates
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class TierTemplate:
    tier: Tier
    description: str
    persona: PersonaProfile
    phrasing_buckets: tuple[str, ...]
    optimal_calls: int
    expected_turns: tuple[int, int]
    build_override: Callable[[random.Random, dict[str, Any]], AvailabilityOverride]


TIER_TEMPLATES: dict[int, TierTemplate] = {
    1: TierTemplate(
        tier=1,
        description="Direct match — requested time IS available; book without negotiation.",
        persona="cooperative",
        phrasing_buckets=("relative",),
        optimal_calls=1,
        expected_turns=(4, 5),
        build_override=_override_direct_match,
    ),
    2: TierTemplate(
        tier=2,
        description="Near miss — requested day has availability but not at the requested time.",
        persona="cooperative",
        phrasing_buckets=("relative",),
        optimal_calls=1,
        expected_turns=(5, 7),
        build_override=_override_near_miss,
    ),
    3: TierTemplate(
        tier=3,
        description="Day shift — requested day fully booked; agent must suggest other days.",
        persona="negotiating",
        phrasing_buckets=("relative",),
        optimal_calls=2,
        expected_turns=(6, 8),
        build_override=_override_day_shift,
    ),
    4: TierTemplate(
        tier=4,
        description="Broad window — wide/vague window; agent decides how to chunk options.",
        persona="negotiating",
        phrasing_buckets=("vague", "compound"),
        optimal_calls=2,
        expected_turns=(5, 8),
        build_override=_override_broad_window,
    ),
    5: TierTemplate(
        tier=5,
        description="Multi-round negotiation — first suggestion rejected; user changes preference.",
        persona="adversarial",
        phrasing_buckets=("relative",),
        optimal_calls=3,
        expected_turns=(7, 10),
        build_override=_override_multi_round,
    ),
    6: TierTemplate(
        tier=6,
        description="Other — deadline-driven / negative-constraint / open-ended shapes.",
        persona="negotiating",
        phrasing_buckets=("deadline-driven", "negative constraint", "open-ended"),
        optimal_calls=2,
        expected_turns=(5, 9),
        build_override=_override_tier6,
    ),
    7: TierTemplate(
        tier=7,
        description="Out-of-scope — request cannot be fulfilled; correct behaviour is a polite refusal.",
        persona="edge",
        phrasing_buckets=("unsupported",),
        optimal_calls=0,
        expected_turns=(2, 5),
        build_override=_override_tier7,
    ),
}


# ---------------------------------------------------------------------------
# Tier-quota + language-mix configuration
# ---------------------------------------------------------------------------


@dataclass(slots=True)
class TierQuota:
    tier: Tier
    count: int
    unreachable_count: int     # subset of `count` with booking_reachable=False
    lang_mix: dict[LanguageVariant, int]  # absolute counts that sum to `count`


# Distribution matches the plan §B2 table.
TIER_QUOTAS: tuple[TierQuota, ...] = (
    TierQuota(1, 80, 8, {"en_native": 50, "en_de": 16, "en_fr": 9, "en_it": 5}),
    TierQuota(2, 80, 8, {"en_native": 50, "en_de": 16, "en_fr": 9, "en_it": 5}),
    TierQuota(3, 80, 8, {"en_native": 50, "en_de": 16, "en_fr": 9, "en_it": 5}),
    TierQuota(4, 80, 8, {"en_native": 50, "en_de": 16, "en_fr": 9, "en_it": 5}),
    TierQuota(5, 80, 8, {"en_native": 50, "en_de": 16, "en_fr": 9, "en_it": 5}),
    TierQuota(6, 60, 0, {"en_native": 40, "en_de": 12, "en_fr": 5, "en_it": 3}),
    TierQuota(7, 40, 40, {"en_native": 25, "en_de": 8, "en_fr": 4, "en_it": 3}),
)


# ---------------------------------------------------------------------------
# Preferred-slot heuristics + simulator-goal composition
# ---------------------------------------------------------------------------


def _sample_primary_offset(rng: random.Random) -> str:
    """Sample a relative-date offset within the scheduling horizon (today+1..today+14).

    Avoid today+0 (lead-time issues) and stay well within
    ``SCHEDULING_HORIZON_DAYS=21`` so the runner always finds the slot.
    """
    return f"today+{rng.randint(1, 14)}"


def _sample_preferred_slot(rng: random.Random) -> str:
    """Sample a preferred slot string from the default day-grid."""
    return rng.choice(_DEFAULT_DAY_SLOTS)


def _quantize_hour_to_slot(hour: int, minute: int) -> str:
    """Quantize an (hour, minute) to one of the standard 1-hour slot windows.

    Business hours are 08:00-17:00 (`mcp_server/config.py`). If the parsed time
    falls outside, we clip to the nearest in-range slot. The standard slot
    grid is `_DEFAULT_DAY_SLOTS` (1-hour windows at 9, 10, 11, 14, 15, 16).
    """
    # Round to the nearest hour (>=:30 rounds up)
    h = hour + (1 if minute >= 30 else 0)
    # Clip to business hours 9-16 (the start hours in _DEFAULT_DAY_SLOTS)
    valid_starts = (9, 10, 11, 14, 15, 16)
    nearest = min(valid_starts, key=lambda v: abs(v - h))
    return f"{nearest:02d}:00-{nearest + 1:02d}:00"


_DATEPARSER_SETTINGS = {
    "PREFER_DATES_FROM": "future",
    "RETURN_AS_TIMEZONE_AWARE": False,
}


# Swiss-variant "next week <weekday>" calques (en_de/fr/it: "next week Tuesday",
# "the Tuesday of next week") are mis-handled by dateparser/search_dates: it
# either drops the weekday and returns the start of next week (today+7 = the
# Monday) or returns None → a random fallback offset. Either way the override
# lands on a day the agent (which reads the calque correctly) never queries.
# This deterministic resolver runs BEFORE dateparser so generation AND the
# fixture-alignment invariant share one correct reading. (Native "next week
# <weekday>" phrasings are `vague`-tagged → Tier 4, a non-alignment tier, so
# they never reach this path.) Added 2026-06-06.
_WEEKDAYS: dict[str, int] = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}
_NEXT_WEEK_RE = re.compile(r"next\s+week", re.IGNORECASE)


def _extract_hour(text: str) -> tuple[int, int] | None:
    """Best-effort (hour, minute) from a calque time expression, else None.

    Handles "2pm" / "2:30 pm", "14 o'clock", "15h", "at 14", "14:00".
    """
    t = text.lower()
    m = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", t)
    if m:
        hour = int(m.group(1)) % 12 + (12 if m.group(3) == "pm" else 0)
        return hour, int(m.group(2) or 0)
    m = re.search(r"\b(\d{1,2})\s*(?:o['’]?clock|h\b|:00\b)", t)
    if m:
        return int(m.group(1)), 0
    m = re.search(r"\bat\s+(\d{1,2})\b", t)
    if m:
        return int(m.group(1)), 0
    return None


def _resolve_next_week_weekday(
    phrasing: str, rng_now: datetime
) -> tuple[str, str] | None:
    """Resolve "next week <weekday>" calques → (offset, slot), else None.

    "Next week <weekday>" means the <weekday> of the week AFTER ``rng_now``'s
    week (weeks start Monday). With ``rng_now`` = Monday 2026-06-01, "next week
    Tuesday" = 2026-06-09 = today+8 (NOT today+7, the Monday dateparser returns).
    Returns None when the phrasing is not a next-week-weekday calque so callers
    fall through to the existing dateparser path.
    """
    t = phrasing.lower()
    if not _NEXT_WEEK_RE.search(t):
        return None
    weekday = next(
        (idx for name, idx in _WEEKDAYS.items() if re.search(rf"\b{name}\b", t)),
        None,
    )
    if weekday is None:
        return None
    # Start of next week = the Monday strictly after rng_now's week.
    days_to_next_monday = 7 - rng_now.weekday()
    target = rng_now.date() + timedelta(days=days_to_next_monday + weekday)
    days_ahead = (target - rng_now.date()).days
    if not 1 <= days_ahead <= 14:
        return None
    hm = _extract_hour(phrasing)
    slot = _quantize_hour_to_slot(*hm) if hm is not None else "09:00-10:00"
    return f"today+{days_ahead}", slot


def _parse_phrasing_alignment(
    phrasing: str, rng_now: datetime
) -> tuple[str, str] | None:
    """Parse phrasing → (offset, slot). Returns None when parse is unreliable.

    Tries two strategies in order:
    1. Direct ``dateparser.parse(phrasing)`` — works on short, clean phrasings.
    2. ``dateparser.search.search_dates(phrasing)`` — extracts the temporal
       substring from a conversational sentence. SGD/MultiWOZ phrasings are
       often full conversational turns ("I would like to go this Sunday")
       where the temporal expression is embedded; the search variant handles
       these better than direct parsing.

    Used by tiers where the simulator's verbal request must align with the
    `expected_datetime_window` for parse-accuracy KPI to be meaningful
    (Tiers 1, 2, 3, 5 — EVALUATION_FRAMEWORK.md §4f).
    """
    # Handle "next week <weekday>" calques first — dateparser mis-reads them.
    calque = _resolve_next_week_weekday(phrasing, rng_now)
    if calque is not None:
        return calque

    settings = {**_DATEPARSER_SETTINGS, "RELATIVE_BASE": rng_now}

    parsed: datetime | None = None
    try:
        parsed = dateparser.parse(phrasing, settings=settings)
    except Exception:  # noqa: BLE001
        parsed = None

    if parsed is None:
        try:
            hits = dateparser.search.search_dates(phrasing, settings=settings) or []
        except Exception:  # noqa: BLE001
            hits = []
        # Pick the first hit whose resolved date is in [rng_now+1, rng_now+14]
        for _matched_text, dt in hits:
            if dt is None:
                continue
            ahead = (dt.date() - rng_now.date()).days
            if 1 <= ahead <= 14:
                parsed = dt
                break

    if parsed is None:
        return None
    days_ahead = (parsed.date() - rng_now.date()).days
    if days_ahead < 1 or days_ahead > 14:
        return None
    slot = _quantize_hour_to_slot(parsed.hour, parsed.minute)
    return f"today+{days_ahead}", slot


# Tiers where strict phrasing↔window alignment matters most. Other tiers
# tolerate looser alignment per §3c "calibrate against first baseline run".
_ALIGNMENT_TIERS: frozenset[int] = frozenset({1, 2, 3, 5})

# Tiers where alignment MUST succeed (otherwise the simulator's frozen
# phrasing will contradict the scenario's `expected_datetime_window` and the
# scenario's tier contract is violated — see plan §4 "Tier 1 misalignment").
# For Tier 1 ("Direct Match") the contract is "requested time IS available";
# if the phrasing's date/time can't be parsed, the scenario CANNOT honor that
# contract, so we re-sample the phrasing instead of falling back to a random
# slot. (Tiers 2/3/5 still tolerate loose alignment per §3c.)
_STRICT_ALIGNMENT_TIERS: frozenset[int] = frozenset({1})
_PHRASING_ALIGNMENT_MAX_RETRIES: int = 25


def _natural_window(preferred_slot: str) -> str:
    """Turn '14:00-15:00' into a human-readable hint ('around 2pm')."""
    start = preferred_slot.split("-", 1)[0]
    hour = int(start.split(":", 1)[0])
    if hour < 12:
        return f"around {hour}am"
    if hour == 12:
        return "around noon"
    return f"around {hour - 12}pm"


def _expected_window(offset: str, preferred_slot: str) -> ExpectedDateTimeWindow:
    """The window the agent's *first* check_availability should target."""
    start_hm = preferred_slot.split("-", 1)[0]
    end_hm = preferred_slot.split("-", 1)[1]
    return ExpectedDateTimeWindow(
        start_offset=f"{offset}T{start_hm}",
        end_offset=f"{offset}T{end_hm}",
    )


def _topic_label(topic_id: str) -> str:
    return {"investing": "investing", "mortgage": "mortgage", "pension": "pension"}.get(
        topic_id, topic_id
    )


def _medium_label(medium_id: str) -> str:
    return {
        "branch": "an in-branch meeting",
        "online": "an online meeting",
        "phone": "a phone meeting",
    }.get(medium_id, medium_id)


def _compose_goal(
    tier: int,
    topic_id: str,
    medium_id: str,
    preferred_slot: str | None,
    primary_offset: str | None,
    booking_reachable: bool,
) -> str:
    """Compose the simulator's goal string.

    The phrasing is pinned separately (``frozen_phrasing``). The goal tells
    the simulator *what to do* — book a topic via a medium, with a preferred
    time. For Tier 7 / unreachable scenarios, the goal also encodes the
    correct termination condition.
    """
    topic = _topic_label(topic_id)
    medium = _medium_label(medium_id)

    if tier == 7:
        return (
            f"You want a {topic} appointment that the system cannot fulfil by design. "
            "Use the pinned phrasing verbatim. When the agent politely declines and "
            "explains the limitation, accept the refusal — that is success."
        )

    if not booking_reachable:
        return (
            f"You want to book {medium} about {topic}. Use the pinned phrasing "
            "verbatim for your first time request. If the agent reports no "
            "availability in the requested horizon, accept that honestly — "
            "do NOT pressure for a fabricated booking."
        )

    when_hint = _natural_window(preferred_slot) if preferred_slot else "unspecified"
    return (
        f"You want to book {medium} about {topic}. Your preferred time is {when_hint} "
        f"on offset {primary_offset}. Use the pinned phrasing verbatim for your first "
        "time request. Confirm and book when a matching slot is offered."
    )


# ---------------------------------------------------------------------------
# Per-tier expansion
# ---------------------------------------------------------------------------


def _generate_tier(
    quota: TierQuota,
    banks: PhraseBanks,
    pairs: list[tuple[str, str]],
    rng: random.Random,
) -> list[Scenario]:
    """Generate ``quota.count`` scenarios for one tier."""
    tmpl = TIER_TEMPLATES[quota.tier]
    scenarios: list[Scenario] = []
    # Fixed "now" for the whole tier so dateparser's relative resolution is
    # deterministic per-seed. This is the suite-wide reference clock; every
    # generated scenario also carries it as ``reference_date`` so the runner
    # resolves the override and the phrasing against the *same* date (§3a).
    rng_now = REFERENCE_DATETIME

    # Build a flat list of language variants matching the absolute counts in
    # quota.lang_mix, then shuffle so per-scenario variant assignment is mixed.
    lang_pool: list[LanguageVariant] = []
    for variant, n in quota.lang_mix.items():
        lang_pool.extend([variant] * n)
    if len(lang_pool) != quota.count:
        raise ValueError(
            f"Tier {quota.tier} language mix sums to {len(lang_pool)} but count={quota.count}"
        )
    rng.shuffle(lang_pool)

    # Choose which indices are unreachable.
    unreachable_idxs = (
        set(rng.sample(range(quota.count), k=quota.unreachable_count))
        if quota.unreachable_count > 0
        else set()
    )

    for i in range(quota.count):
        variant = lang_pool[i]
        topic_id, medium_id = rng.choice(pairs)

        is_unreachable = (i in unreachable_idxs) or quota.tier == 7

        # Tier 7 doesn't need primary offset / preferred slot
        if quota.tier == 7:
            phrase = banks.sample(rng, tmpl.phrasing_buckets, variant)
            primary_offset = None
            preferred_slot = None
            expected_window = None
            override = tmpl.build_override(rng, {})
            phrasing_alignment_source = "n/a"
        else:
            # Sample phrasing — for strict-alignment tiers (Tier 1) we retry
            # up to N times to find a phrase the parser can align, so the
            # override actually contains the requested slot.
            phrase, aligned, phrasing_alignment_source = _sample_with_alignment(
                rng=rng,
                banks=banks,
                buckets=tmpl.phrasing_buckets,
                variant=variant,
                rng_now=rng_now,
                tier=quota.tier,
            )

            if aligned is not None:
                primary_offset, preferred_slot = aligned
            else:
                primary_offset = _sample_primary_offset(rng)
                preferred_slot = _sample_preferred_slot(rng)

            ctx = {"primary_offset": primary_offset, "preferred_slot": preferred_slot}
            if is_unreachable:
                override = _override_unreachable(rng, ctx)
            else:
                override = tmpl.build_override(rng, ctx)
            expected_window = _expected_window(primary_offset, preferred_slot)

        booking_reachable = not is_unreachable

        scenario = Scenario(
            scenario_id=f"t{quota.tier}_{variant}_{i:03d}",
            tier=quota.tier,
            description=tmpl.description,
            topic_id=topic_id,
            contact_medium_id=medium_id,
            availability_override=override,
            reference_date=REFERENCE_DATE,
            simulator_goal=_compose_goal(
                quota.tier, topic_id, medium_id, preferred_slot, primary_offset, booking_reachable
            ),
            persona_profile=tmpl.persona,
            frozen_phrasing=phrase["expression_text"],
            language_variant=variant,
            expected_datetime_window=expected_window,
            optimal_availability_calls=tmpl.optimal_calls,
            expected_turn_range=tmpl.expected_turns,
            booking_reachable=booking_reachable,
            notes=(
                f"phrasing source: {phrase.get('source_dataset')}/"
                f"{phrase.get('source_service')} "
                f"({phrase.get('difficulty_tag')}); "
                f"alignment: {phrasing_alignment_source}"
            ),
        )

        # Invariant check — fail loudly during generation rather than producing
        # a scenario the runner cannot honor. See `evaluation/scenarios/validate.py`
        # for the post-write replay.
        _assert_scenario_invariants(scenario)

        scenarios.append(scenario)

    return scenarios


def _sample_with_alignment(
    *,
    rng: random.Random,
    banks: PhraseBanks,
    buckets: tuple[str, ...],
    variant: LanguageVariant,
    rng_now: datetime,
    tier: int,
) -> tuple[dict, tuple[str, str] | None, str]:
    """Sample a phrase and (optionally) align it to a (offset, slot).

    For tiers in `_STRICT_ALIGNMENT_TIERS` (Tier 1), retries up to
    `_PHRASING_ALIGNMENT_MAX_RETRIES` times to find a phrase whose temporal
    expression parses cleanly. If no alignable phrase is found in N tries,
    raises RuntimeError — that's a signal the phrase bank has too few
    parseable entries for the bucket.

    For other tiers in `_ALIGNMENT_TIERS`, performs alignment best-effort and
    falls back to random when parsing fails (preserving the old behaviour).

    Returns: ``(phrase_dict, aligned_or_None, source_label)`` where source_label
    is one of ``"parsed"``, ``"parsed_after_retry"``, ``"random"``.
    """
    strict = tier in _STRICT_ALIGNMENT_TIERS
    do_alignment = tier in _ALIGNMENT_TIERS

    if not do_alignment:
        return banks.sample(rng, buckets, variant), None, "random"

    last_phrase: dict | None = None
    for attempt in range(_PHRASING_ALIGNMENT_MAX_RETRIES if strict else 1):
        phrase = banks.sample(rng, buckets, variant)
        last_phrase = phrase
        aligned = _parse_phrasing_alignment(phrase["expression_text"], rng_now)
        if aligned is not None:
            label = "parsed" if attempt == 0 else "parsed_after_retry"
            return phrase, aligned, label

    if strict:
        raise RuntimeError(
            f"Tier {tier}: could not find an alignable phrase in {_PHRASING_ALIGNMENT_MAX_RETRIES} "
            f"attempts for buckets={buckets}, variant={variant}. The phrase bank may "
            "have too few parseable entries — check `evaluation/phrase_bank/` and "
            "the cleanup filter."
        )

    return last_phrase or banks.sample(rng, buckets, variant), None, "random"


def _offset_day(offset_str: str) -> int | None:
    """Extract ``N`` from a ``today+N`` or ``today+NTHH:MM`` offset string.

    Returns ``None`` when the string is not in the ``today+N`` shape (e.g. a
    literal ISO date), so callers can skip rather than fail.
    """
    prefix = "today+"
    if not offset_str.startswith(prefix):
        return None
    day_part = offset_str[len(prefix):].split("T", 1)[0]
    try:
        return int(day_part)
    except ValueError:
        return None


def _assert_fixture_alignment(scenario: Scenario) -> None:
    """Fixture-alignment invariant (EVALUATION_FRAMEWORK §3a).

    For the alignment tiers (1/2/3/5), the day the frozen phrasing resolves to —
    parsed against the scenario's own ``reference_date`` — must equal the day the
    ``expected_datetime_window`` targets. This is the assertion that would have
    caught the date-drift bug (``t1_en_native_031``): when the availability-override
    offsets and the weekday phrasing resolve against *different* clocks they land
    on different days. Pinning both to ``reference_date`` makes them agree, and this
    check enforces that agreement at generation time and on every committed JSON.

    Because the generator picks the offset with the *same* parser and the *same*
    anchor (``REFERENCE_DATETIME``), this is a no-op on the generated suite — it
    only fires on a hand-misaligned fixture or a generator regression where the
    stamped ``reference_date`` diverges from the anchor used to pick the offset.

    Skip rules (the invariant does not apply / cannot assert):
    - Non-alignment tiers (4/6/7) — no single resolvable requested day.
    - No ``expected_datetime_window`` (Tier 7 / unreachable).
    - The phrasing does not parse to a concrete relative day (vague/compound or a
      random-fallback phrasing) — there is no single day to align against.

    Raises:
        ValueError if the parsed phrasing day disagrees with the expected window.
    """
    if scenario.tier not in _ALIGNMENT_TIERS:
        return
    win = scenario.expected_datetime_window
    if win is None:
        return
    ref = scenario.reference_date
    ref_dt = datetime(ref.year, ref.month, ref.day)
    aligned = _parse_phrasing_alignment(scenario.frozen_phrasing, ref_dt)
    if aligned is None:
        return  # phrasing is not a concrete relative day — nothing to assert
    parsed_day = _offset_day(aligned[0])
    expected_day = _offset_day(win.start_offset)
    if parsed_day is None or expected_day is None:
        return
    if parsed_day != expected_day:
        raise ValueError(
            f"{scenario.scenario_id}: fixture-alignment invariant violated — "
            f"frozen_phrasing {scenario.frozen_phrasing!r} resolves to today+{parsed_day} "
            f"against reference_date {ref.isoformat()} ({ref.strftime('%A')}), but "
            f"expected_datetime_window targets today+{expected_day}. The weekday "
            "phrasing and the availability-override offsets would drift apart at run "
            "time. (Pin reference_date so both resolve against one clock — §3a.)"
        )


def _assert_scenario_invariants(scenario: Scenario) -> None:
    """Enforce per-tier contracts on a freshly generated scenario.

    Currently checks:
    - Tier 1 (Direct Match) with ``booking_reachable=True``: the
      `expected_datetime_window`'s slot is present in
      `availability_override.slots_by_offset[primary_offset]`. Otherwise
      the "requested time IS available" contract is violated and the
      scenario will (mis)test something else.
    - Tier 1 with ``booking_reachable=False``: the contract is inverted —
      the override is intentionally empty so the agent must honestly report
      "nothing available". No slot-presence check applies.
    - Fixture-alignment (all alignment tiers): the phrasing-resolved day and the
      expected-window day agree given ``reference_date`` (see
      ``_assert_fixture_alignment``).

    Raises:
        ValueError if any invariant is violated.
    """
    _assert_fixture_alignment(scenario)

    if scenario.tier == 1 and scenario.booking_reachable:
        win = scenario.expected_datetime_window
        if win is None:
            raise ValueError(
                f"{scenario.scenario_id}: Tier 1 requires an expected_datetime_window."
            )
        # start_offset / end_offset have shape "today+NTHH:MM"
        try:
            primary_offset = win.start_offset.split("T", 1)[0]
            start_hm = win.start_offset.split("T", 1)[1]
            end_hm = win.end_offset.split("T", 1)[1]
        except (IndexError, ValueError) as exc:
            raise ValueError(
                f"{scenario.scenario_id}: malformed expected_datetime_window: {win!r}"
            ) from exc
        expected_slot = f"{start_hm}-{end_hm}"
        day_slots = scenario.availability_override.slots_by_offset.get(primary_offset, [])
        if expected_slot not in day_slots:
            raise ValueError(
                f"{scenario.scenario_id}: Tier 1 invariant violated — expected slot "
                f"{expected_slot!r} on {primary_offset} not present in override "
                f"{day_slots!r}. (The 'requested time IS available' contract requires "
                "the parsed/aligned slot to be in the override.)"
            )


def generate_all(seed: int = 1234) -> dict[int, list[Scenario]]:
    """Generate the full suite. Returns a dict keyed by tier."""
    rng = random.Random(seed)
    banks = PhraseBanks.load()
    pairs = _load_topic_medium_pairs()

    out: dict[int, list[Scenario]] = {}
    for quota in TIER_QUOTAS:
        out[quota.tier] = _generate_tier(quota, banks, pairs, rng)
        log.info("Tier %d: generated %d scenarios", quota.tier, len(out[quota.tier]))
    return out


def write_all(seed: int = 1234) -> dict[int, Path]:
    """Generate + write the suite to disk. Returns paths keyed by tier."""
    suite = generate_all(seed=seed)
    SCENARIOS_DIR.mkdir(parents=True, exist_ok=True)
    written: dict[int, Path] = {}
    for tier, scenarios in suite.items():
        out_path = SCENARIOS_DIR / TIER_OUTPUT_FILES[tier]
        # mode="json" renders date -> ISO string (reference_date) and tuple ->
        # list, so the output is directly JSON-serializable.
        out_path.write_text(
            json.dumps(
                [s.model_dump(mode="json") for s in scenarios],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        written[tier] = out_path
        log.info("Wrote %d scenarios -> %s", len(scenarios), out_path)
    return written
