"""Unit tests for pure helper functions in evaluation.runner.

These tests exercise _resolve_override and _sample_scenarios without
starting the MCP server, Gemini client, or LangGraph graph.
"""

from datetime import date, timedelta

import pytest

from evaluation.runner import _resolve_override, _sample_scenarios


class TestResolveOverride:
    def test_today_plus_n(self):
        today = date(2026, 5, 24)
        result = _resolve_override({"today+2": ["09:00-10:00"]}, today=today)
        assert result == {"2026-05-26": ["09:00-10:00"]}

    def test_today_plus_zero(self):
        today = date(2026, 5, 24)
        result = _resolve_override({"today+0": ["10:00-11:00"]}, today=today)
        assert result == {"2026-05-24": ["10:00-11:00"]}

    def test_today_minus_n(self):
        today = date(2026, 5, 24)
        result = _resolve_override({"today-1": ["09:00-10:00"]}, today=today)
        assert result == {"2026-05-23": ["09:00-10:00"]}

    def test_today_key(self):
        today = date(2026, 5, 24)
        result = _resolve_override({"today": ["11:00-12:00"]}, today=today)
        assert result == {"2026-05-24": ["11:00-12:00"]}

    def test_literal_iso_date_passes_through(self):
        today = date(2026, 5, 24)
        result = _resolve_override({"2026-06-01": ["09:00-10:00"]}, today=today)
        assert result == {"2026-06-01": ["09:00-10:00"]}

    def test_multiple_keys(self):
        today = date(2026, 5, 24)
        inp = {
            "today+1": ["09:00-10:00"],
            "today+3": ["14:00-15:00", "15:00-16:00"],
        }
        result = _resolve_override(inp, today=today)
        assert set(result.keys()) == {"2026-05-25", "2026-05-27"}
        assert result["2026-05-25"] == ["09:00-10:00"]
        assert len(result["2026-05-27"]) == 2

    def test_empty_input(self):
        result = _resolve_override({}, today=date(2026, 5, 24))
        assert result == {}

    def test_uses_date_today_when_no_ref(self):
        """Without an explicit today, the function should not raise."""
        result = _resolve_override({"today+2": ["09:00-10:00"]})
        assert len(result) == 1
        # Key should be a valid ISO date
        key = list(result.keys())[0]
        assert date.fromisoformat(key) == date.today() + timedelta(days=2)


class TestSampleScenarios:
    """Tests for _sample_scenarios using synthetic scenario data."""

    @staticmethod
    def _make_scenarios(tier: int, count: int) -> list[dict]:
        return [
            {"scenario_id": f"t{tier}_scen_{i:03d}", "tier": tier}
            for i in range(count)
        ]

    def test_smoke_profile_max_per_tier(self):
        scenarios_by_tier = {
            1: self._make_scenarios(1, 10),
            2: self._make_scenarios(2, 10),
            3: self._make_scenarios(3, 10),
        }
        profile = {
            "tiers": [1, 2, 3],
            "max_per_tier": 2,
            "include_ids": [],
            "exclude_ids": [],
            "seed": 17,
            "reps": 1,
        }
        runs = _sample_scenarios(profile, scenarios_by_tier)
        assert len(runs) <= 6  # 3 tiers × 2 per tier

        # Each tier should have ≤ 2 scenarios
        tiers_seen: dict[int, int] = {}
        for scenario, reps in runs:
            t = scenario["tier"]
            tiers_seen[t] = tiers_seen.get(t, 0) + 1
        for count in tiers_seen.values():
            assert count <= 2

    def test_include_ids_takes_precedence(self):
        scenarios_by_tier = {1: self._make_scenarios(1, 10)}
        # Only these two IDs should be included, ignoring max_per_tier
        profile = {
            "tiers": [1],
            "max_per_tier": 1,
            "include_ids": ["t1_scen_003", "t1_scen_007"],
            "exclude_ids": [],
            "seed": 42,
            "reps": 1,
        }
        runs = _sample_scenarios(profile, scenarios_by_tier)
        selected_ids = {s["scenario_id"] for s, _ in runs}
        assert selected_ids == {"t1_scen_003", "t1_scen_007"}

    def test_exclude_ids_removes_scenarios(self):
        scenarios_by_tier = {1: self._make_scenarios(1, 5)}
        profile = {
            "tiers": [1],
            "max_per_tier": 100,
            "include_ids": [],
            "exclude_ids": ["t1_scen_000", "t1_scen_002"],
            "seed": 42,
            "reps": 1,
        }
        runs = _sample_scenarios(profile, scenarios_by_tier)
        selected_ids = {s["scenario_id"] for s, _ in runs}
        assert "t1_scen_000" not in selected_ids
        assert "t1_scen_002" not in selected_ids
        assert len(selected_ids) == 3

    def test_reps_applied_per_scenario(self):
        scenarios_by_tier = {1: self._make_scenarios(1, 3)}
        profile = {
            "tiers": [1],
            "max_per_tier": 100,
            "include_ids": [],
            "exclude_ids": [],
            "seed": 42,
            "reps": 3,
        }
        runs = _sample_scenarios(profile, scenarios_by_tier)
        for _, reps in runs:
            assert reps == 3

    def test_deterministic_across_calls_with_same_seed(self):
        scenarios_by_tier = {1: self._make_scenarios(1, 20)}
        profile = {
            "tiers": [1],
            "max_per_tier": 5,
            "include_ids": [],
            "exclude_ids": [],
            "seed": 99,
            "reps": 1,
        }
        runs1 = _sample_scenarios(profile, scenarios_by_tier)
        runs2 = _sample_scenarios(profile, scenarios_by_tier)
        ids1 = [s["scenario_id"] for s, _ in runs1]
        ids2 = [s["scenario_id"] for s, _ in runs2]
        assert ids1 == ids2

    def test_empty_tier_handled_gracefully(self):
        scenarios_by_tier: dict[int, list[dict]] = {1: [], 2: self._make_scenarios(2, 3)}
        profile = {
            "tiers": [1, 2],
            "max_per_tier": 10,
            "include_ids": [],
            "exclude_ids": [],
            "seed": 42,
            "reps": 1,
        }
        runs = _sample_scenarios(profile, scenarios_by_tier)
        tiers = {s["tier"] for s, _ in runs}
        assert 2 in tiers
        assert 1 not in tiers  # empty tier skipped
