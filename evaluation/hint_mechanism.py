"""Mechanism analysis for the NLP-HINTS deep dive (2026-06-11).

Answers *why* the prompt-side NLP-HINTS block fails to improve the strong agent
(representative null, n=120/stage) and directionally hurts the weak agent
(smoke, n=14) — by re-reading the recorded conversations deterministically.
Run records are read-only inputs; this module never launches agent runs.

Analyses (pre-registered in
``project_presentation/progress/deep_dive_nlp_hints_2026-06-11.md`` §2):

- A1  Outcome-flip inventory (paired by scenario_id × rep, arm vs family baseline)
- A2  Divergence-turn detection (first material agent-behaviour difference)
- A3  Hint correctness × adoption × outcome cross-tab
- A4  Booking-funnel localization (deterministic stages; acceptance = heuristic)
- A5  Prompt-side accounting (rendered hint block size via the production
      ``_format_nlp_hints`` — byte-faithful reconstruction from ``last_annotation``)
- A6  Degenerate/stale-hint trace (per-turn flags, turn-1 vs mid-conversation)
- A7  Scripted failure-taxonomy coding of flip cases (pass 1 of the two-pass design)
- A8  Cross-family consistency (the same statistics on both families)

CLI::

    python -m evaluation.hint_mechanism            # both families, default runs
    python -m evaluation.hint_mechanism --family weak

Outputs land under ``evaluation/reports/hint_mechanism/``:
``<family>_summary.json`` (machine-readable aggregates + per-case rows),
``<family>_flips.csv`` (one row per booking flip), and ``SUMMARY.md``.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import re
import statistics
from collections import Counter
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

from evaluation.metrics import (
    _count_slots_in_text,
    _is_empty_availability_response,
    _parse_dt_safe,
    _resolve_offset,
)
from orchestrator.nodes.agent import _build_system_prompt, _format_nlp_hints

logger = logging.getLogger(__name__)

_ZURICH = ZoneInfo("Europe/Zurich")
_RUNS_DIR = Path(__file__).parent / "runs"
_SCENARIOS_DIR = Path(__file__).parent / "scenarios"
_OUT_DIR = Path(__file__).parent / "reports" / "hint_mechanism"

# Frozen anchor runs (same ids as the pinned snapshots). The registry is a
# module constant because these are the only runs the deep dive is about;
# --runs-dir exists for tests.
RUN_REGISTRY: dict[str, dict[str, str]] = {
    "strong": {
        "baseline": "baseline/20260606_205242__baseline__e1626fa__representative_reduced",
        "nlp_arm1": "nlp_arm1/20260606_222357__nlp_arm1__e1626fa__representative_reduced",
        "nlp_arm2": "nlp_arm2/20260607_014848__nlp_arm2__e1626fa__representative_reduced",
        "nlp_arm3": "nlp_arm3/20260606_234404__nlp_arm3__e1626fa__representative_reduced",
    },
    "weak": {
        "baseline": "weak_baseline/20260610_183456__weak_baseline__a368480__smoke",
        "nlp_arm1": "weak_nlp_arm1/20260610_192943__weak_nlp_arm1__e4073f5__smoke",
        "nlp_arm2": "weak_nlp_arm2/20260610_193716__weak_nlp_arm2__99324a4__smoke",
        "nlp_arm3": "weak_nlp_arm3/20260610_215714__weak_nlp_arm3__8119c12__smoke",
    },
}

# Scheduling horizon (mcp_server/config.py SCHEDULING_HORIZON_DAYS) — used for
# the out-of-horizon hint flag without importing the server package.
_HORIZON_DAYS = 21
_BUSINESS_START_HOUR = 8
_BUSINESS_END_HOUR = 17
# Server-side per-call window cap (mcp_server/config.py
# MAX_AVAILABILITY_WINDOW_DAYS = 3); wider calls are silently truncated.
_HORIZON_CAP_HOURS = 72.0

# Material check_availability difference thresholds (A2).
_MATERIAL_START_SHIFT_HOURS = 2.0
_MATERIAL_SPAN_DIFF_HOURS = 24.0

# Hint-adoption tolerance (A3): the first query "adopts" a hint range when it
# starts on the same day within this many minutes of the range start.
_ADOPTION_TIME_TOLERANCE_MIN = 60.0

# A4 acceptance heuristic (explicitly labelled heuristic in all outputs).
_ACCEPT_RE = re.compile(
    r"\b(yes|yep|sure|perfect|great|sounds good|that works|works for me"
    r"|book it|please book|go ahead|confirm|i'?ll take|let'?s do)\b",
    re.IGNORECASE,
)

_FUNNEL_STAGES = [
    "queried",          # >=1 check_availability call
    "nonempty_result",  # >=1 check_availability returned >=1 slot
    "slots_presented",  # >=1 agent turn presented >=1 slot in text
    "user_accepted",    # heuristic: acceptance keyword after first presentation
    "booking_attempted",  # book_appointment called
    "booked",           # derived.booked
]


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_scenarios(scenarios_dir: Path = _SCENARIOS_DIR) -> dict[str, dict]:
    """Load every tier JSON into a scenario_id → scenario-dict lookup."""
    out: dict[str, dict] = {}
    for path in sorted(scenarios_dir.glob("tier*.json")):
        with path.open(encoding="utf-8") as f:
            data = json.load(f)
        for sc in data if isinstance(data, list) else [data]:
            out[sc["scenario_id"]] = sc
    return out


def load_run(run_rel: str, runs_dir: Path = _RUNS_DIR) -> dict[str, dict]:
    """Load all records of one run into a ``scenario_id__rep<k>`` → record map."""
    rec_dir = runs_dir / run_rel / "records"
    if not rec_dir.is_dir():
        raise FileNotFoundError(f"records dir not found: {rec_dir}")
    out: dict[str, dict] = {}
    for path in sorted(rec_dir.glob("*.json")):
        with path.open(encoding="utf-8") as f:
            rec = json.load(f)
        rec["turns"] = sorted(rec.get("turns") or [], key=lambda t: t.get("turn_index", 0))
        out[f"{rec['scenario_id']}__rep{rec['run_index']}"] = rec
    return out


def _booked(rec: dict) -> bool:
    return bool((rec.get("derived") or {}).get("booked"))


def _is_error_record(rec: dict) -> bool:
    return rec.get("termination_reason") == "error"


def _reference_date(scenario: dict) -> date:
    return date.fromisoformat(scenario["reference_date"])


# ---------------------------------------------------------------------------
# Turn-level helpers
# ---------------------------------------------------------------------------


def _tool_calls(turn: dict, name: str | None = None) -> list[dict]:
    calls = turn.get("tool_calls") or []
    if name is None:
        return calls
    return [tc for tc in calls if tc.get("tool_name") == name]


def _ca_response_slot_count(response: Any) -> int:
    """Number of slots in a ``check_availability`` response payload.

    The mock server returns ``[]``, a single-slot dict, or a list of slot
    dicts; ``{"status": "error"}`` carries no slots.
    """
    if isinstance(response, list):
        return len(response)
    if isinstance(response, dict):
        if response.get("status") == "error":
            return 0
        return 1 if response.get("datetime_start") else 0
    return 0


def _ca_signature(params: dict | None) -> tuple[date | None, float | None, float | None]:
    """(start_date, start_hour, span_hours) of a check_availability call."""
    if not params:
        return (None, None, None)
    start = _parse_dt_safe(str(params.get("start_datetime", "")))
    end = _parse_dt_safe(str(params.get("end_datetime", "")))
    if start is None:
        return (None, None, None)
    span = (end - start).total_seconds() / 3600.0 if end is not None else None
    return (start.date(), start.hour + start.minute / 60.0, span)


def material_ca_difference(params_a: dict | None, params_b: dict | None) -> bool:
    """True when two check_availability calls target materially different windows.

    Material = different start date, start time shifted more than
    ``_MATERIAL_START_SHIFT_HOURS``, or window span differing by more than
    ``_MATERIAL_SPAN_DIFF_HOURS``. One side missing/unparseable while the other
    is present is material.
    """
    date_a, hour_a, span_a = _ca_signature(params_a)
    date_b, hour_b, span_b = _ca_signature(params_b)
    if (date_a is None) != (date_b is None):
        return True
    if date_a is None:
        return False
    if date_a != date_b:
        return True
    if hour_a is not None and hour_b is not None and abs(hour_a - hour_b) > _MATERIAL_START_SHIFT_HOURS:
        return True
    if span_a is not None and span_b is not None and abs(span_a - span_b) > _MATERIAL_SPAN_DIFF_HOURS:
        return True
    return False


def turn_intent(turn: dict) -> str:
    """Coarse agent-behaviour class for one turn (used for A2 divergence)."""
    if _tool_calls(turn, "book_appointment"):
        return "booking_attempt"
    if _count_slots_in_text(turn.get("agent_response")) > 0:
        return "presents_slots"
    empty_ca = any(
        _is_empty_availability_response(tc.get("response"))
        for tc in _tool_calls(turn, "check_availability")
        if tc.get("success")
    )
    if empty_ca:
        return "no_slots_reply"
    return "question_or_other"


def _norm_text(text: str | None) -> str:
    return re.sub(r"\s+", " ", (text or "").strip().lower())


# ---------------------------------------------------------------------------
# A1 — outcome-flip inventory
# ---------------------------------------------------------------------------


def classify_flips(base: dict[str, dict], arm: dict[str, dict]) -> dict[str, list[str]]:
    """Classify paired baseline→arm booking transitions.

    Returns lists of conversation keys under ``lost`` (booked→unbooked),
    ``gained`` (unbooked→booked), ``same_booked``, ``same_unbooked``, and
    ``excluded`` (missing on one side or error-terminated on either side).
    """
    out: dict[str, list[str]] = {
        "lost": [], "gained": [], "same_booked": [], "same_unbooked": [], "excluded": [],
    }
    for key in sorted(set(base) | set(arm)):
        b, a = base.get(key), arm.get(key)
        if b is None or a is None or _is_error_record(b) or _is_error_record(a):
            out["excluded"].append(key)
            continue
        bb, ab = _booked(b), _booked(a)
        if bb and not ab:
            out["lost"].append(key)
        elif ab and not bb:
            out["gained"].append(key)
        elif bb:
            out["same_booked"].append(key)
        else:
            out["same_unbooked"].append(key)
    return out


# ---------------------------------------------------------------------------
# A2 — divergence-turn detection
# ---------------------------------------------------------------------------


def find_divergence(base_rec: dict, arm_rec: dict) -> dict:
    """First turn where agent behaviour materially diverges between a pair.

    Compares per-turn tool-name sequences, first check_availability windows,
    and coarse response intent. Also records the first turn where the *user*
    text differs — when that precedes the agent divergence the attribution is
    confounded by simulator non-determinism (flagged, not dropped).
    """
    base_turns, arm_turns = base_rec["turns"], arm_rec["turns"]
    n = min(len(base_turns), len(arm_turns))

    user_diverged_at: int | None = None
    for i in range(n):
        if _norm_text(base_turns[i].get("user_message")) != _norm_text(arm_turns[i].get("user_message")):
            user_diverged_at = base_turns[i].get("turn_index", i + 1)
            break

    divergence_turn: int | None = None
    kind: str | None = None
    detail = ""
    for i in range(n):
        bt, at = base_turns[i], arm_turns[i]
        t_idx = bt.get("turn_index", i + 1)
        b_tools = [tc.get("tool_name") for tc in _tool_calls(bt)]
        a_tools = [tc.get("tool_name") for tc in _tool_calls(at)]
        if b_tools != a_tools:
            divergence_turn, kind = t_idx, "tool_choice"
            detail = f"baseline={b_tools} arm={a_tools}"
            break
        b_ca, a_ca = _tool_calls(bt, "check_availability"), _tool_calls(at, "check_availability")
        if b_ca and a_ca and material_ca_difference(b_ca[0].get("parameters"), a_ca[0].get("parameters")):
            divergence_turn, kind = t_idx, "query_window"
            detail = (
                f"baseline={_ca_signature(b_ca[0].get('parameters'))} "
                f"arm={_ca_signature(a_ca[0].get('parameters'))}"
            )
            break
        b_int, a_int = turn_intent(bt), turn_intent(at)
        if b_int != a_int:
            divergence_turn, kind = t_idx, "response_intent"
            detail = f"baseline={b_int} arm={a_int}"
            break
    if divergence_turn is None and len(base_turns) != len(arm_turns):
        divergence_turn = n + 1
        kind = "conversation_length"
        detail = f"baseline_turns={len(base_turns)} arm_turns={len(arm_turns)}"

    return {
        "turn_index": divergence_turn,
        "kind": kind,
        "position": (
            None if divergence_turn is None
            else ("first" if divergence_turn <= 1 else "mid_late")
        ),
        "user_text_diverged_first": (
            user_diverged_at is not None
            and divergence_turn is not None
            and user_diverged_at < divergence_turn
        ),
        "user_diverged_at": user_diverged_at,
        "detail": detail,
    }


# ---------------------------------------------------------------------------
# A3 — hint correctness × adoption × outcome
# ---------------------------------------------------------------------------


def _turn_annotation(turn: dict) -> dict | None:
    snap = turn.get("state_snapshot") or {}
    return snap.get("last_annotation")


def _annotation_ranges(ann: dict | None) -> list[dict]:
    return list((ann or {}).get("datetime_ranges") or [])


def _expected_window(scenario: dict) -> tuple[datetime, datetime] | None:
    win = scenario.get("expected_datetime_window")
    if not win:
        return None
    base = _reference_date(scenario)
    try:
        return (
            _resolve_offset(win["start_offset"], base),
            _resolve_offset(win["end_offset"], base),
        )
    except (KeyError, ValueError):
        return None


def assess_hint(ann: dict | None, scenario: dict) -> dict:
    """Score the turn-1 hint against the scenario's expected window.

    Status: ``no_hint`` (no datetime ranges), ``exact`` (some range starts on
    the expected day within 30 min), ``partial`` (right day, wrong time),
    ``wrong`` (no range on the expected day), or ``unscorable`` (scenario has
    no expected window — Tier 6/7 shapes). The *best* range counts: the agent
    sees all ranges, so the hint is as good as its best line.
    """
    ranges = _annotation_ranges(ann)
    if not ranges:
        return {"status": "no_hint", "best_score": None}
    expected = _expected_window(scenario)
    if expected is None:
        return {"status": "unscorable", "best_score": None}
    exp_start, _exp_end = expected
    best = 0.0
    for rng in ranges:
        start = _parse_dt_safe(str(rng.get("start_datetime", "")))
        if start is None:
            continue
        if start.date() != exp_start.date():
            score = 0.0
        elif abs((start - exp_start).total_seconds()) / 60.0 <= 30.0:
            score = 1.0
        else:
            score = 0.5
        best = max(best, score)
    status = "exact" if best >= 1.0 else ("partial" if best >= 0.5 else "wrong")
    return {"status": status, "best_score": best}


def first_ca_params(rec: dict) -> dict | None:
    """Parameters of the conversation's first check_availability call."""
    derived = rec.get("derived") or {}
    if derived.get("first_check_availability_params"):
        return derived["first_check_availability_params"]
    for turn in rec["turns"]:
        for tc in _tool_calls(turn, "check_availability"):
            return tc.get("parameters")
    return None


