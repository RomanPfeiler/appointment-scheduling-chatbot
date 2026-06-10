"""Evaluation framework package.

Step 6 of the architecture, designed in ``architecture/EVALUATION_FRAMEWORK.md``.
Public surface for the conversation-record and metrics subsystems:

- :class:`ConversationRecord`, :class:`RunManifest`, :class:`RunConfig`,
  :class:`TurnRecord`, :class:`ToolCallRecord`, :class:`LLMCallRecord`,
  :class:`DerivedMetrics`, :class:`JudgeScoreSet`, :class:`KPIHistoryRow`,
  :class:`LatencyModel` — all in :mod:`evaluation.schemas`.
- :class:`ConversationRecorder` — runtime API for both the runner and the
  always-on Chainlit ad-hoc hook, in :mod:`evaluation.recorder`.
- :func:`render` — markdown transcript renderer, in
  :mod:`evaluation.transcript`.
- Metrics functions (Step 4) in :mod:`evaluation.metrics`.
- Storage helpers in :mod:`evaluation.storage`.
"""

from evaluation.judge import JudgeError, JudgeRunner, JudgeSummary, ScenarioJudge
from evaluation.metrics import (
    RunSummary,
    PerTierStats,
    build_kpi_row,
    compute_derived_metrics,
    compute_run_summary,
    extract_grounding_facts,
    write_run_summary,
)
from evaluation.recorder import ConversationRecorder
from evaluation.runner import enrich_record
from evaluation.schemas import (
    DEFAULT_LATENCY_MODEL,
    SCHEMA_VERSION,
    ConversationRecord,
    DerivedMetrics,
    GroundingFact,
    JudgeScoreSet,
    KPIHistoryRow,
    LatencyModel,
    LLMCallRecord,
    RunConfig,
    RunManifest,
    ToolCallRecord,
    TurnRecord,
)

__all__ = [
    "SCHEMA_VERSION",
    "DEFAULT_LATENCY_MODEL",
    # schemas
    "ConversationRecord",
    "DerivedMetrics",
    "GroundingFact",
    "JudgeScoreSet",
    "KPIHistoryRow",
    "LatencyModel",
    "LLMCallRecord",
    "RunConfig",
    "RunManifest",
    "ToolCallRecord",
    "TurnRecord",
    # recorder
    "ConversationRecorder",
    # metrics (Step 4)
    "PerTierStats",
    "RunSummary",
    "build_kpi_row",
    "compute_derived_metrics",
    "compute_run_summary",
    "extract_grounding_facts",
    "write_run_summary",
    # runner (Step 5)
    "enrich_record",
    # judge (Step 6)
    "JudgeError",
    "JudgeRunner",
    "JudgeSummary",
    "ScenarioJudge",
]
