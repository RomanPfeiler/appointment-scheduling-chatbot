"""Deterministic KPI computation from ConversationRecord.

Step 4 of EVALUATION_FRAMEWORK.md Section 12. Provides five public functions
consumed by the runner (Step 3) after each scenario run:

    grounding = extract_grounding_facts(record)
    record.grounding_facts = grounding
    derived = compute_derived_metrics(record, scenario)  # reads record.grounding_facts
    record.derived = derived
    write_record(paths, record, ...)                      # overwrite with enriched record

After all scenarios in a run:

    summary = compute_run_summary(all_records, scenarios_by_id)
    write_run_summary(run_paths, summary)
    row = build_kpi_row(manifest, summary)
    kpi_history.append_row(row)

Grounding normalization approach (resolves EVALUATION_FRAMEWORK.md §14 TODO):
- Topics: case-insensitive substring match of known topic_names in agent text.
- Media: same for contact_medium_names.
- Slots: ISO datetime regex (primary), dateparser fallback (secondary).
  Match with ±5-minute tolerance against prior check_availability responses.
- Bookings: booking_id string presence in agent text.
Knowledge is cumulative across turns (tool calls within turn N feed turn N's
agent_response check and all subsequent turns).
"""

from __future__ import annotations

import dataclasses
import logging
import re
import statistics
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from evaluation.schemas import (
    ConversationRecord,
    DerivedMetrics,
    GroundingFact,
    KPIHistoryRow,
    RunManifest,
    Scenario,
    ToolCallRecord,
)
from evaluation.storage import RunPaths, atomic_write_text, write_json

logger = logging.getLogger(__name__)

_ZURICH = ZoneInfo("Europe/Zurich")

# ISO datetime pattern: 2026-05-24T09:00 (with or without seconds / offset)
_ISO_DT_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}")
# Loose time pattern for slot-count fallback: 9:00, 14:00, 9:00 AM, 2:30 PM
_TIME_RE = re.compile(r"\b\d{1,2}:\d{2}(?:\s*(?:am|pm))?\b", re.IGNORECASE)

_SLOT_TOLERANCE_MINUTES: float = 5.0
_PARSE_ACCURACY_TIME_TOLERANCE_MINUTES: float = 30.0


# ---------------------------------------------------------------------------
# Internal knowledge accumulator
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class _KnowledgeSet:
    topics: set[str] = dataclasses.field(default_factory=set)
    media: set[str] = dataclasses.field(default_factory=set)
    slots: list[datetime] = dataclasses.field(default_factory=list)
    booking_id: str | None = None
    booking_datetimes: list[datetime] = dataclasses.field(default_factory=list)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _resolve_offset(offset_str: str, base_date: date) -> datetime:
    """Parse "today+NTH:MM" to a tz-aware datetime in Europe/Zurich.

    Args:
        offset_str: e.g. "today+2T09:00" or "today+0T17:00".
        base_date: Reference date (typically record.timestamp_start.date()).

    Raises:
        ValueError: If the format is malformed.
    """
    prefix = "today+"
    if not offset_str.startswith(prefix):
        raise ValueError(f"Expected 'today+N...' format, got: {offset_str!r}")
    rest = offset_str[len(prefix):]
    if "T" not in rest:
        raise ValueError(f"Missing 'T' time separator in: {offset_str!r}")
    day_part, time_part = rest.split("T", 1)
    try:
        day_offset = int(day_part)
    except ValueError:
        raise ValueError(f"Day offset not an integer in: {offset_str!r}") from None
    if ":" not in time_part:
        raise ValueError(f"Time part missing ':' in: {offset_str!r}")
    h_str, m_str = time_part.split(":", 1)
    try:
        hour, minute = int(h_str), int(m_str)
    except ValueError:
        raise ValueError(f"Time part not valid integers in: {offset_str!r}") from None
    target = base_date + timedelta(days=day_offset)
    return datetime(target.year, target.month, target.day, hour, minute, tzinfo=_ZURICH)


