# Scenario Selection Profiles

This directory holds **named selection profiles** that tell the evaluation
runner which scenarios to execute. The profiles are the project's answer to
"how many scenarios should be taken for the evaluation, and which ones."

> **Status (2026-05-24):** the profiles below are committed *stubs*. The actual
> scenario JSON files (Tier 1–7) under `evaluation/scenarios/` are not yet
> authored — that is the deferred Step 1b. The profile schema is frozen
> now so scenarios can target it the moment they exist. The runner that
> consumes these profiles is Step 3 (EVALUATION_FRAMEWORK.md §11).

## How a selection profile is read by the runner

```
candidate_set = union(scenario for tier in profile.tiers if scenario.tier == tier)
if profile.include_ids:
    selected = candidate_set ∩ profile.include_ids   # explicit inclusion wins
else:
    selected = sample(candidate_set per tier, k=profile.max_per_tier, seed=profile.seed)
selected = selected \ profile.exclude_ids
runs = [scenario × profile.reps for scenario in selected]
```

This precedence means: `include_ids` is the surgical override; sampling +
`max_per_tier` is the bulk knob; `exclude_ids` is the last-mile cleanup.

## Schema

```yaml
name: <string>              # must match the filename without .yaml
description: <string>       # one line, shown by the runner CLI
tiers: [int, ...]           # tiers to include (1..7)
max_per_tier: <int>         # cap per tier (use a large number for "all")
include_ids: [str, ...]     # optional — exact scenario_ids to include
exclude_ids: [str, ...]     # optional — exact scenario_ids to exclude
seed: <int>                 # sampling determinism (consistent across re-runs)
reps: <int>                 # times each scenario runs (statistics, §10)
notes: <string>             # free text
```

## Committed profiles

| File                   | Intended use                                  | Approx. scenarios | Approx. conversations (× reps) |
|------------------------|-----------------------------------------------|-------------------|-------------------------------|
| `smoke.yaml`           | Dev iteration / quick smoke                   | ~14               | ~14 (reps=1)                  |
| `representative.yaml`  | Realistic-cost evaluation                     | ~70               | ~210                          |
| `tier1_2_only.yaml`    | Time-short fallback (per §12 cut-list)        | ~40               | ~120                          |
| `full.yaml`            | The ~500-scenario target from §12             | ~500              | ~1500 baseline + ~1500 +NLP   |

## Authoring conventions

- The filename (sans `.yaml`) **must** equal the `name:` field — the runner
  uses both for cross-checks.
- `seed` should differ across profiles meant to compose different samples
  (don't reuse `42` everywhere if you want diversity across the smoke and
  representative samples).
- `reps` controls statistical power per §10. Don't drop below 3 for the
  representative or full profiles unless you accept wider confidence intervals.
- Use `include_ids` when you need a specific scenario in the run regardless
  of sampling — e.g. when reproducing a previous regression.
