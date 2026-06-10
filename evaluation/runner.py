"""
runner.py — Scenario runner for the evaluation framework (Step 3).

Loads a selection profile, injects scenario-specific availability overrides
into the mock MCP server, drives the agent graph via a LLM user simulator,
captures structured ConversationRecord JSON + markdown transcripts, and
writes a KPI summary row to kpi_history.csv.

See EVALUATION_FRAMEWORK.md §11–12 for design rationale.

CLI:
    python -m evaluation.runner run --profile smoke --stage baseline \\
        [--change-note "..."] [--max-turns 12] [--simulate-latency]
    python -m evaluation.runner list [--limit 10]
"""

import argparse
import asyncio
import json
import logging
import os
import random
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv
from google import genai
from google.genai import types

from evaluation.kpi_history import append_row, ensure_kpi_history_exists
from evaluation.metrics import (
    build_kpi_row,
    compute_derived_metrics,
    compute_run_summary,
    extract_grounding_facts,
    write_run_summary,
)
from evaluation.recorder import ConversationRecorder
from evaluation.schemas import (
    DEFAULT_LATENCY_MODEL,
    REFERENCE_DATE,
    ConversationRecord,
    RunConfig,
    RunManifest,
    Scenario,
)
from evaluation.simulator import UserSimulator
from evaluation.storage import (
    RunPaths,
    build_run_id,
    evaluation_root,
    get_git_commit,
    get_git_dirty,
    now_utc,
    write_manifest,
    write_record,
)
from orchestrator.graph import appointment_graph

# Imported lazily inside _build_nlp_resources so a baseline run does not
# pull in spaCy / dateparser at module-import time. Kept here as a reminder
# of the dependency surface.
# from nlp.factory import build_datetime_parser, build_entity_extractor


# ──────────────────────────────────────────────────────────────────────────
# Per-stage NLP feature-flag mapping (IMPROVEMENT_PLAN §5).
#
# Single source of truth: ``--stage X`` deterministically maps to the set of
# ``config["configurable"]`` flags the annotate node reads. ``RunConfig.extras``
# carries the same dict so each ConversationRecord is self-describing.
# ──────────────────────────────────────────────────────────────────────────

def stage_to_flags(stage: str) -> dict[str, Any]:
    """Map ``--stage`` to the NLP flags the agent reads via configurable.

    Defaults are baseline behavior (every NLP component OFF). Each ``nlp_arm*``
    stage turns on both components and selects the per-component arm.

    Returns a plain dict, suitable to be merged into both ``RunConfig.extras``
    and the per-turn ``graph_config["configurable"]`` block.
    """
    if stage.startswith("weak_"):
        # Weak-agent-model family (ARCHITECTURE §8 2026-06-10): identical flag
        # families to the strong counterpart — the agent model + thinking budget
        # are what differ, and those live in RunConfig / configurable, never in
        # the NLP flags, so the paired weak-vs-weak comparisons isolate exactly
        # the same interventions as the strong family did.
        return stage_to_flags(stage.removeprefix("weak_"))
    base: dict[str, Any] = {
        "nlp_datetime_enabled": False,
        "nlp_entity_enabled": False,
        "datetime_arm": None,
        "entity_arm": None,
        "nlp_llm_backend": None,
        # Orthogonal to NLP — the executor-side window-expansion policy. Off for
        # every NLP/baseline stage; only the dedicated ``expansion`` stage turns it
        # on (with NLP off), so the comparison isolates agentic strategy from NLP.
        "expansion_policy_enabled": False,
    }
    if stage == "expansion":
        return {**base, "expansion_policy_enabled": True}
    if stage == "nlp_arm1":
        return {
            **base,
            "nlp_datetime_enabled": True,
            "nlp_entity_enabled": True,
            "datetime_arm": "dateparser",
            "entity_arm": "spacy",
        }
    if stage == "nlp_arm2":
        return {
            **base,
            "nlp_datetime_enabled": True,
            "nlp_entity_enabled": True,
            "datetime_arm": "local_llm",
            "entity_arm": "local_llm",
            "nlp_llm_backend": "local",
        }
    if stage == "nlp_arm3":
        return {
            **base,
            "nlp_datetime_enabled": True,
            "nlp_entity_enabled": True,
            "datetime_arm": "api_llm",
            "entity_arm": "api_llm",
            "nlp_llm_backend": "api",
        }
    if stage == "nlp_arm3_expansion":
        # Combined: Arm 3 NLP (annotate-side preprocessing) *and* the executor-side
        # window-expansion policy. The two flag families are orthogonal — Arm 3
        # drives the ``annotate`` node, expansion drives ``execute_node`` — so they
        # compose with no shared key. Measures whether better upfront datetime
        # parsing makes the agent's first ``check_availability`` correct more often,
        # so the ladder fires *less* (complementary) or buys little (redundant).
        return {
            **base,
            "nlp_datetime_enabled": True,
            "nlp_entity_enabled": True,
            "datetime_arm": "api_llm",
            "entity_arm": "api_llm",
            "nlp_llm_backend": "api",
            "expansion_policy_enabled": True,
        }
    return base  # baseline | nlp | planner | robustness | adhoc → all off