def assess_adoption(rec: dict) -> str:
    """Did the agent's first availability query adopt the turn-1 hint window?

    ``adopted_window`` — same day, start within ±60 min of a hint range;
    ``adopted_day`` — same day only; ``ignored`` — queried a different day;
    ``no_query`` / ``no_hint`` — degenerate cases.
    """
    turn1 = rec["turns"][0] if rec["turns"] else None
    ranges = _annotation_ranges(_turn_annotation(turn1)) if turn1 else []
    if not ranges:
        return "no_hint"
    params = first_ca_params(rec)
    if not params:
        return "no_query"
    q_start = _parse_dt_safe(str(params.get("start_datetime", "")))
    if q_start is None:
        return "no_query"
    best = "ignored"
    for rng in ranges:
        h_start = _parse_dt_safe(str(rng.get("start_datetime", "")))
        if h_start is None or q_start.date() != h_start.date():
            continue
        if abs((q_start - h_start).total_seconds()) / 60.0 <= _ADOPTION_TIME_TOLERANCE_MIN:
            return "adopted_window"
        best = "adopted_day"
    return best


# ---------------------------------------------------------------------------
# A4 — booking funnel
# ---------------------------------------------------------------------------


def funnel_stages(rec: dict) -> dict[str, bool]:
    """Deterministic funnel stage flags for one conversation.

    ``user_accepted`` is a keyword heuristic (the only non-deterministic-ish
    stage definition) and is labelled as such everywhere it is reported.
    """
    queried = False
    nonempty = False
    presented_turn: int | None = None
    accepted = False
    attempted = False
    for turn in rec["turns"]:
        t_idx = turn.get("turn_index", 0)
        for tc in _tool_calls(turn, "check_availability"):
            queried = True
            if tc.get("success") and _ca_response_slot_count(tc.get("response")) > 0:
                nonempty = True
        if presented_turn is None and _count_slots_in_text(turn.get("agent_response")) > 0:
            presented_turn = t_idx
        if (
            presented_turn is not None
            and t_idx > presented_turn
            and _ACCEPT_RE.search(turn.get("user_message") or "")
        ):
            accepted = True
        if _tool_calls(turn, "book_appointment"):
            attempted = True
    return {
        "queried": queried,
        "nonempty_result": nonempty,
        "slots_presented": presented_turn is not None,
        "user_accepted": accepted,
        "booking_attempted": attempted,
        "booked": _booked(rec),
    }


