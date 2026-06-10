"""Deterministic executor-side availability expansion policy.

When ``check_availability`` returns an empty result, the *executor* (not the LLM)
escalates the search through a small, bounded ladder of widening windows and a
per-session availability cache — moving the windowing/retry decision out of the
agent's discretion (where the baseline showed it loops/widens unboundedly) into
deterministic code.

This module is pure orchestration logic so it can be unit-tested in isolation:

- ``AvailabilityCache`` — per-session cache keyed ``(topic, medium, date)`` → the
  day's slot list (an empty list means *known-empty*; a missing key means
  *unknown*). The executor consults it before every MCP call so a known day is
  never re-queried (directly attacks the dead-end / call-blowup metric).
- ``build_ladder`` — the deterministic widening windows (cap ``MAX_EXPANSION_STEPS``),
  clamped to the scheduling horizon and to ``now`` (no runaway, no past scans).
- ``run_expansion`` — walks the ladder, querying only **cache-miss** days
  (grouped into contiguous runs so a cached day is never re-counted), records every
  real MCP call, and stops at the first non-empty step.

Safety: the policy can never manufacture a slot the MCP server does not return
(under the eval override, ``booking_reachable=false`` / Tier-7 scenarios have an
empty override → every widened call returns ``[]`` → nothing is surfaced or booked).
Lead-time and weekend filtering are delegated to the MCP server
(``generate_available_slots``); the executor only bounds the day-range to the
horizon and uses business hours.
"""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Any

from mcp_server.config import (
    BUSINESS_HOURS_END,
    BUSINESS_HOURS_START,
    MAX_AVAILABILITY_WINDOW_DAYS,
    SCHEDULING_HORIZON_DAYS,
    TIMEZONE,
)

logger = logging.getLogger(__name__)

# The widening ladder, expressed as (start_day_offset, end_day_offset) from the
# anchor day. **Bidirectional** (2026-06-07 smoke fix): the cheap common cases first
# — anchor day (same-day near-miss, Tier 2) → near forward 3-day block (Tier 3/5
# day-shift) → near backward 3-day block — then a far forward and a far backward
# block. Backward steps rescue the case the forward-only ladder could not: the agent
# anchoring *after* the available slots (smoke `t5_en_native_014`: asked "next
# Thursday" → resolved a week late, slots sat at anchor−4/−5). Reach: anchor−6 …
# anchor+5. Blocks are clamped to [now, horizon] (past/horizon-overflow trimmed or
# dropped) and overlap is absorbed by the cache, so an empty/unreachable horizon
# makes ≤ MAX_EXPANSION_STEPS widening calls then gives up — no runaway.
LADDER_OFFSETS: tuple[tuple[int, int], ...] = ((0, 0), (0, 2), (-3, -1), (3, 5), (-6, -4))
MAX_EXPANSION_STEPS: int = 5


# ---------------------------------------------------------------------------
# Datetime / day helpers
# ---------------------------------------------------------------------------


def parse_iso(value: Any) -> datetime | None:
    """Parse an ISO 8601 string to a tz-aware datetime, or ``None`` on failure.

    Naive datetimes are assumed Europe/Zurich (the project default), matching the
    MCP server's own parsing.
    """
    if not value or not isinstance(value, str):
        return None
    try:
        dt = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TIMEZONE)
    return dt


def days_in_window(start_dt: datetime, end_dt: datetime) -> list[date]:
    """Return the list of calendar dates spanned by ``[start_dt, end_dt]`` inclusive."""
    out: list[date] = []
    d = start_dt.date()
    last = end_dt.date()
    while d <= last:
        out.append(d)
        d += timedelta(days=1)
    return out


def contiguous_runs(days: list[date]) -> list[list[date]]:
    """Group ``days`` into runs of consecutive calendar dates (sorted, de-duped).

    Used so a multi-day MCP call only ever spans cache-miss days, never re-querying
    a day already in the cache.
    """
    if not days:
        return []
    ordered = sorted(set(days))
    runs: list[list[date]] = [[ordered[0]]]
    for d in ordered[1:]:
        if (d - runs[-1][-1]).days == 1:
            runs[-1].append(d)
        else:
            runs.append([d])
    return runs


def _chunk(run: list[date], max_days: int) -> list[list[date]]:
    """Split a contiguous run into chunks of at most ``max_days`` (MCP window cap)."""
    return [run[i : i + max_days] for i in range(0, len(run), max_days)]


