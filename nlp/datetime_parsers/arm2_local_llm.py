"""Arm 2 datetime parser — local LLM (NLP only) + shared ``dateparser`` resolution.

IMPROVEMENT_PLAN §7 Arm 2 + §9. The local model does **NLP only**: it detects
the temporal expression(s), classifies ``specificity``, and may **normalize** a
calque into a parseable surface form (lexical/format/relative rephrasing only,
e.g. "14 Uhr" → "14:00", "le 14 mars" → "14 March", "nächste Woche" →
"next week"). It **MUST NEVER compute a relative expression into an absolute
calendar date** — that *arithmetic* is delegated to the shared deterministic
resolver (``nlp.datetime_parsers.resolution.resolve_expression``, the same
``dateparser`` engine Arm 1 uses), with the protocol's ``now`` passed explicitly
as ``RELATIVE_BASE``. Holding the arithmetic constant across arms makes the
comparison about *recognition*, and structurally separates recognition errors
(model) from resolution errors (``dateparser``).

Elicitation is **GBNF-constrained inline tags, not JSON** (ARCHITECTURE
Decision Log): ``<dt><expr>NORMALIZED</expr><spec>SPEC</spec></dt>`` per
expression, or ``<none/>``. The output is normalised to the common ``DateRange``
contract so the format choice never leaks into the cross-arm comparison.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from nlp import local_llm
from nlp.datetime_parsers.resolution import (
    VALID_SPEC,
    reconcile_exact_time,
    resolve_expression,
)
from nlp.datetime_parsers.windows import (
    compute_end_datetime,
    is_flexible_for,
    snap_start,
)
from nlp.schemas import DateRange

# GBNF: the <none/> sentinel, or one-or-more <dt> blocks (≥2 = compound).
# `expr` is free temporal text that cannot contain "<" (so it can't break tags);
# `spec` is constrained to the four per-range specificity values.
GBNF_DATETIME = r"""
root ::= none | dt+
none ::= "<none/>"
dt ::= "<dt><expr>" expr "</expr><spec>" spec "</spec></dt>"
expr ::= [^<]+
spec ::= "exact_time" | "day_specific" | "day_vague" | "multi_day_vague"
"""

_SYSTEM = """You extract temporal expressions from a user's message to a Swiss bank appointment assistant.

For EACH temporal expression in the message, output exactly one block:
<dt><expr>NORMALIZED</expr><spec>SPECIFICITY</spec></dt>
If the message contains NO temporal expression, output exactly: <none/>
Output ONLY these tags — no other text, no explanations.

NORMALIZED is a clean, English, parseable rewrite of the expression:
- Convert clock formats: "14 Uhr" -> "14:00"; "2pm" -> "14:00"; "halb 3" -> "14:30".
- Convert written dates to day + month: "14.03" -> "14 March"; "le 14 mars" -> "14 March".
- Keep RELATIVE phrases relative: "morgen" -> "tomorrow"; "nächste Woche" -> "next week";
  "la semaine prochaine" -> "next week"; "next week Tuesday" -> "next Tuesday".
- You MAY pass through a date that is literally stated ("March 20th" -> "March 20th").
- NEVER compute a calendar date. Do NOT turn "next Tuesday" into a YYYY-MM-DD date.
  Resolving relative expressions to absolute dates happens downstream, not here.

SPECIFICITY is exactly one of:
- exact_time: an explicit clock time together with a day ("tomorrow at 14:00").
- day_specific: an absolute calendar date, no clock time ("14 March").
- day_vague: a relative day, no clock time ("tomorrow", "next Tuesday").
- multi_day_vague: a multi-day span, no clock time ("next week", "soon", "in a few days").

A date or day with NO clock time is NEVER exact_time. Use exact_time ONLY when an
explicit clock time (e.g. "14:00", "2pm", "noon") is present: "14 March" is
day_specific, "next Tuesday" is day_vague — not exact_time.

