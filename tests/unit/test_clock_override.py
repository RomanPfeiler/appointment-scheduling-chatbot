"""Unit tests for the scenario clock override (EVALUATION_FRAMEWORK §3a / §14).

``get_current_datetime`` returns the real wall clock by default; during an
evaluation scenario run the runner pins it to the scenario ``reference_date`` so
the agent's date arithmetic shares one clock with the availability override.
Without this the agent anchors on the real run-day and misses every override slot
whenever run-day != suite anchor (observed 2026-06-06: run-day 06-06 vs anchor
06-01). These tests cover set / use / clear / bad-input, and clock↔availability
override independence.
"""

from __future__ import annotations

from datetime import date

import pytest

from mcp_server import tools


@pytest.fixture(autouse=True)
def _clean_overrides():
    """Ensure each test starts and ends with no clock override set."""
    tools.admin_clear_clock_override()
    yield
    tools.admin_clear_clock_override()


def test_default_is_real_clock() -> None:
    """With no override, get_current_datetime tracks the real wall clock."""
    assert tools.get_current_datetime()["date"] == date.today().isoformat()


def test_override_pins_clock_to_reference_date() -> None:
    resp = tools.admin_set_clock_override("2026-06-01")
    assert resp["status"] == "ok"
    gc = tools.get_current_datetime()
    assert gc["date"] == "2026-06-01"
    assert gc["weekday"] == "Monday"  # the suite anchor is a Monday
    # Noon Europe/Zurich (CEST in June) — date arithmetic is the point, not the hour.
    assert gc["datetime"].startswith("2026-06-01T12:00:00+02:00")


def test_clear_reverts_to_real_clock() -> None:
    tools.admin_set_clock_override("2026-06-01")
    assert tools.get_current_datetime()["date"] == "2026-06-01"
    assert tools.admin_clear_clock_override()["status"] == "cleared"
    assert tools.get_current_datetime()["date"] == date.today().isoformat()


def test_bad_reference_date_returns_error_and_does_not_set() -> None:
    resp = tools.admin_set_clock_override("not-a-date")
    assert resp["status"] == "error"
    # A failed set must not pin the clock.
    assert tools.get_current_datetime()["date"] == date.today().isoformat()


def test_clock_override_independent_of_availability_override() -> None:
    """Setting/clearing the clock must not touch the availability override flag."""
    from mcp_server import mock_data

    mock_data.clear_availability_override()
    assert mock_data.is_override_active() is False
    tools.admin_set_clock_override("2026-06-01")
    assert mock_data.is_override_active() is False  # unchanged by the clock override
    tools.admin_clear_clock_override()
    assert mock_data.is_override_active() is False