def last_funnel_stage(stages: dict[str, bool]) -> str:
    """Name of the deepest funnel stage reached (``none`` when not even queried)."""
    last = "none"
    for stage in _FUNNEL_STAGES:
        if stages.get(stage):
            last = stage
    return last


# ---------------------------------------------------------------------------
# A5 — prompt-side accounting
# ---------------------------------------------------------------------------


def hint_block_accounting(rec: dict, scenario: dict) -> list[dict]:
    """Per-turn size of the rendered NLP-HINTS block (production renderer).

    Reconstructs the exact block the agent saw by feeding the recorded
    ``last_annotation`` through ``_format_nlp_hints`` and measuring it against
    the full system prompt built by ``_build_system_prompt`` for the
    scenario's pinned clock. Token counts are chars/4 estimates.
    """
    ref = _reference_date(scenario)
    noon = datetime(ref.year, ref.month, ref.day, 12, 0, tzinfo=_ZURICH)
    rows: list[dict] = []
    for turn in rec["turns"]:
        ann = _turn_annotation(turn)
        if not ann:
            continue
        hint = _format_nlp_hints(ann)
        total = len(_build_system_prompt(now=noon, annotation=ann))
        rows.append(
            {
                "turn_index": turn.get("turn_index"),
                "hint_chars": len(hint),
                "hint_tokens_est": round(len(hint) / 4.0, 1),
                "prompt_chars": total,
                "hint_share": round(len(hint) / total, 4) if total else 0.0,
                "n_ranges": len(_annotation_ranges(ann)),
            }
        )
    return rows