Examples:
User: I'd like to come in next Tuesday at 2pm.
<dt><expr>next Tuesday at 14:00</expr><spec>exact_time</spec></dt>
User: Können wir uns nächste Woche treffen?
<dt><expr>next week</expr><spec>multi_day_vague</spec></dt>
User: Geht der 14.03?
<dt><expr>14 March</expr><spec>day_specific</spec></dt>
User: Tuesday or Thursday works for me.
<dt><expr>Tuesday</expr><spec>day_vague</spec></dt><dt><expr>Thursday</expr><spec>day_vague</spec></dt>
User: I want to talk about my mortgage.
<none/>"""

_DT_RE = re.compile(
    r"<dt>\s*<expr>(.*?)</expr>\s*<spec>(.*?)</spec>\s*</dt>",
    re.DOTALL | re.IGNORECASE,
)


def parse_datetime_tags(raw: str, *, now: datetime) -> list[DateRange]:
    """Turn the model's tagged output into ``DateRange`` objects (deterministic).

    Pure string→object logic (plus shared ``dateparser`` resolution), unit-tested
    against mocked LLM strings. Edge handling: ``<none/>`` (no ``<dt>`` blocks) →
    ``[]``; an ``<expr>`` that ``dateparser`` cannot resolve → **skipped** (no
    wrong commit); an out-of-enum ``<spec>`` → skipped (defensive — GBNF prevents
    it in production); ≥2 ``<dt>`` → ≥2 ranges (annotate flags ``compound``).
    """
    ranges: list[DateRange] = []
    for expr_raw, spec_raw in _DT_RE.findall(raw or ""):
        expr = expr_raw.strip()
        spec = spec_raw.strip().lower()
        if not expr or spec not in VALID_SPEC:
            continue
        # Guard the model's self-reported spec: a date/day with no clock time
        # mislabelled ``exact_time`` would otherwise produce a midnight 1-hour
        # window (see resolution.reconcile_exact_time). Shared with Arm 3.
        spec = reconcile_exact_time(expr, spec)
        resolved = resolve_expression(expr, now=now)
        if resolved is None:
            continue
        start = snap_start(resolved, spec)  # type: ignore[arg-type]
        ranges.append(
            DateRange(
                start_datetime=start,
                end_datetime=compute_end_datetime(start, spec),  # type: ignore[arg-type]
                is_flexible=is_flexible_for(spec),  # type: ignore[arg-type]
                original_text=expr,
                specificity=spec,  # type: ignore[arg-type]
            )
        )
    return ranges


def _diagnose(raw: str, ranges: list[DateRange]) -> dict[str, Any]:
    """Per-call diagnostics for recognition-vs-resolution failure analysis.

    ``recognized`` = the ``<expr>`` values the model emitted (with a valid spec);
    ``resolved`` = those that ``dateparser`` resolved into a DateRange;
    ``unresolved`` = recognized but not resolved (a *resolution* failure). An
    empty ``recognized`` on a gold row that has a datetime is a *recognition*
    failure.
    """
    recognized = [
        e.strip()
        for e, s in _DT_RE.findall(raw or "")
        if e.strip() and s.strip().lower() in VALID_SPEC
    ]
    resolved = [r.original_text for r in ranges]
    unresolved = [e for e in recognized if e not in resolved]
    return {
        "raw": (raw or "").strip(),
        "recognized": recognized,
        "resolved": resolved,
        "unresolved": unresolved,
    }


class LocalLLMDatetimeParser:
    """Arm 2 datetime parser. Construct once per session and reuse.

    The model is loaded lazily on the first ``parse`` call (via
    ``nlp.local_llm``), not in ``__init__`` — so the factory can build this arm,
    and the unit tests can mock ``local_llm.generate``, without touching the
    native library or the GGUF.
    """

    arm_name: str = "local_llm"

    def __init__(self) -> None:
        self._last_diag: dict[str, Any] | None = None

    def parse(self, text: str, *, now: datetime) -> list[DateRange]:
        if not text or not text.strip():
            self._last_diag = {"raw": "", "recognized": [], "resolved": [], "unresolved": []}
            return []
        prompt = (
            f"Current date: {now:%A, %d %B %Y} (Europe/Zurich).\n\n"
            f"User message:\n{text}"
        )
        raw = local_llm.generate(prompt, GBNF_DATETIME, system=_SYSTEM, max_tokens=256)
        ranges = parse_datetime_tags(raw, now=now)
        self._last_diag = _diagnose(raw, ranges)
        return ranges

    def last_diagnostics(self) -> dict[str, Any] | None:
        """Most recent ``parse`` call's raw output + recognized/resolved/unresolved.

        Lets the intrinsic eval separate a *recognition* failure (model emitted
        ``<none/>`` — nothing recognized) from a *resolution* failure (an
        ``<expr>`` was recognized but ``dateparser`` could not resolve it).
        Arm-specific; the eval reads it duck-typed and falls back gracefully for
        arms that do not expose it (e.g. Arm 1).
        """
        return self._last_diag