def _active_local_model(flags: dict[str, Any]) -> str | None:
    """Resolve the active local GGUF model key when a local arm is selected.

    Recorded in ``RunConfig.extras`` so an ``nlp_arm2`` record is **self-describing
    about which model produced it**. Two runs can share the ``nlp_arm2`` stage
    label yet use different GGUFs via the ``LOCAL_LLM_MODEL`` env swap — exactly
    the gap that let a Qwen smoke run masquerade as the chosen Llama Arm 2 (94
    unsupported facts attributed to the wrong model; see ARCHITECTURE Decision Log
    2026-06-04). Returns ``None`` when no local arm is in play (no import cost on
    baseline / API-arm runs).
    """
    if "local_llm" not in (flags.get("datetime_arm"), flags.get("entity_arm")):
        return None
    from nlp.local_llm import active_model_key  # lazy: only for local-arm runs

    return active_model_key()


def _active_api_model(flags: dict[str, Any]) -> str | None:
    """Resolve the pinned NLP-extraction Gemini model when an API arm is selected.

    Mirrors :func:`_active_local_model`: records make themselves self-describing
    about which model produced the Arm 3 extractions (``NLP_API_MODEL`` env →
    default ``gemini-2.5-flash``). Imports the config accessor only, never the
    client/runtime — enforced by the scope guard
    (``tests/unit/test_local_llm_scope_guard.py``).
    """
    arms = (flags.get("datetime_arm"), flags.get("entity_arm"))
    if "api_llm" not in arms:
        return None
    from nlp.api_llm import active_model  # lazy: only for api-arm runs

    return active_model()


def _resolve_agent_config(
    stage: str,
    agent_model: str | None,
    agent_thinking_budget: int | None,
) -> tuple[str, int]:
    """Resolve the agent model + thinking budget for a run (ARCHITECTURE §8 2026-06-10).

    Guard rails so historical stage labels can never silently change meaning:
    ``weak_*`` stages REQUIRE an explicit non-default agent model; every other
    stage REJECTS one. The thinking budget defaults per family — ``weak_*`` → 0
    (thinking off, the weak-model decision), else → -1 (dynamic thinking, the
    standing config every anchor run used) — and may be overridden explicitly.

    Returns:
        ``(agent_model, thinking_budget)`` — both always concrete values, so the
        manifest records the *effective* config, never an implicit default.
    """
    is_weak = stage.startswith("weak_")
    if is_weak:
        if not agent_model or agent_model == _DEFAULT_MODEL:
            raise ValueError(
                f"Stage {stage!r} requires an explicit --agent-model different from "
                f"the default {_DEFAULT_MODEL!r} — weak-agent stages must name their model."
            )
    elif agent_model and agent_model != _DEFAULT_MODEL:
        raise ValueError(
            f"Stage {stage!r} is pinned to {_DEFAULT_MODEL!r}; --agent-model "
            f"{agent_model!r} is only valid for weak_* stages."
        )
    model = agent_model or _DEFAULT_MODEL
    if agent_thinking_budget is not None:
        budget = agent_thinking_budget
    else:
        budget = 0 if is_weak else -1
    return model, budget


class AgentConfigMismatchError(RuntimeError):
    """A record's agent LLM calls contradict the run's configured agent model or
    thinking budget — a measurement bug. Aborts the whole run (never counted as
    an ordinary scenario failure)."""


def _verify_agent_config(record: ConversationRecord, run_config: RunConfig) -> None:
    """Tripwire: every agent LLM call must match the manifest's agent config.

    Two checks per Gemini call (ARCHITECTURE §8 2026-06-10):

    - **Model**: the model that actually answered (``model_version`` echoed by the
      API) must equal ``RunConfig.llm_model``, allowing only a version suffix
      (``-0...``) — so ``gemini-2.5-flash`` answering a ``gemini-2.5-flash-lite``
      run (or vice versa) is caught, while ``...-001`` style pinning is not a
      false positive.
    - **Thinking**: when the run declares ``agent_thinking_budget=0``, no call may
      report thought tokens.

    Raises:
        AgentConfigMismatchError: on the first violation found.
    """
    expected_model = run_config.llm_model
    budget = run_config.agent_thinking_budget
    for turn in record.turns:
        for call in turn.llm_calls:
            if call.provider != "gemini":
                continue
            answered = call.model
            if (
                answered
                and answered != expected_model
                and not answered.startswith(expected_model + "-0")
            ):
                raise AgentConfigMismatchError(
                    f"Scenario {record.scenario_id} rep {record.run_index}: agent call "
                    f"answered by {answered!r} but the run is configured for "
                    f"{expected_model!r} — measurement bug, aborting run."
                )
            if budget == 0 and (call.thoughts_tokens or 0) > 0:
                raise AgentConfigMismatchError(
                    f"Scenario {record.scenario_id} rep {record.run_index}: agent call "
                    f"reported {call.thoughts_tokens} thought tokens but the run is "
                    f"configured with thinking_budget=0 — measurement bug, aborting run."
                )


def _build_nlp_resources(flags: dict[str, Any]) -> dict[str, Any]:
    """Construct parser + extractor instances once per run for caching.

    Empty dict when neither NLP component is enabled — avoids importing spaCy
    or loading the dateparser settings during baseline runs.
    """
    if not (flags.get("nlp_datetime_enabled") or flags.get("nlp_entity_enabled")):
        return {}
    from nlp.factory import build_datetime_parser, build_entity_extractor  # noqa: E402

    resources: dict[str, Any] = {}
    if flags.get("nlp_datetime_enabled"):
        resources["_dt_parser"] = build_datetime_parser(flags["datetime_arm"])
    if flags.get("nlp_entity_enabled"):
        resources["_ent_extractor"] = build_entity_extractor(flags["entity_arm"])
    return resources
from orchestrator.expansion import AvailabilityCache
from orchestrator.mcp_bridge import MCPBridge
from orchestrator.state import default_state

load_dotenv(override=True)

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------
# Module-level constants
# ------------------------------------------------------------------

