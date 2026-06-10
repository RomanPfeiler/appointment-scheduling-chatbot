# Bucket Log

Tracks difficulty buckets added beyond the five seed buckets in
EVALUATION_FRAMEWORK.md §5. Required by Section 5: "Record bucket additions
in `phrase_bank/bucket_log.md` with the trigger phrasing and a one-line
definition."

## Seed buckets (not additions — recorded here for reference)

| Bucket           | Definition                                                  |
|------------------|-------------------------------------------------------------|
| `specific date`  | Explicit calendar date / clock time — e.g. "March 20th at 2pm". |
| `relative`       | Relative-to-now — e.g. "next Tuesday", "tomorrow morning".  |
| `vague`          | Under-specified time reference — e.g. "sometime next week". |
| `compound`       | Multiple or disjunctive constraints — e.g. "Tuesday or Thursday afternoon". |
| `unsupported`    | Patterns the API cannot fulfil by design — recurring series, attendee constraints, multi-week durations. Feeds Tier 7. |

## Discovery buckets

Added when ≥3 phrasings cluster around a pattern that doesn't fit the seeds.
Each entry must include: trigger phrasing examples, one-line definition,
date added, who added it.

### `deadline-driven`

| Field       | Value                                                                              |
|-------------|------------------------------------------------------------------------------------|
| Date added  | 2026-05-24                                                                         |
| Triggers    | "before Friday", "by noon Monday", "no later than the 15th"                        |
| Definition  | Open-window request bounded by an upper deadline; agent must search backwards from the deadline. |
| Anticipated tier | Tier 6 (Other)                                                                |

### `negative constraint`

| Field       | Value                                                                              |
|-------------|------------------------------------------------------------------------------------|
| Date added  | 2026-05-24                                                                         |
| Triggers    | "not Monday", "any day except Tuesday", "avoid mornings"                           |
| Definition  | Request defined by exclusion; agent must search the complement.                    |
| Anticipated tier | Tier 6 (Other)                                                                |

### `open-ended`

| Field       | Value                                                                              |
|-------------|------------------------------------------------------------------------------------|
| Date added  | 2026-05-24                                                                         |
| Triggers    | "whenever you have time", "anytime", "whenever works"                              |
| Definition  | No constraint at all; agent must propose a sensible default window.                |
| Anticipated tier | Tier 6 (Other) and as a corner case for Tier 4 (Broad Window)                 |

---

> The first three discovery buckets are pre-seeded into the tagging heuristics
> (`evaluation/mining/tagging.py`) because the framework explicitly predicts
> them as "likely discovery buckets" (§5). They graduate to "real" discovery
> buckets only when the mined data actually fills them — verify against
> `SUMMARY.md` after a mining run. If a bucket stays empty, drop it.

## Language-variant axis (added 2026-05-24)

Beyond the difficulty bucket, every phrase-bank entry carries a
``language_variant`` tag at the *scenario* level:

| Variant      | Source                                        | Rationale |
|--------------|-----------------------------------------------|-----------|
| `en_native`  | Mined SGD + MultiWOZ (this file's entries)    | The empirical bulk; American/British native English. |
| `en_de`      | Hand-curated `swiss_variants.json` (40)       | German-influenced calques in customers' English — DD.MM dates, 24-h "o'clock", "next week Tuesday", "half 3" = 14:30. |
| `en_fr`      | Hand-curated `swiss_variants.json` (35)       | French-influenced calques — `13h30` notation, "the 14 of march", "rendez-vous", code-switched day names. |
| `en_it`      | Hand-curated `swiss_variants.json` (25)       | Italian-influenced calques — code-switched month/day names ("marzo", "martedi"), "of morning". |

**Scope and caveats (carry into the report's Limitations section):**

- The Swiss set is small (~100 entries) compared to the mined bank (~5,400).
  Coverage of (difficulty × variant) is uneven by design — some buckets
  have only 3 entries per variant.
- "Speakers with German/French/Italian L1 background using English" is a
  modelled construct, not an empirically measured population. The calques
  reflect plausible patterns from the author's familiarity, not corpus
  evidence — collecting that corpus is future work.
- Code-switched nouns ("rendez-vous", "Donnerstag", "martedi") are
  represented; full code-switching, non-Latin scripts, and L2 grammatical
  errors orthogonal to syntax calques are not covered.

The scenario generator (`evaluation/scenarios/generator.py`) samples from the
mined bank when `language_variant == en_native` and from
`swiss_variants.json` otherwise, falling back to the mined bank if the
specific (variant × bucket) subset is empty.
## 2026-05-25 — out-of-domain filter pass

- Entries before: 5404
- Entries after: 2663
- Dropped: 2741 (2741 by keyword, 0 by source service)
- Example drops:
  - [keyword='dentist'] 'No, but I want to make an appointment with the dentist on that day at 2:30 pm.'
  - [keyword='dentist'] 'I want to complete my Check up soon for which I want to search for a Dentist. Can you help me to find the one for me?'
  - [keyword='dentist'] 'No, skip adding this event. Could you make an appointment with the dentist on that day. Is there anything available at 11:30 am?'
  - [keyword='dentist'] 'Sounds good. Could you make me an appointmet with the dentist at 12:30 pm?'
  - [keyword='dentist'] 'Good, can you book me appointment to the dentist at 3:15 pm?'
  - [keyword='dentist'] 'That dentist sounds good to me. Can you check when I have time availanble on the 10th of March?'
  - [keyword='dentist'] 'Please try to book an appointment at 11:45 am on that date with the dentist.'
  - [keyword='dentist'] 'Is it possible to book an appointment with the dentist on March 12th?'
  - [keyword='dentist'] 'Would you set up an appointment with a dentist around 12:30 pm?'
  - [keyword='dentist'] 'That sounds nice. Could I also make an appointment with the dentist on that day around 3 in the afternoon?'

