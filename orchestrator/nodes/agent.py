"""Agent node: calls the active LLM provider and processes the response."""

import asyncio
import logging
import os
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

from google import genai
from google.genai import types
from langchain_core.runnables import RunnableConfig

from orchestrator.prompts import load_prompt
from orchestrator.providers import (
    LLMResult,
    call_gemini,
    gemini_messages_to_claude,
)
from orchestrator.state import ConversationState
from orchestrator.tool_defs import CLAUDE_TOOLS, get_tool_declarations

logger = logging.getLogger(__name__)


_STATIC_SYSTEM_PROMPT = load_prompt("appointment_assistant")
_ZURICH = ZoneInfo("Europe/Zurich")

CLAUDE_MODEL = "claude-sonnet-4-20250514"


_SPEC_GUIDANCE = {
    "exact_time": "tight 1-hour window; do not pad",
    "day_specific": "single-day window; expand to adjacent days only on empty",
    "day_vague": "single-day window; expand to adjacent days on empty",
    "multi_day_vague": "use 3-day max window immediately (MCP cap)",
    "compound": "one check_availability call per range, do not merge",
}


def _format_nlp_hints(annotation: dict) -> str:
    """Render the NLP HINTS block appended to the runtime context.

    Empty string when annotation carries nothing actionable, so the block
    only appears when the NLP layer actually contributed something.
    """
    lines: list[str] = []
    topic = annotation.get("topic")
    medium = annotation.get("contact_medium")
    ranges = annotation.get("datetime_ranges") or []
    is_compound = bool((annotation.get("entities_raw") or {}).get("compound"))

    if not (topic or medium or ranges):
        return ""

    lines.append(
        "NLP HINTS for this user message (use these to set window width and "
        "save asking, but the user's text is the source of truth — never invent slots):"
    )
    if topic:
        lines.append(f"- topic: {topic} (extracted)")
    if medium:
        lines.append(f"- contact_medium: {medium} (extracted)")
    for rng in ranges:
        spec = rng.get("specificity", "day_vague")
        guidance = _SPEC_GUIDANCE.get(spec, "")
        lines.append(
            f"- datetime range: {rng.get('start_datetime')} to "
            f"{rng.get('end_datetime')} "
            f"(text: {rng.get('original_text')!r}, specificity: {spec} — {guidance})"
        )
    if is_compound:
        lines.append("- compound request: one check_availability call per range, do not merge.")
    return "\n".join(lines) + "\n\n"