_SCENARIOS_DIR = evaluation_root() / "scenarios"
_SELECTIONS_DIR = _SCENARIOS_DIR / "selections"

# Tier JSON file names pattern: tier{N}_*.json
_TIER_FILE_PATTERN = "tier{tier}_*.json"

# Default Gemini model for the agent loop (override per run via --agent-model).
_DEFAULT_MODEL = "gemini-2.5-flash"

# The user-simulator model is PINNED — deliberately decoupled from the agent
# model knob so a weak-agent run still converses with the same simulated
# customer as every anchor run (ARCHITECTURE §8 2026-06-10). Do not derive
# this from RunConfig.llm_model.
_SIMULATOR_MODEL = "gemini-2.5-flash"

# Schema version for runner-produced manifests
_RUNNER_VERSION = "step3/1.0"


# ------------------------------------------------------------------
# Pure helper functions
# ------------------------------------------------------------------


def _resolve_override(
    slots_by_offset: dict[str, list[str]],
    today: date | None = None,
) -> dict[str, list[str]]:
    """Convert ``today+N`` offset keys to ISO date strings.

    Accepts keys in the forms: ``today``, ``today+N``, ``today-N``, or
    literal ISO dates (``YYYY-MM-DD``).  Values (lists of ``"HH:MM-HH:MM"``
    strings) are passed through unchanged.

    Args:
        slots_by_offset: The ``availability_override.slots_by_offset`` dict
            from a scenario JSON.
        today: Reference date; defaults to ``date.today()``.

    Returns:
        Dict mapping ISO date strings to slot lists.
    """
    today = today or date.today()
    resolved: dict[str, list[str]] = {}
    for key, slots in slots_by_offset.items():
        if key == "today":
            d = today
        elif key.startswith("today+"):
            d = today + timedelta(days=int(key[6:]))
        elif key.startswith("today-"):
            d = today - timedelta(days=int(key[6:]))
        else:
            d = date.fromisoformat(key)
        resolved[d.isoformat()] = slots
    return resolved


def _scenario_reference_date(scenario: dict) -> date:
    """Return the scenario's pinned ``reference_date`` (EVALUATION_FRAMEWORK §3a).

    Scenarios loaded from JSON carry ``reference_date`` as an ISO date string.
    Falls back to the suite-wide ``REFERENCE_DATE`` for any older scenario file
    that predates the field, so the runner never crashes on a missing value.
    """
    raw = scenario.get("reference_date")
    if isinstance(raw, date):
        return raw
    if isinstance(raw, str) and raw:
        try:
            return date.fromisoformat(raw)
        except ValueError:
            logger.warning(
                "Scenario %s has unparseable reference_date %r — using %s",
                scenario.get("scenario_id"), raw, REFERENCE_DATE,
            )
    return REFERENCE_DATE


def _load_scenarios(tiers: list[int]) -> dict[int, list[dict]]:
    """Load scenario dicts from tier JSON files.

    Returns a mapping of tier → list of scenario dicts.  Missing tier files
    are silently skipped (logged at WARNING).
    """
    scenarios_by_tier: dict[int, list[dict]] = {}
    for tier in tiers:
        pattern = _TIER_FILE_PATTERN.format(tier=tier)
        matches = list(_SCENARIOS_DIR.glob(pattern))
        if not matches:
            logger.warning("No scenario file found for tier %d (pattern: %s)", tier, pattern)
            continue
        # Load all matching files for this tier (usually one)
        tier_scenarios: list[dict] = []
        for path in matches:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                tier_scenarios.extend(data)
            else:
                tier_scenarios.append(data)
        scenarios_by_tier[tier] = tier_scenarios
        logger.debug("Loaded %d scenarios for tier %d", len(tier_scenarios), tier)
    return scenarios_by_tier


def _sample_scenarios(
    profile: dict,
    scenarios_by_tier: dict[int, list[dict]],
) -> list[tuple[dict, int]]:
    """Apply a selection profile to produce ``(scenario, reps)`` pairs.

    Precedence (from selections/README.md):
    1. ``include_ids`` — surgical inclusion; bypasses per-tier sampling.
    2. Sampling: ``max_per_tier`` random scenarios per tier using ``seed``.
    3. ``exclude_ids`` — last-mile removal applied after the above.

    Returns:
        List of ``(scenario_dict, rep_count)`` tuples in a stable order.
    """
    reps: int = profile.get("reps", 1)
    include_ids: list[str] = profile.get("include_ids") or []
    exclude_ids: set[str] = set(profile.get("exclude_ids") or [])
    max_per_tier: int = profile.get("max_per_tier", 9999)
    seed: int = profile.get("seed", 42)
    tiers: list[int] = profile.get("tiers", list(scenarios_by_tier.keys()))

    # Flatten all scenarios for include_ids lookup
    all_scenarios = {
        s["scenario_id"]: s
        for tier_list in scenarios_by_tier.values()
        for s in tier_list
    }

    selected: list[dict] = []

    if include_ids:
        for sid in include_ids:
            if sid in all_scenarios:
                selected.append(all_scenarios[sid])
            else:
                logger.warning("include_id '%s' not found in loaded scenarios", sid)
    else:
        rng = random.Random(seed)
        for tier in tiers:
            tier_list = scenarios_by_tier.get(tier, [])
            # Exclude before sampling so quota is based on eligible candidates
            eligible = [s for s in tier_list if s["scenario_id"] not in exclude_ids]
            if max_per_tier < len(eligible):
                eligible = rng.sample(eligible, max_per_tier)
            selected.extend(eligible)

    # Apply exclude_ids to include_ids path too
    selected = [s for s in selected if s["scenario_id"] not in exclude_ids]

    return [(s, reps) for s in selected]


