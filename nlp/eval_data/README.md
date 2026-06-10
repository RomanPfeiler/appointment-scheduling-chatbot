# `nlp/eval_data/` — Intrinsic-eval gold datasets

This folder holds the two held-out gold sets used by the NLP intrinsic-eval
harness (`nlp/eval_datetime.py`, `nlp/eval_entity.py`). They are reused
**unchanged** across all three NLP arms (Arm 1 spaCy/dateparser, Arm 2 local
LLM, Arm 3 API LLM), so the cross-arm comparison is honest.

These datasets are **held out**: spaCy's matcher is built from
`nlp/synonyms.py`, not from any data here. The dateparser arm uses only its
library defaults plus our surface-text heuristics, with no fitting on these
samples.

## Files

| File | Schema | Source | Status |
|---|---|---|---|
| `datetime_gold.json` | JSON with `_meta` + `rows[]` | sampled from `evaluation/phrase_bank/` | needs human verification of `verified_*` fields |
| `entity_gold.jsonl`  | one row per line | controls from SGD raw + with-label authored by Claude in chat | needs human verification of `verified_*` fields |
| `entity_with_label.jsonl` | one row per line | authored by Claude in chat — see `_build_entity_with_label.py` | input to `_combine_entity_gold.py` |
| `entity_controls.jsonl`   | one row per line | sampled from `evaluation/datasets/mined/sgd_temporal_raw.jsonl` — see `_build_entity_controls.py` | input to `_combine_entity_gold.py` |
| `_build_datetime_gold.py`   | one-shot builder | – | re-run anytime |
| `_build_entity_with_label.py` | one-shot builder | – | re-run anytime |
| `_build_entity_controls.py`   | one-shot builder | – | re-run anytime |
| `_combine_entity_gold.py`     | combiner + anti-bleed audit gate | – | re-run after either input changes |
| `results/`           | `.json` per `(component, arm, timestamp)` | written by eval CLIs | not yet populated |

## Datetime gold (`datetime_gold.json`)

- **Source banks**: `evaluation/phrase_bank/temporal_expressions.json`
  (en_native, SGD + MultiWOZ) and `evaluation/phrase_bank/swiss_variants.json`
  (en_de, en_fr, en_it).
- **Inclusion filter**: only rows whose `expression_text` contains an actual
  datetime surface token (regex set in `_build_datetime_gold.py`). The 2,861
  `unsupported` bucket is out of scope for parse accuracy.
- **Stratification target**: 30 per `(difficulty_bucket × language_variant)`,
  buckets ∈ `{specific date, relative, vague, compound}`, variants ∈
  `{en_native, en_de, en_fr, en_it}`. Sparse cells (e.g. `compound × en_it`)
  sample all available.
- **Anchor for relative-date resolution**: `2026-05-31T12:00:00+02:00`
  (Europe/Zurich). Fixed by the harness so re-runs are reproducible.
- **`verified_*` fields**: intentionally left `null`. Auto-deriving from the
  same regex set the Arm 1 parser uses would test the parser against itself.
  Human verification required before the intrinsic eval is reportable.
- **Held-out from scenarios**: scenarios reference phrase-bank text inline
  (`frozen_phrasing`), not by `expression_id`, so there is no ID-based
  conflict. If `evaluation/scenarios/generator.py` is rerun in the future,
  the sampled IDs in `datetime_gold.json` should be excluded from `frozen_phrasing`
  sampling at that time.

## Entity gold (`entity_gold.jsonl`)

The plan originally specified pure-SGD sourcing for the entity-gold rows.
During Step 1 of the Arm 1 slice this assumption was checked and rejected:
SGD's `Banks_1` covers event ticketing / account balances, not Swiss-bank
appointment topics (investing / mortgage / pension). The 2,663 SGD entries in
`temporal_expressions.json` contain **zero** banking topic/medium synonym
substrings.

**Decision (recorded here, will be folded into ARCHITECTURE Decision Log when
Arm 1 implementation lands)**: hybrid sourcing — SGD for the `(none, none)`
controls (natural-language false-positive test), Claude-authored in-chat
banking utterances for the 150 with-label rows under the stratification
below. Anti-bleed (IMPROVEMENT_PLAN §6) is preserved because:

- The canonical synonym list (`nlp/synonyms.py`) was authored from domain
  knowledge **before** the eval rows.
- The 60 paraphrase rows are authored **under the explicit constraint** that
  no surface substring overlaps with any synonym in `nlp/synonyms.py`. The
  builder asserts this row-by-row at write time.
- The 50 SGD controls are sampled from a corpus independent of both the
  synonym list and the authoring context.
- The combiner runs an automated audit on every build and refuses to write
  the gold file if `paraphrase_coverage < 0.30`.

Disclosure for the report's Data section: "Entity intrinsic-eval gold is a
hybrid set — 50 negative controls sampled from SGD `sgd_temporal_raw.jsonl`
and 150 banking-appointment utterances authored in-chat by Claude under
explicit canonical/paraphrase constraints, then human-verified."

### Stratification (200 rows)

| `row_kind` | Count | Topic distribution | Medium distribution |
|---|---:|---|---|
| `canonical_topic_only`   | 30 | 10 investing, 10 mortgage, 10 pension | – |
| `paraphrase_topic_only`  | 30 | 10 investing, 10 mortgage, 10 pension | – |
| `canonical_medium_only`  | 30 | – | 10 branch, 10 online, 10 phone |
| `paraphrase_medium_only` | 30 | – | 10 branch, 10 online, 10 phone |
| `canonical_both`         | 30 | distributed across all 9 (topic × medium) combos | distributed |
| `control_none_none`      | 50 | – (all `none`) | – (all `none`) |
| **Total**                | **200** | investing 31, mortgage 30, pension 29, none 110 | branch 32, online 31, phone 27, none 110 |

**Hard negatives** in the controls (20 of 50): SGD utterances containing a
synonym substring incidentally (e.g. `"What's their phone number?"` — has
`phone` but means phone number, not contact-by-phone intent). These test the
matcher's context-sensitivity. The remaining 30 controls have no synonym
substring at all.

### Anti-bleed audit

`_combine_entity_gold.py` computes `paraphrase_coverage` =
(# labelled rows whose labelled class has no corresponding synonym substring) /
(# labelled rows). It refuses to write the gold file if this is below
**0.30**. Current value: **0.400** (60 paraphrase rows / 150 labelled rows).
The report should quote this number.

## Re-building everything

```bash
python -m nlp.eval_data._build_datetime_gold
python -m nlp.eval_data._build_entity_with_label
python -m nlp.eval_data._build_entity_controls
python -m nlp.eval_data._combine_entity_gold
```

The first three are independent; the combiner depends on the second and
third.

## Human verification workflow

Each gold row has `verified_*` fields set to `null` and `verified: false`.
Reviewing means:

1. Open the file in an editor.
2. For each row: read `utterance` (or `expression_text`), decide the correct
   labels, fill the `verified_*` fields, set `verified: true`.
3. If `topic_proposed`/`contact_medium_proposed` (entity) or the
   `difficulty_bucket` (datetime) was wrong, override in the `verified_*`
   fields and add a `verification_notes` string.
4. The intrinsic eval CLIs ignore rows with `verified: false` and refuse to
   produce a final result if fewer than N% of rows are verified (configurable;
   default 90%).

Authorship of `entity_with_label.jsonl` is **Claude Code (Anthropic) in the
implementation session**, guided by `nlp/synonyms.py`. The builder script
that emitted the rows is committed for full reproducibility.