def _score_parse_accuracy(
    actual_start: datetime,
    actual_end: datetime,  # kept for potential future end-time scoring
    expected_start: datetime,
    expected_end: datetime,
) -> float:
    """Return 1.0 / 0.5 / 0.0 per EVALUATION_FRAMEWORK.md §4f.

    1.0 — dates match AND |actual_start − expected_start| ≤ 30 min.
    0.5 — dates match, times differ beyond tolerance.
    0.0 — dates don't match.
    """
    if actual_start.date() != expected_start.date():
        return 0.0
    delta_min = abs((actual_start - expected_start).total_seconds()) / 60.0
    return 1.0 if delta_min <= _PARSE_ACCURACY_TIME_TOLERANCE_MINUTES else 0.5


def _count_slots_in_text(text: str | None) -> int:
    """Count distinct slot mentions in agent response text.

    Primary: ISO datetime regex. Fallback: H:MM pattern when ISO finds nothing.
    Returns 0 for None / empty text.
    """
    if not text:
        return 0
    iso_matches = _ISO_DT_RE.findall(text)
    if iso_matches:
        return len(set(iso_matches))
    time_matches = _TIME_RE.findall(text)
    return len({m.lower().strip() for m in time_matches})


def _parse_dt_safe(iso_str: str) -> datetime | None:
    """Parse an ISO 8601 string; return None on any failure."""
    if not iso_str:
        return None
    try:
        dt = datetime.fromisoformat(iso_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=_ZURICH)
        return dt
    except (TypeError, ValueError):
        return None


def _slot_matches_known(candidate: datetime, known_slots: list[datetime]) -> bool:
    """Return True if candidate is within ±SLOT_TOLERANCE_MINUTES of any known slot."""
    for known in known_slots:
        try:
            diff_min = abs((candidate - known).total_seconds()) / 60.0
            if diff_min <= _SLOT_TOLERANCE_MINUTES:
                return True
        except TypeError:
            continue
    return False


def _collect_tool_knowledge(
    tool_calls: list[ToolCallRecord], cumulative: _KnowledgeSet
) -> None:
    """Mutate cumulative knowledge set with facts from these tool calls."""
    for tc in tool_calls:
        name = tc.tool_name
        resp = tc.response

        if name == "get_appointment_topics":
            items = resp if isinstance(resp, list) else [resp] if isinstance(resp, dict) else []
            for item in items:
                if isinstance(item, dict) and "topic_name" in item:
                    cumulative.topics.add(str(item["topic_name"]).lower())

        elif name == "get_appointment_contact_medium":
            items = resp if isinstance(resp, list) else [resp] if isinstance(resp, dict) else []
            for item in items:
                if isinstance(item, dict) and "contact_medium_name" in item:
                    cumulative.media.add(str(item["contact_medium_name"]).lower())

        elif name == "check_availability":
            items = resp if isinstance(resp, list) else [resp] if isinstance(resp, dict) else []
            for item in items:
                if not isinstance(item, dict):
                    continue
                for key in ("datetime_start", "datetime_end"):
                    dt = _parse_dt_safe(str(item.get(key, "")))
                    if dt is not None:
                        cumulative.slots.append(dt)

        elif name == "book_appointment":
            if isinstance(resp, dict) and resp.get("status") == "success":
                cumulative.booking_id = resp.get("booking_id")
                details = resp.get("details") or {}
                if isinstance(details, dict):
                    for key in ("datetime_start", "datetime_end"):
                        dt = _parse_dt_safe(str(details.get(key, "")))
                        if dt is not None:
                            cumulative.booking_datetimes.append(dt)


def _extract_topic_facts(
    agent_text: str, known: _KnowledgeSet, turn_index: int
) -> list[GroundingFact]:
    text_lower = agent_text.lower()
    return [
        GroundingFact(
            fact_type="topic",
            asserted_value=name,
            asserted_in_turn=turn_index,
            supported=True,
            notes="case-insensitive substring match against get_appointment_topics response",
        )
        for name in known.topics
        if name in text_lower
    ]


def _extract_medium_facts(
    agent_text: str, known: _KnowledgeSet, turn_index: int
) -> list[GroundingFact]:
    text_lower = agent_text.lower()
    return [
        GroundingFact(
            fact_type="medium",
            asserted_value=name,
            asserted_in_turn=turn_index,
            supported=True,
            notes="case-insensitive substring match against get_appointment_contact_medium response",
        )
        for name in known.media
        if name in text_lower
    ]