def _extract_agent_text(messages: list) -> str:
    """Extract the last model text response from LangGraph state messages.

    Mirrors the agent-text extraction in ``app.py``.
    """
    for content in reversed(messages):
        if hasattr(content, "role") and content.role == "model":
            for part in content.parts:
                if hasattr(part, "text") and part.text and not getattr(part, "thought", False):
                    return part.text
    return ""


def _serialize_messages(messages: list) -> list[dict]:
    """Serialize Gemini Content objects to JSON-safe dicts for record storage.

    Mirrors the logic in ``app.py`` ``on_chat_end``.
    """
    result = []
    for msg in messages:
        if hasattr(msg, "model_dump"):
            result.append(msg.model_dump())
        elif hasattr(msg, "to_json_dict"):
            result.append(msg.to_json_dict())
        else:
            result.append({"role": getattr(msg, "role", None), "repr": repr(msg)})
    return result


def enrich_record(
    record: ConversationRecord,
    scenario_dict: dict,
    paths: RunPaths,
) -> ConversationRecord:
    """Attach grounding facts and full DerivedMetrics to a finalized record.

    Called after ``recorder.finalize()`` has written the lightweight record.
    Overwrites the on-disk JSON with the enriched version via an atomic write.

    Args:
        record: Finalized ConversationRecord with lightweight derived metrics.
        scenario_dict: Raw scenario dict from the tier JSON file.
        paths: RunPaths for the current eval run (used for the overwrite path).

    Returns:
        Enriched ConversationRecord with ``grounding_facts`` and ``derived`` set.
    """
    grounding = extract_grounding_facts(record)
    scenario = Scenario.model_validate(scenario_dict)
    enriched = record.model_copy(update={"grounding_facts": grounding})
    derived = compute_derived_metrics(enriched, scenario)
    enriched = enriched.model_copy(update={"derived": derived})
    write_record(paths, enriched, scenario_id=record.scenario_id, rep=record.run_index)
    return enriched


# ------------------------------------------------------------------
# ScenarioRunner
# ------------------------------------------------------------------


