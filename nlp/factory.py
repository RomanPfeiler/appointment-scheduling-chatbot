"""Factory functions that build per-arm NLP components.

The annotate node, the intrinsic eval CLIs, and the runner all go through
these factories — there is no other entry point. Keeping the arm-selection
logic in one place means Arms 2 and 3 only need to add their constructors
to the respective dispatch dicts.

Unknown arms raise ``ValueError`` immediately so a config typo surfaces
before any inference happens.
"""

from __future__ import annotations

from nlp.datetime_parser import DatetimeParser
from nlp.datetime_parsers.arm1_dateparser import DateparserDatetimeParser
from nlp.datetime_parsers.arm2_local_llm import LocalLLMDatetimeParser
from nlp.datetime_parsers.arm3_api_llm import ApiLLMDatetimeParser
from nlp.entity_extractor import EntityExtractor
from nlp.entity_extractors.arm1_spacy import SpacyEntityExtractor
from nlp.entity_extractors.arm2_local_llm import LocalLLMEntityExtractor
from nlp.entity_extractors.arm3_api_llm import ApiLLMEntityExtractor


_DATETIME_ARMS = {
    "dateparser": DateparserDatetimeParser,
    "local_llm": LocalLLMDatetimeParser,
    "api_llm": ApiLLMDatetimeParser,
}

_ENTITY_ARMS = {
    "spacy": SpacyEntityExtractor,
    "local_llm": LocalLLMEntityExtractor,
    "api_llm": ApiLLMEntityExtractor,
}


def build_datetime_parser(arm: str) -> DatetimeParser:
    """Return a ``DatetimeParser`` instance for the named arm.

    Construction may be expensive (local-LLM model load, etc.) — call once
    per session/run and reuse.
    """
    try:
        cls = _DATETIME_ARMS[arm]
    except KeyError:
        raise ValueError(
            f"unknown datetime arm: {arm!r}. "
            f"Legal values: {sorted(_DATETIME_ARMS)}."
        ) from None
    return cls()


def build_entity_extractor(arm: str) -> EntityExtractor:
    """Return an ``EntityExtractor`` instance for the named arm.

    Construction may be expensive (spaCy model load ≈ 0.5–1 s, local-LLM
    much more) — call once per session/run and reuse.
    """
    try:
        cls = _ENTITY_ARMS[arm]
    except KeyError:
        raise ValueError(
            f"unknown entity arm: {arm!r}. "
            f"Legal values: {sorted(_ENTITY_ARMS)}."
        ) from None
    return cls()