def _extract_slot_facts(
    agent_text: str, known: _KnowledgeSet, turn_index: int
) -> list[GroundingFact]:
    facts: list[GroundingFact] = []
    seen: set[str] = set()

    iso_matches = _ISO_DT_RE.findall(agent_text)
    for iso_str in iso_matches:
        if iso_str in seen:
            continue
        seen.add(iso_str)
        candidate = _parse_dt_safe(iso_str)
        if candidate is None:
            continue
        supported = _slot_matches_known(candidate, known.slots)
        facts.append(GroundingFact(
            fact_type="slot",
            asserted_value=iso_str,
            asserted_in_turn=turn_index,
            supported=supported,
            notes=(
                "ISO datetime matched within ±5 min of prior check_availability response"
                if supported
                else "ISO datetime not found in prior check_availability responses"
            ),
        ))

    # Fallback: dateparser per sentence — only when ISO extraction found nothing
    # and the knowledge set has at least one known slot to match against.
    if not iso_matches and known.slots:
        try:
            import dateparser  # already in requirements.txt
            for sentence in re.split(r"[.!?\n]", agent_text):
                if not re.search(r"\d", sentence):
                    continue
                result = dateparser.parse(
                    sentence,
                    settings={
                        "PREFER_DAY_OF_MONTH": "first",
                        "RETURN_AS_TIMEZONE_AWARE": True,
                        "TIMEZONE": "Europe/Zurich",
                        "RETURN_TIME_AS_PERIOD": False,
                    },
                )
                if result is None:
                    continue
                key = result.isoformat()[:16]
                if key in seen:
                    continue
                seen.add(key)
                supported = _slot_matches_known(result, known.slots)
                facts.append(GroundingFact(
                    fact_type="slot",
                    asserted_value=key,
                    asserted_in_turn=turn_index,
                    supported=supported,
                    notes=(
                        "dateparser fallback matched within ±5 min"
                        if supported
                        else "dateparser fallback slot not in prior check_availability responses"
                    ),
                ))
        except ImportError:
            logger.debug("dateparser not available; slot fallback skipped for turn %d", turn_index)

    return facts


def _extract_booking_facts(
    agent_text: str, known: _KnowledgeSet, turn_index: int
) -> list[GroundingFact]:
    if known.booking_id and known.booking_id in agent_text:
        return [GroundingFact(
            fact_type="booking",
            asserted_value=known.booking_id,
            asserted_in_turn=turn_index,
            supported=True,
            notes="booking_id from book_appointment success response",
        )]
    return []


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def extract_grounding_facts(record: ConversationRecord) -> list[GroundingFact]:
    """Extract and check all concrete facts the agent asserted across all turns.

    Knowledge is cumulative: tool responses in turn N become known facts that
    can be checked against the agent_response of turn N (tool calls happen
    before the response within a turn) and all subsequent turns.

    Returns [] for records with no turns.
    """
    if not record.turns:
        return []

    known = _KnowledgeSet()
    all_facts: list[GroundingFact] = []

    for turn in sorted(record.turns, key=lambda t: t.turn_index):
        # Update knowledge from this turn's tool calls first (they precede the response).
        _collect_tool_knowledge(turn.tool_calls, known)

        agent_text = turn.agent_response
        if not agent_text:
            continue

        all_facts.extend(_extract_topic_facts(agent_text, known, turn.turn_index))
        all_facts.extend(_extract_medium_facts(agent_text, known, turn.turn_index))
        all_facts.extend(_extract_slot_facts(agent_text, known, turn.turn_index))
        all_facts.extend(_extract_booking_facts(agent_text, known, turn.turn_index))

    return all_facts


def _is_empty_availability_response(response: object) -> bool:
    """Return True if a `check_availability` response carries zero slots.

    The mock server returns:
      - ``[]`` when there are no slots in the queried window
      - a single ``{"datetime_start": ..., "datetime_end": ...}`` dict for one slot
      - a list of such dicts for multiple slots
      - ``{"status": "error", ...}`` on errors (these are NOT dead-ends — the
        agent never got the chance to surface anything to the user)
    """
    if isinstance(response, list):
        return len(response) == 0
    if isinstance(response, dict):
        # Error responses aren't "no availability"; they're "tool refused to run".
        if response.get("status") == "error":
            return False
        # A single-slot dict has datetime_start/end — that's NOT empty.
        return not response  # empty dict {} -> True; populated -> False
    # Unexpected payload — treat as not-empty so we don't false-flag dead-ends.
    return False


