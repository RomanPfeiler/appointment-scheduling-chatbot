"""Unit tests for evaluation/recorder.py.

Drives a ConversationRecorder with synthetic events end-to-end and verifies:
- begin_turn / end_turn capture user/agent messages + state snapshot.
- record_llm_call and record_tool_call attach to the currently-open turn.
- finalize() writes a JSON record and a markdown transcript at the expected
  paths.
- Lightweight derived metrics are computed (booking detected, call counts).
- The manifest status flips to ``complete`` after finalize.
- ``state_snapshot`` strips the bulky ``messages`` key.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from evaluation import storage
from evaluation.adhoc import make_session_recorder
from evaluation.recorder import ConversationRecorder
from evaluation.schemas import ConversationRecord, RunConfig, RunManifest
from evaluation.storage import RunPaths, load_manifest, load_record, now_utc


@pytest.fixture
def temp_runs_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect ``runs_root()`` and ``reports_root()`` into a temp dir.

    The recorder writes under ``runs_root()``; redirecting it keeps tests
    hermetic and avoids polluting the real ``evaluation/runs/`` folder.
    """
    runs = tmp_path / "runs"
    reports = tmp_path / "reports"
    runs.mkdir()
    reports.mkdir()
    monkeypatch.setattr(storage, "runs_root", lambda: runs)
    monkeypatch.setattr(storage, "reports_root", lambda: reports)
    return tmp_path


def _make_recorder(temp_runs_root: Path) -> ConversationRecorder:
    config = RunConfig(
        llm_provider="gemini",
        llm_model="gemini-2.5-flash",
        llm_temperature=0.5,
    )
    run_id = "20260524_120000__adhoc__abcd123__sess0001"
    paths = RunPaths(run_id=run_id, stage="adhoc")
    manifest = RunManifest(
        run_id=run_id,
        stage="adhoc",
        timestamp_start=now_utc(),
        git_commit="abcd1234",
        config=config,
    )
    return ConversationRecorder(
        scenario_id="adhoc",
        tier="adhoc",
        stage="adhoc",
        persona_profile="adhoc",
        run_index=1,
        run_id=run_id,
        paths=paths,
        config=config,
        manifest=manifest,
    )


def test_end_to_end_recording_and_finalize(temp_runs_root: Path) -> None:
    recorder = _make_recorder(temp_runs_root)

    recorder.begin_turn(user_message="Book me a mortgage appointment.")
    recorder.record_llm_call(
        provider="gemini",
        model="gemini-2.5-flash",
        prompt_message_count=1,
        response_type="function_call",
        function_name="get_appointment_topics",
        function_args={},
        latency_ms=812.0,
        input_tokens=120,
        output_tokens=18,
        temperature=0.5,
    )
    recorder.record_tool_call(
        tool_name="get_appointment_topics",
        parameters={},
        response=[{"topic_id": "mortgage", "topic_name": "Mortgage"}],
        actual_latency_ms=43.1,
        simulated_latency_ms=None,
        success=True,
    )
    recorder.record_llm_call(
        provider="gemini",
        model="gemini-2.5-flash",
        prompt_message_count=3,
        response_type="text",
        text_preview="Sure — which contact medium?",
        latency_ms=520.5,
        input_tokens=190,
        output_tokens=22,
        temperature=0.5,
    )
    recorder.end_turn(
        agent_response="Sure — which contact medium?",
        state_snapshot={
            "phase": "medium",
            "topic_id": "mortgage",
            "messages": ["bulky list that should be stripped"],
        },
    )

    record = recorder.finalize(termination_reason="session_end", final_messages=[{"role": "user", "text": "hi"}])

    assert isinstance(record, ConversationRecord)
    assert record.derived is not None
    assert record.derived.total_mcp_calls == 1
    assert record.derived.total_turn_count == 1
    assert record.derived.booked is False

    # Files written
    record_path = temp_runs_root / "runs" / "adhoc" / record.run_id / "records" / "conversation.json"
    transcript_path = temp_runs_root / "runs" / "adhoc" / record.run_id / "transcripts" / "conversation.md"
    manifest_path = temp_runs_root / "runs" / "adhoc" / record.run_id / "manifest.json"
    assert record_path.exists()
    assert transcript_path.exists()

    # state_snapshot must strip the heavy ``messages`` key
    on_disk = load_record(record_path)
    assert "messages" not in on_disk.turns[0].state_snapshot
    assert on_disk.turns[0].state_snapshot["topic_id"] == "mortgage"

    # Transcript contains the conversation surface
    transcript = transcript_path.read_text(encoding="utf-8")
    assert "Book me a mortgage appointment." in transcript
    assert "get_appointment_topics" in transcript
    assert "Termination" in transcript

    # Manifest housekeeping (we passed manifest=, so recorder owns it)
    manifest_on_disk = load_manifest(manifest_path)
    assert manifest_on_disk.status == "complete"
    assert manifest_on_disk.record_count_written == 1


