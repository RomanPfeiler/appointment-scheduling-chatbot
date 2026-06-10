"""Unit tests for evaluation/metrics.py.

All fixtures use synthetic ConversationRecord objects — no filesystem writes
(except write_run_summary which uses tmp_path) and no LLM calls.
"""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

from evaluation.metrics import (
    PerTierStats,
    RunSummary,
    _count_slots_in_text,
    _resolve_offset,
    _score_parse_accuracy,
    build_kpi_row,
    compute_derived_metrics,
    compute_run_summary,
    extract_grounding_facts,
    write_run_summary,
)
from evaluation.schemas import (
    AvailabilityOverride,
    ConversationRecord,
    DerivedMetrics,
    ExpectedDateTimeWindow,
    GroundingFact,
    RunConfig,
    RunManifest,
    Scenario,
    ToolCallRecord,
    TurnRecord,
)
from evaluation import storage
from evaluation.storage import RunPaths

_ZURICH = ZoneInfo("Europe/Zurich")
_UTC = timezone.utc


# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------


def _config() -> RunConfig:
    return RunConfig(
        llm_provider="gemini",
        llm_model="gemini-2.5-flash",
        llm_temperature=0.5,
    )


def _base_record(**overrides) -> ConversationRecord:
    defaults = dict(
        scenario_id="t1_test_000",
        tier=1,
        stage="baseline",
        persona_profile="cooperative",
        run_index=1,
        run_id="20260524_120000__baseline__abcd123",
        timestamp_start=datetime(2026, 5, 24, 10, 0, 0, tzinfo=_UTC),
        git_commit="abcd123",
        config=_config(),
    )
    defaults.update(overrides)
    return ConversationRecord(**defaults)


def _make_scenario(**overrides) -> Scenario:
    defaults = dict(
        scenario_id="t1_test_000",
        tier=1,
        description="Test scenario",
        topic_id="mortgage",
        contact_medium_id="branch",
        availability_override=AvailabilityOverride(
            slots_by_offset={"today+2": ["09:00-10:00", "10:00-11:00"]}
        ),
        # Parse-accuracy now resolves the expected window against the scenario's
        # reference_date (not the record's timestamp). These records query around
        # 2026-05-26 (= reference_date + 2), so anchor the scenario there.
        reference_date=date(2026, 5, 24),
        simulator_goal="Book a mortgage appointment.",
        persona_profile="cooperative",
        frozen_phrasing="I'd like an appointment next Tuesday at 9am.",
        language_variant="en_native",
        optimal_availability_calls=1,
    )
    defaults.update(overrides)
    return Scenario(**defaults)


def _turn(
    turn_index: int,
    user_message: str | None = None,
    agent_response: str | None = None,
    tool_calls: list[ToolCallRecord] | None = None,
) -> TurnRecord:
    return TurnRecord(
        turn_index=turn_index,
        timestamp=datetime(2026, 5, 24, 10, 0, turn_index, tzinfo=_UTC),
        user_message=user_message,
        agent_response=agent_response,
        tool_calls=tool_calls or [],
    )


def _tool_call(name: str, params: dict, response, *, success: bool = True,
               actual_ms: float | None = None, sim_ms: float | None = None) -> ToolCallRecord:
    return ToolCallRecord(
        tool_name=name,
        parameters=params,
        response=response,
        success=success,
        actual_latency_ms=actual_ms,
        simulated_latency_ms=sim_ms,
    )


# ---------------------------------------------------------------------------
# Group 1: _resolve_offset
# ---------------------------------------------------------------------------


def test_resolve_offset_today_plus_2_at_9am():
    base = date(2026, 5, 24)
    result = _resolve_offset("today+2T09:00", base)
    assert result.date() == date(2026, 5, 26)
    assert result.hour == 9
    assert result.minute == 0
    assert result.tzinfo is not None


def test_resolve_offset_today_plus_0_at_8am():
    base = date(2026, 5, 24)
    result = _resolve_offset("today+0T08:00", base)
    assert result.date() == base
    assert result.hour == 8


