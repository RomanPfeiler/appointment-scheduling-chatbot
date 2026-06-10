"""Arm 3 datetime parser — Gemini JSON mode (NLP only) + shared resolver.

IMPROVEMENT_PLAN §7 Arm 3. Like Arm 2, the model does **NLP only**: it detects the
temporal expression(s), classifies ``specificity``, and may **normalize** a calque
into a parseable surface form ("14 Uhr" → "14:00", "next week Tuesday" →
"next Tuesday"). It **MUST NEVER compute a relative expression into an absolute
calendar date** — that *arithmetic* is delegated to the **shared deterministic
resolver** (``nlp.datetime_parsers.resolution.resolve_expression``, the same
``dateparser`` engine Arms 1 & 2 use), with the protocol's ``now`` passed
explicitly as ``RELATIVE_BASE``. Holding the arithmetic constant across all three
arms makes the comparison about *recognition*.

Elicitation is **Gemini JSON mode** (``response_mime_type="application/json"`` + a
JSON-Schema ``response_schema``), not Arm 2's GBNF inline tags — the two LLM arms
differ in elicitation *format* by design, but both normalise to the identical
``DateRange`` contract, so the format choice never leaks into the cross-arm
comparison (ARCHITECTURE Decision Log).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from nlp import api_llm
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

# JSON-Schema constraining the model to a list of {expr, specificity} objects —
# the JSON equivalent of Arm 2's ``<dt><expr>…</expr><spec>…</spec></dt>``. The
# model emits the expression + specificity ONLY; it must not emit a resolved date.
_DT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "expressions": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "expr": {"type": "string"},
                    "specificity": {
                        "type": "string",
                        "enum": [
                            "exact_time",
                            "day_specific",
                            "day_vague",
                            "multi_day_vague",
                        ],
                    },
                },
                "required": ["expr", "specificity"],
            },
        }
    },
    "required": ["expressions"],
}

# Same recognition/normalization brief as Arm 2 ([arm2_local_llm._SYSTEM]),
# reworded for JSON output — the bright line against computing relative dates is
# preserved so the model never reintroduces date drift.
_SYSTEM = """You extract temporal expressions from a user's message to a Swiss bank appointment assistant.

Return JSON matching the schema: an "expressions" array with one object per temporal
expression in the message. Each object has:
- "expr": a clean, English, parseable rewrite of the expression.
- "specificity": exactly one of the four values below.

If the message contains NO temporal expression, return {"expressions": []}.

"expr" normalization rules:
- Convert clock formats: "14 Uhr" -> "14:00"; "2pm" -> "14:00"; "halb 3" -> "14:30".
- Convert written dates to day + month: "14.03" -> "14 March"; "le 14 mars" -> "14 March".
- Keep RELATIVE phrases relative: "morgen" -> "tomorrow"; "nächste Woche" -> "next week";
  "la semaine prochaine" -> "next week"; "next week Tuesday" -> "next Tuesday".
- You MAY pass through a date that is literally stated ("March 20th" -> "March 20th").
- NEVER compute a calendar date. Do NOT turn "next Tuesday" into a YYYY-MM-DD date.
  Resolving relative expressions to absolute dates happens downstream, not here.

"specificity" is exactly one of:
- exact_time: an explicit clock time together with a day ("tomorrow at 14:00").
- day_specific: an absolute calendar date, no clock time ("14 March").
- day_vague: a relative day, no clock time ("tomorrow", "next Tuesday").
- multi_day_vague: a multi-day span, no clock time ("next week", "soon", "in a few days").

A date or day with NO clock time is NEVER exact_time. Use exact_time ONLY when an
explicit clock time (e.g. "14:00", "2pm", "noon") is present: "14 March" is
day_specific, "next Tuesday" is day_vague — not exact_time.

