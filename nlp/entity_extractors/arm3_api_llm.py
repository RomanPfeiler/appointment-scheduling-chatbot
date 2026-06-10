"""Arm 3 entity extractor — Gemini JSON mode, enum-constrained slots.

IMPROVEMENT_PLAN §8 Arm 3. Same task as Arm 2: map the user's appointment request
to a TOPIC and a CONTACT MEDIUM. The prompt carries the **canonical synonyms** from
``nlp.synonyms`` so the comparison is "different mechanisms over the same
knowledge" (not "spaCy with synonyms vs LLM without"); the model maps paraphrases
the dictionary does not cover to the closest canonical category. Anti-bleed: the
synonym list is authoritative — do **not** extend it to cover eval failures.

Elicitation is **Gemini JSON mode** (``response_mime_type="application/json"`` + a
JSON-Schema ``response_schema`` whose slots are enum-constrained), not Arm 2's GBNF
inline tags. Both arms normalise to the identical ``(topic, medium, raw)`` contract,
so the format choice never leaks into the cross-arm comparison.
"""

from __future__ import annotations

import json
from typing import Any

from nlp import api_llm
from nlp.synonyms import SYNONYMS_MEDIUM, SYNONYMS_TOPIC

_VALID_TOPIC: frozenset[str] = frozenset({"investing", "mortgage", "pension"})
_VALID_MEDIUM: frozenset[str] = frozenset({"branch", "online", "phone"})

# JSON-Schema constraining each slot to its enum (or "none") — no invalid label
# possible. The JSON equivalent of Arm 2's GBNF-constrained ``<topic>/<medium>``.
_ENTITY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "topic": {
            "type": "string",
            "enum": ["investing", "mortgage", "pension", "none"],
        },
        "contact_medium": {
            "type": "string",
            "enum": ["branch", "online", "phone", "none"],
        },
    },
    "required": ["topic", "contact_medium"],
}


def _format_synonyms(d: dict[str, list[str]]) -> str:
    """Render the canonical synonym map for the prompt (local — no cross-arm import)."""
    return "\n".join(f"- {cat}: {', '.join(syns)}" for cat, syns in d.items())


_SYSTEM = f"""You classify a user's appointment request to a Swiss bank.

Identify the TOPIC and the CONTACT MEDIUM, then return JSON matching the schema:
{{"topic": VALUE, "contact_medium": VALUE}}.

TOPIC is one of: investing, mortgage, pension, none.
CONTACT MEDIUM is one of: branch, online, phone, none.
Use "none" for a category the user does not mention.

Map paraphrases to the closest category. These canonical phrasings define each
category — the user may use other words with the same meaning:

Topics:
{_format_synonyms(SYNONYMS_TOPIC)}

Contact media:
{_format_synonyms(SYNONYMS_MEDIUM)}

Examples:
"I'd like to grow my savings for the long term." -> {{"topic": "investing", "contact_medium": "none"}}
"Can we do a video call about my home loan?" -> {{"topic": "mortgage", "contact_medium": "online"}}
"I need to sort out my retirement; I'd prefer to come to the office." -> {{"topic": "pension", "contact_medium": "branch"}}
"What are your opening hours?" -> {{"topic": "none", "contact_medium": "none"}}"""


def _norm(value: Any, valid: frozenset[str]) -> str | None:
    """Lowercase/strip a slot value; keep it only if in the valid enum, else None.

    ``"none"``, empty, missing, or any out-of-enum value (defensive — the JSON
    schema prevents the latter in production) all map to ``None``.
    """
    text = str(value or "").strip().lower()
    return text if text in valid else None


def parse_entity_response(data: dict[str, Any]) -> tuple[str | None, str | None, dict[str, Any]]:
    """Turn the model's decoded JSON object into ``(topic, medium, raw_diagnostics)``.

    Pure dict→tuple logic, unit-tested against hand-written dicts — the JSON
    analogue of Arm 2's :func:`parse_entity_tags`. ``"none"`` / empty / out-of-enum
    → ``None`` for that slot.
    """
    topic = _norm(data.get("topic"), _VALID_TOPIC)
    medium = _norm(data.get("contact_medium"), _VALID_MEDIUM)
    diagnostics: dict[str, Any] = {
        "api_llm_raw": json.dumps(data, ensure_ascii=False),
        "model": api_llm.active_model(),
    }
    return topic, medium, diagnostics


class ApiLLMEntityExtractor:
    """Arm 3 entity extractor. Stateless — construct once per session and reuse.

    The Gemini client is created lazily on the first ``extract`` call (via
    ``nlp.api_llm``), not in ``__init__`` — so the factory can build this arm, and
    unit tests can mock ``api_llm.generate_json``, without an API key or a network
    call.
    """

    arm_name: str = "api_llm"

    def extract(self, text: str) -> tuple[str | None, str | None, dict[str, Any]]:
        if not text or not text.strip():
            return None, None, {}
        data = api_llm.generate_json(
            text, response_schema=_ENTITY_SCHEMA, system=_SYSTEM, max_tokens=64
        )
        return parse_entity_response(data)
