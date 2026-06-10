"""
tests/integration/test_graph_e2e.py — End-to-end LangGraph integration tests.

Runs appointment_graph.ainvoke() with a MOCKED LLM provider that returns scripted
LLMResult objects. Catches:
- State-merge bugs (operator.add on messages / debug_log)
- Routing bugs (should_continue dispatching to execute vs end)
- Message-history corruption (function_call/function_response alternation)
- pending_tool_call lifecycle (set by agent_node, cleared by execute_node)

Uses a real MCPBridge so the execute_node leg exercises actual MCP tool calls.
Marked @pytest.mark.integration so they can be skipped during fast local
iteration: pytest -m "not integration".
"""

from contextlib import asynccontextmanager
from unittest.mock import patch

import pytest
from google.genai import types

from orchestrator.graph import appointment_graph
from orchestrator.mcp_bridge import MCPBridge
from orchestrator.providers import LLMResult
from orchestrator.state import default_state

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Bridge helper + LLMResult builders
# ---------------------------------------------------------------------------
#
# See tests/integration/test_mcp_roundtrip.py for why we use an
# asynccontextmanager instead of a pytest_asyncio fixture.


@asynccontextmanager
async def connected_bridge():
    b = MCPBridge(server_script_path="mcp_server/server.py")
    await b.connect()
    try:
        await b.call_tool("reset_bookings", {})
        yield b
    finally:
        await b.disconnect()


def _text_result(text: str) -> LLMResult:
    """Build an LLMResult that simulates a final text response from Gemini.

    The agent node reads `raw_response.candidates[0].content` to build the
    canonical message history, so we have to construct a minimally-shaped
    object that path can traverse.
    """
    response_content = types.Content(
        role="model",
        parts=[types.Part.from_text(text=text)],
    )
    # Fake the candidates[0].content path used in agent.py:126
    fake_response = type(
        "FakeResponse",
        (),
        {"candidates": [type("FakeCandidate", (), {"content": response_content})]},
    )
    return LLMResult(
        has_tool_call=False,
        tool_name=None,
        tool_args=None,
        text_response=text,
        raw_response=fake_response,
        provider="gemini",
    )


def _tool_call_result(name: str, args: dict) -> LLMResult:
    """Build an LLMResult that simulates a function_call from Gemini."""
    response_content = types.Content(
        role="model",
        parts=[types.Part.from_function_call(name=name, args=args)],
    )
    fake_response = type(
        "FakeResponse",
        (),
        {"candidates": [type("FakeCandidate", (), {"content": response_content})]},
    )
    return LLMResult(
        has_tool_call=True,
        tool_name=name,
        tool_args=args,
        text_response=None,
        raw_response=fake_response,
        provider="gemini",
    )


def _initial_state_with_user_msg(text: str) -> dict:
    """Return a fresh ConversationState with one user message appended."""
    state = default_state()
    user_msg = types.Content(role="user", parts=[types.Part.from_text(text=text)])
    state["messages"] = [user_msg]
    return state


def _config(bridge: MCPBridge) -> dict:
    """RunnableConfig payload matching what app.py builds."""
    return {
        "configurable": {
            "gemini_client": None,  # mocked away
            "claude_client": None,
            "mcp_bridge": bridge,
            "model": "fake-model",
            "temperature": 0,
            "llm_provider": "gemini",
        }
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_graph_terminates_on_text_response():
    """Single text response from the LLM should terminate the graph."""
    async with connected_bridge() as bridge:
        with patch(
            "orchestrator.nodes.agent.call_gemini",
            return_value=_text_result("Hi, I can help you book an appointment."),
        ):
            result = await appointment_graph.ainvoke(
                _initial_state_with_user_msg("hello"),
                config=_config(bridge),
            )

    assert result["pending_tool_call"] is None
    assert result["turn_count"] == 1
    # User message + model text response
    assert len(result["messages"]) == 2
    last = result["messages"][-1]
    assert getattr(last, "role", None) == "model"
    assert any(getattr(p, "text", "") for p in last.parts)


async def test_graph_executes_tool_then_responds():
    """Scripted LLM: first call returns function_call, second returns text.

    Verifies the full agent → execute → agent → end path: state mutates
    correctly, pending_tool_call is set and then cleared, tool_result is
    consumed, and debug_log accumulates one record per node invocation.
    """
    call_sequence = [
        _tool_call_result("get_appointment_topics", {}),
        _text_result("We offer Investing, Mortgage, and Pension consultations."),
    ]

    async with connected_bridge() as bridge:
        with patch(
            "orchestrator.nodes.agent.call_gemini",
            side_effect=call_sequence,
        ):
            result = await appointment_graph.ainvoke(
                _initial_state_with_user_msg("what can I book?"),
                config=_config(bridge),
            )

    # Final state: tool call consumed, response sent.
    assert result["pending_tool_call"] is None
    assert result["tool_result"] is None
    assert result["turn_count"] == 1

    # debug_log: 1 agent (function_call) + 1 execute (mcp_tool_call) + 1 agent (text) = 3
    actions = [rec["action"] for rec in result["debug_log"]]
    assert actions == ["gemini_call", "mcp_tool_call", "gemini_call"]

    # Final message must be a model text response.
    last = result["messages"][-1]
    assert getattr(last, "role", None) == "model"
    assert any(getattr(p, "text", "") for p in last.parts)


async def test_graph_message_history_alternates_correctly():
    """function_call must be followed by function_response in the history.

    Gemini's API rejects history that doesn't strictly alternate
    function_call → function_response. This test guards the message-shape
    contract that bit us before (see ARCHITECTURE.md Decision Log).
    """
    async with connected_bridge() as bridge:
        with patch(
            "orchestrator.nodes.agent.call_gemini",
            side_effect=[
                _tool_call_result("get_appointment_topics", {}),
                _text_result("Here are the options."),
            ],
        ):
            result = await appointment_graph.ainvoke(
                _initial_state_with_user_msg("show me topics"),
                config=_config(bridge),
            )

    # Expected sequence:
    #   [0] user text       (the original input)
    #   [1] model fn_call   (from first agent call)
    #   [2] user fn_resp    (built by agent_node when consuming tool_result)
    #   [3] model text      (from second agent call)
    msgs = result["messages"]
    assert len(msgs) == 4

    def has_function_call(m):
        return any(hasattr(p, "function_call") and p.function_call for p in m.parts)

    def has_function_response(m):
        return any(hasattr(p, "function_response") and p.function_response for p in m.parts)

    assert msgs[0].role == "user"
    assert msgs[1].role == "model" and has_function_call(msgs[1])
    assert msgs[2].role == "user" and has_function_response(msgs[2])
    assert msgs[3].role == "model"