def _day_window(
    first: date,
    last: date,
    tz: Any,
    *,
    business_start: int = BUSINESS_HOURS_START,
    business_end: int = BUSINESS_HOURS_END,
) -> tuple[datetime, datetime]:
    """Build a business-hours ``(start, end)`` datetime window spanning two dates."""
    start = datetime(first.year, first.month, first.day, business_start, 0, tzinfo=tz)
    end = datetime(last.year, last.month, last.day, business_end, 0, tzinfo=tz)
    return start, end


# ---------------------------------------------------------------------------
# Session availability cache
# ---------------------------------------------------------------------------


class AvailabilityCache:
    """Per-session cache of ``check_availability`` results, keyed by day.

    Created once per scenario / chat session and threaded through
    ``config["configurable"]["availability_cache"]`` (infrastructure object — not
    stored in ``ConversationState``). Stores the full-day slot list per
    ``(topic_id, contact_medium_id, date)``; an empty list is *known-empty*, a
    missing key is *unknown*.
    """

    def __init__(self) -> None:
        self._store: dict[tuple[str, str, date], list[dict]] = {}

    def known(self, topic_id: str, medium_id: str, day: date) -> bool:
        """Return True if this day has already been queried (slots or known-empty)."""
        return (topic_id, medium_id, day) in self._store

    def covers(self, topic_id: str, medium_id: str, days: list[date]) -> bool:
        """Return True if every day in ``days`` is already cached."""
        return all((topic_id, medium_id, d) in self._store for d in days)

    def put_day(self, topic_id: str, medium_id: str, day: date, slots: list[dict]) -> None:
        """Cache the full slot list for a day (empty list = known-empty)."""
        self._store[(topic_id, medium_id, day)] = list(slots)

    def invalidate(self, topic_id: str, medium_id: str, day: date) -> None:
        """Drop a single day's cache entry (e.g. after a booking changes that day)."""
        self._store.pop((topic_id, medium_id, day), None)

    def slots_in_window(
        self, topic_id: str, medium_id: str, start_dt: datetime, end_dt: datetime
    ) -> list[dict]:
        """Return cached slots that fall fully within ``[start_dt, end_dt]``.

        De-duplicated by (start, end). Only consults already-cached days; unknown
        days contribute nothing.
        """
        out: list[dict] = []
        seen: set[tuple[str, str]] = set()
        for day in days_in_window(start_dt, end_dt):
            cached = self._store.get((topic_id, medium_id, day))
            if not cached:
                continue
            for slot in cached:
                s = parse_iso(slot.get("datetime_start")) if isinstance(slot, dict) else None
                e = parse_iso(slot.get("datetime_end")) if isinstance(slot, dict) else None
                if s is None or e is None:
                    continue
                if s >= start_dt and e <= end_dt:
                    key = (slot["datetime_start"], slot["datetime_end"])
                    if key not in seen:
                        seen.add(key)
                        out.append(slot)
        return out


# ---------------------------------------------------------------------------
# Ladder construction
# ---------------------------------------------------------------------------


def build_ladder(
    start_dt: datetime,
    end_dt: datetime,
    *,
    now: datetime,
    horizon_days: int = SCHEDULING_HORIZON_DAYS,
    max_window_days: int = MAX_AVAILABILITY_WINDOW_DAYS,
    max_steps: int = MAX_EXPANSION_STEPS,
    business_start: int = BUSINESS_HOURS_START,
    business_end: int = BUSINESS_HOURS_END,
) -> list[tuple[datetime, datetime]]:
    """Build the bounded, **bidirectional** widening ladder for an empty result.

    The anchor is ``max(start_dt.date(), now.date())`` so an override-bypassed past
    request cannot scan backwards forever. Each ladder block (forward and backward)
    is clamped to ``[now.date(), now.date() + horizon_days]`` — blocks that fall
    entirely in the past or beyond the horizon are dropped, partial overflow is
    trimmed — and to ``max_window_days``. Identical clamped windows are de-duplicated
    (the cache would no-op them anyway). At most ``max_steps`` blocks are considered,
    so an empty horizon makes a bounded number of calls (no runaway).
    """
    tz = now.tzinfo
    anchor = max(start_dt.date(), now.date())
    earliest = now.date()
    horizon_end = now.date() + timedelta(days=horizon_days)

    windows: list[tuple[datetime, datetime]] = []
    seen: set[tuple[date, date]] = set()
    for lo, hi in LADDER_OFFSETS[:max_steps]:
        d0 = anchor + timedelta(days=lo)
        d1 = anchor + timedelta(days=hi)
        # Clamp the block to the bookable range; drop it if nothing remains.
        if d0 < earliest:
            d0 = earliest
        if d1 > horizon_end:
            d1 = horizon_end
        if d0 > d1:
            continue
        # Enforce the MCP per-call window cap.
        if (d1 - d0).days + 1 > max_window_days:
            d1 = d0 + timedelta(days=max_window_days - 1)
        if (d0, d1) in seen:
            continue
        seen.add((d0, d1))
        windows.append(
            _day_window(d0, d1, tz, business_start=business_start, business_end=business_end)
        )
    return windows


