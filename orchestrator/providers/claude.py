"""Claude provider — wraps anthropic.messages.create with @traceable."""

import time

import anthropic
from langsmith import traceable

from orchestrator.providers.base import LLMResult


def _extract_token_counts(response) -> tuple[int | None, int | None]:
    """Best-effort extraction of input/output token counts from a Claude response."""
    usage = getattr(response, "usage", None)
    if usage is None:
        return None, None
    return getattr(usage, "input_tokens", None), getattr(usage, "output_tokens", None)


@traceable(name="claude_function_calling", run_type="llm")
def call_claude(
    client: anthropic.Anthropic,
    model: str,
    messages: list[dict],
    system: str,
    tools: list[dict],
) -> LLMResult:
    """Call Claude and return a standardised LLMResult.

    Claude returns content blocks with distinct types:
    - {"type": "tool_use", "name": ..., "input": ...} — tool call
    - {"type": "text", "text": ...} — text response
    Clean separation — no scanning needed.
    """
    started = time.perf_counter()
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=system,
        messages=messages,
        tools=tools,
    )
    latency_ms = (time.perf_counter() - started) * 1000.0
    input_tokens, output_tokens = _extract_token_counts(response)

    tool_use_block = next(
        (block for block in response.content if block.type == "tool_use"),
        None,
    )

    if tool_use_block:
        return LLMResult(
            has_tool_call=True,
            tool_name=tool_use_block.name,
            tool_args=dict(tool_use_block.input),
            text_response=None,
            raw_response=response,
            provider="claude",
            model_used=model,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
        )
    text = "\n".join(block.text for block in response.content if block.type == "text")
    return LLMResult(
        has_tool_call=False,
        tool_name=None,
        tool_args=None,
        text_response=text,
        raw_response=response,
        provider="claude",
        model_used=model,
        latency_ms=latency_ms,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
    )
