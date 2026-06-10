"""LLM-as-a-Judge for the appointment scheduling chatbot evaluation.

Implements Step 6 of the evaluation framework (EVALUATION_FRAMEWORK.md §8).
The judge is a **separate CLI step** run after the runner completes for a given
``run_id``. It reads each :class:`ConversationRecord`, calls Gemini 3 times per
record (variance reduction per §8b), writes :class:`JudgeScoreSet` objects back
into the records and into a ``judge/`` sidecar directory, then updates
``kpi_history.csv`` with aggregate ``judge_mean_*`` fields.

Usage::

    python -m evaluation.judge run \\
        --run-id <run_id> \\
        --stage baseline \\
        [--model gemini-2.5-flash] \\
        [--temperature 0.3] \\
        [--overwrite]

    python -m evaluation.judge list [--limit 10]
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import logging
import os
import statistics
import sys
import time
from pathlib import Path
from typing import Any

from google import genai
from google.genai import types

from evaluation import kpi_history as kpi_history_mod
from evaluation.schemas import ConversationRecord, JudgeScoreSet
from evaluation.storage import (
    RunPaths,
    load_record,
    write_json,
    write_record,
)
from evaluation.transcript import render as render_transcript

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

JUDGE_MODEL_DEFAULT = "gemini-2.5-flash"
JUDGE_TEMPERATURE = 0.3
# Default reps per record. Was 3 (per the original §8b draft). Lowered to 1 in
# 2026-05 because with T=0.3 + strict JSON schema, the 3 reps produced
# essentially identical integer scores (only the justification wording
# varied) — so the cost was 3× without measurable variance information.
# Pass --judge-reps N on the CLI to override (e.g. for a one-off reliability run).
# `JUDGE_REPS` is kept as a backwards-compat alias for code/tests that import it.
JUDGE_REPS_DEFAULT = 1
JUDGE_REPS = JUDGE_REPS_DEFAULT

_RECOVERY_TIERS: frozenset[int] = frozenset({3, 4, 5})

# Tier 7 (out-of-scope) systematically mis-scores on Negotiation Effectiveness
# and Customer Experience because the standard rubrics reward "offered
# alternatives" and "smooth booking" — but a correct Tier 7 outcome is a
# polite refusal that by design does neither. Surfaced in the 2026-05-25
# post-fix smoke run; see `project_presentation/progress/learnings.md`.
# These dimensions are now SKIPPED for Tier 7 (set to null in the JSON output);
# Tier 7 success is signalled by the deterministic `refusal_accepted`
# termination reason in the conversation record.
_NEGOTIATION_NOT_SCORED_TIERS: frozenset[int] = frozenset({7})
_CUSTOMER_EXPERIENCE_NOT_SCORED_TIERS: frozenset[int] = frozenset({7})

_PROMPT_PATH = Path(__file__).parent / "judge_prompt.md"

_NEGOTIATION_RUBRIC = """\
### 2. Negotiation Effectiveness (1–5)

When availability didn't match the user's request, how well did the agent
handle it?

- **5** — Proposed close alternatives in the same turn, offered 3–5 options,
  avoided slots the user had already rejected
- **4** — Proposed reasonable alternatives, minor issues (slightly too few or
  too many options)
- **3** — Proposed alternatives but needed an extra turn, or proposed distant
  alternatives first
- **2** — Just reported unavailability and asked the user to pick a new time
  without offering options
- **1** — Got stuck, repeated the same unavailable options, or lost context
  entirely"""

_NEGOTIATION_NOT_SCORED = (
    "### 2. Negotiation Effectiveness\n\n"
    "Not scored for this tier (Tier 7 is out-of-scope by design — refusing IS "
    "the correct behavior, not negotiating alternatives). "
    "Set ``negotiation_effectiveness`` to ``null`` in your output."
)

_CUSTOMER_EXPERIENCE_RUBRIC = """\
### 4. Customer Experience (1–5)