Examples:
"I'd like to come in next Tuesday at 2pm." -> {"expressions": [{"expr": "next Tuesday at 14:00", "specificity": "exact_time"}]}
"Können wir uns nächste Woche treffen?" -> {"expressions": [{"expr": "next week", "specificity": "multi_day_vague"}]}
"Geht der 14.03?" -> {"expressions": [{"expr": "14 March", "specificity": "day_specific"}]}
"Tuesday or Thursday works for me." -> {"expressions": [{"expr": "Tuesday", "specificity": "day_vague"}, {"expr": "Thursday", "specificity": "day_vague"}]}
"I want to talk about my mortgage." -> {"expressions": []}"""


def build_ranges(expressions: list[dict[str, Any]], *, now: datetime) -> list[DateRange]:
    """Turn the model's [{expr, specificity}] list into ``DateRange`` objects.

    Pure dict→object logic (plus shared ``dateparser`` resolution), unit-tested
    against hand-written expression lists — the JSON analogue of Arm 2's
    :func:`parse_datetime_tags`. Edge handling is identical: empty list → ``[]``;
    an ``expr`` that ``dateparser`` cannot resolve → **skipped** (no wrong commit);
    an out-of-enum ``specificity`` → skipped (defensive — the JSON schema prevents
    it in production); ≥2 items → ≥2 ranges (annotate flags ``compound``).
    """
    ranges: list[DateRange] = []
    for item in expressions:
        if not isinstance(item, dict):
            continue
        expr = str(item.get("expr") or "").strip()
        spec = str(item.get("specificity") or "").strip().lower()
        if not expr or spec not in VALID_SPEC:
            continue
        # Guard the model's self-reported spec: a date/day with no clock time
        # mislabelled ``exact_time`` would otherwise produce a midnight 1-hour
        # window (see resolution.reconcile_exact_time).
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


def _diagnose(
    expressions: list[dict[str, Any]], ranges: list[DateRange]
) -> dict[str, Any]:
    """Per-call diagnostics for recognition-vs-resolution failure analysis.

    ``recognized`` = the ``expr`` values the model emitted (with a valid spec);
    ``resolved`` = those that ``dateparser`` resolved into a DateRange;
    ``unresolved`` = recognized but not resolved (a *resolution* failure). An empty
    ``recognized`` on a gold row that has a datetime is a *recognition* failure.
    Mirrors Arm 2's ``_diagnose`` so the intrinsic eval reads both arms the same way.
    """
    recognized = [
        str(i.get("expr") or "").strip()
        for i in expressions
        if isinstance(i, dict)
        and str(i.get("expr") or "").strip()
        and str(i.get("specificity") or "").strip().lower() in VALID_SPEC
    ]
    resolved = [r.original_text for r in ranges]
    unresolved = [e for e in recognized if e not in resolved]
    return {
        "raw": expressions,
        "recognized": recognized,
        "resolved": resolved,
        "unresolved": unresolved,
    }


class ApiLLMDatetimeParser:
    """Arm 3 datetime parser. Construct once per session and reuse.

    The Gemini client is created lazily on the first ``parse`` call (via
    ``nlp.api_llm``), not in ``__init__`` — so the factory can build this arm, and
    unit tests can mock ``api_llm.generate_json``, without an API key or a network
    call.
    """

    arm_name: str = "api_llm"

    def __init__(self) -> None:
        self._last_diag: dict[str, Any] | None = None

    def parse(self, text: str, *, now: datetime) -> list[DateRange]:
        if not text or not text.strip():
            self._last_diag = {"raw": [], "recognized": [], "resolved": [], "unresolved": []}
            return []
        prompt = (
            f"Current date: {now:%A, %d %B %Y} (Europe/Zurich).\n\n"
            f"User message:\n{text}"
        )
        data = api_llm.generate_json(
            prompt, response_schema=_DT_SCHEMA, system=_SYSTEM, max_tokens=256
        )
        expressions = data.get("expressions") or []
        if not isinstance(expressions, list):
            expressions = []
        ranges = build_ranges(expressions, now=now)
        self._last_diag = _diagnose(expressions, ranges)
        return ranges

    def last_diagnostics(self) -> dict[str, Any] | None:
        """Most recent ``parse`` call's expressions + recognized/resolved/unresolved.

        Lets the intrinsic eval separate a *recognition* failure (model emitted no
        expression) from a *resolution* failure (an ``expr`` was recognized but
        ``dateparser`` could not resolve it). Read duck-typed by the eval, exactly
        as Arm 2's ``last_diagnostics`` is.
        """
        return self._last_diag