def test_resolve_offset_today_plus_5_at_17():
    base = date(2026, 5, 24)
    result = _resolve_offset("today+5T17:00", base)
    assert result.date() == date(2026, 5, 29)
    assert result.hour == 17


def test_resolve_offset_invalid_prefix_raises():
    with pytest.raises(ValueError, match="today\\+"):
        _resolve_offset("next+2T09:00", date(2026, 5, 24))


def test_resolve_offset_missing_T_raises():
    with pytest.raises(ValueError, match="separator"):
        _resolve_offset("today+2 09:00", date(2026, 5, 24))


def test_resolve_offset_non_integer_day_raises():
    with pytest.raises(ValueError, match="integer"):
        _resolve_offset("today+xT09:00", date(2026, 5, 24))


# ---------------------------------------------------------------------------
# Group 2: _score_parse_accuracy
# ---------------------------------------------------------------------------

_BASE_DT = datetime(2026, 5, 26, 9, 0, tzinfo=_ZURICH)


def test_score_exact_match():
    score = _score_parse_accuracy(_BASE_DT, _BASE_DT, _BASE_DT, _BASE_DT)
    assert score == 1.0


def test_score_within_tolerance():
    actual = _BASE_DT + timedelta(minutes=20)
    score = _score_parse_accuracy(actual, actual, _BASE_DT, _BASE_DT)
    assert score == 1.0


def test_score_correct_date_wrong_time():
    actual = _BASE_DT + timedelta(minutes=60)  # same day, 60 min off
    score = _score_parse_accuracy(actual, actual, _BASE_DT, _BASE_DT)
    assert score == 0.5


def test_score_wrong_date():
    actual = _BASE_DT + timedelta(days=1)
    score = _score_parse_accuracy(actual, actual, _BASE_DT, _BASE_DT)
    assert score == 0.0


# ---------------------------------------------------------------------------
# Group 3: _count_slots_in_text
# ---------------------------------------------------------------------------


def test_count_slots_iso_datetimes():
    text = "Available: 2026-05-26T09:00, 2026-05-26T10:00, 2026-05-27T14:00."
    assert _count_slots_in_text(text) == 3


def test_count_slots_deduplicates_iso():
    text = "2026-05-26T09:00 and 2026-05-26T09:00 again"
    assert _count_slots_in_text(text) == 1


def test_count_slots_fallback_time_patterns():
    # No ISO datetimes — should fall back to H:MM patterns
    text = "I have slots at 9:00 AM and 11:00 AM on Tuesday."
    count = _count_slots_in_text(text)
    assert count == 2


def test_count_slots_none_returns_zero():
    assert _count_slots_in_text(None) == 0


def test_count_slots_empty_returns_zero():
    assert _count_slots_in_text("") == 0


def test_count_slots_no_time_in_text():
    assert _count_slots_in_text("No times mentioned here.") == 0


# ---------------------------------------------------------------------------
# Group 4: extract_grounding_facts — topics
# ---------------------------------------------------------------------------


def test_grounding_topic_supported_after_tool_call():
    tc = _tool_call(
        "get_appointment_topics", {},
        [{"topic_id": "mortgage", "topic_name": "Mortgage"}],
    )
    record = _base_record(turns=[
        _turn(1, tool_calls=[tc], agent_response="I can help with a Mortgage appointment."),
    ])
    facts = extract_grounding_facts(record)
    topic_facts = [f for f in facts if f.fact_type == "topic"]
    assert len(topic_facts) == 1
    assert topic_facts[0].supported is True
    assert topic_facts[0].asserted_value == "mortgage"


def test_grounding_topic_case_insensitive():
    tc = _tool_call(
        "get_appointment_topics", {},
        [{"topic_id": "mortgage", "topic_name": "Mortgage"}],
    )
    record = _base_record(turns=[
        _turn(1, tool_calls=[tc], agent_response="Let's discuss MORTGAGE options."),
    ])
    facts = extract_grounding_facts(record)
    assert any(f.fact_type == "topic" and f.supported for f in facts)