def compute_derived_metrics(record: ConversationRecord, scenario: Scenario) -> DerivedMetrics:
    """Compute the full DerivedMetrics for a finalized ConversationRecord.

    Re-derives all basic counts from the raw turns (does not trust the
    recorder's lightweight pass) and adds parse_accuracy_score,
    efficiency_ratio, slots_presented_per_turn, dead_end_turn_count,
    and grounding counts.

    Call extract_grounding_facts() and attach the result to
    record.grounding_facts BEFORE calling this function so that
    unsupported_facts_count and faithful are populated correctly.
    """
    # Step A: basic counts
    total_mcp_calls = 0
    availability_calls = 0
    first_check_params: dict | None = None
    booked = False
    total_sim_latency = 0.0
    total_actual_latency = 0.0
    dead_end_turn_count = 0

    for turn in record.turns:
        # Did THIS turn issue a check_availability that returned no slots?
        # A "dead-end" turn is one where the agent both got [] from the tool
        # AND surfaced 0 slots in its text response (§4h). These are the
        # turns customers experience as "Sorry, nothing available" walls.
        turn_had_empty_availability = any(
            tc.tool_name == "check_availability"
            and tc.success
            and _is_empty_availability_response(tc.response)
            for tc in turn.tool_calls
        )
        if turn_had_empty_availability and _count_slots_in_text(turn.agent_response) == 0:
            dead_end_turn_count += 1

        for tc in turn.tool_calls:
            total_mcp_calls += 1
            if tc.simulated_latency_ms is not None:
                total_sim_latency += tc.simulated_latency_ms
            if tc.actual_latency_ms is not None:
                total_actual_latency += tc.actual_latency_ms
            if tc.tool_name == "check_availability":
                availability_calls += 1
                if first_check_params is None:
                    first_check_params = dict(tc.parameters) if tc.parameters else {}
            if tc.tool_name == "book_appointment" and tc.success:
                if isinstance(tc.response, dict) and tc.response.get("status") == "success":
                    booked = True

    # Step B: parse accuracy (§4f)
    parse_accuracy: float | None = None
    if scenario.expected_datetime_window is not None and first_check_params is not None:
        # Resolve the expected window against the scenario's PINNED reference_date
        # — the same clock the agent was given — not the run's wall-clock
        # timestamp. Using timestamp_start would re-introduce the date-drift the
        # fix removes (EVALUATION_FRAMEWORK §3a).
        base_date = scenario.reference_date
        try:
            exp_start = _resolve_offset(
                scenario.expected_datetime_window.start_offset, base_date
            )
            exp_end = _resolve_offset(
                scenario.expected_datetime_window.end_offset, base_date
            )
            act_start = _parse_dt_safe(str(first_check_params.get("start_datetime", "")))
            act_end = _parse_dt_safe(str(first_check_params.get("end_datetime", "")))
            if act_start is not None and act_end is not None:
                parse_accuracy = _score_parse_accuracy(act_start, act_end, exp_start, exp_end)
            else:
                logger.debug(
                    "parse_accuracy: unparseable datetimes in first check_availability "
                    "params for scenario %s",
                    scenario.scenario_id,
                )
        except ValueError as exc:
            logger.debug(
                "parse_accuracy: offset resolution failed for %s: %s",
                scenario.scenario_id,
                exc,
            )

    # Step C: efficiency ratio (§4e). Undefined when the scenario has no optimal
    # availability calls (Tier 7 refusal scenarios: optimal == 0) — guard against
    # the division so enrichment never crashes on a T7 record that nonetheless
    # made availability calls.
    efficiency_ratio: float | None = None
    if availability_calls > 0 and scenario.optimal_availability_calls > 0:
        efficiency_ratio = availability_calls / scenario.optimal_availability_calls

    # Step D: slot presentation per turn (§4g)
    slots_per_turn = [
        _count_slots_in_text(turn.agent_response)
        for turn in sorted(record.turns, key=lambda t: t.turn_index)
    ]

    # Step E: grounding counts from pre-attached facts
    unsupported = sum(1 for f in record.grounding_facts if not f.supported)
    faithful = unsupported == 0

    return DerivedMetrics(
        total_turn_count=len(record.turns),
        total_mcp_calls=total_mcp_calls,
        availability_calls=availability_calls,
        first_check_availability_params=first_check_params,
        booked=booked,
        total_simulated_latency_ms=total_sim_latency,
        total_actual_latency_ms=total_actual_latency,
        parse_accuracy_score=parse_accuracy,
        unsupported_facts_count=unsupported,
        faithful=faithful,
        slots_presented_per_turn=slots_per_turn,
        efficiency_ratio=efficiency_ratio,
        optimal_availability_calls=scenario.optimal_availability_calls,
        dead_end_turn_count=dead_end_turn_count,
    )