# ---------------------------------------------------------------------------
# A6 — degenerate/stale-hint trace
# ---------------------------------------------------------------------------


def hint_range_flags(rng: dict, scenario: dict) -> list[str]:
    """Degeneracy flags for one hint range (empty list = clean).

    Specificity-aware: day-level ranges (``day_specific`` / ``day_vague`` /
    ``multi_day_vague``) snap to midnight **by design**
    (``nlp/datetime_parsers/windows.py``), so a 00:00 start is degenerate only
    for ``exact_time`` — there it means the resolver lost the clock time (the
    historical exact_time→midnight failure shape). Out-of-horizon and
    unparseable starts are degenerate for every specificity.
    """
    flags: list[str] = []
    start = _parse_dt_safe(str(rng.get("start_datetime", "")))
    if start is None:
        return ["unparseable"]
    if rng.get("specificity") == "exact_time":
        if start.hour == 0 and start.minute == 0:
            flags.append("midnight_exact_time")
        elif not (_BUSINESS_START_HOUR <= start.hour < _BUSINESS_END_HOUR):
            flags.append("off_hours_exact_time")
    ref = _reference_date(scenario)
    if start.date() < ref or start.date() > ref + timedelta(days=_HORIZON_DAYS):
        flags.append("out_of_horizon")
    return flags


def trace_hints(rec: dict, scenario: dict) -> list[dict]:
    """Per-turn hint trace: flags + whether the same-turn query followed it.

    ``followed`` means a same-turn check_availability starts on one of the
    hint days; ``overrode`` means the agent queried only other days that turn;
    ``no_query`` when the turn made no availability call.
    """
    rows: list[dict] = []
    for turn in rec["turns"]:
        ann = _turn_annotation(turn)
        ranges = _annotation_ranges(ann)
        if not ranges:
            continue
        all_flags: set[str] = set()
        deg_days: set[date] = set()
        clean_days: set[date] = set()
        for rng in ranges:
            flags = hint_range_flags(rng, scenario)
            all_flags.update(flags)
            start = _parse_dt_safe(str(rng.get("start_datetime", "")))
            if start is None:
                continue
            (deg_days if flags else clean_days).add(start.date())
        hint_days = deg_days | clean_days
        ca = _tool_calls(turn, "check_availability")
        followed_degenerate_only = False
        if not ca:
            relation = "no_query"
        else:
            q_days = {
                d for tc in ca
                if (d := _ca_signature(tc.get("parameters"))[0]) is not None
            }
            relation = "followed" if (q_days & hint_days) else "overrode"
            # Strict garbled-hint adoption: the agent queried a day that ONLY a
            # degenerate range names (a clean range pointing at the same day
            # would make the follow benign).
            followed_degenerate_only = bool(q_days & (deg_days - clean_days))
        rows.append(
            {
                "turn_index": turn.get("turn_index"),
                "is_first_turn": turn.get("turn_index") == 1,
                "n_ranges": len(ranges),
                "flags": sorted(all_flags),
                "degenerate": bool(all_flags),
                "query_relation": relation,
                "followed_degenerate_only": followed_degenerate_only,
            }
        )
    return rows


# ---------------------------------------------------------------------------
# A7 — scripted taxonomy coding (pass 1 of the two-pass design)
# ---------------------------------------------------------------------------

TAXONOMY_PRIORITY = [
    "wrong_hint_adopted",
    "degenerate_midconv_hint_followed",
    "never_found_slots",
    "closure_lost",
    "exploration_suppressed",
    "format_leakage",
    "simulator_path_divergence",
]


def _distinct_days_queried(rec: dict) -> int:
    days = set()
    for turn in rec["turns"]:
        for tc in _tool_calls(turn, "check_availability"):
            d = _ca_signature(tc.get("parameters"))[0]
            if d is not None:
                days.add(d)
    return len(days)


def _midnight_ca_calls(rec: dict) -> int:
    """Count check_availability calls whose window starts at 00:00.

    No scenario legitimately requests midnight; these queries are the
    downstream footprint of a garbled exact_time→midnight hint.
    """
    n = 0
    for turn in rec["turns"]:
        for tc in _tool_calls(turn, "check_availability"):
            start = _parse_dt_safe(str((tc.get("parameters") or {}).get("start_datetime", "")))
            if start is not None and start.hour == 0 and start.minute == 0:
                n += 1
    return n


def _first_ca_span_hours(rec: dict) -> float | None:
    """Window span (hours) of the conversation's first check_availability call."""
    span = _ca_signature(first_ca_params(rec))[2]
    return round(span, 2) if span is not None else None