def test_grounding_topic_not_extracted_before_tool_call():
    # Agent mentions "Mortgage" in turn 1, but get_appointment_topics is only called in turn 2.
    record = _base_record(turns=[
        _turn(1, agent_response="I can help with a Mortgage appointment."),
        _turn(2, tool_calls=[
            _tool_call("get_appointment_topics", {},
                       [{"topic_id": "mortgage", "topic_name": "Mortgage"}])
        ], agent_response="Topics retrieved."),
    ])
    facts = extract_grounding_facts(record)
    turn1_topic_facts = [f for f in facts if f.fact_type == "topic" and f.asserted_in_turn == 1]
    # Known topics is empty when turn 1 is processed → no facts emitted for turn 1
    assert len(turn1_topic_facts) == 0


# ---------------------------------------------------------------------------
# Group 5: extract_grounding_facts — media
# ---------------------------------------------------------------------------


def test_grounding_medium_supported():
    tc = _tool_call(
        "get_appointment_contact_medium", {"topic_id": "mortgage"},
        [{"contact_medium_id": "branch", "contact_medium_name": "Branch Meeting"}],
    )
    record = _base_record(turns=[
        _turn(1, tool_calls=[tc], agent_response="We can schedule a Branch Meeting."),
    ])
    facts = extract_grounding_facts(record)
    medium_facts = [f for f in facts if f.fact_type == "medium"]
    assert len(medium_facts) == 1
    assert medium_facts[0].supported is True


# ---------------------------------------------------------------------------
# Group 6: extract_grounding_facts — slots
# ---------------------------------------------------------------------------


def test_grounding_slot_iso_within_tolerance():
    iso_slot = "2026-05-26T09:00:00+02:00"
    tc = _tool_call(
        "check_availability",
        {"start_datetime": "2026-05-26T08:00:00+02:00",
         "end_datetime": "2026-05-26T17:00:00+02:00"},
        [{"datetime_start": iso_slot, "datetime_end": "2026-05-26T10:00:00+02:00"}],
    )
    # Agent mentions the exact ISO string
    record = _base_record(turns=[
        _turn(1, tool_calls=[tc],
              agent_response=f"I have an opening at 2026-05-26T09:00."),
    ])
    facts = extract_grounding_facts(record)
    slot_facts = [f for f in facts if f.fact_type == "slot"]
    assert len(slot_facts) == 1
    assert slot_facts[0].supported is True


def test_grounding_slot_outside_tolerance_unsupported():
    iso_slot = "2026-05-26T09:00:00+02:00"
    tc = _tool_call(
        "check_availability",
        {"start_datetime": "2026-05-26T08:00:00+02:00",
         "end_datetime": "2026-05-26T17:00:00+02:00"},
        [{"datetime_start": iso_slot, "datetime_end": "2026-05-26T10:00:00+02:00"}],
    )
    # Agent mentions a datetime that's 2 hours away from the known slot
    record = _base_record(turns=[
        _turn(1, tool_calls=[tc],
              agent_response="I have an opening at 2026-05-26T11:00."),
    ])
    facts = extract_grounding_facts(record)
    slot_facts = [f for f in facts if f.fact_type == "slot"]
    assert len(slot_facts) == 1
    assert slot_facts[0].supported is False


def test_grounding_slot_unsupported_without_check_availability():
    # Agent mentions a slot but no check_availability was ever called
    record = _base_record(turns=[
        _turn(1, agent_response="There's a slot on 2026-05-26T09:00."),
    ])
    facts = extract_grounding_facts(record)
    slot_facts = [f for f in facts if f.fact_type == "slot"]
    # known.slots is empty → _slot_matches_known always False
    assert all(not f.supported for f in slot_facts)


def test_grounding_empty_turns_returns_empty():
    record = _base_record(turns=[])
    assert extract_grounding_facts(record) == []


