# Evaluation Datasets

This directory documents the external datasets the evaluation depends on and
holds the **mined intermediates** that feed `../phrase_bank/temporal_expressions.json`.

> **Storage policy** (EVALUATION_FRAMEWORK.md §6d): raw datasets are *not*
> committed. They load via `datasets.load_dataset()` from the HuggingFace cache
> (`~/.cache/huggingface/datasets/`). Mined JSONL extracts live under `mined/`
> and may be committed for reproducibility (they are small text files); the
> final tagged bank is under `../phrase_bank/`.

## Sources

### Primary — Schema-Guided Dialogue (SGD)

| Field            | Value                                                         |
|------------------|---------------------------------------------------------------|
| Upstream source  | Schema-Guided Dialogue (DSTC8) — Google Research               |
| HF mirror used   | `bentrevett/schema_guided_dialog` (parquet, GEM-flattened)     |
| Loader call      | `load_dataset("bentrevett/schema_guided_dialog")`              |
| License          | CC BY-SA 4.0 (inherited from upstream)                         |
| Why this dataset | ~18k task-oriented dialogues across 17 domains explicitly including **banking** and **calendar** — the closest existing match to this project's domain (EVALUATION_FRAMEWORK.md §6a). |
| Services mined   | `Calendar_1`, `Services_1`, `Services_2`, `Services_3`, `Services_4`, `Banks_1`, `Banks_2` |
| Filter rule      | Keep rows whose `service` is a target service AND whose `dialog_acts` contains at least one slot in `evaluation/mining/sgd.py::TIME_SLOT_NAMES`. From each qualifying row, emit one record per *user* utterance in the `context` (deduplicated by `(dialog_id, context_index)`). |

**Why the mirror, not the canonical loader.** The canonical
`google-research-datasets/schema_guided_dstc8` requires a dataset script,
which `datasets>=4` rejects with "Dataset scripts are no longer supported".
The bentrevett mirror is the parquet fallback named in EVALUATION_FRAMEWORK.md
§6a; it is reformatted (one row per system turn, user utterances live in
`context`, `dialog_acts` are dialog-level rather than turn-level) but it
preserves the source `dialog_id`, `turn_id`, and `dialog_acts` — enough for
our purposes. The miner adapts to this structure.

**Trade-offs of using the mirror:** (a) per-turn slot annotations are not
available — only dialog-level. The miner therefore uses *dialog-level*
temporal presence as the filter and yields all user turns from those
dialogues; the tagging step is what actually classifies each user turn
(any user utterance that isn't temporal-looking ends up in
`_unclassified.json` and is excluded from the bank). (b) The
`normalized_meaning` field is populated from the dialog-level slot values
rather than the per-turn annotation — adequate as a traceability hint.

### Secondary — MultiWOZ 2.2

| Field            | Value                                                          |
|------------------|----------------------------------------------------------------|
| Upstream source  | MultiWOZ 2.2                                                   |
| HF mirror used   | `tuetschek/multi_woz_v22` — JSON re-upload of pfb30/multi_woz_v22 |
| Loader call      | `load_dataset("tuetschek/multi_woz_v22")`                      |
| License          | Apache-2.0 (inherited from upstream)                           |
| Why this dataset | Widens the variety of time-negotiation phrasings from booking sub-flows. Not primary — wrong domain. (EVALUATION_FRAMEWORK.md §6b) |
| Services mined   | `restaurant`, `hotel` — `train`/`taxi` removed 2026-05-24 as wrong-domain (transit-time idiom biases the bank away from appointment scheduling) |
| Filter rule      | Keep user turns whose frame state contains a temporal slot suffix in `evaluation/mining/multiwoz.py::TEMPORAL_SLOT_SUFFIXES` (`book_time`, `book_day`, `leaveat`, `arriveby`, `duration`). |

**Why the mirror, not the canonical loader.** Same reason as SGD —
`pfb30/multi_woz_v22` requires a dataset script that `datasets>=4` rejects.
The tuetschek mirror is the pfb30 builder's output saved as plain JSON files,
so the schema is preserved (columnar turns, parallel `slots_values_name` /
`slots_values_list` arrays per state).

### Optional — KVRET

Not currently mined. See EVALUATION_FRAMEWORK.md §6c.

## Domain-noun stripping

Each mined utterance is also written in a domain-stripped form so the phrasing
is reusable in the banking-appointment domain (Section 5). The substitution
table lives in [`evaluation/mining/substitutions.py`](../mining/substitutions.py)
— it is intentionally light-touch and preserves the *temporal* surface intact.
The unstripped original is always retained under `original_context` for
traceability.

## Workflow

```bash
# 1. Mine both datasets (writes mined/sgd_temporal_raw.jsonl and mined/multiwoz_temporal_raw.jsonl)
python -m evaluation.mining.cli mine --source all

# 2. Tag with difficulty buckets (writes ../phrase_bank/temporal_expressions.json + _unclassified.json)
python -m evaluation.mining.cli tag

# 3. Generate the summary (writes ../phrase_bank/SUMMARY.md)
python -m evaluation.mining.cli summarize

# Or do all three in one go:
python -m evaluation.mining.cli all
```

After step 2, the **manual review pass** kicks in:
- Open `../phrase_bank/_unclassified.json` and decide for each entry whether
  to widen heuristics in `evaluation/mining/tagging.py`, add a discovery
  bucket (log it in `../phrase_bank/bucket_log.md`), or drop the entry.
- Re-run step 2 after tweaking heuristics. Tagging is idempotent.
- Spot-check auto-tagged entries via `SUMMARY.md` — if a bucket looks wrong,
  iterate on the regex set.

## Where the bank goes from here

The simulator prompt is composed as `goal + persona_profile + frozen_phrasing`
(EVALUATION_FRAMEWORK.md §2a). `frozen_phrasing` is sampled from the tagged
bank at the tier's difficulty level — Tier 1 → `specific date`, Tier 4 →
`vague`, Tier 7 → `unsupported`, and so on (§5). Pinning the sampled phrasing
per scenario-run is what makes parse accuracy comparable across reps.
