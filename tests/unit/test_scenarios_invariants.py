"""Unit tests for the Tier 1 alignment invariant + standalone validator.

The generator must reject Tier 1 scenarios whose `expected_datetime_window`'s
slot isn't actually in the override, and the validator must replay the same
check against committed JSONs.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from evaluation.scenarios.generator import _assert_scenario_invariants
from evaluation.scenarios.validate import validate_tier
from evaluation.schemas import (
    REFERENCE_DATE,
    AvailabilityOverride,
    ExpectedDateTimeWindow,
    Scenario,
)


def _make_tier1(
    *,
    override_slots: dict[str, list[str]],
    expected_start: str,
    expected_end: str,
    frozen_phrasing: str = "next Tuesday at 9am",
    reference_date: date = REFERENCE_DATE,
) -> Scenario:
    # NOTE: the default frozen_phrasing "next Tuesday at 9am" deliberately does
    # NOT parse to a concrete relative day, so the fixture-alignment invariant
    # SKIPS it and the slot-invariant tests below stay focused on the slot check.
    # The alignment tests pass an explicit, parseable phrasing + reference_date.
    return Scenario(
        scenario_id="t1_test_001",
        tier=1,
        description="Direct match",
        topic_id="investing",
        contact_medium_id="phone",
        availability_override=AvailabilityOverride(slots_by_offset=override_slots),
        reference_date=reference_date,
        simulator_goal="Book it.",
        persona_profile="cooperative",
        frozen_phrasing=frozen_phrasing,
        language_variant="en_native",
        expected_datetime_window=ExpectedDateTimeWindow(
            start_offset=expected_start, end_offset=expected_end
        ),
        optimal_availability_calls=1,
    )


def test_tier1_invariant_passes_when_slot_in_override() -> None:
    scenario = _make_tier1(
        override_slots={"today+3": ["09:00-10:00", "10:00-11:00"]},
        expected_start="today+3T09:00",
        expected_end="today+3T10:00",
    )
    # Must not raise.
    _assert_scenario_invariants(scenario)


def test_tier1_invariant_rejects_missing_slot() -> None:
    # Expected 15:00-16:00, but override only has 09:00 and 11:00.
    scenario = _make_tier1(
        override_slots={"today+3": ["09:00-10:00", "11:00-12:00"]},
        expected_start="today+3T15:00",
        expected_end="today+3T16:00",
    )
    with pytest.raises(ValueError, match="invariant violated"):
        _assert_scenario_invariants(scenario)


def test_tier1_invariant_rejects_missing_offset() -> None:
    # Expected slot on today+5, but override only has today+3.
    scenario = _make_tier1(
        override_slots={"today+3": ["09:00-10:00"]},
        expected_start="today+5T09:00",
        expected_end="today+5T10:00",
    )
    with pytest.raises(ValueError, match="invariant violated"):
        _assert_scenario_invariants(scenario)


def test_tier1_invariant_rejects_missing_window() -> None:
    scenario = Scenario(
        scenario_id="t1_test_002",
        tier=1,
        description="Direct match",
        topic_id="investing",
        contact_medium_id="phone",
        availability_override=AvailabilityOverride(slots_by_offset={"today+1": ["09:00-10:00"]}),
        simulator_goal="Book it.",
        persona_profile="cooperative",
        frozen_phrasing="x",
        language_variant="en_native",
        expected_datetime_window=None,
        optimal_availability_calls=1,
    )
    with pytest.raises(ValueError, match="requires an expected_datetime_window"):
        _assert_scenario_invariants(scenario)


# ─── Fixture-alignment invariant (EVALUATION_FRAMEWORK §3a) ────────────────
#
# Reproduces the t1_en_native_031 date-drift bug as a fixture-internal check:
# the day the weekday phrasing resolves to (given reference_date) must equal the
# day the expected_datetime_window targets. With reference_date pinned to a
# Monday this holds; on a Sunday "next Tuesday" lands a day later and the
# invariant must catch the drift.


def test_fixture_alignment_passes_when_phrasing_matches_window() -> None:
    # Monday 2026-06-01: "next Tuesday" → today+1; window targets today+1 → aligned.
    scenario = _make_tier1(
        override_slots={"today+1": ["09:00-10:00", "10:00-11:00"]},
        expected_start="today+1T09:00",
        expected_end="today+1T10:00",
        frozen_phrasing="next Tuesday",
        reference_date=date(2026, 6, 1),  # Monday — the suite anchor
    )
    # Must not raise: phrasing day == expected-window day == today+1.
    _assert_scenario_invariants(scenario)


def test_fixture_alignment_fails_on_drifted_reference_date() -> None:
    # Sunday 2026-05-31: "next Tuesday" → today+2, but the window still targets
    # today+1 (exactly the t1_en_native_031 drift). The invariant must fire.
    scenario = _make_tier1(
        override_slots={"today+1": ["09:00-10:00"]},
        expected_start="today+1T09:00",
        expected_end="today+1T10:00",
        frozen_phrasing="next Tuesday",
        reference_date=date(2026, 5, 31),  # Sunday — wrong weekday
    )
    with pytest.raises(ValueError, match="fixture-alignment invariant violated"):
        _assert_scenario_invariants(scenario)


def test_fixture_alignment_skips_unparseable_phrasing() -> None:
    # A non-temporal phrasing has no concrete day to align — invariant skips even
    # when the window offset is arbitrary (here today+5, no matching parse).
    scenario = _make_tier1(
        override_slots={"today+5": ["09:00-10:00"]},
        expected_start="today+5T09:00",
        expected_end="today+5T10:00",
        frozen_phrasing="I would like to book an appointment please",
        reference_date=date(2026, 6, 1),
    )
    _assert_scenario_invariants(scenario)  # must not raise


def test_non_tier1_scenarios_skip_invariant() -> None:
    """Tiers 2–7 don't enforce the strict slot-in-override invariant (yet)."""
    scenario = _make_tier1(
        override_slots={"today+3": ["09:00-10:00"]},
        expected_start="today+3T15:00",
        expected_end="today+3T16:00",
    )
    # Re-cast as tier 2 and confirm no raise.
    scenario_t2 = scenario.model_copy(update={"tier": 2})
    _assert_scenario_invariants(scenario_t2)