def test_finalize_is_idempotent(temp_runs_root: Path) -> None:
    recorder = _make_recorder(temp_runs_root)
    recorder.begin_turn(user_message="hi")
    recorder.end_turn(agent_response="hello", state_snapshot={"phase": "intent"})
    first = recorder.finalize(termination_reason="session_end")
    second = recorder.finalize(termination_reason="session_end")
    assert first is second


def test_record_calls_without_open_turn_are_dropped(temp_runs_root: Path) -> None:
    recorder = _make_recorder(temp_runs_root)
    # No begin_turn — these should silently no-op.
    recorder.record_llm_call(
        provider="gemini",
        model="gemini-2.5-flash",
        prompt_message_count=0,
        response_type="text",
    )
    recorder.record_tool_call(
        tool_name="get_appointment_topics",
        parameters={},
        response=[],
    )
    record = recorder.finalize(termination_reason="session_end")
    assert record.turns == []


def test_book_appointment_success_flips_booked(temp_runs_root: Path) -> None:
    recorder = _make_recorder(temp_runs_root)
    recorder.begin_turn(user_message="confirm")
    recorder.record_tool_call(
        tool_name="book_appointment",
        parameters={"topic_id": "mortgage", "contact_medium_id": "branch",
                    "datetime_start": "2026-05-25T10:00:00+02:00",
                    "datetime_end": "2026-05-25T11:00:00+02:00"},
        response={"status": "success", "booking_id": "abc"},
        actual_latency_ms=50.0,
        success=True,
    )
    recorder.end_turn(agent_response="Booked.", state_snapshot={"phase": "booked"})
    record = recorder.finalize(termination_reason="booked")
    assert record.derived is not None
    assert record.derived.booked is True


def test_make_session_recorder_writes_in_progress_manifest(temp_runs_root: Path) -> None:
    recorder = make_session_recorder(
        session_id="abcd-1234-ef",
        provider="gemini",
        model="gemini-2.5-flash",
        temperature=0.5,
    )
    manifest_path = recorder.paths.manifest
    assert manifest_path.exists()
    manifest = load_manifest(manifest_path)
    assert manifest.status == "in_progress"
    # Finalize and re-check
    recorder.finalize(termination_reason="session_end")
    manifest = load_manifest(manifest_path)
    assert manifest.status == "complete"


def test_atomic_write_does_not_leave_tmp_file(temp_runs_root: Path) -> None:
    recorder = _make_recorder(temp_runs_root)
    recorder.begin_turn(user_message="ping")
    recorder.end_turn(agent_response="pong", state_snapshot={"phase": "intent"})
    recorder.finalize(termination_reason="session_end")
    run_dir = temp_runs_root / "runs" / "adhoc" / recorder.record.run_id
    leftover = list(run_dir.rglob("*.tmp"))
    assert leftover == [], f"unexpected .tmp files left behind: {leftover}"


def test_record_json_is_valid_json(temp_runs_root: Path) -> None:
    recorder = _make_recorder(temp_runs_root)
    recorder.begin_turn(user_message="hi")
    recorder.end_turn(agent_response="hello", state_snapshot={"phase": "intent"})
    recorder.finalize(termination_reason="session_end")
    record_path = recorder.paths.adhoc_record
    parsed = json.loads(record_path.read_text(encoding="utf-8"))
    assert parsed["scenario_id"] == "adhoc"
    assert parsed["schema_version"] == "1.0"


def test_timestamp_end_set_on_finalize(temp_runs_root: Path) -> None:
    recorder = _make_recorder(temp_runs_root)
    recorder.begin_turn(user_message="hi")
    recorder.end_turn(agent_response="hello", state_snapshot={})
    record = recorder.finalize(termination_reason="session_end")
    assert record.timestamp_end is not None
    assert isinstance(record.timestamp_end, datetime)
    assert record.timestamp_end >= record.timestamp_start
    # Sanity: timezone-aware
    assert record.timestamp_end.tzinfo is not None
    assert record.timestamp_end.utcoffset() == timezone.utc.utcoffset(None)
