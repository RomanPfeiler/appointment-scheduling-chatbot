"""Unit tests for the executor-side window-expansion policy.

Covers the three components and their safety guards:
- ``build_ladder`` — escalation shape, horizon clamp, past-anchor clamp, cap N (no runaway).
- ``AvailabilityCache`` — round-trip, known-empty vs unknown, per-key invalidation.
- ``run_expansion`` — adjacent-slot surfacing, cache prevents re-query, empty horizon
  fabricates nothing, error aborts.
- ``execute_node`` — flag-off byte-identical path, error never triggers the ladder, booking
  invalidates the booked day, an empty narrow window widens to nearby slots.
- ``stage_to_flags("expansion")`` wiring.

All tests use a deterministic fake bridge (no real MCP), so the flag-off equality check is a
genuine code-path equality, not a behavioural approximation.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from mcp_server.config import (
    BUSINESS_HOURS_END,
    BUSINESS_HOURS_START,
    MAX_AVAILABILITY_WINDOW_DAYS,
    SCHEDULING_HORIZON_DAYS,
    TIMEZONE,
)
from orchestrator.expansion import (
    AvailabilityCache,
    build_ladder,
    contiguous_runs,
    days_in_window,
    parse_iso,
    run_expansion,
)
from orchestrator.nodes.execute import execute_node


# ---------------------------------------------------------------------------
# Fixtures / fakes
# ---------------------------------------------------------------------------


def _dt(y, m, d, h=0):
    return datetime(y, m, d, h, 0, tzinfo=TIMEZONE)


def _slot(d, h_start, h_end=None):
    """Build a slot dict like the MCP server's TimeSlot.to_iso()."""
    h_end = h_end if h_end is not None else h_start + 1
    return {
        "datetime_start": _dt(d.year, d.month, d.day, h_start).isoformat(),
        "datetime_end": _dt(d.year, d.month, d.day, h_end).isoformat(),
    }


class FakeBridge:
    """Records calls and returns slots per a date→hours map (mimics check_availability)."""

    def __init__(self, slots_by_date=None, error_on_call=None):
        self.calls: list[dict] = []
        self._slots_by_date = slots_by_date or {}
        self._error_on_call = error_on_call  # 1-based index to error on, or None

    async def call_tool_with_metrics(
        self, tool_name, arguments, *, latency_model=None, simulate_latency=False
    ):
        self.calls.append(dict(arguments))
        if self._error_on_call is not None and len(self.calls) == self._error_on_call:
            resp = {"status": "error", "message": "boom"}
            return {"response": resp, "actual_latency_ms": 1.0, "simulated_latency_ms": 2.0, "success": False}
        start = parse_iso(arguments["start_datetime"])
        end = parse_iso(arguments["end_datetime"])
        out = []
        d = start.date()
        while d <= end.date():
            for h in self._slots_by_date.get(d, []):
                # Mimic check_availability: slot must fall fully within the window.
                s_start = _dt(d.year, d.month, d.day, h)
                s_end = _dt(d.year, d.month, d.day, h + 1)
                if s_start >= start and s_end <= end:
                    out.append(_slot(d, h))
            d += timedelta(days=1)
        return {"response": out, "actual_latency_ms": 1.0, "simulated_latency_ms": 2.0, "success": True}


class FakeRecorder:
    def __init__(self):
        self.tool_calls: list[dict] = []
        self.ladder_steps: list[dict] = []

    def record_tool_call(self, **kwargs):
        self.tool_calls.append(kwargs)

    def record_ladder_steps(self, steps):
        # Mirror ConversationRecorder.record_ladder_steps — the clean per-turn
        # ladder-fire signal (ARCHITECTURE §8 2026-06-08).
        self.ladder_steps.extend(steps)


def _ca_call(args: dict) -> dict:
    return {"name": "check_availability", "args": args}


# ---------------------------------------------------------------------------
# Day helpers
# ---------------------------------------------------------------------------


def test_days_in_window_inclusive():
    days = days_in_window(_dt(2026, 6, 1, 9), _dt(2026, 6, 3, 17))
    assert [d.day for d in days] == [1, 2, 3]


def test_contiguous_runs_splits_gaps():
    from datetime import date

    runs = contiguous_runs([date(2026, 6, 1), date(2026, 6, 2), date(2026, 6, 5)])
    assert [[d.day for d in r] for r in runs] == [[1, 2], [5]]


