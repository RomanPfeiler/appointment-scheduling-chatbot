"""Provider-agnostic result type returned by every LLM call.

Keeping this in its own file means every concrete provider can import it
without pulling in another provider's SDK.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class LLMResult:
    """Provider-agnostic result from an LLM call.

    Latency/token fields are populated by the provider wrapper around the
    actual SDK call. They are ``None`` if the SDK didn't expose the value
    (older client, unsupported model) — never raise; record what's available.
    """

    has_tool_call: bool
    tool_name: str | None  # e.g. "get_appointment_topics"
    tool_args: dict | None  # e.g. {"topic_id": "mortgage"}
    text_response: str | None  # final text for the user (None if tool call)
    raw_response: Any  # original provider response, kept for message history
    provider: str  # "gemini" or "claude"
    model_used: str | None = None  # exact model id the call hit
    latency_ms: float | None = None  # wall-clock around the SDK call
    input_tokens: int | None = None  # prompt token count
    output_tokens: int | None = None  # completion token count
    thoughts_tokens: int | None = None  # reasoning ("thinking") token count, if reported