# ---------------------------------------------------------------------------
# Run-level aggregation
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class PerTierStats:
    """Per-tier KPI aggregates for a single evaluation run."""

    tier: int | str
    scenario_count: int
    booking_completion_rate: float | None
    median_turns: float | None
    median_efficiency_ratio: float | None
    faithful_rate: float | None
    mean_parse_accuracy: float | None
    mean_simulated_latency_ms: float | None
    # §4h: per-tier mean of `dead_end_turn_count` (turns where check_availability
    # returned [] and the agent surfaced 0 slots). Higher = more customer-frustration.
    mean_dead_end_turns: float | None = None


@dataclasses.dataclass
class RunSummary:
    """Aggregated KPIs for a completed evaluation run, written to summary.json/md."""

    run_id: str
    stage: str
    git_commit: str
    change_note: str | None
    timestamp: str  # ISO 8601 UTC
    scenario_count: int
    record_count: int
    # Headline KPIs
    booking_completion_rate: float | None
    median_turns: float | None
    median_efficiency_ratio: float | None
    faithful_rate: float | None
    mean_total_simulated_latency_ms: float | None
    mean_parse_accuracy: float | None
    # Distributions for box/violin plots in the report
    turn_counts: list[int]
    efficiency_ratios: list[float]
    simulated_latencies_ms: list[float]
    parse_accuracy_scores: list[float]
    slots_presented_flat: list[int]
    # Per-tier breakdown
    per_tier: list[PerTierStats]
    # Faithfulness
    unsupported_facts_total: int
    faithful_count: int
    unfaithful_count: int
    # §4h: aggregate dead-end turn counts across the run.
    dead_end_turns_total: int = 0
    mean_dead_end_turns: float | None = None


def _safe_median(values: list) -> float | None:
    xs = [v for v in values if v is not None]
    return statistics.median(xs) if xs else None


def _safe_mean(values: list) -> float | None:
    xs = [v for v in values if v is not None]
    return statistics.mean(xs) if xs else None


def _tier_stats(records: list[ConversationRecord], tier: int | str) -> PerTierStats:
    tier_recs = [r for r in records if r.tier == tier]
    n = len(tier_recs)
    if not n:
        return PerTierStats(
            tier=tier, scenario_count=0,
            booking_completion_rate=None, median_turns=None,
            median_efficiency_ratio=None, faithful_rate=None,
            mean_parse_accuracy=None, mean_simulated_latency_ms=None,
            mean_dead_end_turns=None,
        )
    booked = sum(1 for r in tier_recs if r.derived and r.derived.booked)
    faithful = sum(1 for r in tier_recs if r.derived and r.derived.faithful)
    return PerTierStats(
        tier=tier,
        scenario_count=n,
        booking_completion_rate=booked / n,
        median_turns=_safe_median(
            [r.derived.total_turn_count for r in tier_recs if r.derived]
        ),
        median_efficiency_ratio=_safe_median(
            [r.derived.efficiency_ratio for r in tier_recs if r.derived]
        ),
        faithful_rate=faithful / n,
        mean_parse_accuracy=_safe_mean(
            [r.derived.parse_accuracy_score for r in tier_recs if r.derived]
        ),
        mean_simulated_latency_ms=_safe_mean(
            [r.derived.total_simulated_latency_ms for r in tier_recs if r.derived]
        ),
        mean_dead_end_turns=_safe_mean(
            [r.derived.dead_end_turn_count for r in tier_recs if r.derived]
        ),
    )