# ---------------------------------------------------------------------------
# Ladder execution
# ---------------------------------------------------------------------------


async def run_expansion(
    *,
    bridge: Any,
    recorder: Any,
    simulate_latency: bool,
    latency_model: dict | None,
    topic_id: str,
    contact_medium_id: str,
    ladder: list[tuple[datetime, datetime]],
    cache: AvailabilityCache,
    business_start: int = BUSINESS_HOURS_START,
    business_end: int = BUSINESS_HOURS_END,
) -> tuple[list[dict], list[dict]]:
    """Walk the ladder until a step yields slots; return ``(slots, debug_steps)``.

    For each ladder window: decompose into days, serve cached days from the cache,
    and issue one ``bridge.call_tool_with_metrics`` per contiguous run of
    cache-miss days (chunked to the MCP window cap). Every real MCP call is recorded
    so the efficiency / latency cost is honest; cache hits make no call and are not
    recorded. Stops at the first window whose cached union is non-empty. An error
    response on a widening call aborts (returns no new slots) — the policy never
    fabricates.
    """
    debug_steps: list[dict] = []

    for step_idx, (w_start, w_end) in enumerate(ladder):
        days = days_in_window(w_start, w_end)
        miss = [d for d in days if not cache.known(topic_id, contact_medium_id, d)]
        mcp_calls = 0

        for run in contiguous_runs(miss):
            for chunk in _chunk(run, MAX_AVAILABILITY_WINDOW_DAYS):
                c_start, c_end = _day_window(
                    chunk[0], chunk[-1], w_start.tzinfo,
                    business_start=business_start, business_end=business_end,
                )
                args = {
                    "topic_id": topic_id,
                    "contact_medium_id": contact_medium_id,
                    "start_datetime": c_start.isoformat(),
                    "end_datetime": c_end.isoformat(),
                }
                metrics = await bridge.call_tool_with_metrics(
                    "check_availability",
                    args,
                    latency_model=latency_model,
                    simulate_latency=simulate_latency,
                )
                mcp_calls += 1
                resp = metrics["response"]
                if recorder is not None:
                    recorder.record_tool_call(
                        tool_name="check_availability",
                        parameters=args,
                        response=resp,
                        simulated_latency_ms=metrics["simulated_latency_ms"],
                        actual_latency_ms=metrics["actual_latency_ms"],
                        success=metrics["success"],
                        error_message=(
                            resp.get("message")
                            if isinstance(resp, dict) and not metrics["success"]
                            else None
                        ),
                    )
                if not metrics["success"]:
                    debug_steps.append(
                        {"step": step_idx, "mcp_calls": mcp_calls, "error": True}
                    )
                    return [], debug_steps

                # Split the response by date and cache every day in the chunk
                # (days with no returned slot are cached known-empty).
                slots_list = resp if isinstance(resp, list) else []
                by_day: dict[date, list[dict]] = {d: [] for d in chunk}
                for slot in slots_list:
                    if not isinstance(slot, dict):
                        continue
                    s = parse_iso(slot.get("datetime_start"))
                    if s is not None and s.date() in by_day:
                        by_day[s.date()].append(slot)
                for d in chunk:
                    cache.put_day(topic_id, contact_medium_id, d, by_day[d])

        found = cache.slots_in_window(topic_id, contact_medium_id, w_start, w_end)
        debug_steps.append(
            {
                "step": step_idx,
                "window": [w_start.isoformat(), w_end.isoformat()],
                "miss_days": len(miss),
                "mcp_calls": mcp_calls,
                "found": len(found),
            }
        )
        if found:
            return found, debug_steps

    return [], debug_steps
