"""Protocol for the datetime parser, shared by Arms 1, 2, 3."""

from __future__ import annotations

from datetime import datetime
from typing import Protocol, runtime_checkable

from nlp.schemas import DateRange


@runtime_checkable
class DatetimeParser(Protocol):
    """All three arms (dateparser, local LLM, API LLM) implement this.

    The intrinsic eval and the annotate node depend only on the Protocol —
    arm-specific code is reached through ``nlp.factory.build_datetime_parser``.
    """

    arm_name: str

    def parse(self, text: str, *, now: datetime) -> list[DateRange]:
        """Parse temporal expressions from ``text``.

        Returns one DateRange per parsed sub-expression. Compound utterances
        (e.g. "Tuesday or Thursday") yield ≥2 ranges. Empty list if no
        temporal expression is found.

        ``now`` is the anchor for relative resolution ("tomorrow", "next
        Tuesday"). Must be timezone-aware Europe/Zurich.
        """
        ...