def _cap_truncated_ca_calls(rec: dict) -> int:
    """Count check_availability calls wider than the server's 3-day cap.

    The mock server silently truncates such windows to the first 3 days
    (``mcp_server/tools.py``), so the agent believes it scanned the whole
    range — the precondition for a false "nothing available for weeks" claim.
    """
    n = 0
    for turn in rec["turns"]:
        for tc in _tool_calls(turn, "check_availability"):
            span = _ca_signature(tc.get("parameters"))[2]
            if span is not None and span > _HORIZON_CAP_HOURS:
                n += 1
    return n


def _hint_leaked_into_text(rec: dict) -> bool:
    """Crude H5 marker: hint-machinery vocabulary in user-facing text."""
    marker = re.compile(r"nlp hint|specificity|day_vague|multi_day_vague|exact_time", re.I)
    return any(marker.search(turn.get("agent_response") or "") for turn in rec["turns"])


def code_flip_case(
    base_rec: dict,
    arm_rec: dict,
    scenario: dict,
    divergence: dict,
    hint: dict,
    adoption: str,
) -> list[str]:
    """Deterministic multi-label coding of one lost-booking flip case.

    Order of the returned labels follows ``TAXONOMY_PRIORITY``; the first one
    is the primary code. Labels are signals, not verdicts — the manual pass
    (A7 pass 2) reconciles against transcripts.
    """
    labels: list[str] = []
    base_funnel = funnel_stages(base_rec)
    arm_funnel = funnel_stages(arm_rec)
    trace = trace_hints(arm_rec, scenario)

    if hint["status"] == "wrong" and adoption in ("adopted_window", "adopted_day"):
        labels.append("wrong_hint_adopted")
    if any((not row["is_first_turn"]) and row["degenerate"] and row["query_relation"] == "followed" for row in trace):
        labels.append("degenerate_midconv_hint_followed")
    if base_funnel["nonempty_result"] and not arm_funnel["nonempty_result"]:
        labels.append("never_found_slots")
    if arm_funnel["slots_presented"] and not arm_funnel["booking_attempted"]:
        labels.append("closure_lost")
    if (
        arm_rec.get("termination_reason") == "max_turns"
        and _distinct_days_queried(arm_rec) < _distinct_days_queried(base_rec)
    ):
        labels.append("exploration_suppressed")
    if _hint_leaked_into_text(arm_rec):
        labels.append("format_leakage")
    if divergence.get("user_text_diverged_first"):
        labels.append("simulator_path_divergence")

    return sorted(labels, key=TAXONOMY_PRIORITY.index) or ["uncoded"]


# ---------------------------------------------------------------------------
# Family-level analysis
# ---------------------------------------------------------------------------