class ScenarioRunner:
    """Runs a single scenario once and returns the ConversationRecord.

    Stateless — all resources are passed per call so the same instance can
    be reused across many scenario runs within a single ``EvalRunner`` session.
    """

    async def run_once(
        self,
        scenario: dict,
        rep_index: int,
        *,
        bridge: MCPBridge,
        gemini_client: Any,
        paths: RunPaths,
        run_config: RunConfig,
        stage: str,
        change_note: str | None,
        max_turns: int = 12,
        scenario_timeout_s: float = 600.0,
        total_reps: int = 1,
        nlp_flags: dict[str, Any] | None = None,
        nlp_resources: dict[str, Any] | None = None,
    ) -> ConversationRecord:
        """Run one scenario once end-to-end.

        Sets the MCP availability override, resets bookings, drives the
        agent graph via a UserSimulator, records every turn, then finalizes
        and returns the ConversationRecord.

        Args:
            scenario: Scenario dict loaded from the tier JSON file.
            rep_index: 1-based repetition index (written into the record).
            bridge: Connected MCPBridge shared for the entire eval run.
            gemini_client: Gemini client for both agent and simulator calls.
            paths: ``RunPaths`` for the current eval run.
            run_config: Configuration snapshot written into each record.
            stage: Evaluation stage string (e.g. ``"baseline"``).
            change_note: Optional free-text description of changes since last run.
            max_turns: Hard cap on agent turns before forcing termination.
            scenario_timeout_s: Per-scenario wall-clock budget. If the turn loop
                exceeds it (a runaway intra-turn agent↔execute loop that --max-turns
                cannot bound), the scenario aborts to a ``timeout`` record and the
                run continues.
            total_reps: Total repetitions for this scenario (for logging only).
        """
        scenario_id: str = scenario["scenario_id"]
        tier = scenario["tier"]
        persona_profile = scenario.get("persona_profile", "cooperative")
        frozen_phrasing: str = scenario.get("frozen_phrasing", "")
        simulator_goal: str = scenario.get("simulator_goal", "Book an appointment.")

        logger.info(
            "Running scenario %s (tier=%s, rep=%d/%d)",
            scenario_id, tier, rep_index, total_reps,
        )

        # 1. Resolve relative date offsets → ISO date strings against the
        # scenario's PINNED reference_date (not the wall clock), so the override
        # and the agent's "today" share one clock (EVALUATION_FRAMEWORK §3a).
        reference_date = _scenario_reference_date(scenario)
        override_raw: dict = scenario.get("availability_override", {})
        slots_by_offset: dict = override_raw.get("slots_by_offset", {})
        resolved_override = _resolve_override(slots_by_offset, today=reference_date)

        # 2. Inject override + reset bookings — always clean up in finally
        try:
            override_resp = await bridge.call_tool(
                "admin_set_availability_override",
                {"override_json": json.dumps(resolved_override)},
            )
            if isinstance(override_resp, dict) and override_resp.get("status") == "error":
                logger.error(
                    "admin_set_availability_override failed for %s: %s",
                    scenario_id, override_resp.get("message"),
                )

            # Pin the server clock to the scenario's reference_date so the agent's
            # get_current_datetime() shares ONE clock with the availability override
            # and the simulator (EVALUATION_FRAMEWORK §3a). Without this the agent
            # anchors date arithmetic on the real run-day and queries days the
            # override never populated whenever run-day != suite anchor.
            clock_resp = await bridge.call_tool(
                "admin_set_clock_override",
                {"reference_date": reference_date.isoformat()},
            )
            if isinstance(clock_resp, dict) and clock_resp.get("status") == "error":
                logger.error(
                    "admin_set_clock_override failed for %s: %s",
                    scenario_id, clock_resp.get("message"),
                )

            await bridge.call_tool("reset_bookings", {})

            # 3. Create recorder for this scenario run
            recorder = ConversationRecorder(
                scenario_id=scenario_id,
                tier=tier,
                stage=stage,
                persona_profile=persona_profile,
                run_index=rep_index,
                run_id=paths.run_id,
                paths=paths,
                config=run_config,
                availability_override=override_raw,
                frozen_phrasing=frozen_phrasing,
                expected_datetime_window=scenario.get("expected_datetime_window"),
                change_note=change_note,
            )

            # 4. Create user simulator (anchored to the same reference_date so the
            # customer's notion of "today" matches the agent's and the override).
            simulator = UserSimulator(
                goal=simulator_goal,
                persona_profile=persona_profile,
                frozen_phrasing=frozen_phrasing,
                gemini_client=gemini_client,
                # PINNED — never run_config.llm_model: the agent-model knob must
                # not weaken the simulated customer (ARCHITECTURE §8 2026-06-10).
                model=run_config.simulator_model or _SIMULATOR_MODEL,
                temperature=run_config.llm_temperature or 0.3,
                reference_date=reference_date,
            )

            # 5. Prime the conversation — simulator opens
            current_user_msg = await simulator.first_turn()
            state = default_state()

            # Fresh per-scenario availability cache for the expansion policy.
            # Created once here so it persists across turns within this scenario and
            # resets automatically for the next scenario (new object). Only built when
            # the policy is on — None otherwise, so execute_node takes the baseline path.
            expansion_cache = (
                AvailabilityCache()
                if (nlp_flags or {}).get("expansion_policy_enabled")
                else None
            )

            termination_reason = "max_turns"
            final_state = state
            drive_error: str | None = None

            # 6. Turn loop — wrapped in a per-scenario wall-clock guard.
            # ``--max-turns`` bounds the number of *user turns* (ainvokes) but NOT
            # the number of tool calls *within* one turn. A single adversarial
            # scenario can therefore drive an intra-turn agent↔execute loop that
            # issues hundreds of check_availability calls and never returns
            # (observed 2026-06-06: 287 empty calls scanning dates into 2032,
            # ~25 min on one scenario). asyncio.wait_for aborts such a runaway to a
            # ``timeout`` record so the run continues instead of stalling.
            async def _run_turns() -> None:
                nonlocal current_user_msg, state, termination_reason
                nonlocal final_state, drive_error
                for turn_idx in range(max_turns):
                    recorder.begin_turn(user_message=current_user_msg)

                    # Build user content for the graph
                    user_content = types.Content(
                        role="user",
                        parts=[types.Part.from_text(text=current_user_msg)],
                    )
                    graph_input = {**state, "messages": state["messages"] + [user_content]}

                    configurable = {
                        "gemini_client": gemini_client,
                        "mcp_bridge": bridge,
                        "model": run_config.llm_model or _DEFAULT_MODEL,
                        "temperature": run_config.llm_temperature or 0.7,
                        # Effective agent thinking budget — recorded in the
                        # manifest and asserted per record (§8 2026-06-10).
                        "thinking_budget": (
                            run_config.agent_thinking_budget
                            if run_config.agent_thinking_budget is not None
                            else -1
                        ),
                        "llm_provider": run_config.llm_provider or "gemini",
                        "recorder": recorder,
                        # The agent's injected "today" for this scenario-run — pins the
                        # RUNTIME CONTEXT block to reference_date so "next Tuesday" means
                        # the same day the override targets (EVALUATION_FRAMEWORK §3a).
                        "reference_date": reference_date.isoformat(),
                        "simulate_latency": run_config.simulate_latency,
                        "latency_model": (
                            run_config.latency_model.model_dump()
                            if run_config.latency_model
                            else DEFAULT_LATENCY_MODEL.model_dump()
                        ),
                    }
                    # NLP flags + cached parser/extractor instances per
                    # IMPROVEMENT_PLAN §5. When baseline, all flags are False and
                    # resources is empty — annotate_node short-circuits to a no-op
                    # and the prompt is byte-identical to pre-NLP behavior.
                    if nlp_flags:
                        configurable.update(nlp_flags)
                    if nlp_resources:
                        configurable.update(nlp_resources)
                    if expansion_cache is not None:
                        configurable["availability_cache"] = expansion_cache
                    graph_config = {"configurable": configurable}

                    try:
                        result_state = await appointment_graph.ainvoke(
                            graph_input, config=graph_config
                        )
                    except Exception as exc:
                        logger.error(
                            "Graph invocation failed for %s turn %d: %s",
                            scenario_id, turn_idx + 1, exc,
                        )
                        recorder.end_turn(agent_response=None, state_snapshot=None)
                        termination_reason = "error"
                        drive_error = str(exc)
                        final_state = state
                        return

                    agent_text = _extract_agent_text(result_state.get("messages", []))
                    state_snapshot = {k: v for k, v in result_state.items() if k != "debug_log"}
                    recorder.end_turn(agent_response=agent_text or None, state_snapshot=state_snapshot)

                    final_state = result_state

                    # --- Termination: booking confirmed? ---
                    last_turn = recorder.record.turns[-1] if recorder.record.turns else None
                    if last_turn:
                        for tc in last_turn.tool_calls:
                            if tc.tool_name == "book_appointment" and tc.success:
                                termination_reason = "booked"
                                break
                    if termination_reason == "booked":
                        return

                    # --- Simulator's next turn ---
                    if not agent_text:
                        agent_text = "I'm looking into that for you."

                    next_msg, is_done = await simulator.next_turn(agent_text)

                    if is_done:
                        # Tier 7: simulator accepts a polite refusal — that IS goal-complete.
                        if tier == 7:
                            termination_reason = "refusal_accepted"
                            return

                        # Tiers 1–6: simulator_goal_complete is only honest if a
                        # `book_appointment` actually succeeded. Otherwise the simulator
                        # is signalling acceptance of an OFFER, not a real booking —
                        # keep going until the agent either books or hits max_turns.
                        has_real_booking = any(
                            tc.tool_name == "book_appointment" and tc.success
                            for turn in recorder.record.turns
                            for tc in turn.tool_calls
                        )
                        if has_real_booking:
                            termination_reason = "simulator_goal_complete"
                            return

                        logger.info(
                            "Scenario %s: simulator emitted [GOAL_COMPLETE] without a "
                            "successful book_appointment — continuing conversation.",
                            scenario_id,
                        )

                    current_user_msg = next_msg
                    state = result_state

            try:
                await asyncio.wait_for(_run_turns(), timeout=scenario_timeout_s)
            except asyncio.TimeoutError:
                termination_reason = "timeout"
                drive_error = (
                    f"scenario exceeded {scenario_timeout_s:.0f}s wall-clock "
                    "(per-scenario runaway guard)"
                )
                logger.error(
                    "Scenario %s aborted: exceeded %.0fs wall-clock — per-scenario "
                    "runaway guard tripped.", scenario_id, scenario_timeout_s,
                )

            # 7. Finalize record then enrich with full metrics
            final_messages = _serialize_messages(final_state.get("messages", []))
            record = recorder.finalize(
                termination_reason=termination_reason,
                final_messages=final_messages,
                error=drive_error,
            )
            try:
                record = enrich_record(record, scenario, paths)
            except Exception:
                logger.exception(
                    "enrich_record failed for %s rep %d", scenario_id, rep_index
                )
            logger.info(
                "Scenario %s rep %d done — termination=%s booked=%s turns=%d",
                scenario_id, rep_index, termination_reason,
                record.derived.booked if record.derived else "?",
                len(record.turns),
            )
            return record

        finally:
            # Always clear both overrides so the next scenario gets a clean slate.
            try:
                await bridge.call_tool("admin_clear_availability_override", {})
            except Exception as exc:
                logger.warning("Failed to clear override after %s: %s", scenario_id, exc)
            try:
                await bridge.call_tool("admin_clear_clock_override", {})
            except Exception as exc:
                logger.warning("Failed to clear clock override after %s: %s", scenario_id, exc)


