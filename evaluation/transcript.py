"""Render a ConversationRecord to a human-readable markdown transcript.

The transcript is the judge-facing view (Section 7a) and the primary
artifact a developer reads when analysing an ad-hoc Chainlit session.

Design choices:
- Plain markdown — viewable on GitHub and inside Chainlit.
- Tool calls and LLM calls go into ``<details>`` blocks so the conversation
  itself reads cleanly while still letting the reader expand into the
  internals.
- JSON payloads are pretty-printed with two-space indent.
"""

from __future__ import annotations

import json
from typing import Any

from evaluation.schemas import ConversationRecord, TurnRecord


def _fmt_json(value: Any) -> str:
    """Pretty-print a value as JSON with a graceful fallback for non-JSON types."""
    try:
        return json.dumps(value, indent=2, ensure_ascii=False, default=str)
    except Exception:
        return str(value)


def _fmt_ms(value: float | None) -> str:
    return f"{value:.1f} ms" if value is not None else "—"


def _fmt_int(value: int | None) -> str:
    return str(value) if value is not None else "—"


def render(record: ConversationRecord) -> str:
    """Render a ConversationRecord as markdown."""
    lines: list[str] = []
    _render_header(record, lines)
    for turn in record.turns:
        _render_turn(turn, lines)
    _render_footer(record, lines)
    return "\n".join(lines).rstrip() + "\n"


# ---------------------------------------------------------------------------
# Sections
# ---------------------------------------------------------------------------


def _render_header(record: ConversationRecord, lines: list[str]) -> None:
    lines.append(f"# Conversation — {record.scenario_id}")
    lines.append("")
    lines.append(f"- **Run id:** `{record.run_id}`")
    lines.append(f"- **Stage:** `{record.stage}`")
    lines.append(f"- **Tier:** `{record.tier}`")
    if record.persona_profile:
        lines.append(f"- **Persona:** `{record.persona_profile}`")
    lines.append(f"- **Started:** {record.timestamp_start.isoformat()}")
    if record.timestamp_end:
        lines.append(f"- **Ended:** {record.timestamp_end.isoformat()}")
    lines.append(
        f"- **Provider:** `{record.config.llm_provider}` "
        f"(model `{record.config.llm_model}`, temp `{record.config.llm_temperature}`)"
    )
    lines.append(f"- **Git commit:** `{record.git_commit[:12]}`"
                 f"{' (dirty)' if record.git_dirty else ''}")
    if record.change_note:
        lines.append(f"- **Change note:** {record.change_note}")
    if record.frozen_phrasing:
        lines.append(f"- **Frozen phrasing:** {record.frozen_phrasing!r}")
    if record.langsmith_trace_url:
        lines.append(f"- **LangSmith trace:** {record.langsmith_trace_url}")
    elif record.langsmith_trace_id:
        lines.append(f"- **LangSmith trace id:** `{record.langsmith_trace_id}`")
    lines.append("")


def _render_turn(turn: TurnRecord, lines: list[str]) -> None:
    lines.append(f"## Turn {turn.turn_index}")
    lines.append(f"_{turn.timestamp.isoformat()}_  ·  duration {_fmt_ms(turn.turn_duration_ms)}")
    lines.append("")

    if turn.user_message is not None:
        lines.append("**User:**")
        lines.append("")
        lines.append("> " + turn.user_message.replace("\n", "\n> "))
        lines.append("")

    # Interleave: agent response after tool/LLM details so the reader sees
    # the agent's user-facing words first; details below.
    if turn.agent_response:
        lines.append("**Agent:**")
        lines.append("")
        lines.append("> " + turn.agent_response.replace("\n", "\n> "))
        lines.append("")

    for idx, call in enumerate(turn.tool_calls, start=1):
        outcome = "✓" if call.success else "✗"
        lines.append(
            f"<details><summary>Tool call #{idx}: <code>{call.tool_name}</code> "
            f"{outcome}  ·  actual {_fmt_ms(call.actual_latency_ms)}  ·  "
            f"simulated {_fmt_ms(call.simulated_latency_ms)}</summary>"
        )
        lines.append("")
        lines.append("**Parameters**")
        lines.append("")
        lines.append("```json")
        lines.append(_fmt_json(call.parameters))
        lines.append("```")
        lines.append("")
        lines.append("**Response**")
        lines.append("")
        lines.append("```json")
        lines.append(_fmt_json(call.response))
        lines.append("```")
        if call.error_message:
            lines.append("")
            lines.append(f"**Error:** {call.error_message}")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    for idx, call in enumerate(turn.llm_calls, start=1):
        header_extra = f" → `{call.function_name}`" if call.function_name else ""
        lines.append(
            f"<details><summary>LLM call #{idx}: <code>{call.provider}</code> "
            f"({call.response_type}){header_extra}  ·  {_fmt_ms(call.latency_ms)}  ·  "
            f"in {_fmt_int(call.input_tokens)} / out {_fmt_int(call.output_tokens)} tokens</summary>"
        )
        lines.append("")
        lines.append(f"- model: `{call.model}`")
        lines.append(f"- prompt messages: `{call.prompt_message_count}`")
        if call.temperature is not None:
            lines.append(f"- temperature: `{call.temperature}`")
        if call.function_args is not None:
            lines.append("")
            lines.append("**Function args**")
            lines.append("")
            lines.append("```json")
            lines.append(_fmt_json(call.function_args))
            lines.append("```")
        if call.text_preview:
            lines.append("")
            lines.append("**Text preview**")
            lines.append("")
            lines.append("```")
            lines.append(call.text_preview)
            lines.append("```")
        lines.append("")
        lines.append("</details>")
        lines.append("")

    if turn.state_snapshot:
        lines.append("<details><summary>State snapshot</summary>")
        lines.append("")
        lines.append("```json")
        lines.append(_fmt_json(turn.state_snapshot))
        lines.append("```")
        lines.append("")
        lines.append("</details>")
        lines.append("")


def _render_footer(record: ConversationRecord, lines: list[str]) -> None:
    lines.append("---")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    if record.termination_reason:
        lines.append(f"- **Termination:** `{record.termination_reason}`")
    if record.error:
        lines.append(f"- **Error:** {record.error}")
    derived = record.derived
    if derived is not None:
        lines.append(f"- **Turns:** {derived.total_turn_count}")
        lines.append(f"- **MCP calls:** {derived.total_mcp_calls} "
                     f"({derived.availability_calls} check_availability)")
        lines.append(f"- **Booked:** {'yes' if derived.booked else 'no'}")
        lines.append(f"- **Simulated latency total:** {_fmt_ms(derived.total_simulated_latency_ms)}")
        lines.append(f"- **Actual latency total:** {_fmt_ms(derived.total_actual_latency_ms)}")
        if derived.parse_accuracy_score is not None:
            lines.append(f"- **Parse accuracy:** {derived.parse_accuracy_score:.2f}")
        if derived.unsupported_facts_count:
            lines.append(f"- **Unsupported facts:** {derived.unsupported_facts_count}")
    if record.judge_scores:
        lines.append("")
        lines.append("### Judge scores")
        lines.append("")
        for js in record.judge_scores:
            lines.append(
                f"- rep {js.rep_index} — temporal {js.temporal_understanding}/5, "
                f"negotiation {js.negotiation_effectiveness}/5, "
                f"efficiency {js.conversational_efficiency}/5, "
                f"recovery {js.recovery_quality if js.recovery_quality is not None else '—'}"
            )
    lines.append("")


__all__ = ["render"]
