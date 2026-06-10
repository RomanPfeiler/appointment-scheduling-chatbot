# `evaluation/reports/`

Cross-run reporting artifacts. Per EVALUATION_FRAMEWORK.md §13, this folder
backs the report's Data, EDA, and Results sections.

## Files

- [`kpi_history.csv`](kpi_history.csv) — one row per scenario-run, tagged
  with `git_commit` + `change_note`. The project's "track difference over
  time" mechanism (Section 7d). Ad-hoc Chainlit sessions do **not** append
  to this file.

## Subdirectories

- [`figures/`](figures/) — plots and tables generated for the report
  (turn-count box plots, judge radar charts, latency histograms, etc.).
  Committed so the report builds reproducibly.
