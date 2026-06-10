"""Unit tests for the dead_end_turn_count metric (§4h).

A "dead-end turn" is one where check_availability returned [] AND the agent's
text response presented 0 slots. Empty dicts also count as no-slot responses;
explicit error dicts ({"status":"error",...}) do NOT (the agent never got a
chance to surface anything to the user).
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from evaluation.metrics import _is_empty_availability_response, compute_derived_metrics
from evaluation.schemas import (
    AvailabilityOverride,
    ConversationRecord,
    RunConfig,
    Scenario,
    ToolCallRecord,
    TurnRecord,
)

_UTC = timezone.utc


def _config() -> RunConfig:
    return RunConfig(
        llm_provider="gemini",
        llm_model="gemini-2.5-flash",
        llm_temperature=0.5,
    )


def _scenario() -> Scenario:
    return Scenario(
        scenario_id="t1_test_000",
        tier=1,
        description="Test",
        topic_id="investing",
        contact_medium_id="phone",
        availability_override=AvailabilityOverride(
            slots_by_offset={"today+1": ["09:00-10:00"]}
        ),
        simulator_goal="Book it.",
        persona_profile="cooperative",
        frozen_phrasing="x",
        language_variant="en_native",
        optimal_availability_calls=1,
    )


def _record(turns: list[TurnRecord]) -> ConversationRecord:
    return ConversationRecord(
        scenario_id="t1_test_000",
        tier=1,
        stage="baseline",
        persona_profile="cooperative",
        run_index=1,
        run_id="20260524_120000__baseline__abc",
        timestamp_start=datetime(2026, 5, 24, 10, 0, 0, tzinfo=_UTC),
        git_commit="abc",
        config=_config(),
        turns=turns,
    )


def _turn(
    idx: int,
    *,
    agent_response: str | None,
    check_availability_response: object,
    success: bool = True,
) -> TurnRecord:
    return TurnRecord(
        turn_index=idx,
        timestamp=datetime(2026, 5, 24, 10, idx, 0, tzinfo=_UTC),
        user_message=f"user {idx}",
        agent_response=agent_response,
        tool_calls=[
            ToolCallRecord(
                tool_name="check_availability",
                parameters={"topic_id": "investing"},
                response=check_availability_response,
                success=success,
                error_message=None if success else "x",
            )
        ],
    )


# --- _is_empty_availability_response edge cases -----------------------------


def test_empty_list_is_empty() -> None:
    assert _is_empty_availability_response([]) is True


def test_non_empty_list_is_not_empty() -> None:
    assert _is_empty_availability_response([{"datetime_start": "..."}]) is False


def test_populated_single_dict_is_not_empty() -> None:
    assert _is_empty_availability_response({"datetime_start": "..."}) is False


def test_error_dict_is_not_empty() -> None:
    """Errors aren't 'no availability' — they're tool refusals. Don't count as dead-end."""
    assert _is_empty_availability_response({"status": "error", "message": "boom"}) is False


def test_empty_dict_is_empty() -> None:
    """An empty dict {} is treated as no slots (defensive)."""
    assert _is_empty_availability_response({}) is True


# --- compute_derived_metrics with dead_end_turn_count -----------------------


def test_no_dead_end_when_slots_returned() -> None:
    turns = [
        _turn(1, agent_response="I have 2:00 PM available.",
              check_availability_response=[{"datetime_start": "x"}]),
    ]
    derived = compute_derived_metrics(_record(turns), _scenario())
    assert derived.dead_end_turn_count == 0


def test_one_dead_end_when_empty_list_and_no_slots_in_text() -> None:
    turns = [
        _turn(1, agent_response="Sorry, nothing available on that day.",
              check_availability_response=[]),
    ]
    derived = compute_derived_metrics(_record(turns), _scenario())
    assert derived.dead_end_turn_count == 1


def test_not_dead_end_when_text_has_slots_despite_empty_response() -> None:
    """If the agent surfaces slots in text (from earlier cached knowledge), the
    turn isn't a dead end from the user's perspective."""
    turns = [
        _turn(1, agent_response="Earlier I found 14:00 — want that?",
              check_availability_response=[]),
    ]
    derived = compute_derived_metrics(_record(turns), _scenario())
    assert derived.dead_end_turn_count == 0


def test_multiple_dead_ends_summed() -> None:
    turns = [
        _turn(1, agent_response="Nothing on Monday.", check_availability_response=[]),
        _turn(2, agent_response="Nothing on Tuesday.", check_availability_response=[]),
        _turn(3, agent_response="Here are 2 options: 09:00 and 14:00.",
              check_availability_response=[{"datetime_start": "x"}]),
        _turn(4, agent_response="Nothing on Wednesday.", check_availability_response=[]),
    ]
    derived = compute_derived_metrics(_record(turns), _scenario())
    assert derived.dead_end_turn_count == 3


def test_error_response_does_not_count_as_dead_end() -> None:
    turns = [
        _turn(1, agent_response="Let me try again.",
              check_availability_response={"status": "error", "message": "past"}),
    ]
    derived = compute_derived_metrics(_record(turns), _scenario())
    assert derived.dead_end_turn_count == 0