# ---------------------------------------------------------------------------
# build_ladder
# ---------------------------------------------------------------------------


def test_build_ladder_shape_and_cap():
    # Anchor far from now + horizon so all 5 bidirectional blocks materialize cleanly.
    now = _dt(2026, 6, 1, 12)
    start = _dt(2026, 6, 10, 9)
    end = _dt(2026, 6, 10, 10)
    ladder = build_ladder(start, end, now=now)

    assert len(ladder) == 5  # cap N = 5 (bidirectional)
    # Each window within the MCP per-call cap and business-hours bounded.
    for w_start, w_end in ladder:
        span_days = (w_end.date() - w_start.date()).days + 1
        assert span_days <= MAX_AVAILABILITY_WINDOW_DAYS
        assert w_start.hour == BUSINESS_HOURS_START
        assert w_end.hour == BUSINESS_HOURS_END
    # Offsets from the anchor (06-10): anchor, fwd-near, back-near, fwd-far, back-far.
    starts = [(w[0].month, w[0].day) for w in ladder]
    ends = [(w[1].month, w[1].day) for w in ladder]
    assert starts == [(6, 10), (6, 10), (6, 7), (6, 13), (6, 4)]
    assert ends == [(6, 10), (6, 12), (6, 9), (6, 15), (6, 6)]


def test_build_ladder_clamps_to_horizon_no_runaway():
    now = _dt(2026, 6, 1, 12)
    horizon_end = now.date() + timedelta(days=SCHEDULING_HORIZON_DAYS)
    # Anchor close to the horizon end.
    start = _dt(2026, 6, 20, 9)
    end = _dt(2026, 6, 20, 10)
    ladder = build_ladder(start, end, now=now)

    assert len(ladder) <= 5
    for w_start, w_end in ladder:
        assert w_end.date() <= horizon_end  # never scans past the horizon
        assert w_start.date() >= now.date()  # never scans before now


def test_build_ladder_past_anchor_clamped_to_now():
    now = _dt(2026, 6, 10, 12)
    start = _dt(2026, 6, 1, 9)  # in the past relative to now
    end = _dt(2026, 6, 1, 10)
    ladder = build_ladder(start, end, now=now)
    # First window's anchor day is now's date, not the past request date.
    assert ladder[0][0].date() == now.date()


# ---------------------------------------------------------------------------
# AvailabilityCache
# ---------------------------------------------------------------------------


def test_cache_roundtrip_known_empty_and_invalidate():
    cache = AvailabilityCache()
    from datetime import date

    day = date(2026, 6, 2)
    assert cache.known("investing", "online", day) is False

    # Known-empty: cached with an empty list → known True, no slots.
    cache.put_day("investing", "online", day, [])
    assert cache.known("investing", "online", day) is True
    assert cache.slots_in_window("investing", "online", _dt(2026, 6, 2, 8), _dt(2026, 6, 2, 17)) == []

    # Populated day → slots returned, filtered to the window (10:00 in, 16:00 out).
    cache.put_day("investing", "online", day, [_slot(day, 10), _slot(day, 16)])
    got = cache.slots_in_window("investing", "online", _dt(2026, 6, 2, 8), _dt(2026, 6, 2, 12))
    assert len(got) == 1
    assert got[0]["datetime_start"].startswith("2026-06-02T10:00")

    cache.invalidate("investing", "online", day)
    assert cache.known("investing", "online", day) is False


def test_cache_covers():
    from datetime import date

    cache = AvailabilityCache()
    cache.put_day("investing", "online", date(2026, 6, 2), [])
    assert cache.covers("investing", "online", [date(2026, 6, 2)]) is True
    assert cache.covers("investing", "online", [date(2026, 6, 2), date(2026, 6, 3)]) is False


# ---------------------------------------------------------------------------
# run_expansion
# ---------------------------------------------------------------------------


async def _run_ladder(bridge, cache, *, recorder=None, anchor=_dt(2026, 6, 2, 9), now=_dt(2026, 6, 1, 12)):
    ladder = build_ladder(anchor, anchor + timedelta(hours=1), now=now)
    return await run_expansion(
        bridge=bridge,
        recorder=recorder,
        simulate_latency=False,
        latency_model=None,
        topic_id="investing",
        contact_medium_id="online",
        ladder=ladder,
        cache=cache,
    )


