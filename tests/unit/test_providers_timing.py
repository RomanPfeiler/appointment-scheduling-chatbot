"""Unit tests for provider + bridge timing/token instrumentation.

Mocks the SDKs so the tests are hermetic and fast. Verifies:
- ``call_gemini`` returns ``latency_ms`` populated and reads token counts
  off ``response.usage_metadata``.
- ``call_claude`` does the same off ``response.usage``.
- ``MCPBridge.call_tool_with_metrics`` reports ``actual_latency_ms``
  reflecting the underlying call duration, and computes simulated latency
  per the EVALUATION_FRAMEWORK.md §9 model when ``simulate_latency=True``.
"""

from __future__ import annotations

import asyncio
import time
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from orchestrator import mcp_bridge as mcp_bridge_module
from orchestrator.mcp_bridge import (
    MCPBridge,
    _compute_simulated_latency_ms,
    _days_queried,
)
from orchestrator.providers.claude import call_claude
from orchestrator.providers.gemini import call_gemini


# ---------------------------------------------------------------------------
# Gemini
# ---------------------------------------------------------------------------


def _fake_gemini_response_text(text: str, prompt_tokens: int, completion_tokens: int):
    part = SimpleNamespace(text=text, function_call=None, thought=False)
    candidate = SimpleNamespace(content=SimpleNamespace(parts=[part]))
    usage = SimpleNamespace(prompt_token_count=prompt_tokens, candidates_token_count=completion_tokens)
    return SimpleNamespace(candidates=[candidate], usage_metadata=usage)