def compute_run_summary(
    all_records: list[ConversationRecord],
    scenarios_by_id: dict[str, Scenario],
) -> RunSummary:
    """Aggregate per-record metrics into run-level summary statistics.

    Args:
        all_records: All ConversationRecords from the run (enriched with derived + grounding).
        scenarios_by_id: Mapping scenario_id → Scenario; its length sets scenario_count.
    """
    n = len(all_records)
    if n == 0:
        return RunSummary(
            run_id="", stage="", git_commit="", change_note=None,
            timestamp=datetime.utcnow().isoformat() + "Z",
            scenario_count=len(scenarios_by_id), record_count=0,
            booking_completion_rate=None, median_turns=None,
            median_efficiency_ratio=None, faithful_rate=None,
            mean_total_simulated_latency_ms=None, mean_parse_accuracy=None,
            turn_counts=[], efficiency_ratios=[], simulated_latencies_ms=[],
            parse_accuracy_scores=[], slots_presented_flat=[],
            per_tier=[], unsupported_facts_total=0, faithful_count=0, unfaithful_count=0,
            dead_end_turns_total=0, mean_dead_end_turns=None,
        )

    first = all_records[0]
    booked_count = sum(1 for r in all_records if r.derived and r.derived.booked)
    faithful_count = sum(1 for r in all_records if r.derived and r.derived.faithful)
    unsupported_total = sum(
        r.derived.unsupported_facts_count for r in all_records if r.derived
    )

    turn_counts = [r.derived.total_turn_count for r in all_records if r.derived]
    eff_ratios = [
        r.derived.efficiency_ratio
        for r in all_records
        if r.derived and r.derived.efficiency_ratio is not None
    ]
    latencies = [r.derived.total_simulated_latency_ms for r in all_records if r.derived]
    parse_scores = [
        r.derived.parse_accuracy_score
        for r in all_records
        if r.derived and r.derived.parse_accuracy_score is not None
    ]
    slots_flat = [
        s for r in all_records if r.derived for s in r.derived.slots_presented_per_turn
    ]
    dead_end_counts = [r.derived.dead_end_turn_count for r in all_records if r.derived]

    tiers = sorted({r.tier for r in all_records}, key=lambda t: (isinstance(t, str), t))
    per_tier = [_tier_stats(all_records, tier) for tier in tiers]

    return RunSummary(
        run_id=first.run_id,
        stage=first.stage,
        git_commit=first.git_commit,
        change_note=first.change_note,
        timestamp=datetime.utcnow().isoformat() + "Z",
        scenario_count=len(scenarios_by_id),
        record_count=n,
        booking_completion_rate=booked_count / n,
        median_turns=_safe_median(turn_counts),
        median_efficiency_ratio=_safe_median(eff_ratios),
        faithful_rate=faithful_count / n,
        mean_total_simulated_latency_ms=_safe_mean(latencies),
        mean_parse_accuracy=_safe_mean(parse_scores),
        turn_counts=turn_counts,
        efficiency_ratios=eff_ratios,
        simulated_latencies_ms=latencies,
        parse_accuracy_scores=parse_scores,
        slots_presented_flat=slots_flat,
        per_tier=per_tier,
        unsupported_facts_total=unsupported_total,
        faithful_count=faithful_count,
        unfaithful_count=n - faithful_count,
        dead_end_turns_total=sum(dead_end_counts),
        mean_dead_end_turns=_safe_mean(dead_end_counts),
    )


def write_run_summary(run_paths: RunPaths, summary: RunSummary) -> tuple[Path, Path]:
    """Write summary.json and summary.md to run_paths.metrics_dir atomically.

    Returns:
        Tuple of (json_path, md_path).
    """
    run_paths.metrics_dir.mkdir(parents=True, exist_ok=True)
    json_path = run_paths.metrics_dir / "summary.json"
    md_path = run_paths.metrics_dir / "summary.md"
    write_json(json_path, dataclasses.asdict(summary))
    atomic_write_text(md_path, _render_summary_md(summary))
    return json_path, md_path