async def test_run_expansion_surfaces_adjacent_day():
    from datetime import date

    # Anchor (06-02) empty; adjacent day (06-03) has slots.
    bridge = FakeBridge(slots_by_date={date(2026, 6, 3): [10, 11]})
    cache = AvailabilityCache()
    recorder = FakeRecorder()
    found, debug = await _run_ladder(bridge, cache, recorder=recorder)

    assert len(found) == 2
    assert all(f["datetime_start"].startswith("2026-06-03") for f in found)
    # Every real MCP call was recorded (honest cost accounting).
    assert len(recorder.tool_calls) == len(bridge.calls)


async def test_run_expansion_backward_widening_rescues_late_anchor():
    from datetime import date

    # Regression for smoke `t5_en_native_014`: the agent anchored a week late
    # (06-11) but the real slots sit BEHIND it (06-06 = anchor−5). A forward-only
    # ladder never reaches them; the backward block (-6,-4 → 06-05..06-07) must.
    bridge = FakeBridge(slots_by_date={date(2026, 6, 6): [9, 16]})
    cache = AvailabilityCache()
    found, debug = await _run_ladder(
        bridge, cache, anchor=_dt(2026, 6, 11, 9), now=_dt(2026, 6, 1, 12)
    )
    assert len(found) == 2
    assert all(f["datetime_start"].startswith("2026-06-06") for f in found)


async def test_run_expansion_cache_prevents_requery():
    from datetime import date

    cache = AvailabilityCache()
    # Anchor day already known-empty from a prior turn.
    cache.put_day("investing", "online", date(2026, 6, 2), [])
    bridge = FakeBridge(slots_by_date={date(2026, 6, 3): [9]})
    await _run_ladder(bridge, cache)

    # No bridge call should ever span the anchor day (06-02) — it was cached.
    for call in bridge.calls:
        start = parse_iso(call["start_datetime"]).date()
        assert start >= date(2026, 6, 3)


async def test_run_expansion_empty_horizon_fabricates_nothing_and_is_bounded():
    """booking_reachable=false guard: empty everywhere → no slots, bounded calls."""
    bridge = FakeBridge(slots_by_date={})  # nothing anywhere
    cache = AvailabilityCache()
    found, debug = await _run_ladder(bridge, cache)
    assert found == []
    assert len(bridge.calls) <= 5  # cap N — no runaway


async def test_run_expansion_error_aborts_without_fabrication():
    bridge = FakeBridge(slots_by_date={}, error_on_call=1)
    cache = AvailabilityCache()
    found, debug = await _run_ladder(bridge, cache)
    assert found == []
    assert len(bridge.calls) == 1  # aborted on the first error
    assert debug[-1].get("error") is True


# ---------------------------------------------------------------------------
# execute_node integration with the flag
# ---------------------------------------------------------------------------


def _config(*, expansion=False, cache=None, recorder=None, bridge=None, reference_date=None):
    cfg = {
        "mcp_bridge": bridge,
        "recorder": recorder,
        "simulate_latency": False,
        "latency_model": None,
    }
    if expansion:
        cfg["expansion_policy_enabled"] = True
    if cache is not None:
        cfg["availability_cache"] = cache
    if reference_date is not None:
        cfg["reference_date"] = reference_date
    return {"configurable": cfg}


async def test_execute_node_flag_off_byte_identical():
    from datetime import date

    args = {
        "topic_id": "investing",
        "contact_medium_id": "online",
        "start_datetime": _dt(2026, 6, 2, 9).isoformat(),
        "end_datetime": _dt(2026, 6, 2, 10).isoformat(),
    }
    state = {"pending_tool_call": _ca_call(args)}

    # Flag absent.
    b1, r1 = FakeBridge(slots_by_date={date(2026, 6, 2): [9]}), FakeRecorder()
    out_absent = await execute_node(state, _config(bridge=b1, recorder=r1))

    # Flag explicitly False (no cache).
    b2, r2 = FakeBridge(slots_by_date={date(2026, 6, 2): [9]}), FakeRecorder()
    cfg = _config(bridge=b2, recorder=r2)
    cfg["configurable"]["expansion_policy_enabled"] = False
    out_false = await execute_node(state, cfg)

    # Exactly one MCP call + one record in both; identical tool_result + debug action.
    assert len(b1.calls) == len(b2.calls) == 1
    assert len(r1.tool_calls) == len(r2.tool_calls) == 1
    assert out_absent["tool_result"] == out_false["tool_result"]
    assert out_absent["debug_log"][0]["action"] == out_false["debug_log"][0]["action"] == "mcp_tool_call"