Imagine you are the customer who walked away from this conversation. How does
the interaction feel as a piece of customer service? Weight: tone of voice,
number of unproductive turns, whether the agent ever exposed tool errors
(e.g. "end_datetime is in the past", "the system is encountering an issue")
or technical jargon to the user, repeated/identical apologies, fabricated
system explanations, and your overall satisfaction with the outcome.

- **5** — Smooth, professional, you'd happily recommend this bank to a friend
- **4** — Mostly fine; one minor friction point you'd shrug off
- **3** — Workable but tiring; multiple apologies, a clarification you
  shouldn't have had to give, or a small amount of jargon
- **2** — Frustrating; agent leaked system internals or felt clueless; you
  seriously considered hanging up
- **1** — You would switch banks after this conversation"""

_CUSTOMER_EXPERIENCE_NOT_SCORED = (
    "### 4. Customer Experience\n\n"
    "Not scored for this tier (Tier 7 is out-of-scope by design — the standard "
    "Customer Experience rubric rewards smooth bookings, but a correct Tier 7 "
    "outcome is a polite refusal which the standard rubric mis-scores). "
    "Set ``customer_experience`` to ``null`` in your output."
)

_RECOVERY_RUBRIC = """\
### 5. Recovery Quality (1–5)

When the first slot proposal was rejected or unavailable, how gracefully did the
agent recover?

- **5** — Maintained full context, expanded search intelligently, never
  re-asked information the user had already given
- **4** — Good recovery with one minor context loss
- **3** — Recovered but lost some context or made redundant API calls
- **2** — Partial restart — re-asked topic or contact medium the user had
  already specified
