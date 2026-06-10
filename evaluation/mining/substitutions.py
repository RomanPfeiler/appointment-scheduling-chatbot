"""Domain-noun substitution for mined phrasings.

Per EVALUATION_FRAMEWORK.md §5, mined utterances must have domain-specific
nouns stripped so the phrasing is reusable in the banking-appointment domain.
This is intentionally light-touch — preserve the *temporal* phrasing, replace
only the topical noun. The original utterance is kept in ``original_context``.
"""

from __future__ import annotations

import re

# Order matters: longer/specific patterns first so they win over shorter ones.
_SUBSTITUTIONS: list[tuple[re.Pattern[str], str]] = [
    # Multi-word patterns first
    (re.compile(r"\bdoctor'?s appointment\b", re.IGNORECASE), "appointment"),
    (re.compile(r"\bdentist'?s appointment\b", re.IGNORECASE), "appointment"),
    (re.compile(r"\bsalon appointment\b", re.IGNORECASE), "appointment"),
    (re.compile(r"\bhair appointment\b", re.IGNORECASE), "appointment"),
    (re.compile(r"\bhotel (?:room|booking|reservation)\b", re.IGNORECASE), "appointment"),
    (re.compile(r"\btrain (?:ticket|trip|journey|ride)\b", re.IGNORECASE), "appointment"),
    (re.compile(r"\btaxi (?:ride|trip)\b", re.IGNORECASE), "appointment"),
    (re.compile(r"\brestaurant (?:reservation|booking|table)\b", re.IGNORECASE), "appointment"),
    # Single-word topical nouns -> generic "appointment" (only when surrounded by typical scheduling verbs/articles)
    (re.compile(r"\b(?:a|an|the|my|book|schedule|cancel|reserve)\s+haircut\b", re.IGNORECASE), r"an appointment"),
    (re.compile(r"\bhaircut\b", re.IGNORECASE), "appointment"),
    (re.compile(r"\bdental\b", re.IGNORECASE), ""),
    (re.compile(r"\bmedical\b", re.IGNORECASE), ""),
    # Strip parenthetical service hints that leak from SGD utterances
    (re.compile(r"\s{2,}"), " "),
]


def strip_domain_nouns(text: str) -> str:
    """Apply the substitution table to ``text``.

    Returns the cleaned phrasing. Idempotent on already-clean strings.
    """
    out = text
    for pattern, replacement in _SUBSTITUTIONS:
        out = pattern.sub(replacement, out)
    return out.strip()