def test_grounding_none_agent_response_skipped():
    tc = _tool_call(
        "get_appointment_topics", {},
        [{"topic_id": "mortgage", "topic_name": "Mortgage"}],
    )
    record = _base_record(turns=[
        _turn(1, tool_calls=[tc], agent_response=None),
    ])
    facts = extract_grounding_facts(record)
    assert facts == []


# ---------------------------------------------------------------------------
# Group 7: extract_grounding_facts — booking
# ---------------------------------------------------------------------------


def test_grounding_booking_id_supported():
    book_tc = _tool_call(
        "book_appointment",
        {"topic_id": "mortgage", "contact_medium_id": "branch",
         "datetime_start": "2026-05-26T09:00:00+02:00",
         "datetime_end": "2026-05-26T10:00:00+02:00"},
        {"status": "success", "booking_id": "BK-001",
         "details": {"datetime_start": "2026-05-26T09:00:00+02:00"}},
    )
    record = _base_record(turns=[
        _turn(1, tool_calls=[book_tc],
              agent_response="Your booking BK-001 is confirmed."),
    ])
    facts = extract_grounding_facts(record)
    booking_facts = [f for f in facts if f.fact_type == "booking"]
    assert len(booking_facts) == 1
    assert booking_facts[0].supported is True
    assert booking_facts[0].asserted_value == "BK-001"


def test_grounding_booking_without_book_call_not_flagged():
    # No book_appointment call — booking_id is None — no booking facts emitted
    record = _base_record(turns=[
        _turn(1, agent_response="Booking BK-001 confirmed."),
    ])
    facts = extract_grounding_facts(record)
    booking_facts = [f for f in facts if f.fact_type == "booking"]
    assert booking_facts == []


# ---------------------------------------------------------------------------
# Group 8: extract_grounding_facts — cumulative knowledge
# ---------------------------------------------------------------------------


def test_grounding_cumulative_topics_across_turns():
    # Turn 1: tool call returns topic; Turn 2: agent mentions topic
    tc = _tool_call(
        "get_appointment_topics", {},
        [{"topic_id": "investing", "topic_name": "Investing"}],
    )
    record = _base_record(turns=[
        _turn(1, tool_calls=[tc], agent_response="Topics loaded."),
        _turn(2, agent_response="I can book an Investing appointment for you."),
    ])
    facts = extract_grounding_facts(record)
    turn2_topic_facts = [
        f for f in facts if f.fact_type == "topic" and f.asserted_in_turn == 2
    ]
    assert len(turn2_topic_facts) == 1
    assert turn2_topic_facts[0].supported is True


def test_grounding_cumulative_slots_across_turns():
    # Turn 1: check_availability; Turn 2: agent references that slot
    check_tc = _tool_call(
        "check_availability",
        {"start_datetime": "2026-05-26T08:00+02:00", "end_datetime": "2026-05-26T17:00+02:00"},
        [{"datetime_start": "2026-05-26T09:00:00+02:00", "datetime_end": "2026-05-26T10:00:00+02:00"}],
    )
    record = _base_record(turns=[
        _turn(1, tool_calls=[check_tc], agent_response="Checking availability…"),
        _turn(2, agent_response="I found a slot at 2026-05-26T09:00 for you."),
    ])
    facts = extract_grounding_facts(record)
    turn2_slots = [f for f in facts if f.fact_type == "slot" and f.asserted_in_turn == 2]
    assert len(turn2_slots) == 1
    assert turn2_slots[0].supported is True


# ---------------------------------------------------------------------------
# Group 9: compute_derived_metrics
# ---------------------------------------------------------------------------


