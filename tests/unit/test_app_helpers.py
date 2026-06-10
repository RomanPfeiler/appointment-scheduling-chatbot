"""Unit tests for the pure helper functions in ``app.py``.

Covers the live-demo safety nets and the 2026-06-10 step-visibility redesign:
- ``_safe_arm`` — server-side coercion of local-LLM arm selections on HF
  (defense in depth, independent of what the UI offered).
- ``_wants_local_arm`` — detection used for the settings-update override notice.
- ``_verbosity_level`` — Step_Verbosity select → numeric level mapping.
- ``_truncate_payload`` — slot-list and oversized-blob truncation for steps.
- ``_summarize_params`` / ``_summarize_tool_result`` / ``_ladder_step_line`` —
  the one-line summaries used at the "Activity summary" verbosity level.

``app.py`` is import-heavy (it compiles the LangGraph at import) but has no
side effects beyond that — no client is created and nothing network-bound runs
at module load, so importing it in a unit test is safe and is itself a cheap
boot-path smoke check.
"""

import pytest

import app


# ---------------------------------------------------------------------------
# _safe_arm / _wants_local_arm — HF local-arm suppression
# ---------------------------------------------------------------------------


def test_safe_arm_falls_back_to_default_when_unset():
    assert app._safe_arm(None, "dateparser") == "dateparser"
    assert app._safe_arm("", "spacy") == "spacy"


def test_safe_arm_passes_local_arm_through_locally(monkeypatch):
    monkeypatch.setattr(app, "IS_HF_SPACE", False)
    assert app._safe_arm("local_llm", "dateparser") == "local_llm"
    assert app._safe_arm("api_llm", "dateparser") == "api_llm"


def test_safe_arm_coerces_local_arm_on_hf(monkeypatch):
    monkeypatch.setattr(app, "IS_HF_SPACE", True)
    assert app._safe_arm("local_llm", "dateparser") == "dateparser"
    # The legacy disabled UI label must also be coerced (stale sessions may
    # still submit it even though it is no longer offered in the Select).
    assert app._safe_arm(app.LOCAL_ARM_DISABLED_LABEL, "spacy") == "spacy"


def test_safe_arm_keeps_non_local_arms_on_hf(monkeypatch):
    monkeypatch.setattr(app, "IS_HF_SPACE", True)
    assert app._safe_arm("api_llm", "dateparser") == "api_llm"
    assert app._safe_arm("dateparser", "dateparser") == "dateparser"


def test_wants_local_arm_detects_both_keys_and_label():
    assert app._wants_local_arm({"Datetime_Arm": "local_llm"})
    assert app._wants_local_arm({"Entity_Arm": "local_llm"})
    assert app._wants_local_arm({"Entity_Arm": app.LOCAL_ARM_DISABLED_LABEL})
    assert not app._wants_local_arm({"Datetime_Arm": "api_llm", "Entity_Arm": "spacy"})
    assert not app._wants_local_arm({})


# ---------------------------------------------------------------------------
# _verbosity_level — Step_Verbosity mapping
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Off", 0),
        ("Activity summary", 1),
        ("Tool calls", 2),
        ("Full debug", 3),
    ],
)
def test_verbosity_level_maps_select_values(value, expected):
    assert app._verbosity_level({"Step_Verbosity": value}) == expected


def test_verbosity_level_defaults_to_off_for_missing_or_unknown():
    assert app._verbosity_level({}) == 0
    assert app._verbosity_level({"Step_Verbosity": "nonsense"}) == 0
    # A stale session that still carries the removed binary switch renders nothing
    # rather than crashing.
    assert app._verbosity_level({"Show_Debug_Steps": True}) == 0


def test_verbosity_values_and_levels_stay_in_sync():
    assert list(app._VERBOSITY_LEVELS) == app.STEP_VERBOSITY_VALUES
    assert sorted(app._VERBOSITY_LEVELS.values()) == list(range(len(app.STEP_VERBOSITY_VALUES)))


# ---------------------------------------------------------------------------
# Payload truncation + one-line summaries
# ---------------------------------------------------------------------------


def test_truncate_payload_truncates_long_slot_lists():
    slots = [
        {"datetime_start": f"2026-06-{day:02d}T09:00:00+02:00"} for day in range(1, 21)
    ]
    text = app._truncate_payload(slots)
    assert f"… and {20 - app._MAX_SLOTS_SHOWN} more" in text
    assert "2026-06-01" in text
    assert "2026-06-20" not in text


def test_truncate_payload_short_list_untouched():
    slots = [{"a": 1}, {"b": 2}]
    text = app._truncate_payload(slots)
    assert "more" not in text


def test_truncate_payload_caps_oversized_blobs():
    blob = {"big": "x" * (app._MAX_PAYLOAD_CHARS * 2)}
    text = app._truncate_payload(blob)
    assert text.endswith("… (truncated)")
    assert len(text) <= app._MAX_PAYLOAD_CHARS + len("\n… (truncated)")


def test_summarize_params():
    assert app._summarize_params({}) == "(no parameters)"
    assert app._summarize_params({"topic_id": "mortgage", "n": 2}) == "topic_id=mortgage, n=2"


def test_summarize_tool_result():
    assert app._summarize_tool_result([1, 2, 3]) == "3 result(s)"
    assert app._summarize_tool_result({"status": "success"}) == "status: success"
    assert app._summarize_tool_result({"status": "error", "message": "boom"}).startswith(
        "error: boom"
    )
    assert app._summarize_tool_result("anything else") == "ok"


def test_ladder_step_line_cache_vs_api():
    cached = {"step": 1, "window": ["2026-06-02T08:00:00+02:00", "2026-06-04T17:00:00+02:00"],
              "mcp_calls": 0, "found": 2}
    line = app._ladder_step_line(cached)
    assert "served from session cache, no API call" in line
    assert "2026-06-02 → 2026-06-04" in line
    assert "2 slot(s) found" in line

    queried = dict(cached, mcp_calls=2, found=0)
    line = app._ladder_step_line(queried)
    assert "2 API call(s)" in line
    assert "0 slot(s) found" in line


def test_ladder_step_line_error():
    assert app._ladder_step_line({"step": 0, "mcp_calls": 1, "error": True}).startswith("aborted")
