"""Date-independence proof for the pinned-reference_date fix (EVALUATION_FRAMEWORK §3a).

The fixture date-drift bug came from resolving a scenario's availability override
against the wall clock while the weekday phrasing was fixed at generation time.
The fix routes every run-time date resolution through the scenario's pinned
``reference_date``. These tests assert that the *effective fixture* a scenario
produces — the resolved availability override, the agent's injected "today", and
the parse-accuracy base date — is **identical regardless of the run day**, which
is the structural guarantee that date drift can no longer occur.
"""

from __future__ import annotations

from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

import evaluation.runner as runner_mod
from evaluation.runner import _resolve_override, _scenario_reference_date
from evaluation.schemas import Scenario
from orchestrator.nodes.agent import _reference_now_from_config

_ZURICH = ZoneInfo("Europe/Zurich")

# A weekday-bearing scenario: the override slot sits on today+1 and the phrasing
# is "next Tuesday" — the exact shape that drifted in t1_en_native_031.
_SCENARIO: dict = {
    "scenario_id": "t1_en_native_031",
    "tier": 1,
    "description": "Direct match",
    "topic_id": "investing",
    "contact_medium_id": "phone",
    "availability_override": {"slots_by_offset": {"today+1": ["09:00-10:00"]}},
    "reference_date": "2026-06-01",  # Monday — pinned anchor
    "simulator_goal": "Book it.",
    "persona_profile": "cooperative",
    "frozen_phrasing": "next Tuesday",
    "language_variant": "en_native",
    "expected_datetime_window": {
        "start_offset": "today+1T09:00",
        "end_offset": "today+1T10:00",
    },
    "optimal_availability_calls": 1,
}


class _FrozenDate(date):
    """A ``date`` subclass whose ``today()`` returns a configurable value, used to
    simulate running the suite on different calendar days."""

    _today = date(2026, 6, 1)

    @classmethod
    def today(cls):  # noqa: D102
        return cls._today


def _effective_fixture(scenario: dict) -> tuple:
    """Compute the (resolved_override, agent_today, parse_base_date) a scenario
    yields through the pinned-reference_date code paths."""
    ref = _scenario_reference_date(scenario)
    resolved_override = _resolve_override(
        scenario["availability_override"]["slots_by_offset"], today=ref
    )
    agent_today = _reference_now_from_config(
        {"configurable": {"reference_date": ref.isoformat()}}
    )
    parse_base_date = Scenario.model_validate(scenario).reference_date
    return resolved_override, agent_today, parse_base_date


@pytest.mark.parametrize("run_day", [date(2026, 6, 1), date(2026, 5, 31)])
def test_effective_fixture_identical_across_run_days(
    run_day: date, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Patch the runner's wall clock to a Monday and a Sunday; the effective
    fixture must be byte-identical because nothing reads the wall clock anymore."""
    _FrozenDate._today = run_day
    monkeypatch.setattr(runner_mod, "date", _FrozenDate)

    resolved, agent_today, base_date = _effective_fixture(_SCENARIO)

    # today+1 from the pinned Monday 2026-06-01 → 2026-06-02, on every run day.
    assert resolved == {"2026-06-02": ["09:00-10:00"]}
    assert agent_today == datetime(2026, 6, 1, 12, 0, tzinfo=_ZURICH)
    assert base_date == date(2026, 6, 1)


def test_two_run_days_produce_the_same_fixture(monkeypatch: pytest.MonkeyPatch) -> None:
    """Direct A/B: the fixture computed on a Monday equals the one on a Sunday."""
    _FrozenDate._today = date(2026, 6, 1)  # Monday
    monkeypatch.setattr(runner_mod, "date", _FrozenDate)
    fixture_mon = _effective_fixture(_SCENARIO)

    _FrozenDate._today = date(2026, 5, 31)  # Sunday
    fixture_sun = _effective_fixture(_SCENARIO)

    assert fixture_mon == fixture_sun


def test_unpinned_resolution_would_have_drifted(monkeypatch: pytest.MonkeyPatch) -> None:
    """Contrast: the OLD wall-clock path (today=None) drifts across run days —
    this is the bug the pin removes."""
    _FrozenDate._today = date(2026, 6, 1)  # Monday
    monkeypatch.setattr(runner_mod, "date", _FrozenDate)
    slots = _SCENARIO["availability_override"]["slots_by_offset"]
    resolved_mon = _resolve_override(slots)  # no today → wall clock

    _FrozenDate._today = date(2026, 5, 31)  # Sunday
    resolved_sun = _resolve_override(slots)

    assert resolved_mon != resolved_sun  # drift — exactly what the fix prevents


def test_scenario_reference_date_ignores_wall_clock(monkeypatch: pytest.MonkeyPatch) -> None:
    """``_scenario_reference_date`` returns the pinned value regardless of today."""
    _FrozenDate._today = date(2030, 1, 1)
    monkeypatch.setattr(runner_mod, "date", _FrozenDate)
    assert _scenario_reference_date(_SCENARIO) == date(2026, 6, 1)


def test_missing_reference_date_falls_back_to_anchor(monkeypatch: pytest.MonkeyPatch) -> None:
    """An older scenario without reference_date falls back to the suite anchor,
    not the wall clock."""
    _FrozenDate._today = date(2030, 1, 1)
    monkeypatch.setattr(runner_mod, "date", _FrozenDate)
    legacy = {k: v for k, v in _SCENARIO.items() if k != "reference_date"}
    assert _scenario_reference_date(legacy) == date(2026, 6, 1)
