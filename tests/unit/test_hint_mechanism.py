"""Unit tests for evaluation/hint_mechanism.py (NLP-HINTS deep-dive analyses).

Exercises the pure analysis functions on synthetic mini-records — no run
directories, MCP server, or LLM clients involved.
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from evaluation.hint_mechanism import (
    assess_adoption,
    assess_hint,
    classify_flips,
    code_flip_case,
    find_divergence,
    funnel_stages,
    hint_block_accounting,
    hint_range_flags,
    last_funnel_stage,
    material_ca_difference,
    trace_hints,
    turn_intent,
)

_ZURICH = ZoneInfo("Europe/Zurich")

SCENARIO = {
    "scenario_id": "t3_test_000",
    "tier": 3,
    "reference_date": "2026-06-01",
    "booking_reachable": True,
    "expected_datetime_window": {
        "start_offset": "today+3T09:00",
        "end_offset": "today+3T10:00",
    },
    "optimal_availability_calls": 2,
}


def _ca(start: str, end: str, response=None, success=True) -> dict:
    return {
        "tool_name": "check_availability",
        "parameters": {
            "topic_id": "pension",
            "contact_medium_id": "phone",
            "start_datetime": start,
            "end_datetime": end,
        },
        "response": response if response is not None else [],
        "success": success,
    }


def _book(success=True) -> dict:
    return {
        "tool_name": "book_appointment",
        "parameters": {},
        "response": {"status": "success", "booking_id": "b1"} if success else {"status": "error"},
        "success": success,
    }


def _turn(idx: int, user="hi", agent="hello", tool_calls=None, annotation=None) -> dict:
    return {
        "turn_index": idx,
        "user_message": user,
        "agent_response": agent,
        "tool_calls": tool_calls or [],
        "state_snapshot": {"last_annotation": annotation},
    }


def _ann(ranges, topic="pension", medium="phone") -> dict:
    return {
        "topic": topic,
        "contact_medium": medium,
        "datetime_ranges": ranges,
        "entities_raw": {},
    }


def _rng(start: str, end: str, spec="day_specific", text="thursday") -> dict:
    return {
        "start_datetime": start,
        "end_datetime": end,
        "specificity": spec,
        "original_text": text,
        "is_flexible": False,
    }


def _rec(key_id="t3_test_000", rep=1, turns=None, booked=False, termination="max_turns") -> dict:
    return {
        "scenario_id": key_id,
        "run_index": rep,
        "tier": 3,
        "turns": turns or [],
        "derived": {"booked": booked, "first_check_availability_params": None},
        "termination_reason": termination,
    }


# ---------------------------------------------------------------------------
# A1 — flip classification
# ---------------------------------------------------------------------------


class TestClassifyFlips:
    def test_all_transitions(self):
        base = {
            "a__rep1": _rec(booked=True),
            "b__rep1": _rec(booked=False),
            "c__rep1": _rec(booked=True),
            "d__rep1": _rec(booked=False),
        }
        arm = {
            "a__rep1": _rec(booked=False),
            "b__rep1": _rec(booked=True),
            "c__rep1": _rec(booked=True),
            "d__rep1": _rec(booked=False),
        }
        flips = classify_flips(base, arm)
        assert flips["lost"] == ["a__rep1"]
        assert flips["gained"] == ["b__rep1"]
        assert flips["same_booked"] == ["c__rep1"]
        assert flips["same_unbooked"] == ["d__rep1"]
        assert flips["excluded"] == []

    def test_error_and_missing_records_excluded(self):
        base = {
            "a__rep1": _rec(booked=True, termination="error"),
            "b__rep1": _rec(booked=True),
        }
        arm = {"a__rep1": _rec(booked=False), "c__rep1": _rec(booked=True)}
        flips = classify_flips(base, arm)
        assert sorted(flips["excluded"]) == ["a__rep1", "b__rep1", "c__rep1"]
        assert flips["lost"] == []


# ---------------------------------------------------------------------------
# A2 — divergence detection
# ---------------------------------------------------------------------------


class TestDivergence:
    def test_material_ca_difference_day(self):
        a = {"start_datetime": "2026-06-04T09:00:00+02:00", "end_datetime": "2026-06-04T10:00:00+02:00"}
        b = {"start_datetime": "2026-06-05T09:00:00+02:00", "end_datetime": "2026-06-05T10:00:00+02:00"}
        assert material_ca_difference(a, b) is True

    def test_material_ca_difference_small_shift_not_material(self):
        a = {"start_datetime": "2026-06-04T09:00:00+02:00", "end_datetime": "2026-06-04T10:00:00+02:00"}
        b = {"start_datetime": "2026-06-04T10:00:00+02:00", "end_datetime": "2026-06-04T11:00:00+02:00"}
        assert material_ca_difference(a, b) is False

    def test_material_ca_difference_span(self):
        a = {"start_datetime": "2026-06-04T09:00:00+02:00", "end_datetime": "2026-06-04T10:00:00+02:00"}
        b = {"start_datetime": "2026-06-04T09:00:00+02:00", "end_datetime": "2026-06-07T10:00:00+02:00"}
        assert material_ca_difference(a, b) is True

    def test_divergence_on_query_window_mid_conversation(self):
        shared1 = _turn(1, user="hi", agent="which day?")
        base = _rec(turns=[
            shared1,
            _turn(2, user="thursday", tool_calls=[_ca("2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00")]),
        ])
        arm = _rec(turns=[
            shared1,
            _turn(2, user="thursday", tool_calls=[_ca("2026-06-09T00:00:00+02:00", "2026-06-09T01:00:00+02:00")]),
        ])
        d = find_divergence(base, arm)
        assert d["turn_index"] == 2
        assert d["kind"] == "query_window"
        assert d["position"] == "mid_late"
        assert d["user_text_diverged_first"] is False

    def test_divergence_first_turn_tool_choice(self):
        base = _rec(turns=[_turn(1, tool_calls=[_ca("2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00")])])
        arm = _rec(turns=[_turn(1)])
        d = find_divergence(base, arm)
        assert d["turn_index"] == 1
        assert d["kind"] == "tool_choice"
        assert d["position"] == "first"

    def test_user_diverged_first_flagged(self):
        base = _rec(turns=[
            _turn(1, user="hi"),
            _turn(2, user="thursday please", tool_calls=[_ca("2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00")]),
        ])
        arm = _rec(turns=[
            _turn(1, user="hi"),
            _turn(2, user="friday please", tool_calls=[_ca("2026-06-05T09:00:00+02:00", "2026-06-05T10:00:00+02:00")]),
        ])
        d = find_divergence(base, arm)
        assert d["kind"] == "query_window"
        # user text diverged at the same turn, not strictly earlier
        assert d["user_text_diverged_first"] is False
        assert d["user_diverged_at"] == 2

    def test_conversation_length_divergence(self):
        t1 = _turn(1)
        base = _rec(turns=[t1, _turn(2)])
        arm = _rec(turns=[t1])
        d = find_divergence(base, arm)
        assert d["kind"] == "conversation_length"

    def test_turn_intent_classes(self):
        assert turn_intent(_turn(1, tool_calls=[_book()])) == "booking_attempt"
        assert turn_intent(_turn(1, agent="How about 2026-06-04T09:00?")) == "presents_slots"
        assert turn_intent(
            _turn(1, agent="Sorry, nothing.", tool_calls=[_ca("2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00", response=[])])
        ) == "no_slots_reply"
        assert turn_intent(_turn(1, agent="Which topic?")) == "question_or_other"


# ---------------------------------------------------------------------------
# A3 — hint correctness × adoption
# ---------------------------------------------------------------------------


class TestHintAssessment:
    def test_exact_hint(self):
        ann = _ann([_rng("2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00")])
        assert assess_hint(ann, SCENARIO)["status"] == "exact"

    def test_partial_hint_right_day_wrong_time(self):
        ann = _ann([_rng("2026-06-04T14:00:00+02:00", "2026-06-04T15:00:00+02:00")])
        assert assess_hint(ann, SCENARIO)["status"] == "partial"

    def test_wrong_hint(self):
        ann = _ann([_rng("2026-06-09T00:00:00+02:00", "2026-06-09T01:00:00+02:00")])
        assert assess_hint(ann, SCENARIO)["status"] == "wrong"

    def test_best_range_counts(self):
        ann = _ann([
            _rng("2026-06-09T00:00:00+02:00", "2026-06-09T01:00:00+02:00"),
            _rng("2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00"),
        ])
        assert assess_hint(ann, SCENARIO)["status"] == "exact"

    def test_no_hint(self):
        assert assess_hint(_ann([]), SCENARIO)["status"] == "no_hint"
        assert assess_hint(None, SCENARIO)["status"] == "no_hint"

    def test_unscorable_without_expected_window(self):
        scenario = dict(SCENARIO, expected_datetime_window=None)
        ann = _ann([_rng("2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00")])
        assert assess_hint(ann, scenario)["status"] == "unscorable"


class TestAdoption:
    def _rec_with(self, hint_start, hint_end, q_start, q_end):
        ann = _ann([_rng(hint_start, hint_end)])
        return _rec(turns=[
            _turn(1, annotation=ann),
            _turn(2, tool_calls=[_ca(q_start, q_end)]),
        ])

    def test_adopted_window(self):
        rec = self._rec_with(
            "2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00",
            "2026-06-04T09:30:00+02:00", "2026-06-04T10:30:00+02:00",
        )
        assert assess_adoption(rec) == "adopted_window"

    def test_adopted_day(self):
        rec = self._rec_with(
            "2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00",
            "2026-06-04T14:00:00+02:00", "2026-06-04T15:00:00+02:00",
        )
        assert assess_adoption(rec) == "adopted_day"

    def test_ignored(self):
        rec = self._rec_with(
            "2026-06-09T00:00:00+02:00", "2026-06-09T01:00:00+02:00",
            "2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00",
        )
        assert assess_adoption(rec) == "ignored"

    def test_no_hint_and_no_query(self):
        assert assess_adoption(_rec(turns=[_turn(1)])) == "no_hint"
        ann = _ann([_rng("2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00")])
        assert assess_adoption(_rec(turns=[_turn(1, annotation=ann)])) == "no_query"


# ---------------------------------------------------------------------------
# A4 — funnel
# ---------------------------------------------------------------------------


class TestFunnel:
    def test_full_funnel(self):
        slot = {"datetime_start": "2026-06-04T09:00:00+02:00", "datetime_end": "2026-06-04T10:00:00+02:00"}
        rec = _rec(
            turns=[
                _turn(1, agent="which day?"),
                _turn(2, agent="I have 2026-06-04T09:00 free.",
                      tool_calls=[_ca("2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00", response=[slot])]),
                _turn(3, user="yes, book it please", agent="Booked!", tool_calls=[_book()]),
            ],
            booked=True,
        )
        stages = funnel_stages(rec)
        assert all(stages[s] for s in
                   ("queried", "nonempty_result", "slots_presented", "user_accepted",
                    "booking_attempted", "booked"))
        assert last_funnel_stage(stages) == "booked"

    def test_loss_after_presentation(self):
        slot = {"datetime_start": "2026-06-04T09:00:00+02:00", "datetime_end": "2026-06-04T10:00:00+02:00"}
        rec = _rec(turns=[
            _turn(1, agent="I have 2026-06-04T09:00 free.",
                  tool_calls=[_ca("2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00", response=[slot])]),
            _turn(2, user="no, too early", agent="anything else?"),
        ])
        stages = funnel_stages(rec)
        assert stages["slots_presented"] is True
        assert stages["user_accepted"] is False
        assert stages["booking_attempted"] is False
        assert last_funnel_stage(stages) == "slots_presented"

    def test_acceptance_only_counts_after_presentation(self):
        rec = _rec(turns=[
            _turn(1, user="yes I want an appointment", agent="which day?"),
        ])
        assert funnel_stages(rec)["user_accepted"] is False

    def test_never_queried(self):
        stages = funnel_stages(_rec(turns=[_turn(1)]))
        assert last_funnel_stage(stages) == "none"

    def test_single_slot_dict_response_is_nonempty(self):
        slot = {"datetime_start": "2026-06-04T09:00:00+02:00", "datetime_end": "2026-06-04T10:00:00+02:00"}
        rec = _rec(turns=[
            _turn(1, tool_calls=[_ca("2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00", response=slot)]),
        ])
        assert funnel_stages(rec)["nonempty_result"] is True


# ---------------------------------------------------------------------------
# A5 — prompt accounting
# ---------------------------------------------------------------------------


class TestPromptAccounting:
    def test_hint_block_measured_with_production_renderer(self):
        ann = _ann([_rng("2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00")])
        rec = _rec(turns=[_turn(1, annotation=ann), _turn(2, annotation=_ann([], topic=None, medium=None))])
        rows = hint_block_accounting(rec, SCENARIO)
        assert len(rows) == 2
        assert rows[0]["hint_chars"] > 0
        assert 0 < rows[0]["hint_share"] < 1
        # turn 2's annotation carries nothing actionable -> renderer emits ""
        assert rows[1]["hint_chars"] == 0

    def test_no_annotation_turns_skipped(self):
        rec = _rec(turns=[_turn(1)])
        assert hint_block_accounting(rec, SCENARIO) == []


# ---------------------------------------------------------------------------
# A6 — degenerate-hint trace
# ---------------------------------------------------------------------------


class TestHintFlags:
    def test_midnight_exact_time_is_degenerate(self):
        rng = _rng("2026-06-09T00:00:00+02:00", "2026-06-09T01:00:00+02:00", spec="exact_time")
        assert "midnight_exact_time" in hint_range_flags(rng, SCENARIO)

    def test_midnight_day_level_is_by_design_not_degenerate(self):
        # windows.snap_start snaps day-level specificities to 00:00 by contract.
        rng = _rng("2026-06-04T00:00:00+02:00", "2026-06-04T23:59:00+02:00", spec="day_vague")
        assert hint_range_flags(rng, SCENARIO) == []

    def test_off_hours_exact_time(self):
        rng = _rng("2026-06-04T19:00:00+02:00", "2026-06-04T20:00:00+02:00", spec="exact_time")
        flags = hint_range_flags(rng, SCENARIO)
        assert "off_hours_exact_time" in flags
        assert "midnight_exact_time" not in flags

    def test_out_of_horizon(self):
        rng = _rng("2026-08-01T09:00:00+02:00", "2026-08-01T10:00:00+02:00")
        assert "out_of_horizon" in hint_range_flags(rng, SCENARIO)

    def test_clean_range(self):
        rng = _rng("2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00", spec="exact_time")
        assert hint_range_flags(rng, SCENARIO) == []

    def test_unparseable(self):
        rng = _rng("not-a-date", "also-not")
        assert hint_range_flags(rng, SCENARIO) == ["unparseable"]


class TestTraceHints:
    def test_followed_vs_overrode(self):
        deg = _ann([_rng("2026-06-09T00:00:00+02:00", "2026-06-09T01:00:00+02:00", spec="exact_time")])
        rec = _rec(turns=[
            _turn(1, annotation=deg,
                  tool_calls=[_ca("2026-06-09T00:00:00+02:00", "2026-06-09T01:00:00+02:00")]),
            _turn(2, annotation=deg,
                  tool_calls=[_ca("2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00")]),
            _turn(3, annotation=deg),
        ])
        rows = trace_hints(rec, SCENARIO)
        assert [r["query_relation"] for r in rows] == ["followed", "overrode", "no_query"]
        assert all(r["degenerate"] for r in rows)
        assert rows[0]["is_first_turn"] is True
        assert rows[1]["is_first_turn"] is False

    def test_turns_without_ranges_skipped(self):
        rec = _rec(turns=[_turn(1, annotation=_ann([], topic=None, medium=None)), _turn(2)])
        assert trace_hints(rec, SCENARIO) == []

    def test_followed_degenerate_only_requires_uniquely_degenerate_day(self):
        # One clean range (June 4) + one garbled range (June 9 midnight).
        mixed = _ann([
            _rng("2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00", spec="exact_time"),
            _rng("2026-06-09T00:00:00+02:00", "2026-06-09T01:00:00+02:00", spec="exact_time"),
        ])
        rec = _rec(turns=[
            # Querying the clean day is NOT a degenerate follow...
            _turn(1, annotation=mixed,
                  tool_calls=[_ca("2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00")]),
            # ...querying the garbled-only day IS.
            _turn(2, annotation=mixed,
                  tool_calls=[_ca("2026-06-09T00:00:00+02:00", "2026-06-09T01:00:00+02:00")]),
        ])
        rows = trace_hints(rec, SCENARIO)
        assert rows[0]["followed_degenerate_only"] is False
        assert rows[1]["followed_degenerate_only"] is True


# ---------------------------------------------------------------------------
# A7 — scripted taxonomy
# ---------------------------------------------------------------------------


class TestTaxonomy:
    def test_wrong_hint_adopted_is_primary(self):
        wrong_ann = _ann([_rng("2026-06-09T09:00:00+02:00", "2026-06-09T10:00:00+02:00")])
        slot = {"datetime_start": "2026-06-04T09:00:00+02:00", "datetime_end": "2026-06-04T10:00:00+02:00"}
        base = _rec(turns=[
            _turn(1, tool_calls=[_ca("2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00", response=[slot])]),
        ], booked=True)
        arm = _rec(turns=[
            _turn(1, annotation=wrong_ann,
                  tool_calls=[_ca("2026-06-09T09:00:00+02:00", "2026-06-09T10:00:00+02:00", response=[])]),
        ], booked=False)
        divergence = find_divergence(base, arm)
        hint = assess_hint(wrong_ann, SCENARIO)
        labels = code_flip_case(base, arm, SCENARIO, divergence, hint, assess_adoption(arm))
        assert labels[0] == "wrong_hint_adopted"
        assert "never_found_slots" in labels

    def test_closure_lost(self):
        slot = {"datetime_start": "2026-06-04T09:00:00+02:00", "datetime_end": "2026-06-04T10:00:00+02:00"}
        good_ann = _ann([_rng("2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00")])
        base = _rec(turns=[
            _turn(1, agent="2026-06-04T09:00 works",
                  tool_calls=[_ca("2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00", response=[slot])]),
            _turn(2, tool_calls=[_book()]),
        ], booked=True)
        arm = _rec(turns=[
            _turn(1, annotation=good_ann, agent="2026-06-04T09:00 works",
                  tool_calls=[_ca("2026-06-04T09:00:00+02:00", "2026-06-04T10:00:00+02:00", response=[slot])]),
            _turn(2, agent="anything else?"),
        ], booked=False)
        divergence = find_divergence(base, arm)
        hint = assess_hint(good_ann, SCENARIO)
        labels = code_flip_case(base, arm, SCENARIO, divergence, hint, assess_adoption(arm))
        assert "closure_lost" in labels
        assert "wrong_hint_adopted" not in labels

    def test_uncoded_fallback(self):
        base = _rec(turns=[_turn(1)], booked=True)
        arm = _rec(turns=[_turn(1)], booked=False, termination="simulator_goal_complete")
        divergence = find_divergence(base, arm)
        labels = code_flip_case(base, arm, SCENARIO, divergence,
                                {"status": "no_hint", "best_score": None}, "no_hint")
        assert labels == ["uncoded"]
