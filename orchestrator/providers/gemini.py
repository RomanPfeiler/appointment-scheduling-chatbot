"""Gemini provider — wraps google-genai's generate_content with @traceable."""

import logging
import re
import time

from google import genai
from google.genai import types
from langsmith import traceable

from orchestrator.providers.base import LLMResult

logger = logging.getLogger(__name__)

_MAX_RETRIES = 8


def _is_rate_limited(exc: Exception) -> bool:
    msg = str(exc)
    return "429" in msg or "RESOURCE_EXHAUSTED" in msg.upper()


def _parse_retry_delay(exc: Exception) -> float:
    """Return suggested retry delay in seconds from the 429 error message, +2s buffer."""
    m = re.search(r"retry in (\d+(?:\.\d+)?)s", str(exc), re.IGNORECASE)
    return float(m.group(1)) + 2.0 if m else 15.0


def _extract_token_counts(response) -> tuple[int | None, int | None, int | None]:
    """Best-effort extraction of input/output/thought token counts from a Gemini response.

    Returns ``(None, None, None)`` if usage metadata is missing — never raises.
    The thoughts count is the runtime evidence for the thinking-config assertion
    (ARCHITECTURE §8 2026-06-10): a thinking-off run must report no thought tokens.
    """
    usage = getattr(response, "usage_metadata", None)
    if usage is None:
        return None, None, None
    prompt = getattr(usage, "prompt_token_count", None)
    completion = getattr(usage, "candidates_token_count", None)
    thoughts = getattr(usage, "thoughts_token_count", None)
    return prompt, completion, thoughts


@traceable(name="gemini_function_calling", run_type="llm")
def call_gemini(
    client: genai.Client,
    model: str,
    contents: list,
    config: types.GenerateContentConfig,
) -> LLMResult:
    """Call Gemini and return a standardised LLMResult.

    Retries up to _MAX_RETRIES times on 429 RESOURCE_EXHAUSTED, sleeping for
    the delay suggested in the error response plus a 2-second buffer.
    """
    for attempt in range(_MAX_RETRIES):
        try:
            started = time.perf_counter()
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config,
            )
            break
        except Exception as exc:
            if _is_rate_limited(exc) and attempt < _MAX_RETRIES - 1:
                delay = _parse_retry_delay(exc)
                logger.warning(
                    "Gemini 429 on attempt %d/%d — sleeping %.1fs",
                    attempt + 1, _MAX_RETRIES, delay,
                )
                time.sleep(delay)
            else:
                raise
    latency_ms = (time.perf_counter() - started) * 1000.0

    candidates = getattr(response, "candidates", None) or []
    response_content = candidates[0].content if candidates else None
    input_tokens, output_tokens, thoughts_tokens = _extract_token_counts(response)
    # Record the model that actually answered (the API echoes its resolved
    # version), falling back to the requested id. Self-describing records are
    # the tripwire for "manifest says X but Y answered" measurement bugs.
    model_used = getattr(response, "model_version", None) or model

    # Gemini Flash occasionally returns a candidate with `content=None` or
    # `content.parts` empty/None (safety filter trims everything, MAX_TOKENS
    # hit before any visible part is emitted, or transient API glitch). The
    # SDK delivers this as a structurally valid response, so we have to guard
    # before iterating. Treat it as an empty text response — agent_node will
    # synthesise an empty Content for history, and the graph terminates cleanly
    # instead of crashing the whole conversation.
    parts = getattr(response_content, "parts", None) if response_content is not None else None
    if not parts:
        finish_reason = getattr(candidates[0], "finish_reason", None) if candidates else None
        logger.warning(
            "Gemini returned no usable parts (finish_reason=%s) — treating as empty text response",
            finish_reason,
        )
        return LLMResult(
            has_tool_call=False,
            tool_name=None,
            tool_args=None,
            text_response="",
            raw_response=response,
            provider="gemini",
            model_used=model_used,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            thoughts_tokens=thoughts_tokens,
        )

    # Scan ALL parts rather than assuming parts[0] is the answer, and skip
    # thought=True parts. This is load-bearing, not defensive: the agent loop
    # runs with thinking ON (thinking_budget=-1 — see ARCHITECTURE §8, the
    # 2026-03-22 correction), so thought parts and function calls share one
    # flat parts list in real responses.
    function_call_part = None
    text_part = None
    for p in parts:
        if function_call_part is None and hasattr(p, "function_call") and p.function_call:
            function_call_part = p
        if text_part is None and hasattr(p, "text") and p.text and not getattr(p, "thought", False):
            text_part = p

    if function_call_part:
        return LLMResult(
            has_tool_call=True,
            tool_name=function_call_part.function_call.name,
            tool_args=dict(function_call_part.function_call.args),
            text_response=None,
            raw_response=response,
            provider="gemini",
            model_used=model_used,
            latency_ms=latency_ms,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            thoughts_tokens=thoughts_tokens,
        )
    return LLMResult(
        has_tool_call=False,
        tool_name=None,
        tool_args=None,
        text_response=text_part.text if text_part else "",
        raw_response=response,
        provider="gemini",
        model_used=model_used,
        latency_ms=latency_ms,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        thoughts_tokens=thoughts_tokens,
    )