- **1** — Full restart or complete loss of conversation context"""

_RECOVERY_NOT_SCORED = (
    "### 5. Recovery Quality\n\n"
    "Not scored for this tier (only Tiers 3–5). "
    "Set ``recovery_quality`` to ``null`` in your output."
)

_JSON_SCHEMA_DESCRIPTION = """\
{
  "temporal_understanding": <integer 1-5>,
  "negotiation_effectiveness": <integer 1-5, or null if not scored>,
  "conversational_efficiency": <integer 1-5>,
  "customer_experience": <integer 1-5, or null if not scored>,
  "recovery_quality": <integer 1-5, or null if not scored>,
  "justifications": {
    "temporal_understanding": "<one sentence>",
    "negotiation_effectiveness": "<one sentence, or null if not scored>",
    "conversational_efficiency": "<one sentence>",
    "customer_experience": "<one sentence, or null if not scored>",
    "recovery_quality": "<one sentence, or null if not scored>"
  },
  "overall_notes": "<optional overall observation, or null>"
}"""

# Response schema for Gemini JSON mode — keeps output deterministic.
# Note: Gemini's schema parser uses its own enum for `type` values and does NOT
# accept JSON-Schema-style arrays like ["integer", "null"]. Use `nullable: True`
# for optional fields instead. Range constraints (minimum/maximum) are validated
# in Python code after parsing.
#
# `negotiation_effectiveness` and `customer_experience` are nullable so the
# judge can correctly emit `null` for Tier 7 (where these dimensions don't
# apply per `_NEGOTIATION_NOT_SCORED_TIERS` / `_CUSTOMER_EXPERIENCE_NOT_SCORED_TIERS`).
_JUDGE_RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "temporal_understanding":    {"type": "integer"},
        "negotiation_effectiveness": {"type": "integer", "nullable": True},
        "conversational_efficiency": {"type": "integer"},
        "customer_experience":       {"type": "integer", "nullable": True},
        "recovery_quality":          {"type": "integer", "nullable": True},
        "justifications": {
            "type": "object",
            "properties": {
                "temporal_understanding":    {"type": "string"},
                "negotiation_effectiveness": {"type": "string", "nullable": True},
                "conversational_efficiency": {"type": "string"},
                "customer_experience":       {"type": "string", "nullable": True},
                "recovery_quality":          {"type": "string", "nullable": True},
            },
        },
        "overall_notes": {"type": "string", "nullable": True},
    },
    "required": [
        "temporal_understanding",
        "negotiation_effectiveness",
        "conversational_efficiency",
        "customer_experience",
        "recovery_quality",
        "justifications",
    ],
}

_MAX_RETRIES = 6


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class JudgeError(Exception):
    """Raised when a single judge rep fails unrecoverably."""


# ---------------------------------------------------------------------------
# JudgeSummary dataclass
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class JudgeSummary:
    """Aggregated judge scores for a completed evaluation run.

    Two kinds of standard deviation are reported (per the user request 2026-05-25):

    - ``std_*`` — cross-scenario stdev over the flat list of all scores. This is
      "how much do scenarios disagree on this dimension" — useful for spotting
      tier-dependent dispersion.
    - ``std_within_*`` — within-record stdev across the N reps, then averaged
      across scenarios. This is "how much does the judge disagree with itself
      on the same conversation" — judge reliability. Only meaningful when reps>1;
      stays ``None`` when reps==1.
    """

    run_id: str
    stage: str
    judge_model: str
    judge_temperature: float
    judge_reps: int
    record_count: int
    scored_count: int
    failed_count: int
    mean_temporal: float | None
    mean_negotiation: float | None
    mean_efficiency: float | None
    mean_customer_experience: float | None
    mean_recovery: float | None
    std_temporal: float | None
    std_negotiation: float | None
    std_efficiency: float | None
    std_customer_experience: float | None
    std_recovery: float | None
    # Within-record (across-rep) stds — judge reliability per scenario, averaged
    std_within_temporal: float | None
    std_within_negotiation: float | None
    std_within_efficiency: float | None
    std_within_customer_experience: float | None
    std_within_recovery: float | None

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


# ---------------------------------------------------------------------------
# ScenarioJudge — scores a single ConversationRecord
# ---------------------------------------------------------------------------


def _is_rate_limited(exc: Exception) -> bool:
    msg = str(exc)
    return "429" in msg or "RESOURCE_EXHAUSTED" in msg.upper()


def _parse_retry_delay(exc: Exception) -> float:
    import re as _re
    m = _re.search(r"retry in (\d+(?:\.\d+)?)s", str(exc), _re.IGNORECASE)
    return float(m.group(1)) + 2.0 if m else 15.0


class ScenarioJudge:
    """Scores a single :class:`ConversationRecord` JUDGE_REPS times.

    Uses Gemini JSON mode for deterministic structured output. Follows the
    same direct-client pattern as ``simulator.py`` — not via ``call_gemini()``
    which is for the agent's function-calling use case.
    """

    def __init__(
        self,
        *,
        gemini_client: Any,
        model: str = JUDGE_MODEL_DEFAULT,
        temperature: float = JUDGE_TEMPERATURE,
        prompt_template: str,
        judge_reps: int = JUDGE_REPS_DEFAULT,
    ) -> None:
        self._client: genai.Client = gemini_client
        self._model = model
        self._temperature = temperature
        self._template = prompt_template
        self._judge_reps = max(1, int(judge_reps))

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def score(
        self,
        record: ConversationRecord,
        transcript: str,
        scenario_description: str,
    ) -> list[JudgeScoreSet]:
        """Run ``judge_reps`` judge calls. Returns list of JudgeScoreSets.

        Individual rep failures are logged and skipped. Returns an empty list
        only if ALL reps fail (caller should log an error and continue).
        """
        results: list[JudgeScoreSet] = []
        for rep_index in range(1, self._judge_reps + 1):
            try:
                score_set = self._score_once(
                    record, transcript, scenario_description, rep_index
                )
                results.append(score_set)
            except Exception as exc:
                logger.warning(
                    "Judge rep %d/%d failed for %s: %s",
                    rep_index,
                    self._judge_reps,
                    record.scenario_id,
                    exc,
                )
        return results

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _score_once(
        self,
        record: ConversationRecord,
        transcript: str,
        scenario_description: str,
        rep_index: int,
    ) -> JudgeScoreSet:
        """Single LLM call → JudgeScoreSet. Raises JudgeError on failure."""
        filled_prompt = self._build_prompt(record, transcript, scenario_description)
        raw_json = self._call_gemini(filled_prompt)
        return self._parse_response(raw_json, record, rep_index)

    def _build_prompt(
        self,
        record: ConversationRecord,
        transcript: str,
        scenario_description: str,
    ) -> str:
        """Fill the template with scenario context and transcript.

        Per-tier rubric inclusion:
        - Recovery Quality: only for Tiers 3–5 (`_RECOVERY_TIERS`).
        - Negotiation Effectiveness: skipped for Tier 7 (out-of-scope refusal
          should not be measured against an "offered alternatives" rubric).
        - Customer Experience: skipped for Tier 7 (same rationale).
        """
        try:
            tier_int = int(record.tier)
        except (ValueError, TypeError):
            # adhoc / unknown tier — keep all dimensions on by default
            tier_int = -1

        include_recovery = tier_int in _RECOVERY_TIERS
        include_negotiation = tier_int not in _NEGOTIATION_NOT_SCORED_TIERS
        include_customer = tier_int not in _CUSTOMER_EXPERIENCE_NOT_SCORED_TIERS

        recovery_section = (
            _RECOVERY_RUBRIC if include_recovery else _RECOVERY_NOT_SCORED
        )
        negotiation_section = (
            _NEGOTIATION_RUBRIC if include_negotiation else _NEGOTIATION_NOT_SCORED
        )
        customer_experience_section = (
            _CUSTOMER_EXPERIENCE_RUBRIC if include_customer else _CUSTOMER_EXPERIENCE_NOT_SCORED
        )

        return self._template.format(
            scenario_id=record.scenario_id,
            tier=record.tier,
            persona_profile=record.persona_profile or "unknown",
            scenario_description=scenario_description,
            transcript=transcript,
            negotiation_section=negotiation_section,
            customer_experience_section=customer_experience_section,
            recovery_section=recovery_section,
            json_schema_description=_JSON_SCHEMA_DESCRIPTION,
        )

    def _call_gemini(self, prompt: str) -> str:
        """Call Gemini with JSON mode. Returns the raw JSON string."""
        contents = [
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)],
            )
        ]
        config = types.GenerateContentConfig(
            temperature=self._temperature,
            response_mime_type="application/json",
            response_schema=_JUDGE_RESPONSE_SCHEMA,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )

        for attempt in range(_MAX_RETRIES):
            try:
                response = self._client.models.generate_content(
                    model=self._model,
                    contents=contents,
                    config=config,
                )
                break
            except Exception as exc:
                if _is_rate_limited(exc) and attempt < _MAX_RETRIES - 1:
                    delay = _parse_retry_delay(exc)
                    logger.warning(
                        "Judge 429 on attempt %d/%d — sleeping %.1fs",
                        attempt + 1,
                        _MAX_RETRIES,
                        delay,
                    )
                    time.sleep(delay)
                else:
                    raise JudgeError(f"Gemini call failed: {exc}") from exc

        # Extract text, skip thought parts (defensive, same as simulator.py).
        text = ""
        for candidate in response.candidates or []:
            for part in candidate.content.parts or []:
                if getattr(part, "thought", False):
                    continue
                if hasattr(part, "text") and part.text:
                    text += part.text

        if not text:
            raise JudgeError("Gemini returned empty response")
        return text

    def _parse_response(
        self,
        raw_json: str,
        record: ConversationRecord,
        rep_index: int,
    ) -> JudgeScoreSet:
        """Parse and validate JSON → JudgeScoreSet. Raises JudgeError on failure."""
        try:
            data = json.loads(raw_json)
        except json.JSONDecodeError as exc:
            raise JudgeError(f"JSON decode error: {exc}") from exc

        try:
            # negotiation_effectiveness, customer_experience, and recovery_quality
            # may all be null on a per-tier basis (see `_build_prompt`).
            negotiation = data.get("negotiation_effectiveness")
            customer_exp = data.get("customer_experience")
            recovery = data.get("recovery_quality")
            justifications = data.get("justifications", {})

            return JudgeScoreSet(
                rep_index=rep_index,
                judge_model=self._model,
                judge_temperature=self._temperature,
                temporal_understanding=int(data["temporal_understanding"]),
                negotiation_effectiveness=int(negotiation) if negotiation is not None else None,
                conversational_efficiency=int(data["conversational_efficiency"]),
                customer_experience=int(customer_exp) if customer_exp is not None else None,
                recovery_quality=int(recovery) if recovery is not None else None,
                justifications={
                    k: (v if v is not None else "")
                    for k, v in justifications.items()
                },
                overall_notes=data.get("overall_notes"),
            )
        except (KeyError, ValueError, TypeError) as exc:
            raise JudgeError(f"Response validation failed: {exc}") from exc


# ---------------------------------------------------------------------------
# JudgeRunner — orchestrates an entire run
# ---------------------------------------------------------------------------


def _safe_mean(vals: list[float]) -> float | None:
    return statistics.mean(vals) if vals else None


def _safe_stdev(vals: list[float]) -> float | None:
    return statistics.stdev(vals) if len(vals) >= 2 else None


class JudgeRunner:
    """Orchestrates judging all records in a completed evaluation run."""

    def run(
        self,
        *,
        run_id: str,
        stage: str,
        judge_model: str = JUDGE_MODEL_DEFAULT,
        judge_temperature: float = JUDGE_TEMPERATURE,
        judge_reps: int = JUDGE_REPS_DEFAULT,
        overwrite: bool = False,
        gemini_api_key: str | None = None,
    ) -> JudgeSummary:
        """Score all records in a completed run.

        Args:
            run_id: The run_id directory name (must have records/ populated).
            stage: Stage name (``baseline``, ``nlp``, etc.) to resolve ``RunPaths``.
            judge_model: Gemini model for the judge.
            judge_temperature: Sampling temperature (default 0.3 per §8).
            judge_reps: How many times to score each record (default 1; raise for
                reliability calibration).
            overwrite: If False (default), skip records with existing judge scores.
            gemini_api_key: Falls back to ``GEMINI_API_KEY`` env var.

        Returns:
            :class:`JudgeSummary` with aggregate statistics.

        Raises:
            FileNotFoundError: If the run's ``records/`` directory does not exist.
            ValueError: If ``records/`` is empty.
        """
        paths = RunPaths(run_id, stage)
        if not paths.records_dir.exists():
            raise FileNotFoundError(
                f"records/ not found for run_id={run_id!r}, stage={stage!r}: "
                f"{paths.records_dir}"
            )

        record_files = sorted(paths.records_dir.glob("*.json"))
        if not record_files:
            raise ValueError(
                f"No record files found in {paths.records_dir} — "
                "run the evaluation runner first."
            )

        api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)

        prompt_template = _PROMPT_PATH.read_text(encoding="utf-8")
        judge = ScenarioJudge(
            gemini_client=client,
            model=judge_model,
            temperature=judge_temperature,
            prompt_template=prompt_template,
            judge_reps=judge_reps,
        )

        all_scores: list[JudgeScoreSet] = []
        failed_count = 0
        record_count = 0

        for record_path in record_files:
            record_count += 1
            try:
                record = load_record(record_path)
            except Exception as exc:
                logger.error("Failed to load record %s: %s", record_path, exc)
                failed_count += 1
                continue

            # Parse scenario_id and rep from filename stem: "<id>__rep<k>.json"
            stem = record_path.stem
            if "__rep" in stem:
                scenario_id, rep_str = stem.rsplit("__rep", 1)
                try:
                    rep = int(rep_str)
                except ValueError:
                    rep = record.run_index
            else:
                scenario_id = stem
                rep = record.run_index

            if not overwrite and record.judge_scores:
                logger.debug(
                    "Skipping already-scored record %s rep %d", scenario_id, rep
                )
                all_scores.extend(record.judge_scores)
                continue

            transcript = self._load_transcript(paths, record, scenario_id, rep)
            scenario_description = self._build_scenario_description(record)

            scores = judge.score(record, transcript, scenario_description)
            if not scores:
                logger.error(
                    "All judge reps failed for %s rep %d — skipping", scenario_id, rep
                )
                failed_count += 1
                continue

            # Write back to record (atomic overwrite)
            enriched = record.model_copy(update={"judge_scores": scores})
            write_record(paths, enriched, scenario_id, rep)

            # Write sidecar to judge/
            self._write_judge_sidecar(paths, scenario_id, rep, scores)

            all_scores.extend(scores)

        # Aggregate
        summary = self._compute_summary(
            run_id=run_id,
            stage=stage,
            judge_model=judge_model,
            judge_temperature=judge_temperature,
            judge_reps=judge_reps,
            all_scores=all_scores,
            record_count=record_count,
            failed_count=failed_count,
        )

        # Persist judge/summary.json
        paths.judge_dir.mkdir(parents=True, exist_ok=True)
        write_json(paths.judge_dir / "summary.json", summary.to_dict())

        # Update kpi_history.csv
        try:
            kpi_history_mod.update_judge_means(
                run_id=run_id,
                mean_temporal=summary.mean_temporal,
                mean_negotiation=summary.mean_negotiation,
                mean_efficiency=summary.mean_efficiency,
                mean_recovery=summary.mean_recovery,
                mean_customer_experience=summary.mean_customer_experience,
            )
        except Exception as exc:
            logger.warning("Failed to update kpi_history.csv: %s", exc)

        return summary

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _load_transcript(
        paths: RunPaths,
        record: ConversationRecord,
        scenario_id: str,
        rep: int,
    ) -> str:
        transcript_path = paths.transcript_path(scenario_id, rep)
        try:
            return transcript_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.warning(
                "Transcript not found at %s — re-rendering from record", transcript_path
            )
            return render_transcript(record)

    @staticmethod
    def _build_scenario_description(record: ConversationRecord) -> str:
        """Construct a compact scenario description from record fields."""
        parts = [
            f"Tier {record.tier} scenario (ID: {record.scenario_id})",
            f"persona={record.persona_profile}",
        ]
        if record.frozen_phrasing:
            parts.append(f'user phrasing: "{record.frozen_phrasing}"')
        return "; ".join(parts)

    @staticmethod
    def _write_judge_sidecar(
        paths: RunPaths,
        scenario_id: str,
        rep: int,
        scores: list[JudgeScoreSet],
    ) -> None:
        paths.judge_dir.mkdir(parents=True, exist_ok=True)
        payload = [s.model_dump(mode="json") for s in scores]
        write_json(paths.judge_path(scenario_id, rep), payload)

    @staticmethod
    def _compute_summary(
        *,
        run_id: str,
        stage: str,
        judge_model: str,
        judge_temperature: float,
        judge_reps: int,
        all_scores: list[JudgeScoreSet],
        record_count: int,
        failed_count: int,
    ) -> JudgeSummary:
        # Flat lists for cross-scenario stats. negotiation, customer, and recovery
        # are all nullable per-tier (Tier 7 → negotiation+customer = None;
        # non-Recovery tiers → recovery = None) so filter None before aggregating.
        temporal = [s.temporal_understanding for s in all_scores]
        negotiation = [
            s.negotiation_effectiveness for s in all_scores
            if s.negotiation_effectiveness is not None
        ]
        efficiency = [s.conversational_efficiency for s in all_scores]
        customer = [s.customer_experience for s in all_scores if s.customer_experience is not None]
        recovery = [s.recovery_quality for s in all_scores if s.recovery_quality is not None]

        # Within-record stats: group scores by (judge_model, rep_index) → no,
        # we need a different key. We don't have scenario_id on JudgeScoreSet,
        # so the JudgeRunner has to bucket them BEFORE calling _compute_summary.
        # See `_within_record_std` below — it operates on the all_scores list
        # by inferring scenario groupings from the order the runner appended in.
        within_temporal = _within_record_std(all_scores, "temporal_understanding", judge_reps)
        within_negotiation = _within_record_std(all_scores, "negotiation_effectiveness", judge_reps)
        within_efficiency = _within_record_std(all_scores, "conversational_efficiency", judge_reps)
        within_customer = _within_record_std(all_scores, "customer_experience", judge_reps)
        within_recovery = _within_record_std(all_scores, "recovery_quality", judge_reps)

        scored_count = record_count - failed_count

        return JudgeSummary(
            run_id=run_id,
            stage=stage,
            judge_model=judge_model,
            judge_temperature=judge_temperature,
            judge_reps=judge_reps,
            record_count=record_count,
            scored_count=scored_count,
            failed_count=failed_count,
            mean_temporal=_safe_mean([float(v) for v in temporal]),
            mean_negotiation=_safe_mean([float(v) for v in negotiation]),
            mean_efficiency=_safe_mean([float(v) for v in efficiency]),
            mean_customer_experience=_safe_mean([float(v) for v in customer]),
            mean_recovery=_safe_mean([float(v) for v in recovery]),
            std_temporal=_safe_stdev([float(v) for v in temporal]),
            std_negotiation=_safe_stdev([float(v) for v in negotiation]),
            std_efficiency=_safe_stdev([float(v) for v in efficiency]),
            std_customer_experience=_safe_stdev([float(v) for v in customer]),
            std_recovery=_safe_stdev([float(v) for v in recovery]),
            std_within_temporal=within_temporal,
            std_within_negotiation=within_negotiation,
            std_within_efficiency=within_efficiency,
            std_within_customer_experience=within_customer,
            std_within_recovery=within_recovery,
        )


def _within_record_std(
    all_scores: list[JudgeScoreSet],
    attribute: str,
    judge_reps: int,
) -> float | None:
    """Mean of per-record stdevs across reps for a given dimension.

    Reps were appended in groups of ``judge_reps`` per record (see
    `JudgeRunner.run`). We slice the flat ``all_scores`` list into groups of
    that size, compute the stdev within each group, and take the mean.

    Returns ``None`` when ``judge_reps < 2`` (variance undefined) or when no
    group has at least 2 valid (non-None) values for ``attribute``.
    """
    if judge_reps < 2 or not all_scores:
        return None

    per_record_stds: list[float] = []
    for i in range(0, len(all_scores), judge_reps):
        group = all_scores[i : i + judge_reps]
        values = [getattr(s, attribute) for s in group]
        valid = [float(v) for v in values if v is not None]
        if len(valid) >= 2:
            per_record_stds.append(statistics.stdev(valid))

    return statistics.mean(per_record_stds) if per_record_stds else None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.judge",
        description="LLM-as-a-Judge for the appointment scheduling evaluation.",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # --- run ---
    run_p = sub.add_parser("run", help="Score all records in a completed run.")
    run_p.add_argument("--run-id", required=True, help="Run ID to judge.")
    run_p.add_argument(
        "--stage",
        required=True,
        choices=[
            "baseline",
            "nlp",
            "nlp_arm1",
            "nlp_arm2",
            "nlp_arm3",
            "expansion",
            "nlp_arm3_expansion",
            "weak_baseline",
            "weak_nlp_arm1",
            "weak_nlp_arm2",
            "weak_nlp_arm3",
            "weak_expansion",
            "weak_nlp_arm3_expansion",
            "planner",
            "robustness",
        ],
        help="Evaluation stage.",
    )
    run_p.add_argument(
        "--model",
        default=JUDGE_MODEL_DEFAULT,
        help=f"Gemini model for the judge (default: {JUDGE_MODEL_DEFAULT}).",
    )
    run_p.add_argument(
        "--temperature",
        type=float,
        default=JUDGE_TEMPERATURE,
        help=f"Judge sampling temperature (default: {JUDGE_TEMPERATURE}).",
    )
    run_p.add_argument(
        "--judge-reps",
        type=int,
        default=JUDGE_REPS_DEFAULT,
        dest="judge_reps",
        help=(
            f"Number of judge reps per record (default: {JUDGE_REPS_DEFAULT}). "
            "Raise to >=2 for within-record-std reliability calibration."
        ),
    )
    run_p.add_argument(
        "--overwrite",
        action="store_true",
        default=False,
        help="Re-score records that already have judge scores.",
    )

    # --- list ---
    list_p = sub.add_parser("list", help="List recent runs with judge scoring status.")
    list_p.add_argument("--limit", type=int, default=10, help="Max runs to show.")

    return parser


def _cmd_run(args: argparse.Namespace) -> int:
    runner = JudgeRunner()
    try:
        summary = runner.run(
            run_id=args.run_id,
            stage=args.stage,
            judge_model=args.model,
            judge_temperature=args.temperature,
            judge_reps=args.judge_reps,
            overwrite=args.overwrite,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        logger.exception("Unexpected error during judge run")
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"\nJudge run complete for {summary.run_id}  (reps={summary.judge_reps})")
    print(f"  Records scored : {summary.scored_count}/{summary.record_count}")
    print(f"  Failed         : {summary.failed_count}")
    print(
        f"  Temporal       : {_fmt_mean(summary.mean_temporal)} ± "
        f"{_fmt_mean(summary.std_temporal)} cross  ·  {_fmt_mean(summary.std_within_temporal)} within"
    )
    print(
        f"  Negotiation    : {_fmt_mean(summary.mean_negotiation)} ± "
        f"{_fmt_mean(summary.std_negotiation)} cross  ·  {_fmt_mean(summary.std_within_negotiation)} within"
    )
    print(
        f"  Efficiency     : {_fmt_mean(summary.mean_efficiency)} ± "
        f"{_fmt_mean(summary.std_efficiency)} cross  ·  {_fmt_mean(summary.std_within_efficiency)} within"
    )
    print(
        f"  Customer Exp   : {_fmt_mean(summary.mean_customer_experience)} ± "
        f"{_fmt_mean(summary.std_customer_experience)} cross  ·  "
        f"{_fmt_mean(summary.std_within_customer_experience)} within"
    )
    print(
        f"  Recovery       : {_fmt_mean(summary.mean_recovery)} ± "
        f"{_fmt_mean(summary.std_recovery)} cross  ·  {_fmt_mean(summary.std_within_recovery)} within"
    )
    return 0


def _fmt_mean(v: float | None) -> str:
    return f"{v:.2f}" if v is not None else "n/a"


def _cmd_list(args: argparse.Namespace) -> int:
    from evaluation.storage import runs_root

    runs_dir = runs_root()
    if not runs_dir.exists():
        print("No runs directory found.")
        return 0

    judge_summaries: list[tuple[str, str, Path]] = []
    for stage_dir in sorted(runs_dir.iterdir()):
        if not stage_dir.is_dir() or stage_dir.name == "adhoc":
            continue
        for run_dir in sorted(stage_dir.iterdir(), reverse=True):
            judge_summary = run_dir / "judge" / "summary.json"
            judge_summaries.append((stage_dir.name, run_dir.name, judge_summary))

    judge_summaries = judge_summaries[: args.limit]
    if not judge_summaries:
        print("No runs found.")
        return 0

    print(f"{'STAGE':<12} {'RUN_ID':<45} {'JUDGED'}")
    print("-" * 70)
    for stage, run_id, summary_path in judge_summaries:
        judged = "yes" if summary_path.exists() else "no"
        print(f"{stage:<12} {run_id:<45} {judged}")
    return 0


def main(argv: list[str] | None = None) -> int:
    from dotenv import load_dotenv

    load_dotenv()  # no-op if key already set in system env — that's correct

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set in environment or .env", file=sys.stderr)
        return 1

    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.command == "run":
        return _cmd_run(args)
    elif args.command == "list":
        return _cmd_list(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())


__all__ = [
    "JudgeError",
    "JudgeSummary",
    "ScenarioJudge",
    "JudgeRunner",
    "JUDGE_MODEL_DEFAULT",
    "JUDGE_TEMPERATURE",
    "JUDGE_REPS",
    "JUDGE_REPS_DEFAULT",
]