def _record_with_booking() -> ConversationRecord:
    check_tc = _tool_call(
        "check_availability",
        {"start_datetime": "2026-05-26T08:00:00+02:00",
         "end_datetime": "2026-05-26T17:00:00+02:00"},
        [{"datetime_start": "2026-05-26T09:00:00+02:00",
          "datetime_end": "2026-05-26T10:00:00+02:00"}],
        actual_ms=80.0, sim_ms=900.0,
    )
    book_tc = _tool_call(
        "book_appointment",
        {"topic_id": "mortgage", "contact_medium_id": "branch",
         "datetime_start": "2026-05-26T09:00:00+02:00",
         "datetime_end": "2026-05-26T10:00:00+02:00"},
        {"status": "success", "booking_id": "BK-001"},
        actual_ms=60.0,
    )
    return _base_record(turns=[
        _turn(1, user_message="Book me a mortgage appointment.",
              tool_calls=[check_tc], agent_response="Available at 2026-05-26T09:00."),
        _turn(2, user_message="That works.", tool_calls=[book_tc],
              agent_response="Booked! Reference BK-001."),
    ])


def test_compute_derived_metrics_happy_path():
    record = _record_with_booking()
    scenario = _make_scenario(
        optimal_availability_calls=1,
        expected_datetime_window=ExpectedDateTimeWindow(
            start_offset="today+2T09:00", end_offset="today+2T10:00"
        ),
    )
    derived = compute_derived_metrics(record, scenario)

    assert derived.total_turn_count == 2
    assert derived.total_mcp_calls == 2
    assert derived.availability_calls == 1
    assert derived.booked is True
    assert derived.efficiency_ratio == pytest.approx(1.0)
    assert derived.optimal_availability_calls == 1
    assert derived.total_simulated_latency_ms == pytest.approx(900.0)
    assert derived.total_actual_latency_ms == pytest.approx(80.0 + 60.0)
    assert len(derived.slots_presented_per_turn) == 2
    assert derived.slots_presented_per_turn[0] == 1  # turn 1 has one ISO slot
    assert derived.parse_accuracy_score is not None
    # first_check_availability_params start is "2026-05-26T08:00:00+02:00"
    # expected window: today+2 = 2026-05-26 at 09:00
    # actual start is 2026-05-26 at 08:00 — same date, 60 min off → 0.5
    assert derived.parse_accuracy_score == pytest.approx(0.5)


def test_compute_derived_metrics_not_booked():
    check_tc = _tool_call(
        "check_availability",
        {"start_datetime": "2026-05-26T08:00:00+02:00",
         "end_datetime": "2026-05-26T17:00:00+02:00"},
        [],  # no availability
    )
    record = _base_record(turns=[
        _turn(1, tool_calls=[check_tc], agent_response="Nothing available."),
    ])
    scenario = _make_scenario()
    derived = compute_derived_metrics(record, scenario)
    assert derived.booked is False
    assert derived.efficiency_ratio == pytest.approx(1.0)


def test_compute_derived_metrics_empty_turns():
    record = _base_record(turns=[])
    scenario = _make_scenario()
    derived = compute_derived_metrics(record, scenario)
    assert derived.total_turn_count == 0
    assert derived.total_mcp_calls == 0
    assert derived.availability_calls == 0
    assert derived.parse_accuracy_score is None
    assert derived.efficiency_ratio is None
    assert derived.booked is False


def test_compute_derived_metrics_no_expected_window():
    check_tc = _tool_call(
        "check_availability",
        {"start_datetime": "2026-05-26T08:00:00+02:00",
         "end_datetime": "2026-05-26T17:00:00+02:00"},
        [],
    )
    record = _base_record(turns=[_turn(1, tool_calls=[check_tc])])
    scenario = _make_scenario(expected_datetime_window=None)
    derived = compute_derived_metrics(record, scenario)
    assert derived.parse_accuracy_score is None


def test_compute_derived_metrics_efficiency_ratio_wasteful():
    # 3 check_availability calls, optimal is 1
    tcs = [
        _tool_call("check_availability",
                   {"start_datetime": f"2026-05-2{i}T08:00:00+02:00",
                    "end_datetime": f"2026-05-2{i}T17:00:00+02:00"}, [])
        for i in range(6, 9)
    ]
    record = _base_record(turns=[
        _turn(i + 1, tool_calls=[tc]) for i, tc in enumerate(tcs)
    ])
    scenario = _make_scenario(optimal_availability_calls=1)
    derived = compute_derived_metrics(record, scenario)
    assert derived.availability_calls == 3
    assert derived.efficiency_ratio == pytest.approx(3.0)


