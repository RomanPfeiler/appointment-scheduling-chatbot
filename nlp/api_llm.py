"""API-LLM scaffolding for the Arm 3 NLP components (IMPROVEMENT_PLAN §7/§8 Arm 3).

A self-contained, lazy **Gemini** client used ONLY by the two NLP extraction tasks
(datetime parser Arm 3, entity extractor Arm 3). It is deliberately **separate**
from the agent loop's Gemini client (``orchestrator/providers/gemini.py``): the
factory builds NLP arms with no threaded client and the intrinsic-eval CLI has no
orchestrator config, so the NLP arm needs its own client. A bidirectional scope
guard (``tests/unit/test_local_llm_scope_guard.py``) enforces that this module and
the agent provider stack never import each other.

Design mirrors ``nlp/local_llm.py``:
- **Lazy process-lifetime singleton client** — built on the first call, never at
  import, so HF-Spaces secret injection has already happened by first use
  (CLAUDE.md).
- **JSON mode** — ``response_mime_type="application/json"`` + a JSON-Schema
  ``response_schema`` constrains the output server-side; the same proven pattern as
  ``evaluation/judge.py``. Deterministic (temperature 0, ``thinking_budget=0``).
- Each call records **real wall-clock ms** (distinct from the *simulated* latency
  KPI in EVALUATION_FRAMEWORK §9) for the API cost/latency data point; it must
  never feed model selection.
"""

from __future__ import annotations

import json
import logging
import os
import re
import statistics
import time
from typing import Any, Final

from google import genai
from google.genai import types
from langsmith import traceable

logger = logging.getLogger(__name__)

# Default model — the same family the agent loop uses ("already in the stack").
DEFAULT_MODEL: Final[str] = "gemini-2.5-flash"
_MAX_RETRIES: Final[int] = 8

# Process-lifetime singletons.
_CLIENT: genai.Client | None = None
_CALL_TIMINGS_MS: list[float] = []


def active_model() -> str:
    """Return the configured Gemini model (``NLP_API_MODEL`` env, else default)."""
    return os.environ.get("NLP_API_MODEL", DEFAULT_MODEL).strip() or DEFAULT_MODEL


def get_client() -> genai.Client:
    """Return the process-lifetime Gemini client (lazy; built on first call).

    Never built at import time — the API key is read on first use, so HF-Spaces
    secret injection (CLAUDE.md) has already happened. No model weights are loaded;
    this is a thin network client.
    """
    global _CLIENT
    if _CLIENT is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            # The intrinsic-eval CLIs don't bootstrap dotenv; load it here (lazily,
            # idempotent, does NOT override an already-set env var → HF-Spaces
            # secrets keep priority) so the API arm works from a local .env too.
            try:
                from dotenv import load_dotenv

                load_dotenv()
            except ImportError:
                pass
            api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set — Arm 3 (API LLM) needs it to call Gemini."
            )
        _CLIENT = genai.Client(api_key=api_key)
    return _CLIENT


def _is_rate_limited(exc: Exception) -> bool:
    msg = str(exc)
    return "429" in msg or "RESOURCE_EXHAUSTED" in msg.upper()


def _parse_retry_delay(exc: Exception) -> float:
    """Suggested retry delay (s) from a 429 message, plus a 2s buffer."""
    m = re.search(r"retry in (\d+(?:\.\d+)?)s", str(exc), re.IGNORECASE)
    return float(m.group(1)) + 2.0 if m else 15.0


@traceable(name="gemini_nlp_json", run_type="llm")
def generate_json(
    prompt: str,
    *,
    response_schema: Any,
    system: str | None = None,
    max_tokens: int = 256,
    temperature: float = 0.0,
    model: str | None = None,
) -> dict[str, Any]:
    """Gemini JSON-mode call → decoded JSON object (``dict``).

    ``response_schema`` is a JSON-Schema ``dict`` passed to Gemini to constrain the
    output server-side (same pattern as ``evaluation/judge.py``); the caller reads
    the returned dict defensively (the Arm-2 parsers do the same enum-validation on
    their side). Returns ``{}`` when Gemini yields no usable text (safety trim /
    ``MAX_TOKENS`` / transient glitch) or non-JSON, so callers degrade to an empty
    extraction instead of crashing. Deterministic (temperature 0, thinking off).
    Retries on 429/``RESOURCE_EXHAUSTED``. Records real wall-clock ms in the timing
    buffer. ``@traceable`` so the NLP-arm calls show cleanly in LangSmith.
    """
    client = get_client()
    contents = [types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
    config = types.GenerateContentConfig(
        system_instruction=system,
        temperature=temperature,
        max_output_tokens=max_tokens,
        response_mime_type="application/json",
        response_schema=response_schema,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )

    response = None
    start = time.perf_counter()
    for attempt in range(_MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=model or active_model(),
                contents=contents,
                config=config,
            )
            break
        except Exception as exc:
            if _is_rate_limited(exc) and attempt < _MAX_RETRIES - 1:
                delay = _parse_retry_delay(exc)
                logger.warning(
                    "Gemini NLP 429 on attempt %d/%d — sleeping %.1fs",
                    attempt + 1, _MAX_RETRIES, delay,
                )
                time.sleep(delay)
            else:
                raise
    _CALL_TIMINGS_MS.append((time.perf_counter() - start) * 1000.0)

    # Scan all parts; skip thought parts (defensive, mirrors providers/gemini.py).
    text = ""
    for candidate in getattr(response, "candidates", None) or []:
        content = getattr(candidate, "content", None)
        for part in getattr(content, "parts", None) or []:
            if getattr(part, "thought", False):
                continue
            if getattr(part, "text", None):
                text += part.text
    if not text:
        cands = getattr(response, "candidates", None) or []
        finish = getattr(cands[0], "finish_reason", None) if cands else None
        logger.warning(
            "Gemini NLP returned no usable text (finish_reason=%s) — empty extraction",
            finish,
        )
        return {}

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        logger.warning("Gemini NLP returned non-JSON text: %r", text[:200])
        return {}
    return data if isinstance(data, dict) else {}


def reset_timings() -> None:
    """Clear the per-call timing buffer (call before a measured eval run)."""
    _CALL_TIMINGS_MS.clear()


def timing_summary() -> dict[str, float]:
    """Mean/median/total/count of real wall-clock per-call API time (ms).

    The *real* network/API cost — distinct from the simulated-latency KPI in
    EVALUATION_FRAMEWORK §9. Reported as the API cost/latency data point; it must
    never feed model selection.
    """
    if not _CALL_TIMINGS_MS:
        return {"count": 0.0, "mean_ms": 0.0, "median_ms": 0.0, "total_ms": 0.0}
    return {
        "count": float(len(_CALL_TIMINGS_MS)),
        "mean_ms": statistics.fmean(_CALL_TIMINGS_MS),
        "median_ms": statistics.median(_CALL_TIMINGS_MS),
        "total_ms": float(sum(_CALL_TIMINGS_MS)),
    }