def analyze_family(
    family: str,
    runs_dir: Path = _RUNS_DIR,
    scenarios: dict[str, dict] | None = None,
    registry: dict[str, dict[str, str]] | None = None,
) -> dict:
    """Run analyses A1–A7 for one family; returns a JSON-serializable dict."""
    registry = registry or RUN_REGISTRY
    scenarios = scenarios or load_scenarios()
    runs = registry[family]
    base = load_run(runs["baseline"], runs_dir)
    result: dict[str, Any] = {"family": family, "runs": runs, "arms": {}}

    for arm_name, run_rel in runs.items():
        if arm_name == "baseline":
            continue
        arm = load_run(run_rel, runs_dir)
        flips = classify_flips(base, arm)
        paired_keys = flips["lost"] + flips["gained"] + flips["same_booked"] + flips["same_unbooked"]

        # A2 + A7 on the flip corpus
        flip_cases: list[dict] = []
        for direction in ("lost", "gained"):
            for key in flips[direction]:
                b_rec, a_rec = base[key], arm[key]
                scenario = scenarios[b_rec["scenario_id"]]
                divergence = find_divergence(b_rec, a_rec)
                ann1 = _turn_annotation(a_rec["turns"][0]) if a_rec["turns"] else None
                hint = assess_hint(ann1, scenario)
                adoption = assess_adoption(a_rec)
                case = {
                    "key": key,
                    "direction": direction,
                    "tier": b_rec.get("tier"),
                    "booking_reachable": scenario.get("booking_reachable"),
                    "divergence": divergence,
                    "hint_status": hint["status"],
                    "adoption": adoption,
                    "base_termination": b_rec.get("termination_reason"),
                    "arm_termination": a_rec.get("termination_reason"),
                    "base_funnel_last": last_funnel_stage(funnel_stages(b_rec)),
                    "arm_funnel_last": last_funnel_stage(funnel_stages(a_rec)),
                    "labels": (
                        code_flip_case(b_rec, a_rec, scenario, divergence, hint, adoption)
                        if direction == "lost" else None
                    ),
                }
                flip_cases.append(case)

        # A3 cross-tab over all paired, non-excluded conversations
        crosstab: dict[str, dict[str, Any]] = {}
        for key in paired_keys:
            a_rec = arm[key]
            scenario = scenarios[a_rec["scenario_id"]]
            ann1 = _turn_annotation(a_rec["turns"][0]) if a_rec["turns"] else None
            hint = assess_hint(ann1, scenario)
            adoption = assess_adoption(a_rec)
            cell = f"{hint['status']}|{adoption}"
            slot = crosstab.setdefault(
                cell, {"n": 0, "arm_booked": 0, "base_booked": 0, "lost": 0, "gained": 0}
            )
            slot["n"] += 1
            slot["arm_booked"] += int(_booked(a_rec))
            slot["base_booked"] += int(_booked(base[key]))
            slot["lost"] += int(key in flips["lost"])
            slot["gained"] += int(key in flips["gained"])

        # A4 funnel (booking-reachable scenarios only)
        funnel_counts = {"baseline": Counter(), "arm": Counter()}
        funnel_n = 0
        for key in paired_keys:
            scenario = scenarios[arm[key]["scenario_id"]]
            if not scenario.get("booking_reachable", True):
                continue
            funnel_n += 1
            for side, rec in (("baseline", base[key]), ("arm", arm[key])):
                stages = funnel_stages(rec)
                for stage in _FUNNEL_STAGES:
                    funnel_counts[side][stage] += int(stages[stage])

        # A5 prompt accounting + A6 hint trace over the whole arm run
        acct_rows: list[dict] = []
        trace_rows: list[dict] = []
        for key in paired_keys:
            a_rec = arm[key]
            scenario = scenarios[a_rec["scenario_id"]]
            for row in hint_block_accounting(a_rec, scenario):
                acct_rows.append({"key": key, **row})
            for row in trace_hints(a_rec, scenario):
                trace_rows.append({"key": key, "booked": _booked(a_rec), **row})

        hinted = [r for r in acct_rows if r["hint_chars"] > 0]
        first = [r for r in trace_rows if r["is_first_turn"]]
        later = [r for r in trace_rows if not r["is_first_turn"]]

        # Confound stat for A2: when the simulator's *opening* message already
        # differs between the paired runs (temperature 0.7), a turn-1 agent
        # divergence cannot be attributed to the hint block alone.
        turn1_identical = sum(
            1 for key in paired_keys
            if base[key]["turns"] and arm[key]["turns"]
            and _norm_text(base[key]["turns"][0].get("user_message"))
            == _norm_text(arm[key]["turns"][0].get("user_message"))
        )

        def _trace_summary(rows: list[dict]) -> dict:
            n = len(rows)
            deg = [r for r in rows if r["degenerate"]]
            return {
                "n_hinted_turns": n,
                "degenerate": len(deg),
                "degenerate_rate": round(len(deg) / n, 3) if n else None,
                "flag_counts": dict(Counter(f for r in rows for f in r["flags"])),
                "followed": sum(1 for r in rows if r["query_relation"] == "followed"),
                "overrode": sum(1 for r in rows if r["query_relation"] == "overrode"),
                "degenerate_followed": sum(
                    1 for r in deg if r["query_relation"] == "followed"
                ),
                # Strict: query targeted a day named ONLY by a degenerate range.
                "followed_degenerate_only": sum(
                    1 for r in rows if r["followed_degenerate_only"]
                ),
            }

        # H3 exploration stats (paired means + medians over non-excluded pairs;
        # medians are the runaway-robust view — two Arm-2 timeout scenarios
        # scanned hundreds of days and inflate the means).
        def _mean(vals: list[float]) -> float | None:
            return round(sum(vals) / len(vals), 2) if vals else None

        def _median(vals: list[float]) -> float | None:
            return round(statistics.median(vals), 2) if vals else None

        def _series(recs: dict[str, dict], fn) -> list[float]:
            return [float(fn(recs[k])) for k in paired_keys]

        days_b = _series(base, _distinct_days_queried)
        days_a = _series(arm, _distinct_days_queried)
        calls_b = _series(base, lambda r: (r.get("derived") or {}).get("availability_calls") or 0)
        calls_a = _series(arm, lambda r: (r.get("derived") or {}).get("availability_calls") or 0)
        dead_b = _series(base, lambda r: (r.get("derived") or {}).get("dead_end_turn_count") or 0)
        dead_a = _series(arm, lambda r: (r.get("derived") or {}).get("dead_end_turn_count") or 0)
        mid_b = _series(base, _midnight_ca_calls)
        mid_a = _series(arm, _midnight_ca_calls)
        cap_b = _series(base, _cap_truncated_ca_calls)
        cap_a = _series(arm, _cap_truncated_ca_calls)
        span_b = [s for k in paired_keys if (s := _first_ca_span_hours(base[k])) is not None]
        span_a = [s for k in paired_keys if (s := _first_ca_span_hours(arm[k])) is not None]
        exploration = {
            # First-query window width (the H3 narrowing statistic): the hint's
            # per-specificity guidance can replace the agent's own padding.
            "median_first_ca_span_h_base": _median(span_b),
            "median_first_ca_span_h_arm": _median(span_a),
            "first_ca_narrow_1h_base": sum(1 for s in span_b if s <= 1.01),
            "first_ca_narrow_1h_arm": sum(1 for s in span_a if s <= 1.01),
            "first_ca_n_base": len(span_b),
            "first_ca_n_arm": len(span_a),
            # Silently cap-truncated wide scans (false-coverage precondition).
            "cap_truncated_calls_base_total": int(sum(cap_b)),
            "cap_truncated_calls_arm_total": int(sum(cap_a)),
            "convs_with_cap_truncation_base": sum(1 for v in cap_b if v > 0),
            "convs_with_cap_truncation_arm": sum(1 for v in cap_a if v > 0),
            "mean_distinct_days_queried_base": _mean(days_b),
            "mean_distinct_days_queried_arm": _mean(days_a),
            "median_distinct_days_queried_base": _median(days_b),
            "median_distinct_days_queried_arm": _median(days_a),
            "mean_availability_calls_base": _mean(calls_b),
            "mean_availability_calls_arm": _mean(calls_a),
            "median_availability_calls_base": _median(calls_b),
            "median_availability_calls_arm": _median(calls_a),
            "mean_dead_end_turns_base": _mean(dead_b),
            "mean_dead_end_turns_arm": _mean(dead_a),
            # Direct garbled-window adoption evidence: check_availability calls
            # that START at 00:00 (no legitimate scenario asks for midnight).
            "midnight_ca_calls_base_total": int(sum(mid_b)),
            "midnight_ca_calls_arm_total": int(sum(mid_a)),
            "convs_with_midnight_ca_base": sum(1 for v in mid_b if v > 0),
            "convs_with_midnight_ca_arm": sum(1 for v in mid_a if v > 0),
        }

        result["arms"][arm_name] = {
            "n_paired": len(paired_keys),
            "exploration": exploration,
            "n_excluded": len(flips["excluded"]),
            "flips": {k: v for k, v in flips.items() if k != "excluded"},
            "flip_counts": {
                "lost": len(flips["lost"]),
                "gained": len(flips["gained"]),
                "same_booked": len(flips["same_booked"]),
                "same_unbooked": len(flips["same_unbooked"]),
            },
            "flip_cases": flip_cases,
            "divergence_positions": dict(
                Counter(
                    c["divergence"]["position"] for c in flip_cases
                    if c["divergence"]["position"]
                )
            ),
            "divergence_kinds": dict(
                Counter(c["divergence"]["kind"] for c in flip_cases if c["divergence"]["kind"])
            ),
            "user_diverged_first_rate": (
                round(
                    sum(1 for c in flip_cases if c["divergence"]["user_text_diverged_first"])
                    / len(flip_cases),
                    3,
                )
                if flip_cases else None
            ),
            "turn1_user_text_identical_rate": (
                round(turn1_identical / len(paired_keys), 3) if paired_keys else None
            ),
            "crosstab": crosstab,
            "funnel": {
                "n_reachable_pairs": funnel_n,
                "baseline": dict(funnel_counts["baseline"]),
                "arm": dict(funnel_counts["arm"]),
            },
            "prompt_accounting": {
                "n_turns_with_annotation": len(acct_rows),
                "n_turns_with_rendered_hint": len(hinted),
                "mean_hint_chars": (
                    round(sum(r["hint_chars"] for r in hinted) / len(hinted), 1)
                    if hinted else 0.0
                ),
                "max_hint_chars": max((r["hint_chars"] for r in hinted), default=0),
                "mean_hint_share": (
                    round(sum(r["hint_share"] for r in hinted) / len(hinted), 4)
                    if hinted else 0.0
                ),
                "mean_hint_tokens_est": (
                    round(sum(r["hint_tokens_est"] for r in hinted) / len(hinted), 1)
                    if hinted else 0.0
                ),
            },
            "hint_trace": {
                "first_turn": _trace_summary(first),
                "mid_conversation": _trace_summary(later),
            },
            "taxonomy_counts": dict(
                Counter(
                    label
                    for c in flip_cases
                    if c["labels"]
                    for label in c["labels"]
                )
            ),
        }
    return result


