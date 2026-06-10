"""Unit test for the per-scenario wall-clock guard in ScenarioRunner.run_once.

A runaway scenario drives an intra-turn agent↔execute loop that ``--max-turns``
cannot bound (observed 2026-06-06: hundreds of check_availability calls within a
single turn). The runner wraps each scenario's turn loop in ``asyncio.wait_for``
so such a scenario aborts to a ``timeout`` record and the run continues.

This test mocks ``appointment_graph.ainvoke`` to hang and asserts the scenario
finalizes with ``termination_reason == "timeout"`` rather than blocking forever.
All async work is hermetic — no LLM calls, no subprocess.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from evaluation import runner as runner_mod
from evaluation import storage
from evaluation.runner import ScenarioRunner
from evaluation.schemas import RunConfig
from evaluation.storage import RunPaths


_SCENARIO = {
    "scenario_id": "t5_timeout_000",
    "tier": 5,
    "description": "Runaway guard fixture",
    "topic_id": "mortgage",
    "contact_medium_id": "branch",
    "availability_override": {"slots_by_offset": {"today+3": ["09:00-10:00"]}, "notes": ""},
    "simulator_goal": "Book a branch mortgage meeting.",
    "persona_profile": "adversarial",
    "frozen_phrasing": "curious about my calendar next Thursday",
    "language_variant": "en_native",
    "expected_datetime_window": None,
    "optimal_availability_calls": 2,
    "expected_turn_range": [7, 10],
    "booking_reachable": True,
    "notes": "test fixture",
}


class _FakeBridge:
    """Async no-op bridge: override set/clear + reset_bookings all succeed."""

    async def call_tool(self, name, args=None):  # noqa: ANN001
        return {"status": "success"}


class _FakeSimulator:
    """Stand-in for UserSimulator — never calls Gemini."""

    def __init__(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        pass

    async def first_turn(self) -> str:
        return "I'm curious about my calendar next Thursday."

    async def next_turn(self, agent_text: str):  # noqa: ANN001
        return "Still looking?", False


@pytest.fixture
def temp_runs_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    runs = tmp_path / "runs"
    reports = tmp_path / "reports"
    runs.mkdir()
    reports.mkdir()
    monkeypatch.setattr(storage, "runs_root", lambda: runs)
    monkeypatch.setattr(storage, "reports_root", lambda: reports)
    return tmp_path


def test_runaway_scenario_aborts_to_timeout_record(
    temp_runs_root: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # A graph whose single turn never returns — the runaway signature.
    class _HangingGraph:
        async def ainvoke(self, graph_input, config=None):  # noqa: ANN001
            await asyncio.sleep(3600)

    monkeypatch.setattr(runner_mod, "appointment_graph", _HangingGraph())
    monkeypatch.setattr(runner_mod, "UserSimulator", _FakeSimulator)

    paths = RunPaths(run_id="20260606_000000__baseline__test__smoke", stage="baseline")
    paths.ensure_dirs()
    run_config = RunConfig(llm_provider="gemini", llm_model="gemini-2.5-flash", llm_temperature=0.7)

    record = asyncio.run(
        ScenarioRunner().run_once(
            _SCENARIO,
            rep_index=1,
            bridge=_FakeBridge(),
            gemini_client=None,
            paths=paths,
            run_config=run_config,
            stage="baseline",
            change_note=None,
            max_turns=12,
            scenario_timeout_s=0.2,  # trips almost immediately
        )
    )

    assert record.termination_reason == "timeout"
    assert record.error and "wall-clock" in record.error
    # The record is still valid and enriched (run can continue to the next scenario).
    assert record.derived is not None
    assert record.derived.booked is False
