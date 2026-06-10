"""Mine temporal/scheduling phrasings from the Schema-Guided Dialogue dataset.

**Loader status (2026-05-24):** the canonical HF dataset
``google-research-datasets/schema_guided_dstc8`` requires a dataset script,
which is rejected by ``datasets>=4`` ("Dataset scripts are no longer supported").
We therefore use the GEM-flattened mirror ``bentrevett/schema_guided_dialog``
as the actual data source. The mirror is the standard parquet fallback named
in EVALUATION_FRAMEWORK.md §6a; it is reformatted (one row per system turn,
user utterances live in ``context``) but preserves dialog_acts and the
source dialog/turn ids, which is enough for our purposes.

Filter targets (EVALUATION_FRAMEWORK.md §6a):
- ``Calendar_1`` — primary calendar service.
- ``Services_1`` .. ``Services_4`` — appointment-style services (salons,
  dentists, doctors, therapists). Closest analogue to the appointment-chatbot
  domain.
- ``Banks_1``, ``Banks_2`` — banking, kept for completeness even though
  time-typed slots are sparse here.

Per row whose ``service`` matches a target and whose ``dialog_acts`` contain a
temporal slot, walk the ``context`` list (alternating user/system, user first)
and emit one mined record per *user* utterance.
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

from .paths import SGD_RAW_JSONL, ensure_dirs
from .substitutions import strip_domain_nouns

log = logging.getLogger(__name__)

TARGET_SERVICES: tuple[str, ...] = (
    "Calendar_1",
    "Services_1",
    "Services_2",
    "Services_3",
    "Services_4",
    "Banks_1",
    "Banks_2",
)

# SGD slot names that carry a temporal value.
TIME_SLOT_NAMES: frozenset[str] = frozenset(
    {
        "event_date",
        "event_time",
        "appointment_date",
        "appointment_time",
        "available_start_time",
        "available_end_time",
        "date",
        "time",
        "start_date",
        "end_date",
        "transfer_time",
        "recurring_date_time",
    }
)


@dataclass(slots=True)
class MinedExpression:
    """One mined temporal expression. Schema mirrored in MultiWOZ miner."""

    expression_id: str
    expression_text: str        # post domain-noun stripping
    source_dataset: str         # "sgd"
    source_service: str         # e.g. "Calendar_1"
    source_dialogue_id: str
    source_turn_idx: int
    original_context: str       # raw utterance
    normalized_meaning: str     # joined temporal slot values for the *dialog*
    raw_slots: dict[str, list[str]]


def _load_sgd_mirror() -> Any:
    """Load the GEM-flattened SGD mirror across all splits.

    Returns a DatasetDict. Raises ``RuntimeError`` with actionable guidance if
    the load fails.
    """
    try:
        from datasets import load_dataset
    except ImportError as e:
        raise RuntimeError(
            "The 'datasets' package is not installed. Run `pip install -r requirements.txt`."
        ) from e

    try:
        return load_dataset("bentrevett/schema_guided_dialog")
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(
            "Failed to load the SGD parquet mirror 'bentrevett/schema_guided_dialog'. "
            "Check network / HF cache. If the mirror is unavailable, the next-best "
            "option is `GEM/schema_guided_dialog` (same upstream source, slightly "
            "different field naming — see EVALUATION_FRAMEWORK.md §6a). "
            f"Original error: {e!r}"
        ) from e


def _temporal_slot_values(dialog_acts: Iterable[dict]) -> dict[str, list[str]]:
    """Collect dialog-level temporal slot annotations.

    Returns a dict[slot_name -> list[value]]. Empty if no temporal slots.
    """
    out: dict[str, list[str]] = {}
    for da in dialog_acts or []:
        slot = da.get("slot")
        if slot in TIME_SLOT_NAMES:
            values = da.get("values") or []
            if isinstance(values, list):
                out.setdefault(slot, []).extend(str(v) for v in values)
            else:
                out.setdefault(slot, []).append(str(values))
    return out


def _user_turns_from_context(context: list[str]) -> Iterable[tuple[int, str]]:
    """Yield (idx, utterance) for user turns.

    Context alternates user, system, user, system... starting with user.
    """
    for idx, utt in enumerate(context or []):
        if idx % 2 != 0:
            continue
        text = (utt or "").strip()
        if text:
            yield idx, text


def mine() -> Path:
    """Run the SGD miner. Writes to ``SGD_RAW_JSONL``."""
    ensure_dirs()
    ds = _load_sgd_mirror()

    log.info("Walking SGD splits: %s", list(ds.keys()) if hasattr(ds, "keys") else ["<single>"])

    count = 0
    seen_keys: set[tuple[str, int]] = set()  # (dialog_id, turn_idx_in_context)
    splits = ds.keys() if hasattr(ds, "keys") else [None]

    with SGD_RAW_JSONL.open("w", encoding="utf-8") as fh:
        for split in splits:
            rows = ds[split] if split is not None else ds
            for row in rows:
                service = row.get("service")
                if service not in TARGET_SERVICES:
                    continue

                dialog_acts = row.get("dialog_acts") or []
                temporal = _temporal_slot_values(dialog_acts)
                if not temporal:
                    continue

                dialog_id = row.get("dialog_id", "")
                context = row.get("context") or []

                for turn_idx, utterance in _user_turns_from_context(context):
                    key = (dialog_id, turn_idx)
                    if key in seen_keys:
                        continue
                    seen_keys.add(key)
                    count += 1

                    expr = MinedExpression(
                        expression_id=f"sgd_{service.lower()}_{count:06d}",
                        expression_text=strip_domain_nouns(utterance),
                        source_dataset="sgd",
                        source_service=service,
                        source_dialogue_id=dialog_id,
                        source_turn_idx=turn_idx,
                        original_context=utterance,
                        normalized_meaning="; ".join(
                            f"{k}={','.join(v)}" for k, v in sorted(temporal.items())
                        ),
                        raw_slots=temporal,
                    )
                    fh.write(json.dumps(asdict(expr), ensure_ascii=False) + "\n")

    log.info("SGD mining done: %d unique user turns -> %s", count, SGD_RAW_JSONL)
    return SGD_RAW_JSONL