def test_call_gemini_records_latency_and_tokens(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_generate(*, model, contents, config):
        time.sleep(0.02)  # 20ms
        return _fake_gemini_response_text("hello", 100, 5)

    fake_client = MagicMock()
    fake_client.models.generate_content.side_effect = fake_generate

    result = call_gemini(fake_client, "gemini-2.5-flash", [], SimpleNamespace(temperature=0.5))

    assert result.has_tool_call is False
    assert result.text_response == "hello"
    assert result.input_tokens == 100
    assert result.output_tokens == 5
    assert result.model_used == "gemini-2.5-flash"
    assert result.latency_ms is not None
    assert result.latency_ms >= 15  # ~20ms ±jitter, leaving generous margin


def test_call_gemini_handles_none_content(monkeypatch: pytest.MonkeyPatch) -> None:
    """Gemini Flash sometimes returns a candidate with content=None (safety
    filter trim, MAX_TOKENS, or transient glitch). The provider must treat it
    as an empty text response rather than crashing on `None.parts`."""
    def fake_generate(*, model, contents, config):
        candidate = SimpleNamespace(content=None, finish_reason="SAFETY")
        return SimpleNamespace(candidates=[candidate], usage_metadata=None)

    fake_client = MagicMock()
    fake_client.models.generate_content.side_effect = fake_generate
    result = call_gemini(fake_client, "gemini-2.5-flash", [], SimpleNamespace(temperature=0.5))
    assert result.has_tool_call is False
    assert result.text_response == ""
    assert result.latency_ms is not None


def test_call_gemini_handles_empty_parts(monkeypatch: pytest.MonkeyPatch) -> None:
    """Same as above but with content present and parts=None — the other
    flavour of the same bug ('NoneType' object is not iterable)."""
    def fake_generate(*, model, contents, config):
        candidate = SimpleNamespace(content=SimpleNamespace(parts=None), finish_reason="MAX_TOKENS")
        return SimpleNamespace(candidates=[candidate], usage_metadata=None)

    fake_client = MagicMock()
    fake_client.models.generate_content.side_effect = fake_generate
    result = call_gemini(fake_client, "gemini-2.5-flash", [], SimpleNamespace(temperature=0.5))
    assert result.has_tool_call is False
    assert result.text_response == ""


def test_call_gemini_handles_missing_usage_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_generate(*, model, contents, config):
        part = SimpleNamespace(text="hi", function_call=None, thought=False)
        candidate = SimpleNamespace(content=SimpleNamespace(parts=[part]))
        return SimpleNamespace(candidates=[candidate])  # no usage_metadata

    fake_client = MagicMock()
    fake_client.models.generate_content.side_effect = fake_generate
    result = call_gemini(fake_client, "gemini-2.5-flash", [], SimpleNamespace(temperature=0.5))
    assert result.input_tokens is None
    assert result.output_tokens is None
    assert result.latency_ms is not None  # latency still recorded


# ---------------------------------------------------------------------------
# Claude
# ---------------------------------------------------------------------------


def test_call_claude_records_latency_and_tokens() -> None:
    text_block = SimpleNamespace(type="text", text="hi there")
    usage = SimpleNamespace(input_tokens=42, output_tokens=8)
    response = SimpleNamespace(content=[text_block], usage=usage)

    def fake_create(**kwargs):
        time.sleep(0.02)
        return response

    fake_client = MagicMock()
    fake_client.messages.create.side_effect = fake_create

    result = call_claude(fake_client, "claude-sonnet-4-20250514", [], system="", tools=[])
    assert result.has_tool_call is False
    assert result.text_response == "hi there"
    assert result.input_tokens == 42
    assert result.output_tokens == 8
    assert result.model_used == "claude-sonnet-4-20250514"
    assert result.latency_ms is not None
    assert result.latency_ms >= 15


# ---------------------------------------------------------------------------
# MCPBridge.call_tool_with_metrics
# ---------------------------------------------------------------------------


def test_days_queried_handles_same_day_window() -> None:
    args = {
        "start_datetime": "2026-05-25T08:00:00+02:00",
        "end_datetime": "2026-05-25T17:00:00+02:00",
    }
    assert _days_queried(args) == 1


def test_days_queried_handles_three_day_window() -> None:
    args = {
        "start_datetime": "2026-05-25T08:00:00+02:00",
        "end_datetime": "2026-05-27T17:00:00+02:00",
    }
    assert _days_queried(args) == 3


def test_days_queried_defaults_to_one_when_dates_missing() -> None:
    assert _days_queried({}) == 1


def test_compute_simulated_latency_check_availability_uses_days() -> None:
    model = {"base_overhead_ms": 400.0, "per_day_cost_ms": 500.0, "jitter_sigma_ms": 0.0}
    args = {
        "start_datetime": "2026-05-25T08:00:00+02:00",
        "end_datetime": "2026-05-27T17:00:00+02:00",
    }
    lat = _compute_simulated_latency_ms("check_availability", args, model)
    # 400 + 500*3 + 0 = 1900
    assert lat == pytest.approx(1900.0, abs=1.0)


def test_compute_simulated_latency_other_tools_use_base_only() -> None:
    model = {"base_overhead_ms": 400.0, "per_day_cost_ms": 500.0, "jitter_sigma_ms": 0.0}
    lat = _compute_simulated_latency_ms("get_appointment_topics", {}, model)
    assert lat == pytest.approx(400.0, abs=1.0)


async def _fake_bridge_with_session(delay_seconds: float, response_value):
    """Build an MCPBridge whose session.call_tool sleeps then returns a response.

    Returns an object that mimics ``await self._session.call_tool(...)`` —
    namely a result with a ``content`` list of TextContent-shaped blocks.
    """
    bridge = MCPBridge(server_script_path="ignored")

    text_block = SimpleNamespace(text='{"status": "ok"}')

    class FakeSession:
        async def call_tool(self, tool_name, arguments):  # noqa: ARG002
            await asyncio.sleep(delay_seconds)
            return SimpleNamespace(content=[text_block])

    bridge._session = FakeSession()
    return bridge


@pytest.mark.asyncio
async def test_call_tool_with_metrics_reports_actual_latency() -> None:
    bridge = await _fake_bridge_with_session(delay_seconds=0.05, response_value=None)
    out = await bridge.call_tool_with_metrics("get_appointment_topics", {})
    assert out["success"] is True
    assert out["actual_latency_ms"] is not None
    assert out["actual_latency_ms"] >= 40  # ~50ms ±scheduler jitter
    assert out["simulated_latency_ms"] is None


@pytest.mark.asyncio
async def test_call_tool_with_metrics_applies_simulated_latency() -> None:
    bridge = await _fake_bridge_with_session(delay_seconds=0.0, response_value=None)
    model = {"base_overhead_ms": 100.0, "per_day_cost_ms": 0.0, "jitter_sigma_ms": 0.0}
    out = await bridge.call_tool_with_metrics(
        "get_appointment_topics",
        {},
        latency_model=model,
        simulate_latency=True,
    )
    assert out["simulated_latency_ms"] == pytest.approx(100.0, abs=1.0)
    # Wall clock paid the simulated cost on top of the (~0) underlying delay.
    assert out["actual_latency_ms"] is not None


@pytest.mark.asyncio
async def test_call_tool_with_metrics_marks_error_response_unsuccessful(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bridge = MCPBridge(server_script_path="ignored")

    async def fake_call_tool(self, tool_name, arguments):  # noqa: ARG001
        return {"status": "error", "message": "boom"}

    monkeypatch.setattr(MCPBridge, "call_tool", fake_call_tool)
    out = await bridge.call_tool_with_metrics("check_availability", {})
    assert out["success"] is False
    assert out["response"]["message"] == "boom"


# Touch the imported module to keep linters happy when the global mock module
# import isn't otherwise used.
assert hasattr(mcp_bridge_module, "MCPBridge")