def test_compute_derived_metrics_grounding_counts_from_facts():
    unsupported_fact = GroundingFact(
        fact_type="slot",
        asserted_value="2026-05-26T11:00",
        asserted_in_turn=1,
        supported=False,
    )
    record = _base_record(
        turns=[_turn(1, agent_response="Try 2026-05-26T11:00.")],
        grounding_facts=[unsupported_fact],
    )
    scenario = _make_scenario()
    derived = compute_derived_metrics(record, scenario)
    assert derived.unsupported_facts_count == 1
    assert derived.faithful is False


def test_compute_derived_metrics_parse_accuracy_exact_match():
    # Run date is 2026-05-24; today+2 = 2026-05-26; expected start 09:00
    # First check_availability also queries 2026-05-26 at 09:00 → score 1.0
    check_tc = _tool_call(
        "check_availability",
        {"start_datetime": "2026-05-26T09:00:00+02:00",
         "end_datetime": "2026-05-26T10:00:00+02:00"},
        [],
    )
    record = _base_record(turns=[_turn(1, tool_calls=[check_tc])])
    scenario = _make_scenario(
        expected_datetime_window=ExpectedDateTimeWindow(
            start_offset="today+2T09:00", end_offset="today+2T10:00"
        ),
    )
    derived = compute_derived_metrics(record, scenario)
    assert derived.parse_accuracy_score == pytest.approx(1.0)


def test_compute_derived_metrics_parse_accuracy_wrong_date():
    # First check_availability queries 2026-05-30 (today+6), expected today+2
    check_tc = _tool_call(
        "check_availability",
        {"start_datetime": "2026-05-30T09:00:00+02:00",
         "end_datetime": "2026-05-30T10:00:00+02:00"},
        [],
    )
    record = _base_record(turns=[_turn(1, tool_calls=[check_tc])])
    scenario = _make_scenario(
        expected_datetime_window=ExpectedDateTimeWindow(
            start_offset="today+2T09:00", end_offset="today+2T10:00"
        ),
    )
    derived = compute_derived_metrics(record, scenario)
    assert derived.parse_accuracy_score == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Group 10: compute_run_summary
# ---------------------------------------------------------------------------


def _booked_record(tier: int = 1, scenario_id: str = "t1_000") -> ConversationRecord:
    book_tc = _tool_call(
        "book_appointment", {},
        {"status": "success", "booking_id": "BK-X"},
    )
    check_tc = _tool_call("check_availability",
                          {"start_datetime": "2026-05-26T08:00+02:00",
                           "end_datetime": "2026-05-26T17:00+02:00"}, [])
    record = _base_record(
        scenario_id=scenario_id, tier=tier,
        turns=[_turn(1, tool_calls=[check_tc]), _turn(2, tool_calls=[book_tc])],
    )
    scenario = _make_scenario(scenario_id=scenario_id, tier=tier)
    grounding = extract_grounding_facts(record)
    record.grounding_facts = grounding
    record.derived = compute_derived_metrics(record, scenario)
    return record


def _unbooked_record(tier: int = 1, scenario_id: str = "t1_001") -> ConversationRecord:
    check_tc = _tool_call("check_availability",
                          {"start_datetime": "2026-05-26T08:00+02:00",
                           "end_datetime": "2026-05-26T17:00+02:00"}, [])
    record = _base_record(
        scenario_id=scenario_id, tier=tier,
        turns=[_turn(1, tool_calls=[check_tc])],
    )
    scenario = _make_scenario(scenario_id=scenario_id, tier=tier)
    grounding = extract_grounding_facts(record)
    record.grounding_facts = grounding
    record.derived = compute_derived_metrics(record, scenario)
    return record


