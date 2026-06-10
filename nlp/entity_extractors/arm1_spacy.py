"""Arm 1 — entity extractor using spaCy ``PhraseMatcher``.

Implements IMPROVEMENT_PLAN.md §8 Arm 1. Topic and medium are extracted by
phrase-matching against the canonical synonym lists in ``nlp.synonyms``.
Matching is case-insensitive (``attr="LOWER"``) and multi-token phrases
(e.g. "video call", "at the branch") work out of the box.

Construction is moderately expensive (spaCy model load ≈ 0.5–1 s). The
factory returns one instance per session, threaded through
``config["configurable"]["_ent_extractor"]`` so the load cost is paid once
per Chainlit session and once per eval run.

If ``en_core_web_sm`` is not installed, the constructor falls back to a
blank English pipeline. Phrase matching still works (the ``LOWER`` attribute
does not require the trained model); lemma-based matching would, but Arm 1
does not depend on it.
"""

from __future__ import annotations

from typing import Any

import spacy
from spacy.lang.en import English
from spacy.matcher import PhraseMatcher

from nlp.synonyms import SYNONYMS_MEDIUM, SYNONYMS_TOPIC


class SpacyEntityExtractor:
    """spaCy PhraseMatcher arm — Arm 1 entity extractor."""

    arm_name: str = "spacy"

    def __init__(self, model_name: str = "en_core_web_sm") -> None:
        try:
            self._nlp = spacy.load(
                model_name, disable=["parser", "ner", "tagger", "lemmatizer"]
            )
        except OSError:
            # Trained model not installed — fall back to blank English.
            self._nlp = English()

        self._topic_matcher = PhraseMatcher(self._nlp.vocab, attr="LOWER")
        self._medium_matcher = PhraseMatcher(self._nlp.vocab, attr="LOWER")

        for topic_id, syns in SYNONYMS_TOPIC.items():
            patterns = [self._nlp.make_doc(s) for s in syns]
            self._topic_matcher.add(topic_id, patterns)

        for medium_id, syns in SYNONYMS_MEDIUM.items():
            patterns = [self._nlp.make_doc(s) for s in syns]
            self._medium_matcher.add(medium_id, patterns)

    def extract(self, text: str) -> tuple[str | None, str | None, dict[str, Any]]:
        if not text or not text.strip():
            return None, None, {}

        doc = self._nlp(text)
        topic_raw = self._topic_matcher(doc)   # list of (match_id, start, end)
        medium_raw = self._medium_matcher(doc)

        strings = self._nlp.vocab.strings

        def _pick(matches: list[tuple[int, int, int]]) -> str | None:
            """Longest match wins — resolves "investment portfolio" → investing
            from the overlapping "invest" / "investment" / "portfolio" matches.
            """
            if not matches:
                return None
            best = max(matches, key=lambda m: m[2] - m[1])
            return strings[best[0]]

        topic = _pick(topic_raw)
        medium = _pick(medium_raw)

        def _enumerate(matches: list[tuple[int, int, int]]) -> list[dict[str, Any]]:
            return [
                {
                    "label": strings[mid],
                    "start": int(start),
                    "end": int(end),
                    "text": doc[start:end].text,
                }
                for (mid, start, end) in matches
            ]

        raw: dict[str, Any] = {
            "topic_matches": _enumerate(topic_raw),
            "medium_matches": _enumerate(medium_raw),
        }
        return topic, medium, raw
