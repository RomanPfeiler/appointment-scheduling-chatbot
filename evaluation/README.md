# Evaluation framework

Implementation of the design in [`../architecture/EVALUATION_FRAMEWORK.md`](../architecture/EVALUATION_FRAMEWORK.md).

This package is built in stages — see `EVALUATION_FRAMEWORK.md` Section 12 for
the build order. The components landed so far:

| Component | Status | File(s) |
|---|---|---|
| Conversation record schema | done | [`schemas.py`](schemas.py) |
| Storage layout + atomic writes | done | [`storage.py`](storage.py) |
| ConversationRecorder runtime API | done | [`recorder.py`](recorder.py) |
| Markdown transcript renderer | done | [`transcript.py`](transcript.py) |
| KPI history CSV writer | done | [`kpi_history.py`](kpi_history.py) |
| Always-on Chainlit ad-hoc hook + CLI | done | [`adhoc.py`](adhoc.py) |
| Phrase bank (mining + tagging) | see parallel Step 1a | `phrase_bank/`, `datasets/`, `mining/` |
| Scenarios | not started | `scenarios/` |
| Runner | not started | (Step 3) |
| Metrics | done | [`metrics.py`](metrics.py) |
| Judge | not started | (Step 6) |

## Where conversation logs go

Every Chainlit chat session (always-on) and every scenario-run (later) writes
to `runs/<stage>/<run_id>/`. Layout:

```
runs/
├── <stage>/<run_id>/                   # scenario runs (baseline, nlp, ...)
│   ├── manifest.json
│   ├── records/<scenario_id>__rep<k>.json
│   ├── transcripts/<scenario_id>__rep<k>.md
│   ├── judge/<scenario_id>__rep<k>.json
│   └── metrics/{summary.json, summary.md}
└── adhoc/<run_id>/                     # one per Chainlit session
    ├── manifest.json
    ├── records/conversation.json
    └── transcripts/conversation.md
```

`run_id` format: `<YYYYMMDD_HHMMSS>__<stage>__<git_commit_short>[__<extra>]`.

## Inspecting ad-hoc runs

```bash
python -m evaluation.adhoc list           # 10 most recent (override with --limit)
python -m evaluation.adhoc show <run_id>  # print the markdown transcript
python -m evaluation.adhoc gc             # mark stale in_progress manifests as crashed
```

For programmatic access:

```python
from evaluation.storage import list_adhoc_runs, load_record
latest = list_adhoc_runs(limit=1)[0]
record = load_record(latest / "records" / "conversation.json")
```

## Subdirectory conventions

- `runs/` — committed-as-`.gitkeep` only; actual run artifacts are gitignored
  by the project root `.gitignore` (TODO: add when the directory has noisy
  output to ignore).
- `reports/kpi_history.csv` — committed. One row per scenario-run; ad-hoc
  sessions do **not** append rows. This is the project's "track difference
  over time" mechanism (Section 7d).
- `reports/figures/` — committed plots/tables for the report.

## Schema versioning

Every record carries a `schema_version` field (currently `"1.0"`). When the
schema changes in a breaking way, bump the version in `schemas.py` and add a
migration note here.