async def test_execute_node_expansion_error_does_not_fire_ladder():
    args = {
        "topic_id": "investing",
        "contact_medium_id": "online",
        "start_datetime": _dt(2026, 6, 2, 9).isoformat(),
        "end_datetime": _dt(2026, 6, 2, 10).isoformat(),
    }
    state = {"pending_tool_call": _ca_call(args)}
    bridge = FakeBridge(error_on_call=1)
    cache = AvailabilityCache()
    out = await execute_node(
        state, _config(expansion=True, cache=cache, bridge=bridge, reference_date="2026-06-01")
    )
    # Only step-0 ran; the ladder never fired on the error.
    assert len(bridge.calls) == 1
    assert isinstance(out["tool_result"]["response"], dict)
    assert out["tool_result"]["response"]["status"] == "error"


async def test_execute_node_expansion_widens_empty_to_adjacent():
    from datetime import date

    # The agent's narrow 09:00-10:00 window on 06-02 is empty; 06-02 has a 10:00 slot
    # and 06-03 too — L1 (whole anchor day) should surface 06-02's 10:00 slot.
    args = {
        "topic_id": "investing",
        "contact_medium_id": "online",
        "start_datetime": _dt(2026, 6, 2, 9).isoformat(),
        "end_datetime": _dt(2026, 6, 2, 10).isoformat(),
    }
    state = {"pending_tool_call": _ca_call(args)}
    bridge = FakeBridge(slots_by_date={date(2026, 6, 2): [10, 11]})
    cache = AvailabilityCache()
    recorder = FakeRecorder()
    out = await execute_node(
        state,
        _config(expansion=True, cache=cache, bridge=bridge, recorder=recorder, reference_date="2026-06-01"),
    )
    resp = out["tool_result"]["response"]
    assert isinstance(resp, list) and len(resp) >= 1
    assert any(s["datetime_start"].startswith("2026-06-02T10:00") for s in resp)
    # Step-0 narrow (empty) + L1 whole-day = 2 recorded calls (honest cost).
    assert len(recorder.tool_calls) == len(bridge.calls) >= 2
    # The clean per-turn ladder-fire signal is persisted (ARCHITECTURE §8 2026-06-08):
    # the ladder fired, so at least one step is recorded on the turn.
    assert len(recorder.ladder_steps) >= 1


async def test_execute_node_booking_invalidates_booked_day_only():
    from datetime import date

    cache = AvailabilityCache()
    cache.put_day("investing", "online", date(2026, 6, 2), [_slot(date(2026, 6, 2), 9)])
    cache.put_day("investing", "online", date(2026, 6, 3), [_slot(date(2026, 6, 3), 9)])

    class BookingBridge:
        def __init__(self):
            self.calls = []

        async def call_tool_with_metrics(self, tool_name, arguments, *, latency_model=None, simulate_latency=False):
            self.calls.append((tool_name, dict(arguments)))
            return {
                "response": {"status": "success", "booking_id": "BK-1"},
                "actual_latency_ms": 1.0,
                "simulated_latency_ms": 2.0,
                "success": True,
            }

    args = {
        "topic_id": "investing",
        "contact_medium_id": "online",
        "datetime_start": _dt(2026, 6, 2, 9).isoformat(),
        "datetime_end": _dt(2026, 6, 2, 10).isoformat(),
    }
    state = {"pending_tool_call": {"name": "book_appointment", "args": args}}
    bridge = BookingBridge()
    await execute_node(state, _config(expansion=True, cache=cache, bridge=bridge))

    # Only the booked day (06-02) is invalidated; 06-03 stays cached.
    assert cache.known("investing", "online", date(2026, 6, 2)) is False
    assert cache.known("investing", "online", date(2026, 6, 3)) is True


# ---------------------------------------------------------------------------
# Runner stage wiring
# ---------------------------------------------------------------------------


def test_stage_to_flags_expansion_isolated_from_nlp():
    from evaluation.runner import stage_to_flags

    flags = stage_to_flags("expansion")
    assert flags["expansion_policy_enabled"] is True
    assert flags["nlp_datetime_enabled"] is False
    assert flags["nlp_entity_enabled"] is False

    base = stage_to_flags("baseline")
    assert base["expansion_policy_enabled"] is False