def test_summary_booking_completion_rate():
    r1 = _booked_record(scenario_id="t1_000")
    r2 = _booked_record(scenario_id="t1_001")
    r3 = _unbooked_record(scenario_id="t1_002")
    scenarios = {r.scenario_id: _make_scenario(scenario_id=r.scenario_id) for r in [r1, r2, r3]}
    summary = compute_run_summary([r1, r2, r3], scenarios)
    assert summary.booking_completion_rate == pytest.approx(2 / 3)
    assert summary.record_count == 3
    assert summary.scenario_count == 3


def test_summary_empty_records():
    summary = compute_run_summary([], {})
    assert summary.booking_completion_rate is None
    assert summary.record_count == 0
    assert summary.per_tier == []


def test_summary_per_tier_breakdown():
    r_t1 = _booked_record(tier=1, scenario_id="t1_000")
    r_t3a = _booked_record(tier=3, scenario_id="t3_000")
    r_t3b = _unbooked_record(tier=3, scenario_id="t3_001")
    scenarios = {
        "t1_000": _make_scenario(scenario_id="t1_000", tier=1),
        "t3_000": _make_scenario(scenario_id="t3_000", tier=3),
        "t3_001": _make_scenario(scenario_id="t3_001", tier=3),
    }
    summary = compute_run_summary([r_t1, r_t3a, r_t3b], scenarios)
    tiers_found = {ts.tier for ts in summary.per_tier}
    assert tiers_found == {1, 3}
    tier3 = next(ts for ts in summary.per_tier if ts.tier == 3)
    assert tier3.scenario_count == 2
    assert tier3.booking_completion_rate == pytest.approx(0.5)


def test_summary_median_turns():
    records = []
    for i, n_turns in enumerate([4, 5, 6, 7, 8]):
        record = _base_record(scenario_id=f"t1_{i:03d}", tier=1,
                              turns=[_turn(j + 1) for j in range(n_turns)])
        scenario = _make_scenario(scenario_id=f"t1_{i:03d}")
        record.grounding_facts = []
        record.derived = compute_derived_metrics(record, scenario)
        records.append(record)
    scenarios = {r.scenario_id: _make_scenario(scenario_id=r.scenario_id) for r in records}
    summary = compute_run_summary(records, scenarios)
    assert summary.median_turns == pytest.approx(6.0)


def test_summary_faithful_rate():
    r_faithful = _booked_record(scenario_id="t1_000")  # no unsupported facts
    r_unfaithful = _base_record(
        scenario_id="t1_001", tier=1,
        turns=[_turn(1, agent_response="Try 2026-05-26T11:00.")],
        grounding_facts=[GroundingFact(
            fact_type="slot", asserted_value="2026-05-26T11:00",
            asserted_in_turn=1, supported=False,
        )],
    )
    scenario_unfaithful = _make_scenario(scenario_id="t1_001")
    r_unfaithful.derived = compute_derived_metrics(r_unfaithful, scenario_unfaithful)
    scenarios = {
        "t1_000": _make_scenario(scenario_id="t1_000"),
        "t1_001": scenario_unfaithful,
    }
    summary = compute_run_summary([r_faithful, r_unfaithful], scenarios)
    assert summary.faithful_rate == pytest.approx(0.5)
    assert summary.unfaithful_count == 1
    assert summary.unsupported_facts_total == 1


# ---------------------------------------------------------------------------
# Group 11: write_run_summary
# ---------------------------------------------------------------------------


def _minimal_summary() -> RunSummary:
    return RunSummary(
        run_id="20260524_120000__baseline__abcd123",
        stage="baseline",
        git_commit="abcd123",
        change_note="first baseline",
        timestamp="2026-05-24T10:00:00Z",
        scenario_count=2,
        record_count=2,
        booking_completion_rate=1.0,
        median_turns=5.0,
        median_efficiency_ratio=1.0,
        faithful_rate=1.0,
        mean_total_simulated_latency_ms=900.0,
        mean_parse_accuracy=0.8,
        turn_counts=[4, 6],
        efficiency_ratios=[1.0, 1.0],
        simulated_latencies_ms=[900.0, 900.0],
        parse_accuracy_scores=[0.8, 0.8],
        slots_presented_flat=[2, 3],
        per_tier=[PerTierStats(
            tier=1, scenario_count=2,
            booking_completion_rate=1.0, median_turns=5.0,
            median_efficiency_ratio=1.0, faithful_rate=1.0,
            mean_parse_accuracy=0.8, mean_simulated_latency_ms=900.0,
        )],
        unsupported_facts_total=0,
        faithful_count=2,
        unfaithful_count=0,
    )