# ---------------------------------------------------------------------------
# Flip-case digests (compact transcript views for the manual taxonomy pass)
# ---------------------------------------------------------------------------


def _digest_turn(turn: dict, with_annotation: bool) -> list[str]:
    """Compact one-turn digest lines for the flip-case review corpus."""
    lines: list[str] = []
    t = turn.get("turn_index")
    if with_annotation:
        ann = _turn_annotation(turn)
        ranges = _annotation_ranges(ann)
        if ann and (ann.get("topic") or ann.get("contact_medium") or ranges):
            rng_txt = "; ".join(
                f"{r.get('start_datetime')}→{r.get('end_datetime')} "
                f"[{r.get('specificity')}] {r.get('original_text')!r}"
                for r in ranges
            )
            lines.append(
                f"  T{t} HINT: topic={ann.get('topic')} medium={ann.get('contact_medium')} {rng_txt}"
            )
    user = (turn.get("user_message") or "").replace("\n", " ")
    agent = (turn.get("agent_response") or "").replace("\n", " ")
    lines.append(f"  T{t} USER: {user[:140]}")
    for tc in _tool_calls(turn):
        name = tc.get("tool_name")
        if name == "check_availability":
            sig = _ca_signature(tc.get("parameters"))
            n_slots = _ca_response_slot_count(tc.get("response"))
            lines.append(
                f"  T{t} TOOL: check_availability({sig[0]} h={sig[1]} span_h={sig[2]}) -> {n_slots} slots"
            )
        else:
            ok = tc.get("success")
            lines.append(f"  T{t} TOOL: {name} (success={ok})")
    lines.append(f"  T{t} AGENT: {agent[:140]}")
    return lines


def render_flip_digests(family: str, result: dict, base_runs: dict[str, dict[str, dict]],
                        arm_runs: dict[str, dict[str, dict]]) -> str:
    """Markdown digest of every flip case (both sides), for manual coding."""
    lines = [
        f"# Flip-case digests — {family} family",
        "",
        "Compact per-turn views of every paired booking flip (baseline vs arm).",
        "Generated by `python -m evaluation.hint_mechanism` for the A7 manual",
        "taxonomy pass; truncated text (140 chars), full transcripts live in the",
        "run directories.",
        "",
    ]
    for arm_name, a in result["arms"].items():
        base = base_runs[arm_name]
        arm = arm_runs[arm_name]
        for case in a["flip_cases"]:
            key = case["key"]
            b_rec, a_rec = base[key], arm[key]
            lines.append(
                f"## {family}/{arm_name} — {key} ({case['direction']}; tier {case['tier']}; "
                f"div T{case['divergence']['turn_index']} {case['divergence']['kind']}; "
                f"hint {case['hint_status']}/{case['adoption']}; "
                f"labels={case['labels']})"
            )
            lines.append(
                f"### baseline ({b_rec.get('termination_reason')}, "
                f"{len(b_rec['turns'])} turns, booked={_booked(b_rec)})"
            )
            for turn in b_rec["turns"]:
                lines.extend(_digest_turn(turn, with_annotation=False))
            lines.append(
                f"### {arm_name} ({a_rec.get('termination_reason')}, "
                f"{len(a_rec['turns'])} turns, booked={_booked(a_rec)})"
            )
            for turn in a_rec["turns"]:
                lines.extend(_digest_turn(turn, with_annotation=True))
            lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def write_outputs(results: dict[str, dict], out_dir: Path = _OUT_DIR) -> None:
    """Write per-family JSON, flip CSVs, and the cross-family SUMMARY.md."""
    out_dir.mkdir(parents=True, exist_ok=True)
    for family, result in results.items():
        with (out_dir / f"{family}_summary.json").open("w", encoding="utf-8") as f:
            json.dump(result, f, indent=1, default=str)
        with (out_dir / f"{family}_flips.csv").open("w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["family", "arm", "key", "direction", "tier", "divergence_turn",
                 "divergence_kind", "position", "user_diverged_first", "hint_status",
                 "adoption", "base_funnel_last", "arm_funnel_last", "labels"]
            )
            for arm_name, arm_data in result["arms"].items():
                for c in arm_data["flip_cases"]:
                    writer.writerow(
                        [family, arm_name, c["key"], c["direction"], c["tier"],
                         c["divergence"]["turn_index"], c["divergence"]["kind"],
                         c["divergence"]["position"],
                         c["divergence"]["user_text_diverged_first"],
                         c["hint_status"], c["adoption"], c["base_funnel_last"],
                         c["arm_funnel_last"],
                         ";".join(c["labels"]) if c["labels"] else ""]
                    )
    (out_dir / "SUMMARY.md").write_text(render_summary_md(results), encoding="utf-8")


