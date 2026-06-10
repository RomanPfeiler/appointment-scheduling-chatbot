"""Pydantic schemas for the NLP annotation layer.

These types are the contract between ``nlp/`` and the orchestrator's
``annotate`` node. They cross a module boundary, so per CLAUDE.md they are
Pydantic ``BaseModel`` (not dataclasses or TypedDict).

``DateRange`` carries a new ``specificity`` field (IMPROVEMENT_PLAN.md §7a)
that tells the agent how wide a ``check_availability`` window to use.
``AnnotatedMessage`` is what the annotate node writes to
``ConversationState["last_annotation"]`` (as ``model_dump(mode="json")``).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


Specificity = Literal[
    "exact_time",
    "day_specific",
    "day_vague",
    "multi_day_vague",
    "compound",
]


class DateRange(BaseModel):
    """A parsed datetime range from a single user utterance.

    Multiple ranges per utterance are possible (compound requests).
    All datetimes are timezone-aware Europe/Zurich.
    """

    start_datetime: datetime
    end_datetime: datetime
    is_flexible: bool = False
    original_text: str
    specificity: Specificity


class AnnotatedMessage(BaseModel):
    """NLP annotations for one user turn — written to ConversationState.

    The agent reads this to seed its system prompt with NLP hints. When all
    NLP flags are off (baseline) the annotate node leaves this field as
    ``None`` and ``agent_node._build_system_prompt`` behaves identically to
    pre-Arm-1.
    """

    raw_text: str
    intent: str = "schedule"
    confidence: float = 1.0
    topic: str | None = None
    contact_medium: str | None = None
    datetime_ranges: list[DateRange] = Field(default_factory=list)
    entities_raw: dict[str, Any] = Field(default_factory=dict)
