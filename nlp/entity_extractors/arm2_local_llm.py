"""Arm 2 entity extractor — local LLM with GBNF-constrained inline tags.

IMPROVEMENT_PLAN §8 Arm 2 + §9. Same local model as the datetime Arm 2. The
prompt carries the **canonical synonyms** from ``nlp.synonyms`` so the
comparison is "different mechanisms over the same knowledge" (not "spaCy with
synonyms vs LLM without"), and the LLM's job is to map paraphrases the
dictionary doesn't cover to the closest canonical category.

Elicitation is **GBNF-constrained inline tags, not JSON** (ARCHITECTURE
Decision Log): ``<topic>VALUE</topic><medium>VALUE</medium>``, with each VALUE
constrained to the valid enum (or ``none``). Output is normalised to the common
``(topic, medium, raw)`` contract so the format choice never leaks into the
cross-arm comparison.
"""

from __future__ import annotations

import re
from typing import Any

from nlp import local_llm
from nlp.synonyms import SYNONYMS_MEDIUM, SYNONYMS_TOPIC

_VALID_TOPIC: frozenset[str] = frozenset({"investing", "mortgage", "pension"})
_VALID_MEDIUM: frozenset[str] = frozenset({"branch", "online", "phone"})

# GBNF constrains each slot to its enum (or "none") — no invalid label possible.
GBNF_ENTITY = r"""
root ::= "<topic>" topic "</topic><medium>" medium "</medium>"
topic ::= "investing" | "mortgage" | "pension" | "none"
medium ::= "branch" | "online" | "phone" | "none"
"""


def _format_synonyms(d: dict[str, list[str]]) -> str:
    return "\n".join(f"- {cat}: {', '.join(syns)}" for cat, syns in d.items())


_SYSTEM = f"""You classify a user's appointment request to a Swiss bank.

Identify the TOPIC and the CONTACT MEDIUM, then output exactly:
<topic>VALUE</topic><medium>VALUE</medium>
Output ONLY these tags — no other text, no explanations.

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
User: I'd like to grow my savings for the long term.
<topic>investing</topic><medium>none</medium>
User: Can we do a video call about my home loan?
<topic>mortgage</topic><medium>online</medium>
User: I need to sort out my retirement; I'd prefer to come to the office.
<topic>pension</topic><medium>branch</medium>
User: What are your opening hours?
<topic>none</topic><medium>none</medium>"""

_TOPIC_RE = re.compile(r"<topic>(.*?)</topic>", re.DOTALL | re.IGNORECASE)
_MEDIUM_RE = re.compile(r"<medium>(.*?)</medium>", re.DOTALL | re.IGNORECASE)


def _extract_slot(raw: str, pattern: re.Pattern[str], valid: frozenset[str]) -> str | None:
    """First tag match, lowercased; returns it only if in the valid enum, else None.

    ``none``, empty, missing, or any out-of-enum value (defensive — GBNF prevents
    the latter in production) all map to ``None``.
    """
    m = pattern.search(raw or "")
    if not m:
        return None
    value = m.group(1).strip().lower()
    return value if value in valid else None


def parse_entity_tags(raw: str) -> tuple[str | None, str | None, dict[str, Any]]:
    """Turn the model's tagged output into ``(topic, medium, raw_diagnostics)``.

    Pure string→object logic, unit-tested against mocked LLM strings. ``"none"``
    / empty / out-of-enum → ``None`` for that slot.
    """
    topic = _extract_slot(raw, _TOPIC_RE, _VALID_TOPIC)
    medium = _extract_slot(raw, _MEDIUM_RE, _VALID_MEDIUM)
    diagnostics: dict[str, Any] = {
        "local_llm_raw": (raw or "").strip(),
        "model": local_llm.active_model_key(),
    }
    return topic, medium, diagnostics


class LocalLLMEntityExtractor:
    """Arm 2 entity extractor. Stateless — construct once per session and reuse.

    The model is loaded lazily on the first ``extract`` call (via
    ``nlp.local_llm``), not in ``__init__`` — so the factory can build this arm,
    and the unit tests can mock ``local_llm.generate``, without touching the
    native library or the GGUF.
    """

    arm_name: str = "local_llm"

    def extract(self, text: str) -> tuple[str | None, str | None, dict[str, Any]]:
        if not text or not text.strip():
            return None, None, {}
        raw = local_llm.generate(text, GBNF_ENTITY, system=_SYSTEM, max_tokens=64)
        return parse_entity_tags(raw)