def build_kpi_row(manifest: RunManifest, summary: RunSummary) -> KPIHistoryRow:
    """Build a KPIHistoryRow from manifest + summary. Judge fields left None."""
    return KPIHistoryRow(
        run_id=manifest.run_id,
        stage=manifest.stage,
        timestamp=manifest.timestamp_start,
        git_commit=manifest.git_commit,
        change_note=manifest.change_note,
        scenario_count=summary.scenario_count,
        rep_count=manifest.rep_count,
        booking_completion_rate=summary.booking_completion_rate,
        median_turns=summary.median_turns,
        median_efficiency_ratio=summary.median_efficiency_ratio,
        faithful_rate=summary.faithful_rate,
        mean_total_simulated_latency_ms=summary.mean_total_simulated_latency_ms,
        dead_end_turns_total=summary.dead_end_turns_total,
    )


# ---------------------------------------------------------------------------
# Markdown renderer (private)
# ---------------------------------------------------------------------------


def _pct(v: float | None) -> str:
    return f"{v * 100:.1f}%" if v is not None else "—"


def _fmt(v: float | None, decimals: int = 2) -> str:
    return f"{v:.{decimals}f}" if v is not None else "—"


def _render_summary_md(s: RunSummary) -> str:
    note = s.change_note or "—"
    lines = [
        f"# KPI Summary — {s.run_id}",
        "",
        f"**Stage:** {s.stage}  **Commit:** `{s.git_commit}`  **Note:** {note}",
        "",
        f"Generated: {s.timestamp}  ·  {s.scenario_count} scenarios  ·  {s.record_count} records",
        "",
        "## Headline KPIs",
        "",
        "| KPI | Value |",
        "|-----|-------|",
        f"| Booking completion rate | {_pct(s.booking_completion_rate)} |",
        f"| Median turns | {_fmt(s.median_turns)} |",
        f"| Median efficiency ratio | {_fmt(s.median_efficiency_ratio)} |",
        f"| Faithful rate | {_pct(s.faithful_rate)} |",
        f"| Mean simulated latency (ms) | {_fmt(s.mean_total_simulated_latency_ms, 1)} |",
        f"| Mean parse accuracy | {_fmt(s.mean_parse_accuracy)} |",
        f"| Dead-end turns total | {s.dead_end_turns_total} |",
        f"| Mean dead-end turns / conversation | {_fmt(s.mean_dead_end_turns)} |",
        "",
        "## Per-Tier Breakdown",
        "",
        "| Tier | Records | Booking % | Median turns | Median eff. ratio | Faithful % | Mean parse acc. | Mean dead-ends |",
        "|------|---------|-----------|--------------|-------------------|------------|-----------------|----------------|",
    ]
    for ts in s.per_tier:
        lines.append(
            f"| {ts.tier} | {ts.scenario_count} | {_pct(ts.booking_completion_rate)} "
            f"| {_fmt(ts.median_turns)} | {_fmt(ts.median_efficiency_ratio)} "
            f"| {_pct(ts.faithful_rate)} | {_fmt(ts.mean_parse_accuracy)} "
            f"| {_fmt(ts.mean_dead_end_turns)} |"
        )

    faithful_total = s.faithful_count + s.unfaithful_count
    lines += [
        "",
        "## Faithfulness",
        "",
        f"- Faithful conversations: {s.faithful_count}/{faithful_total} ({_pct(s.faithful_rate)})",
        f"- Total unsupported facts: {s.unsupported_facts_total}",
        "",
        "## Slot Presentation Distribution",
        "",
    ]
    for label, pred in [
        ("0 slots (failure)", lambda x: x == 0),
        ("1 slot (poor)", lambda x: x == 1),
        ("2–3 slots (acceptable)", lambda x: 2 <= x <= 3),
        ("3–5 slots (good)", lambda x: 3 <= x <= 5),
        ("6+ slots (overwhelming)", lambda x: x >= 6),
    ]:
        count = sum(1 for v in s.slots_presented_flat if pred(v))
        lines.append(f"- {label}: {count} turns")

    return "\n".join(lines) + "\n"


__all__ = [
    "PerTierStats",
    "RunSummary",
    "build_kpi_row",
    "compute_derived_metrics",
    "compute_run_summary",
    "extract_grounding_facts",
    "write_run_summary",
]
