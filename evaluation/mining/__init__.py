"""Phrase-bank mining package (EVALUATION_FRAMEWORK.md §5, §6).

One-shot data-prep tools that extract temporal/scheduling expressions from
SGD + MultiWOZ, tag them by difficulty, and produce the phrase bank that
the simulator pins as `frozen_phrasing` per scenario-run.

Entry point: ``python -m evaluation.mining.cli mine|tag|summarize``.
"""