# ------------------------------------------------------------------
# EvalRunner
# ------------------------------------------------------------------


class EvalRunner:
    """Top-level runner: orchestrates a full selection-profile evaluation run.

    Creates and connects one MCPBridge, iterates over all sampled scenarios ×
    repetitions, collects ConversationRecords, writes metrics/summary, updates
    the RunManifest, and appends a KPIHistoryRow.
    """

    async def run(
        self,
        *,
        profile_path: Path,
        stage: str,
        change_note: str | None = None,
        max_turns: int = 12,
        scenario_timeout_s: float = 600.0,
        simulate_latency: bool = True,
        gemini_api_key: str | None = None,
        inter_scenario_delay_s: float = 0.0,
        agent_model: str | None = None,
        agent_thinking_budget: int | None = None,
    ) -> str:
        """Execute a full evaluation run.

        Args:
            profile_path: Path to a YAML selection profile.
            stage: One of ``baseline``, ``nlp``, ``planner``, ``robustness``.
            change_note: Free-text note describing what changed since the last run.
            max_turns: Hard cap on agent turns per scenario.
            simulate_latency: When True, inject simulated MCP latency per §9.
            gemini_api_key: Gemini API key; falls back to ``GEMINI_API_KEY`` env var.
            inter_scenario_delay_s: Seconds to sleep between scenario-rep iterations.
                Use >0 to stay within API rate limits on free-tier keys.
            agent_model: Agent-loop model override — REQUIRED for ``weak_*``
                stages, rejected otherwise (ARCHITECTURE §8 2026-06-10). The
                simulator/judge/NLP models stay pinned regardless.
            agent_thinking_budget: Explicit agent thinking budget; default is
                resolved per stage family (``weak_*`` → 0, else → -1).

        Returns:
            The ``run_id`` string for the completed run.
        """
        # --- Load profile ---
        with profile_path.open(encoding="utf-8") as f:
            profile: dict = yaml.safe_load(f)

        profile_name = profile.get("name", profile_path.stem)
        tiers: list[int] = profile.get("tiers", list(range(1, 8)))

        # --- Load + sample scenarios ---
        scenarios_by_tier = _load_scenarios(tiers)
        runs = _sample_scenarios(profile, scenarios_by_tier)

        if not runs:
            logger.warning("No scenarios selected by profile '%s' — aborting.", profile_name)
            raise ValueError(f"Profile '{profile_name}' selected 0 scenarios.")

        total_scenarios = len(runs)
        # All entries share the same reps count (from profile); reps may differ if
        # include_ids is used, so count total conversations
        total_conversations = sum(reps for _, reps in runs)

        logger.info(
            "Starting eval run: profile=%s stage=%s scenarios=%d conversations=%d",
            profile_name, stage, total_scenarios, total_conversations,
        )

        # --- Build run identity ---
        git_commit = get_git_commit()
        git_dirty = get_git_dirty()
        run_id = build_run_id(stage, git_commit, extra=profile_name)
        paths = RunPaths(run_id, stage)
        paths.ensure_dirs()

        # --- Per-stage NLP flags + cached resources (built once per run) ---
        nlp_flags = stage_to_flags(stage)
        nlp_resources = _build_nlp_resources(nlp_flags)

        # --- Run config ---
        # Mirror nlp_flags into RunConfig.extras so each ConversationRecord
        # is self-describing (which arm produced it). For local-LLM arms also
        # pin the *model* key — the arm label alone does not disambiguate the GGUF.
        run_extras: dict[str, Any] = {"profile_name": profile_name, **nlp_flags}
        local_model = _active_local_model(nlp_flags)
        if local_model is not None:
            run_extras["local_llm_model"] = local_model
        # Agent model + thinking budget resolved with weak-stage guard rails;
        # the pinned companion models are recorded so every record/manifest is
        # self-describing (ARCHITECTURE §8 2026-06-10).
        resolved_agent_model, resolved_thinking_budget = _resolve_agent_config(
            stage, agent_model, agent_thinking_budget
        )
        run_config = RunConfig(
            llm_provider="gemini",
            llm_model=resolved_agent_model,
            llm_temperature=0.7,
            llm_max_tokens=None,
            judge_model=None,
            simulator_model=_SIMULATOR_MODEL,
            agent_thinking_budget=resolved_thinking_budget,
            nlp_api_model=_active_api_model(nlp_flags),
            seeds={"profile_seed": profile.get("seed", 42)},
            max_turns=max_turns,
            simulate_latency=simulate_latency,
            runner_version=_RUNNER_VERSION,
            extras=run_extras,
        )

        # --- Write in-progress manifest ---
        manifest = RunManifest(
            run_id=run_id,
            stage=stage,
            timestamp_start=now_utc(),
            git_commit=git_commit,
            git_dirty=git_dirty,
            change_note=change_note,
            config=run_config,
            scenario_set_version=None,
            scenario_count=total_scenarios,
            rep_count=profile.get("reps", 1),
            record_count_written=0,
            status="in_progress",
        )
        write_manifest(paths, manifest)

        # --- Create clients and connect bridge ---
        api_key = gemini_api_key or os.getenv("GEMINI_API_KEY")
        gemini_client = genai.Client(api_key=api_key)
        bridge = MCPBridge(server_script_path="mcp_server/server.py")
        await bridge.connect()

        # --- Build scenario lookup for post-run metrics ---
        scenarios_by_id: dict[str, dict] = {s["scenario_id"]: s for s, _ in runs}

        # --- Run all scenarios ---
        scenario_runner = ScenarioRunner()
        records: list[ConversationRecord] = []
        record_count = 0
        failed_count = 0

        first_iteration = True
        try:
            for scenario, reps in runs:
                for rep_index in range(1, reps + 1):
                    if not first_iteration and inter_scenario_delay_s > 0:
                        await asyncio.sleep(inter_scenario_delay_s)
                    first_iteration = False
                    try:
                        record = await scenario_runner.run_once(
                            scenario,
                            rep_index,
                            bridge=bridge,
                            gemini_client=gemini_client,
                            paths=paths,
                            run_config=run_config,
                            stage=stage,
                            nlp_flags=nlp_flags,
                            nlp_resources=nlp_resources,
                            change_note=change_note,
                            max_turns=max_turns,
                            scenario_timeout_s=scenario_timeout_s,
                            total_reps=reps,
                        )
                        # Measurement-bug tripwire: the record must match the
                        # configured agent model + thinking budget. A violation
                        # aborts the entire run (re-raised below) — it must never
                        # be absorbed as an ordinary scenario failure.
                        _verify_agent_config(record, run_config)
                        records.append(record)
                        record_count += 1
                    except AgentConfigMismatchError:
                        raise
                    except Exception as exc:
                        logger.error(
                            "Unhandled error in scenario %s rep %d: %s",
                            scenario["scenario_id"], rep_index, exc,
                        )
                        failed_count += 1
        finally:
            await bridge.disconnect()

        # --- Compute full KPI summary (Step 4 metrics.py) ---
        ensure_kpi_history_exists()
        try:
            scenarios_pydantic = {
                sid: Scenario.model_validate(s)
                for sid, s in scenarios_by_id.items()
            }
            run_summary = compute_run_summary(records, scenarios_pydantic)
            write_run_summary(paths, run_summary)
            row = build_kpi_row(manifest, run_summary)
            append_row(row)
        except Exception as exc:
            logger.warning("Failed to compute/write KPI summary: %s", exc)

        # --- Finalize manifest ---
        manifest.status = "complete" if failed_count == 0 else "failed"
        manifest.timestamp_end = now_utc()
        manifest.record_count_written = record_count
        write_manifest(paths, manifest)

        logger.info(
            "Eval run complete: run_id=%s records=%d failed=%d",
            run_id, record_count, failed_count,
        )
        return run_id