def test_write_run_summary_creates_both_files(tmp_path: Path, monkeypatch):
    import evaluation.storage as _storage_mod
    monkeypatch.setattr(_storage_mod, "runs_root", lambda: tmp_path / "runs")
    (tmp_path / "runs").mkdir()

    paths = RunPaths(run_id="20260524_120000__baseline__abcd123", stage="baseline")
    summary = _minimal_summary()
    json_path, md_path = write_run_summary(paths, summary)

    assert json_path.exists()
    assert md_path.exists()


def test_summary_json_is_valid(tmp_path: Path, monkeypatch):
    import evaluation.storage as _storage_mod
    monkeypatch.setattr(_storage_mod, "runs_root", lambda: tmp_path / "runs")
    (tmp_path / "runs").mkdir()

    paths = RunPaths(run_id="20260524_120000__baseline__abcd123", stage="baseline")
    json_path, _ = write_run_summary(paths, _minimal_summary())
    parsed = json.loads(json_path.read_text(encoding="utf-8"))
    assert "booking_completion_rate" in parsed
    assert parsed["record_count"] == 2


def test_summary_md_has_headline_table(tmp_path: Path, monkeypatch):
    import evaluation.storage as _storage_mod
    monkeypatch.setattr(_storage_mod, "runs_root", lambda: tmp_path / "runs")
    (tmp_path / "runs").mkdir()

    paths = RunPaths(run_id="20260524_120000__baseline__abcd123", stage="baseline")
    _, md_path = write_run_summary(paths, _minimal_summary())
    content = md_path.read_text(encoding="utf-8")
    assert "| Booking completion rate |" in content
    assert "| Faithful rate |" in content
    assert "## Per-Tier Breakdown" in content


# ---------------------------------------------------------------------------
# Group 12: build_kpi_row
# ---------------------------------------------------------------------------


def _minimal_manifest() -> RunManifest:
    return RunManifest(
        run_id="20260524_120000__baseline__abcd123",
        stage="baseline",
        timestamp_start=datetime(2026, 5, 24, 10, 0, 0, tzinfo=_UTC),
        git_commit="abcd123",
        change_note="first baseline",
        config=_config(),
        scenario_count=2,
        rep_count=3,
    )


def test_build_kpi_row_fields_match_manifest():
    row = build_kpi_row(_minimal_manifest(), _minimal_summary())
    assert row.run_id == "20260524_120000__baseline__abcd123"
    assert row.stage == "baseline"
    assert row.git_commit == "abcd123"
    assert row.change_note == "first baseline"
    assert row.rep_count == 3
    assert row.scenario_count == 2


def test_build_kpi_row_kpi_values_from_summary():
    row = build_kpi_row(_minimal_manifest(), _minimal_summary())
    assert row.booking_completion_rate == pytest.approx(1.0)
    assert row.median_turns == pytest.approx(5.0)
    assert row.faithful_rate == pytest.approx(1.0)


def test_build_kpi_row_judge_averages_are_none():
    row = build_kpi_row(_minimal_manifest(), _minimal_summary())
    assert row.judge_mean_temporal is None
    assert row.judge_mean_negotiation is None
    assert row.judge_mean_efficiency is None
    assert row.judge_mean_recovery is None


def test_build_kpi_row_csv_round_trip():
    row = build_kpi_row(_minimal_manifest(), _minimal_summary())
    header = row.csv_header()
    values = row.to_csv_row()
    assert len(header) == len(values)
    assert values[header.index("stage")] == "baseline"
    assert values[header.index("judge_mean_temporal")] == ""
