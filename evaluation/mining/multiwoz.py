"""Mine temporal/scheduling phrasings from MultiWOZ 2.2.

**Loader status (2026-05-24):** the canonical ``pfb30/multi_woz_v22`` requires
a dataset script and is rejected by ``datasets>=4``. We use the JSON re-upload
``tuetschek/multi_woz_v22`` instead, which is the pfb30 builder's output saved
as plain JSON files. Schema is preserved.

Per EVALUATION_FRAMEWORK.md §6b this is a *secondary* source — used only to
widen the variety of time-negotiation phrasings from booking sub-flows
(restaurant/hotel/train/taxi). Domain-noun stripping (``substitutions.py``)
matters more here than for SGD's calendar dialogues.

Schema (tuetschek mirror):
    dialogue_id: str
    services: list[str]                 # e.g. ['restaurant', 'hotel']
    turns: dict                         # columnar:
      turn_id: list[str]
      speaker: list[int]                # 0 = USER, 1 = SYSTEM
      utterance: list[str]
      frames: list[dict]                # per-turn frames (columnar inside)
        service: list[str]              # services touched this turn
        state: list[dict]               # per-service state
          slots_values:
            slots_values_name: list[str]    # e.g. 'restaurant-book_time'
            slots_values_list: list[list[str]]
      dialogue_acts: list[dict]
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from .paths import MULTIWOZ_RAW_JSONL, ensure_dirs
from .substitutions import strip_domain_nouns

log = logging.getLogger(__name__)

TARGET_SERVICES: tuple[str, ...] = ("restaurant", "hotel")
# Note (2026-05-24): `train` and `taxi` were removed as wrong-domain — their
# phrasings carry transit-time idiom ("arrive by", "leaveat") that biases the
# bank away from appointment-scheduling. See ARCHITECTURE.md decision log.

# Temporal slot suffixes. MultiWOZ 2.2 (tuetschek mirror) flattens slot names
# without underscores: "restaurant-booktime", "hotel-bookday", "hotel-bookstay".
# We match by suffix to be robust across mirrors that may or may not preserve
# the original underscored form.
TEMPORAL_SLOT_SUFFIXES: tuple[str, ...] = (
    "booktime",
    "bookday",
    "bookstay",   # hotel duration (number of nights)
    # Legacy / underscored forms — kept for compatibility with other MultiWOZ mirrors
    "book_time",
    "book_day",
)

_USER_SPEAKER = 0


@dataclass(slots=True)
class MinedExpression:
    """Mirrors the SGD miner's record schema."""

    expression_id: str
    expression_text: str
    source_dataset: str
    source_service: str
    source_dialogue_id: str
    source_turn_idx: int
    original_context: str
    normalized_meaning: str
    raw_slots: dict[str, list[str]]


def _load_mirror() -> Any:
    """Load the tuetschek MultiWOZ 2.2 mirror across all splits."""
    try:
        from datasets import load_dataset
    except ImportError as e:
        raise RuntimeError(
            "The 'datasets' package is not installed. Run `pip install -r requirements.txt`."
        ) from e

    try:
        return load_dataset("tuetschek/multi_woz_v22")
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(
            "Failed to load 'tuetschek/multi_woz_v22'. This is the JSON re-upload of "
            "pfb30/multi_woz_v22; if it is unavailable, fall back to one of the "
            "Brendan/multiwoz_turns_v22_* parquet mirrors and adapt this loader. "
            f"Original error: {e!r}"
        ) from e


def _state_temporal_slots(state_entry: dict) -> dict[str, list[str]]:
    """Pull temporal slots out of a single state dict.

    The tuetschek schema stores slots as parallel arrays:
        state.slots_values.slots_values_name: list[str]
        state.slots_values.slots_values_list: list[list[str]]
    """
    out: dict[str, list[str]] = {}
    slots_values = (state_entry or {}).get("slots_values") or {}
    names = slots_values.get("slots_values_name") or []
    lists = slots_values.get("slots_values_list") or []
    for name, values in zip(names, lists):
        if not isinstance(name, str):
            continue
        suffix = name.rsplit("-", 1)[-1].lower()
        if suffix in TEMPORAL_SLOT_SUFFIXES:
            out[name] = [str(v) for v in (values or [])]
    return out


def _walk_turn_frames(
    frames_entry: Any,
) -> Iterable[tuple[str, dict[str, list[str]]]]:
    """Yield (service, temporal_slots) for one turn's frames.

    ``frames_entry`` is the per-turn frames dict. Inner structure (tuetschek):
        frames_entry.service: list[str]   # services touched this turn
        frames_entry.state:   list[dict]  # per-service state
    """
    if not isinstance(frames_entry, dict):
        return
    services = frames_entry.get("service") or []
    states = frames_entry.get("state") or []
    for service, state in zip(services, states):
        if service not in TARGET_SERVICES:
            continue
        temporal = _state_temporal_slots(state)
        if temporal:
            yield service, temporal


def _extract_temporal_user_turns(
    dialogue: dict[str, Any],
) -> Iterable[tuple[int, str, str, dict[str, list[str]]]]:
    """Yield (turn_idx, service, utterance, temporal_slots) for user turns."""
    turns = dialogue.get("turns")
    if not isinstance(turns, dict):
        return

    speakers = turns.get("speaker") or []
    utterances = turns.get("utterance") or []
    frames_list = turns.get("frames") or []

    for turn_idx, (speaker, utterance, frames) in enumerate(
        zip(speakers, utterances, frames_list)
    ):
        if int(speaker) != _USER_SPEAKER:
            continue
        utt_text = (utterance or "").strip()
        if not utt_text:
            continue
        for service, temporal in _walk_turn_frames(frames):
            yield turn_idx, service, utt_text, temporal


def mine() -> Path:
    """Run the MultiWOZ miner. Writes to ``MULTIWOZ_RAW_JSONL``."""
    ensure_dirs()
    ds = _load_mirror()

    splits = ds.keys() if hasattr(ds, "keys") else [None]
    log.info("Walking MultiWOZ splits: %s", list(splits))

    count = 0
    with MULTIWOZ_RAW_JSONL.open("w", encoding="utf-8") as fh:
        for split in splits:
            rows = ds[split] if split is not None else ds
            for dialogue in rows:
                dialogue_id = dialogue.get("dialogue_id", "")
                services = dialogue.get("services") or []
                if not any(s in TARGET_SERVICES for s in services):
                    continue

                for turn_idx, service, utt, temporal in _extract_temporal_user_turns(dialogue):
                    count += 1
                    expr = MinedExpression(
                        expression_id=f"multiwoz_{service}_{count:06d}",
                        expression_text=strip_domain_nouns(utt),
                        source_dataset="multiwoz",
                        source_service=service,
                        source_dialogue_id=dialogue_id,
                        source_turn_idx=turn_idx,
                        original_context=utt,
                        normalized_meaning="; ".join(
                            f"{k}={','.join(v)}" for k, v in sorted(temporal.items())
                        ),
                        raw_slots={k: list(v) for k, v in temporal.items()},
                    )
                    fh.write(json.dumps(asdict(expr), ensure_ascii=False) + "\n")

    log.info("MultiWOZ mining done: %d expressions -> %s", count, MULTIWOZ_RAW_JSONL)
    return MULTIWOZ_RAW_JSONL