# ------------------------------------------------------------------
# CLI
# ------------------------------------------------------------------


def _cmd_run(args: argparse.Namespace) -> int:
    """Execute 'runner run' subcommand."""
    profile_path = Path(args.profile)
    if not profile_path.exists():
        # Try resolving relative to selections directory
        candidate = _SELECTIONS_DIR / profile_path
        if candidate.exists():
            profile_path = candidate
        else:
            # Try adding .yaml extension
            candidate2 = _SELECTIONS_DIR / (profile_path.name + ".yaml")
            if candidate2.exists():
                profile_path = candidate2
            else:
                print(f"Profile not found: {args.profile}", file=sys.stderr)
                return 1

    runner = EvalRunner()
    try:
        run_id = asyncio.run(
            runner.run(
                profile_path=profile_path,
                stage=args.stage,
                change_note=args.change_note,
                max_turns=args.max_turns,
                scenario_timeout_s=args.scenario_timeout_s,
                simulate_latency=args.simulate_latency,
                inter_scenario_delay_s=args.inter_scenario_delay,
                agent_model=args.agent_model,
                agent_thinking_budget=args.agent_thinking_budget,
            )
        )
        print(f"Run complete: {run_id}")
        return 0
    except Exception as exc:
        print(f"Run failed: {exc}", file=sys.stderr)
        logger.exception("EvalRunner.run failed")
        return 1