def _build_system_prompt(
    now: datetime | None = None,
    annotation: dict | None = None,
) -> str:
    """Prepend a runtime-context block (today's date + current Zurich offset)
    to the static system prompt. Optionally append NLP HINTS from the annotate
    node (only when the NLP layer is enabled and contributed something).

    Gemini and Claude both benefit from being told the current date and DST
    state explicitly — without this block, they fall back on training-data
    priors and frequently hallucinate 2024 dates or the `+01:00` offset on
    summer dates (observed in the first baseline run).
    """
    now = now or datetime.now(_ZURICH)
    local = now.astimezone(_ZURICH)
    offset_seconds = local.utcoffset().total_seconds() if local.utcoffset() else 0
    offset_hours = int(offset_seconds // 3600)
    sign = "+" if offset_hours >= 0 else "-"
    offset_label = f"{sign}{abs(offset_hours):02d}:00"
    dst_name = "CEST" if offset_hours == 2 else "CET"
    runtime_block = (
        "RUNTIME CONTEXT (computed for this turn — trust it over any training-data assumption):\n"
        f"- Today is {local.strftime('%A, %Y-%m-%d')} ({local.strftime('%d %B %Y')}).\n"
        f"- Europe/Zurich is currently in {dst_name} ({offset_label}).\n"
        f"- Use {offset_label} as the ISO 8601 timezone offset for all `check_availability` and "
        "`book_appointment` datetime parameters this turn, unless the user names a different timezone.\n"
        "\n"
    )
    if annotation:
        runtime_block += _format_nlp_hints(annotation)
    return runtime_block + _STATIC_SYSTEM_PROMPT


def _reference_now_from_config(config: RunnableConfig) -> datetime | None:
    """Build the agent's injected "today" from a ``reference_date`` in config.

    The evaluation runner passes ``config["configurable"]["reference_date"]`` (an
    ISO date string) so the agent anchors all date arithmetic to the scenario's
    pinned clock rather than the wall clock (EVALUATION_FRAMEWORK §3a). Returns a
    tz-aware Europe/Zurich datetime at midday on that date, or ``None`` when no
    reference_date is set (production / ad-hoc), so the prompt uses real now.
    """
    ref_iso = (config.get("configurable") or {}).get("reference_date")
    if not ref_iso:
        return None
    try:
        rd = date.fromisoformat(ref_iso)
    except (ValueError, TypeError):
        logger.warning("Ignoring unparseable reference_date %r in config", ref_iso)
        return None
    return datetime(rd.year, rd.month, rd.day, 12, 0, tzinfo=_ZURICH)


# Backwards-compat alias for code that imports SYSTEM_PROMPT directly (e.g. tests).
SYSTEM_PROMPT = _STATIC_SYSTEM_PROMPT


async def agent_node(state: ConversationState, config: RunnableConfig) -> dict:
    """Call the active LLM provider with the conversation history and tool declarations.

    If the previous execute node wrote a tool_result into state, this node
    first wraps it as a function_response Content and appends it to the
    messages before calling the LLM.

    Returns a state update with either:
    - ``pending_tool_call`` set (LLM wants to call a tool), or
    - ``pending_tool_call`` cleared (LLM returned a text response for the user).

    If ``config["configurable"]["recorder"]`` is present, the LLM call is
    also recorded into the evaluation ConversationRecord with timing and
    token counts.
    """
    provider: str = config["configurable"].get("llm_provider", "gemini")
    model: str = config["configurable"].get("model", "gemini-2.5-flash")
    temperature: float = config["configurable"].get("temperature", 0.7)
    # Agent-loop thinking budget (Gemini only). Default -1 (dynamic thinking ON)
    # is the standing config every anchor run used (ARCHITECTURE §8 2026-03-22
    # correction); the evaluation runner overrides it per stage — the weak-agent
    # stages run with 0 (ARCHITECTURE §8 2026-06-10).
    thinking_budget: int = config["configurable"].get("thinking_budget", -1)
    recorder = config["configurable"].get("recorder")

    # Start with the existing message history.
    all_messages: list[types.Content] = list(state["messages"])

    # Track any extra Content objects we build here so they can be persisted to
    # LangGraph state alongside the model's response.  Gemini's API requires a
    # strict function_call -> function_response alternation; if function_response
    # is only appended to the local `all_messages` list (and not returned) it
    # will be missing from state on the next turn, causing a 400 error.
    extra_messages_for_state: list[types.Content] = []

    if state.get("tool_result") is not None:
        tool_result = state["tool_result"]
        # Gemini's FunctionResponse requires `response` to be a dict.
        # When the MCP tool returns a list (e.g. multiple topics), wrap it.
        response_payload = tool_result["response"]
        if not isinstance(response_payload, dict):
            response_payload = {"result": response_payload}
        function_response_part = types.Part.from_function_response(
            name=tool_result["name"],
            response=response_payload,
        )
        function_response_content = types.Content(
            role="user",
            parts=[function_response_part],
        )
        all_messages.append(function_response_content)
        # Must be saved to state so the history stays consistent for future turns.
        extra_messages_for_state.append(function_response_content)

    # --- Call the active provider ---
    # Build the per-turn system prompt with current date + Zurich offset so the
    # model cannot fall back to training-data priors for dates/timezones.
    # When the NLP layer is enabled, the annotate node has populated
    # ``state["last_annotation"]`` and the prompt also carries NLP HINTS.
    #
    # During an evaluation scenario-run the runner injects ``reference_date`` so
    # the agent's notion of "today" is the scenario's pinned clock — this is what
    # keeps weekday phrasings ("next Tuesday") aligned with the availability
    # override's ``today+N`` offsets (EVALUATION_FRAMEWORK §3a). In production
    # nobody sets it, so the prompt falls back to the real wall clock unchanged.
    reference_now = _reference_now_from_config(config)
    system_prompt = _build_system_prompt(
        now=reference_now, annotation=state.get("last_annotation")
    )

    if provider == "claude":
        # Lazy import: the Claude provider is retained as code but no longer
        # user-facing. Importing it here (not at module load) keeps the deployed
        # Gemini-only app free of the ``anthropic`` dependency.
        from orchestrator.providers.claude import call_claude

        claude_client = config["configurable"]["claude_client"]
        claude_messages = gemini_messages_to_claude(all_messages)
        logger.debug("Calling Claude with %d messages", len(claude_messages))
        llm_result: LLMResult = await asyncio.to_thread(
            call_claude,
            claude_client,
            CLAUDE_MODEL,
            claude_messages,
            system_prompt,
            CLAUDE_TOOLS,
        )
    else:
        client: genai.Client = config["configurable"]["gemini_client"]
        gen_config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
            tools=[get_tool_declarations()],
            thinking_config=types.ThinkingConfig(thinking_budget=thinking_budget),
        )
        logger.debug("Calling Gemini model=%s with %d messages", model, len(all_messages))
        llm_result = await asyncio.to_thread(
            call_gemini,
            client,
            model,
            all_messages,
            gen_config,
        )

    # --- Build provider-agnostic state update ---
    # For message history, keep Gemini Content format as the canonical store.
    # When provider is Claude, we build a synthetic Content object so the rest
    # of the pipeline (app.py text extraction, execute_node) works unchanged.
    if provider == "gemini":
        candidates = getattr(llm_result.raw_response, "candidates", None) or []
        response_content = candidates[0].content if candidates else None
        if response_content is None or not getattr(response_content, "parts", None):
            # Provider already logged this — synthesise an empty-text Content so
            # the message history stays a valid alternating sequence for the
            # next turn (Gemini's API rejects a history with None content).
            response_content = types.Content(
                role="model",
                parts=[types.Part.from_text(text="")],
            )
        new_messages = extra_messages_for_state + [response_content]
    else:
        # Build a Gemini-compatible Content object from Claude's response.
        if llm_result.has_tool_call:
            # Synthetic function_call Content so execute_node flow is unchanged.
            parts = [types.Part.from_function_call(
                name=llm_result.tool_name,
                args=llm_result.tool_args or {},
            )]
            response_content = types.Content(role="model", parts=parts)
        else:
            parts = [types.Part.from_text(text=llm_result.text_response or "")]
            response_content = types.Content(role="model", parts=parts)
        new_messages = extra_messages_for_state + [response_content]

    if llm_result.has_tool_call:
        logger.info("%s requested tool call: %s(%s)", provider.title(), llm_result.tool_name, llm_result.tool_args)
        debug_record = {
            "node": "agent_node",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": f"{provider}_call",
            "details": {
                "provider": provider,
                "prompt_message_count": len(all_messages),
                "response_type": "function_call",
                "function_name": llm_result.tool_name,
                "function_args": llm_result.tool_args,
                "text_response_preview": None,
                "latency_ms": llm_result.latency_ms,
                "input_tokens": llm_result.input_tokens,
                "output_tokens": llm_result.output_tokens,
            },
        }
        if recorder is not None:
            recorder.record_llm_call(
                provider=provider,
                model=llm_result.model_used or model,
                prompt_message_count=len(all_messages),
                response_type="function_call",
                function_name=llm_result.tool_name,
                function_args=llm_result.tool_args,
                text_preview=None,
                latency_ms=llm_result.latency_ms,
                input_tokens=llm_result.input_tokens,
                output_tokens=llm_result.output_tokens,
                thoughts_tokens=llm_result.thoughts_tokens,
                temperature=temperature,
            )
        return {
            "messages": new_messages,
            "pending_tool_call": {"name": llm_result.tool_name, "args": llm_result.tool_args},
            "tool_result": None,
            "turn_count": state["turn_count"],
            "debug_log": [debug_record],
        }

    # --- Text response branch ---
    logger.info("%s returned text response (turn %d)", provider.title(), state["turn_count"] + 1)
    text_preview = (llm_result.text_response or "")[:200] or None
    debug_record = {
        "node": "agent_node",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "action": f"{provider}_call",
        "details": {
            "provider": provider,
            "prompt_message_count": len(all_messages),
            "response_type": "text",
            "function_name": None,
            "function_args": None,
            "text_response_preview": text_preview,
            "latency_ms": llm_result.latency_ms,
            "input_tokens": llm_result.input_tokens,
            "output_tokens": llm_result.output_tokens,
        },
    }
    if recorder is not None:
        recorder.record_llm_call(
            provider=provider,
            model=llm_result.model_used or model,
            prompt_message_count=len(all_messages),
            response_type="text",
            function_name=None,
            function_args=None,
            text_preview=text_preview,
            latency_ms=llm_result.latency_ms,
            input_tokens=llm_result.input_tokens,
            output_tokens=llm_result.output_tokens,
            thoughts_tokens=llm_result.thoughts_tokens,
            temperature=temperature,
        )
    return {
        "messages": new_messages,
        "pending_tool_call": None,
        "tool_result": None,
        "turn_count": state["turn_count"] + 1,
        "debug_log": [debug_record],
    }


def should_continue(state: ConversationState) -> str:
    """Conditional edge: route to 'execute' if there's a pending tool call, else 'end'."""
    decision = "execute" if state.get("pending_tool_call") is not None else "end"
    if os.getenv("DEBUG_LOG", "false").lower() == "true":
        print(f"  [ROUTE] should_continue -> {decision}")
    return decision
