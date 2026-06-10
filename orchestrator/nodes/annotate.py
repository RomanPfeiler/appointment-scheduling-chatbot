"""Annotate node — Step 2 of the orchestrator, NLP pipeline.

Runs the ``nlp/`` pipeline on the latest user message when the corresponding
feature flags are set in ``config["configurable"]`` (IMPROVEMENT_PLAN.md §5).
Populates ``ConversationState["last_annotation"]`` so the agent node can read
it and inject NLP HINTS into the per-turn system prompt.

When all NLP flags are off (baseline), this returns ``{}`` — byte-identical
to the pass-through stub it replaced. A regression test guards that the
baseline smoke run produces an identical derived-metrics dict whether annotate
is wired in or not.

The parser and extractor instances are heavy (spaCy model load, future local
LLM weights). They are constructed once per session/run and threaded in via
``config["configurable"]["_dt_parser"]`` / ``["_ent_extractor"]``. The
annotate node falls back to building a fresh instance on demand only if the
cache key is missing, so unit tests can exercise the node without setting up
a full session.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from google.genai import types
from langchain_core.runnables import RunnableConfig

from nlp.factory import build_datetime_parser, build_entity_extractor
from nlp.schemas import AnnotatedMessage
from orchestrator.nodes.agent import _reference_now_from_config
from orchestrator.state import ConversationState

logger = logging.getLogger(__name__)

_ZURICH = ZoneInfo("Europe/Zurich")


def _latest_user_text(messages: list[Any]) -> str:
    """Pull the latest user-role utterance text out of the Gemini message list.

    Each Gemini ``Content`` has ``role`` and ``parts``. We scan from the end
    and return the first ``role == "user"`` content whose parts contain a
    plain text part (skip function_response wrappings).
    """
    for content in reversed(messages):
        role = getattr(content, "role", None) or (content.get("role") if isinstance(content, dict) else None)
        if role != "user":
            continue
        parts = getattr(content, "parts", None) or (content.get("parts") if isinstance(content, dict) else None) or []
        for part in parts:
            # types.Part has `.text` (str | None); skip function_response parts.
            text = getattr(part, "text", None)
            if text:
                return text
        # No plain-text part on this user content — keep scanning earlier ones.
    return ""


async def annotate_node(state: ConversationState, config: RunnableConfig) -> dict:
    """Run NLP annotation on the latest user message when flags are set.

    Returns a state update with ``last_annotation`` populated, or ``{}`` when
    NLP is off (baseline behavior — byte-identical to the previous stub).
    """
    cfg = config.get("configurable", {}) or {}
    dt_on = bool(cfg.get("nlp_datetime_enabled", False))
    ent_on = bool(cfg.get("nlp_entity_enabled", False))

    if not (dt_on or ent_on):
        return {}  # baseline — no annotation, no debug log

    user_text = _latest_user_text(state.get("messages", []))
    if not user_text:
        return {}

    # Relative base for datetime resolution: the scenario's pinned ``reference_date``
    # when set (eval/runner — EVALUATION_FRAMEWORK §3a), else the wall clock
    # (interactive chat). Never wall-clock during a pinned run, so the NLP-resolved
    # dates match the agent's injected "today" and the Option-A fixtures.
    now = _reference_now_from_config(config) or datetime.now(_ZURICH)
    ann = AnnotatedMessage(raw_text=user_text)

    # Default arm when NLP is enabled but no arm is named: Arm 3 (api_llm) — it
    # reuses the agent's Gemini stack (no extra dependency) and is a no-harm wash
    # vs baseline at representative scale. Arm 1 (dateparser/spacy) is a wash on
    # the reliable metrics with no E2E benefit, so it is no longer the default.
    # (Its judge-Temporal −0.37 is a measurement artefact, not agent degradation —
    # see ARCHITECTURE §8 Decision Log 2026-06-07.) Production still ships NLP OFF
    # (nlp_*_enabled=False → baseline).
    if dt_on:
        parser = cfg.get("_dt_parser")
        if parser is None:
            parser = build_datetime_parser(cfg.get("datetime_arm", "api_llm"))
        ann.datetime_ranges = parser.parse(user_text, now=now)

    if ent_on:
        extractor = cfg.get("_ent_extractor")
        if extractor is None:
            extractor = build_entity_extractor(cfg.get("entity_arm", "api_llm"))
        topic, medium, raw = extractor.extract(user_text)
        ann.topic = topic
        ann.contact_medium = medium
        ann.entities_raw.update(raw)

    # Flag compound at the AnnotatedMessage level when ≥2 ranges came back.
    if len(ann.datetime_ranges) >= 2:
        ann.entities_raw["compound"] = True

    annotation_dict = ann.model_dump(mode="json")
    debug_record = {
        "node": "annotate_node",
        "timestamp": datetime.now(_ZURICH).isoformat(),  # real wall-clock, not the pinned base
        "action": "nlp_annotation",
        "details": {
            "datetime_enabled": dt_on,
            "entity_enabled": ent_on,
            "datetime_arm": cfg.get("datetime_arm"),
            "entity_arm": cfg.get("entity_arm"),
            "n_ranges": len(ann.datetime_ranges),
            "topic": ann.topic,
            "contact_medium": ann.contact_medium,
            "compound": bool(ann.entities_raw.get("compound")),
        },
    }
    logger.debug(
        "annotate_node: topic=%s medium=%s ranges=%d",
        ann.topic, ann.contact_medium, len(ann.datetime_ranges),
    )
    return {"last_annotation": annotation_dict, "debug_log": [debug_record]}
