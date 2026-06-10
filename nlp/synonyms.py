"""Canonical synonym lists for topic and contact_medium entity extraction.

This is the **authoritative** synonym list authored from domain knowledge of a
Swiss bank's appointment-booking flow. Both the spaCy Arm 1 matcher and the
LLM Arm 2/3 prompts consume this list, so the three arms compare *different
mechanisms over the same knowledge*, not *spaCy with synonyms vs LLM without*.

Anti-bleed (IMPROVEMENT_PLAN §6): the entity-gold *evaluation* utterances in
``nlp/eval_data/entity_gold.jsonl`` deliberately include paraphrases NOT in
this list, sourced independently. Do **not** extend this list to cover
eval-set failures — that defeats the comparison.

Surface forms are stored lowercased. ``arm1_spacy`` builds its ``PhraseMatcher``
with ``attr="LOWER"`` so case is normalised at match time. Multi-token phrases
(e.g. ``"video call"``) are supported natively by ``PhraseMatcher``.
"""

from typing import Final


SYNONYMS_TOPIC: Final[dict[str, list[str]]] = {
    "investing": [
        "investing",
        "investment",
        "investments",
        "invest",
        "portfolio",
        "stocks",
        "mutual funds",
        "wealth",
        "wealth management",
        "asset management",
    ],
    "mortgage": [
        "mortgage",
        "mortgages",
        "home loan",
        "house loan",
        "property loan",
        "hypothek",
        "immobilienfinanzierung",
        "real estate financing",
    ],
    "pension": [
        "pension",
        "pensions",
        "retirement",
        "retirement plan",
        "pillar 3",
        "pillar 3a",
        "altersvorsorge",
        "old-age provision",
        "vorsorge",
    ],
}


SYNONYMS_MEDIUM: Final[dict[str, list[str]]] = {
    "branch": [
        "branch",
        "branch office",
        "at the branch",
        "in-person",
        "in person",
        "face to face",
        "filiale",
        "at your office",
    ],
    "online": [
        "online",
        "video call",
        "video meeting",
        "video chat",
        "videoconference",
        "videokonferenz",
        "zoom",
        "teams",
        "ms teams",
        "web meeting",
        "virtual meeting",
    ],
    "phone": [
        "phone",
        "phone call",
        "telephone",
        "by phone",
        "call me",
        "telefon",
        "anruf",
        "ring me",
    ],
}


def all_topic_synonyms() -> set[str]:
    """Flat set of every topic surface form (used by the anti-bleed audit)."""
    return {s for syns in SYNONYMS_TOPIC.values() for s in syns}


def all_medium_synonyms() -> set[str]:
    """Flat set of every medium surface form (used by the anti-bleed audit)."""
    return {s for syns in SYNONYMS_MEDIUM.values() for s in syns}