def test_tier1_unreachable_skips_slot_check() -> None:
    """booking_reachable=False inverts the contract: empty override is correct."""
    scenario = _make_tier1(
        override_slots={},
        expected_start="today+3T09:00",
        expected_end="today+3T10:00",
    )
    scenario_unreachable = scenario.model_copy(update={"booking_reachable": False})
    # Must NOT raise — empty override is the whole point of unreachable.
    _assert_scenario_invariants(scenario_unreachable)


def test_validator_reports_clean_tier(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The standalone validator must read a committed tier file and replay invariants."""
    # Build a tiny tier 1 file that satisfies the invariant.
    scenario = _make_tier1(
        override_slots={"today+2": ["09:00-10:00", "10:00-11:00"]},
        expected_start="today+2T09:00",
        expected_end="today+2T10:00",
    )
    tier_dir = tmp_path / "scenarios"
    tier_dir.mkdir()
    (tier_dir / "tier1_direct_match.json").write_text(
        json.dumps([scenario.model_dump()], default=str), encoding="utf-8"
    )

    # Point the validator's SCENARIOS_DIR at our tmp_path.
    import evaluation.scenarios.validate as validate_mod

    monkeypatch.setattr(validate_mod, "SCENARIOS_DIR", tier_dir)
    violations = validate_tier(1)
    assert violations == []


def test_validator_reports_violations(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A tier file with a broken Tier 1 scenario must produce a violation message."""
    broken = _make_tier1(
        override_slots={"today+2": ["11:00-12:00"]},
        expected_start="today+2T09:00",
        expected_end="today+2T10:00",
    )
    tier_dir = tmp_path / "scenarios"
    tier_dir.mkdir()
    (tier_dir / "tier1_direct_match.json").write_text(
        json.dumps([broken.model_dump()], default=str), encoding="utf-8"
    )

    import evaluation.scenarios.validate as validate_mod

    monkeypatch.setattr(validate_mod, "SCENARIOS_DIR", tier_dir)
    violations = validate_tier(1)
    assert len(violations) == 1
    assert "invariant violated" in violations[0]
