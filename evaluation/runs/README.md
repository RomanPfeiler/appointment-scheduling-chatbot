# `evaluation/runs/`

One subdirectory per run.

## Directory layout

```
runs/
├── <stage>/<run_id>/                   # scenario runs
│   ├── manifest.json                   # RunManifest — config, git_commit, status
│   ├── records/<scenario_id>__rep<k>.json
│   ├── transcripts/<scenario_id>__rep<k>.md
│   ├── judge/<scenario_id>__rep<k>.json
│   └── metrics/{summary.json, summary.md}
└── adhoc/<run_id>/                     # always-on Chainlit sessions
    ├── manifest.json
    ├── records/conversation.json
    └── transcripts/conversation.md
```

## `run_id` format

`<YYYYMMDD_HHMMSS>__<stage>__<git_commit_short>[__<extra>]`

Examples:
- `20260524_142315__baseline__a00c977` — scheduled scenario run
- `20260524_173042__adhoc__a00c977__abc12345` — Chainlit session (extra =
  short session id)

## `manifest.json` status field

- `in_progress` — recorder constructed; record(s) may or may not have been
  written yet. The session/runner is alive (or, if not, it crashed).
- `complete` — finalized cleanly.
- `crashed` — flipped by `python -m evaluation.adhoc gc` from a stale
  `in_progress`.
- `failed` — finalized with an error (the runner caught it and reported it
  in the manifest).

## Gitignore policy

Run artifacts are not committed by default — they accumulate quickly and
their values are derived from code + config. Add specific `.gitignore`
entries here when the directory starts producing committed-by-accident files.
