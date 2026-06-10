"""Protocol for the entity extractor, shared by Arms 1, 2, 3."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class EntityExtractor(Protocol):
    """All three arms (spaCy, local LLM, API LLM) implement this.

    Returns a tuple ``(topic, contact_medium, raw)``:
      - ``topic``: one of "investing", "mortgage", "pension", or ``None``
      - ``contact_medium``: one of "branch", "online", "phone", or ``None``
      - ``raw``: arm-specific diagnostic metadata (e.g. which synonym matched,
        confidence scores, raw LLM output) — surfaced through
        ``AnnotatedMessage.entities_raw`` for debugging and the report's
        failure analysis.
    """

    arm_name: str

    def extract(self, text: str) -> tuple[str | None, str | None, dict[str, Any]]:
        ...