def render_summary_md(results: dict[str, dict]) -> str:
    """Cross-family markdown summary of the headline tables."""
    lines = [
        "# Hint-mechanism analysis — summary",
        "",
        "Generated by `python -m evaluation.hint_mechanism`. Machine-readable",
        "aggregates: `<family>_summary.json`; flip corpus: `<family>_flips.csv`.",
        "`user_accepted` is a keyword heuristic; all other stages/flags are",
        "deterministic. Weak family is smoke-scale (n=14) — directional only.",
        "",
    ]
    for family, result in results.items():
        lines.append(f"## Family: {family}")
        lines.append("")
        lines.append("| arm | paired n | lost | gained | divergence first/mid-late | user-diverged-first | turn-1 user text identical | mean hint chars (share) | mid-conv degenerate rate |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for arm_name, a in result["arms"].items():
            pos = a["divergence_positions"]
            acct = a["prompt_accounting"]
            mid = a["hint_trace"]["mid_conversation"]
            lines.append(
                f"| {arm_name} | {a['n_paired']} | {a['flip_counts']['lost']} "
                f"| {a['flip_counts']['gained']} "
                f"| {pos.get('first', 0)}/{pos.get('mid_late', 0)} "
                f"| {a['user_diverged_first_rate']} "
                f"| {a['turn1_user_text_identical_rate']} "
                f"| {acct['mean_hint_chars']} ({acct['mean_hint_share']}) "
                f"| {mid['degenerate_rate']} ({mid['degenerate']}/{mid['n_hinted_turns']}) |"
            )
        lines.append("")
        for arm_name, a in result["arms"].items():
            lines.append(f"### {family} / {arm_name}")
            lines.append("")
            lines.append("Hint correctness × adoption (cell: n, arm booked, baseline booked, lost, gained):")
            lines.append("")
            lines.append("| cell | n | arm booked | base booked | lost | gained |")
            lines.append("|---|---|---|---|---|---|")
            for cell, v in sorted(a["crosstab"].items()):
                lines.append(
                    f"| {cell} | {v['n']} | {v['arm_booked']} | {v['base_booked']} "
                    f"| {v['lost']} | {v['gained']} |"
                )
            lines.append("")
            f_n = a["funnel"]["n_reachable_pairs"]
            lines.append(f"Funnel (booking-reachable pairs, n={f_n}; baseline → arm):")
            lines.append("")
            lines.append("| stage | baseline | arm | Δ |")
            lines.append("|---|---|---|---|")
            for stage in _FUNNEL_STAGES:
                b = a["funnel"]["baseline"].get(stage, 0)
                m = a["funnel"]["arm"].get(stage, 0)
                lines.append(f"| {stage} | {b} | {m} | {m - b:+d} |")
            lines.append("")
            exp = a["exploration"]
            lines.append(
                f"First-query window span (base → arm): median "
                f"{exp['median_first_ca_span_h_base']}h → {exp['median_first_ca_span_h_arm']}h; "
                f"narrow (≤1 h) first queries "
                f"{exp['first_ca_narrow_1h_base']}/{exp['first_ca_n_base']} → "
                f"{exp['first_ca_narrow_1h_arm']}/{exp['first_ca_n_arm']}. "
                f"Cap-truncated (>3-day) scans {exp['cap_truncated_calls_base_total']} → "
                f"{exp['cap_truncated_calls_arm_total']} (conversations "
                f"{exp['convs_with_cap_truncation_base']} → {exp['convs_with_cap_truncation_arm']})."
            )
            lines.append(
                f"Exploration (paired, base → arm): distinct days queried mean "
                f"{exp['mean_distinct_days_queried_base']} → {exp['mean_distinct_days_queried_arm']} "
                f"(median {exp['median_distinct_days_queried_base']} → {exp['median_distinct_days_queried_arm']}); "
                f"availability calls mean {exp['mean_availability_calls_base']} → "
                f"{exp['mean_availability_calls_arm']} "
                f"(median {exp['median_availability_calls_base']} → {exp['median_availability_calls_arm']}); "
                f"dead-end turns {exp['mean_dead_end_turns_base']} → {exp['mean_dead_end_turns_arm']}; "
                f"midnight-start availability queries {exp['midnight_ca_calls_base_total']} → "
                f"{exp['midnight_ca_calls_arm_total']} "
                f"(conversations affected {exp['convs_with_midnight_ca_base']} → "
                f"{exp['convs_with_midnight_ca_arm']})."
            )
            lines.append("")
            lines.append(f"Taxonomy (scripted pass-1, lost flips): {a['taxonomy_counts']}")
            lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=["strong", "weak", "both"], default="both")
    parser.add_argument("--runs-dir", type=Path, default=_RUNS_DIR)
    parser.add_argument("--out-dir", type=Path, default=_OUT_DIR)
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    families = ["strong", "weak"] if args.family == "both" else [args.family]
    scenarios = load_scenarios()
    results = {fam: analyze_family(fam, args.runs_dir, scenarios) for fam in families}
    write_outputs(results, args.out_dir)
    for fam in families:
        runs = RUN_REGISTRY[fam]
        base_map = load_run(runs["baseline"], args.runs_dir)
        arm_names = [a for a in runs if a != "baseline"]
        digests = render_flip_digests(
            fam,
            results[fam],
            {a: base_map for a in arm_names},
            {a: load_run(runs[a], args.runs_dir) for a in arm_names},
        )
        (args.out_dir / f"{fam}_flip_digests.md").write_text(digests, encoding="utf-8")
    logger.info("Wrote %s for families: %s", args.out_dir, ", ".join(families))


if __name__ == "__main__":
    main()