def _cmd_list(args: argparse.Namespace) -> int:
    """Execute 'runner list' subcommand — list recent non-adhoc runs."""
    runs_root = evaluation_root() / "runs"
    if not runs_root.exists():
        print("No runs directory found.")
        return 0

    # Collect manifest paths from non-adhoc stage subdirectories
    entries = []
    for stage_dir in sorted(runs_root.iterdir()):
        if not stage_dir.is_dir() or stage_dir.name == "adhoc":
            continue
        for run_dir in sorted(stage_dir.iterdir(), reverse=True):
            manifest_path = run_dir / "manifest.json"
            if manifest_path.exists():
                entries.append(manifest_path)

    # Sort by directory name (run_id starts with timestamp) descending
    entries.sort(key=lambda p: p.parent.name, reverse=True)
    limit = getattr(args, "limit", 10)
    entries = entries[:limit]

    if not entries:
        print("No runs found.")
        return 0

    # Print table
    print(f"{'RUN ID':<55} {'STAGE':<12} {'STATUS':<12} {'RECORDS':>7}")
    print("-" * 90)
    for manifest_path in entries:
        try:
            data = json.loads(manifest_path.read_text(encoding="utf-8"))
            run_id = data.get("run_id", manifest_path.parent.name)
            stage = data.get("stage", "?")
            status = data.get("status", "?")
            count = data.get("record_count_written", "?")
            print(f"{run_id:<55} {stage:<12} {status:<12} {count:>7}")
        except Exception:
            print(f"{manifest_path.parent.name:<55} (manifest unreadable)")

    return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.runner",
        description="Evaluation scenario runner (Step 3).",
    )
    sub = parser.add_subparsers(dest="command")

    # --- run ---
    run_p = sub.add_parser("run", help="Execute a selection-profile evaluation run.")
    run_p.add_argument(
        "--profile",
        required=True,
        help="Path to a YAML selection profile (or bare name like 'smoke').",
    )
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
        help=(
            "Evaluation stage. ``nlp_arm1`` enables spaCy + dateparser, "
            "``nlp_arm2`` the local LLM, ``nlp_arm3`` Gemini JSON mode. "
            "``expansion`` enables the executor-side window-expansion policy with "
            "NLP off (clean agentic-strategy attribution). "
            "``nlp_arm3_expansion`` enables Arm 3 NLP *and* the expansion policy "
            "together (complementary-vs-redundant). "
            "``baseline`` and the others run with all NLP flags off. "
            "``weak_*`` stages mirror their strong counterparts but run the AGENT "
            "on a weaker model (requires --agent-model; thinking defaults off — "
            "ARCHITECTURE §8 2026-06-10)."
        ),
    )
    run_p.add_argument(
        "--agent-model",
        default=None,
        help=(
            "Agent-loop Gemini model. REQUIRED for weak_* stages (e.g. "
            "gemini-2.5-flash-lite); rejected for all other stages, which are "
            f"pinned to {_DEFAULT_MODEL}. Simulator/judge/NLP models are never "
            "affected by this flag."
        ),
    )
    run_p.add_argument(
        "--agent-thinking-budget",
        type=int,
        default=None,
        help=(
            "Explicit agent thinking budget (Gemini thinking_config). Default "
            "resolves per stage family: weak_* -> 0 (off), others -> -1 (dynamic, "
            "the standing anchor config). The effective value is recorded in the "
            "manifest and asserted against every record."
        ),
    )
    run_p.add_argument("--change-note", default=None, help="Free-text note for this run.")
    run_p.add_argument(
        "--max-turns", type=int, default=12, help="Max agent turns per scenario (default 12)."
    )
    run_p.add_argument(
        "--scenario-timeout-s",
        type=float,
        default=600.0,
        dest="scenario_timeout_s",
        help=(
            "Per-scenario wall-clock budget in seconds. A runaway scenario (an "
            "intra-turn agent↔execute loop that --max-turns cannot bound) aborts to "
            "a 'timeout' record and the run continues (default 600). Raise for "
            "CPU-bound stages like nlp_arm2."
        ),
    )
    run_p.add_argument(
        "--simulate-latency",
        action="store_true",
        default=True,
        help="Inject simulated MCP latency per EVALUATION_FRAMEWORK §9 (default: enabled).",
    )
    run_p.add_argument(
        "--no-simulate-latency",
        action="store_false",
        dest="simulate_latency",
        help="Disable simulated MCP latency (overrides --simulate-latency).",
    )
    run_p.add_argument(
        "--inter-scenario-delay",
        type=float,
        default=0.0,
        dest="inter_scenario_delay",
        help="Seconds to sleep between scenario runs (default 0). Use >0 to stay within API rate limits.",
    )

    # --- list ---
    list_p = sub.add_parser("list", help="List recent evaluation runs.")
    list_p.add_argument("--limit", type=int, default=10, help="Number of runs to show.")

    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
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
