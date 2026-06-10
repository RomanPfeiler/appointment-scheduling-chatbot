"""ConversationRecorder — the runtime API for building a ConversationRecord.

Used by:
- The future scenario runner (Step 3) — one recorder per scenario-run.
- The always-on Chainlit ad-hoc hook (``evaluation/adhoc.py``) — one recorder
  per chat session.

The recorder owns one in-flight ConversationRecord and one RunManifest,
writing both to disk in the layout from ``evaluation/storage.py``.

Per-turn lifecycle::

    handle = recorder.begin_turn(user_message="I'd like a meeting tomorrow")
    # ...agent + execute nodes call:
    recorder.record_llm_call(...)
    recorder.record_tool_call(...)
    recorder.record_llm_call(...)
    recorder.end_turn(agent_response=..., state_snapshot=...)

When the conversation ends::

    record = recorder.finalize(termination_reason="booked", final_messages=...)
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Any

from evaluation.schemas import (
    ConversationRecord,
    DerivedMetrics,
    LatencyModel,
    LLMCallRecord,
    PersonaProfile,
    RunConfig,
    RunManifest,
    Stage,
    TerminationReason,
    ToolCallRecord,
    TurnRecord,
)
from evaluation.storage import (
    RunPaths,
    get_git_commit,
    get_git_dirty,
    now_utc,
    write_manifest,
    write_record,
    write_transcript,
)

logger = logging.getLogger(__name__)


# Snapshot helper — state.messages is large (Gemini Content objects with
# growing history); the turn stream already captures user/agent text, so we
# strip messages from the per-turn snapshot to avoid quadratic file growth.
# The full final messages list is captured once at finalize() instead.
_SNAPSHOT_DROP_KEYS = ("messages",)


def _make_state_snapshot(state: dict | None) -> dict:
    """Copy the conversation state for a turn snapshot, dropping bulky keys.

    Returns ``{}`` if the caller passes ``None``.
    """
    if state is None:
        return {}
    return {k: _jsonable(v) for k, v in state.items() if k not in _SNAPSHOT_DROP_KEYS}


def _jsonable(value: Any) -> Any:
    """Best-effort conversion of a state value to a JSON-friendly form.

    Pydantic models, dataclasses with ``.model_dump``/``__dict__``, datetimes,
    and primitives all pass through cleanly; everything else falls back to
    ``str()`` so the snapshot never crashes on an exotic type.
    """
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if hasattr(value, "model_dump"):
        try:
            return value.model_dump(mode="json")
        except Exception:
            return str(value)
    return str(value)


class ConversationRecorder:
    """Build and persist a :class:`ConversationRecord` over the life of a
    conversation.

    Not thread-safe across concurrent turns of the SAME conversation; the
    LangGraph orchestrator runs one node at a time so this is a non-issue
    inside the existing graph.
    """

    def __init__(
        self,
        *,
        scenario_id: str,
        tier: int | str,
        stage: Stage,
        persona_profile: PersonaProfile | None,
        run_index: int,
        run_id: str,
        paths: RunPaths,
        config: RunConfig,
        scenario_set_version: str | None = None,
        availability_override: dict | None = None,
        frozen_phrasing: str | None = None,
        expected_datetime_window: dict | None = None,
        change_note: str | None = None,
        langsmith_trace_id: str | None = None,
        langsmith_trace_url: str | None = None,
        manifest: RunManifest | None = None,
        transcript_renderer=None,
    ) -> None:
        self.paths = paths
        self.scenario_id = scenario_id
        self.run_index = run_index
        self._record = ConversationRecord(
            scenario_id=scenario_id,
            tier=tier,
            stage=stage,
            persona_profile=persona_profile,
            run_index=run_index,
            run_id=run_id,
            timestamp_start=now_utc(),
            git_commit=get_git_commit(),
            git_dirty=get_git_dirty(),
            change_note=change_note,
            config=config,
            scenario_set_version=scenario_set_version,
            availability_override=availability_override,
            frozen_phrasing=frozen_phrasing,
            expected_datetime_window=expected_datetime_window,
            langsmith_trace_id=langsmith_trace_id,
            langsmith_trace_url=langsmith_trace_url,
        )
        self._manifest = manifest
        self._current_turn: TurnRecord | None = None
        self._turn_started_at: float | None = None
        # Lazy import — keeps recorder importable even when callers don't need
        # the markdown view (e.g. unit tests).
        if transcript_renderer is None:
            from evaluation import transcript as _transcript

            transcript_renderer = _transcript.render
        self._render_transcript = transcript_renderer
        self._finalized = False

        self.paths.ensure_dirs()

    # ------------------------------------------------------------------
    # Read-only accessors
    # ------------------------------------------------------------------

    @property
    def record(self) -> ConversationRecord:
        return self._record

    @property
    def latency_model(self) -> LatencyModel:
        return self._record.config.latency_model

    # ------------------------------------------------------------------
    # Turn lifecycle
    # ------------------------------------------------------------------

    def begin_turn(self, user_message: str | None) -> TurnRecord:
        """Open a new turn. Returns the in-flight TurnRecord (also stored as current)."""
        if self._current_turn is not None:
            logger.warning(
                "begin_turn called while a turn was already open (turn_index=%d); auto-closing it.",
                self._current_turn.turn_index,
            )
            self.end_turn(agent_response=None, state_snapshot=None)

        turn = TurnRecord(
            turn_index=len(self._record.turns) + 1,
            timestamp=now_utc(),
            user_message=user_message,
        )
        self._record.turns.append(turn)
        self._current_turn = turn
        self._turn_started_at = time.perf_counter()
        return turn

    def end_turn(
        self,
        agent_response: str | None,
        state_snapshot: dict | None,
    ) -> None:
        """Close the current turn. Safe to call when no turn is open (no-op)."""
        if self._current_turn is None:
            return
        self._current_turn.agent_response = agent_response
        self._current_turn.state_snapshot = _make_state_snapshot(state_snapshot)
        if self._turn_started_at is not None:
            self._current_turn.turn_duration_ms = (
                time.perf_counter() - self._turn_started_at
            ) * 1000.0
        self._current_turn = None
        self._turn_started_at = None

    # ------------------------------------------------------------------
    # Mid-turn event recording
    # ------------------------------------------------------------------

    def record_llm_call(
        self,
        *,
        provider: str,
        model: str | None,
        prompt_message_count: int,
        response_type: str,
        function_name: str | None = None,
        function_args: dict | None = None,
        text_preview: str | None = None,
        latency_ms: float | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        thoughts_tokens: int | None = None,
        temperature: float | None = None,
        raw_response_excerpt: str | None = None,
    ) -> None:
        """Append an LLMCallRecord to the current turn.

        Tolerant: if no turn is open the call is silently dropped (so an
        orchestrator that calls the LLM outside of a turn — e.g. a startup
        priming call — doesn't crash recording).
        """
        if self._current_turn is None:
            logger.debug("record_llm_call dropped — no open turn")
            return
        self._current_turn.llm_calls.append(
            LLMCallRecord(
                provider=provider,
                model=model,
                prompt_message_count=prompt_message_count,
                response_type=response_type,  # validated by Pydantic
                function_name=function_name,
                function_args=function_args,
                text_preview=text_preview,
                latency_ms=latency_ms,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                thoughts_tokens=thoughts_tokens,
                temperature=temperature,
                raw_response_excerpt=raw_response_excerpt,
            )
        )

    def record_tool_call(
        self,
        *,
        tool_name: str,
        parameters: dict,
        response: Any,
        simulated_latency_ms: float | None = None,
        actual_latency_ms: float | None = None,
        success: bool = True,
        error_message: str | None = None,
    ) -> None:
        """Append a ToolCallRecord to the current turn."""
        if self._current_turn is None:
            logger.debug("record_tool_call dropped — no open turn")
            return
        self._current_turn.tool_calls.append(
            ToolCallRecord(
                tool_name=tool_name,
                parameters=parameters,
                response=response,
                simulated_latency_ms=simulated_latency_ms,
                actual_latency_ms=actual_latency_ms,
                success=success,
                error_message=error_message,
            )
        )

    def record_ladder_steps(self, steps: list[dict]) -> None:
        """Attach the executor window-expansion ladder steps to the current turn.

        Called by ``execute_node`` after the bounded widening ladder fires on an
        empty ``check_availability``. Persists the *clean* per-turn ladder-fire
        signal into the record (``TurnRecord.ladder_steps``) so future runs no
        longer rely on the cache-confounded tool-call-count proxy. Tolerant: a
        ``None``/empty ``steps`` or no open turn is a no-op.
        """
        if self._current_turn is None or not steps:
            return
        self._current_turn.ladder_steps.extend(steps)

    # ------------------------------------------------------------------
    # Finalization
    # ------------------------------------------------------------------

    def attach_langsmith(self, trace_id: str | None, trace_url: str | None) -> None:
        """Attach a LangSmith trace pointer post-hoc (e.g. after first LLM call)."""
        if trace_id:
            self._record.langsmith_trace_id = trace_id
        if trace_url:
            self._record.langsmith_trace_url = trace_url

    def attach_derived_metrics(self, metrics: DerivedMetrics) -> None:
        """Attach metrics computed by the metrics step (Step 4)."""
        self._record.derived = metrics

    def finalize(
        self,
        termination_reason: TerminationReason,
        final_messages: list[dict] | None = None,
        error: str | None = None,
    ) -> ConversationRecord:
        """Finalize the record, write JSON + transcript, update manifest, return record.

        Idempotent: a second call returns the cached record without re-writing.
        """
        if self._finalized:
            return self._record

        if self._current_turn is not None:
            self.end_turn(agent_response=None, state_snapshot=None)

        self._record.timestamp_end = now_utc()
        self._record.termination_reason = termination_reason
        self._record.error = error
        if final_messages is not None:
            self._record.final_messages = [_jsonable(m) for m in final_messages]

        # Always populate a lightweight DerivedMetrics summary so ad-hoc
        # records are inspectable without a separate metrics pass.
        if self._record.derived is None:
            self._record.derived = self._compute_lightweight_metrics()

        record_path = write_record(
            self.paths,
            self._record,
            scenario_id=self.scenario_id,
            rep=self.run_index,
        )
        transcript_md = self._render_transcript(self._record)
        write_transcript(
            self.paths,
            transcript_md,
            scenario_id=self.scenario_id,
            rep=self.run_index,
        )

        # Manifest housekeeping — best effort. We only own the manifest in
        # ad-hoc mode (one recorder ↔ one run). Scenario runs share a
        # manifest across many recorders; the runner owns it there.
        if self._manifest is not None:
            self._manifest.record_count_written += 1
            self._manifest.timestamp_end = self._record.timestamp_end
            self._manifest.status = "complete"
            write_manifest(self.paths, self._manifest)

        logger.info(
            "Recorder finalized: %s (%d turns) → %s",
            self._record.scenario_id,
            len(self._record.turns),
            record_path,
        )
        self._finalized = True
        return self._record

    # ------------------------------------------------------------------
    # Lightweight metrics — enough to skim an ad-hoc record without the
    # full metrics step
    # ------------------------------------------------------------------

    def _compute_lightweight_metrics(self) -> DerivedMetrics:
        total_mcp = 0
        availability_calls = 0
        first_avail_params: dict | None = None
        booked = False
        sim_latency = 0.0
        actual_latency = 0.0

        for turn in self._record.turns:
            for call in turn.tool_calls:
                total_mcp += 1
                sim_latency += call.simulated_latency_ms or 0.0
                actual_latency += call.actual_latency_ms or 0.0
                if call.tool_name == "check_availability":
                    availability_calls += 1
                    if first_avail_params is None:
                        first_avail_params = call.parameters
                if call.tool_name == "book_appointment" and call.success:
                    response = call.response
                    if isinstance(response, dict) and response.get("status") == "success":
                        booked = True

        return DerivedMetrics(
            total_turn_count=len(self._record.turns),
            total_mcp_calls=total_mcp,
            availability_calls=availability_calls,
            first_check_availability_params=first_avail_params,
            booked=booked,
            total_simulated_latency_ms=sim_latency,
            total_actual_latency_ms=actual_latency,
        )


__all__ = ["ConversationRecorder"]
