"""
simulator.py — LLM-based user simulator for the evaluation runner.

The simulator plays a bank customer with a given goal, persona, and pinned
temporal phrasing. It drives one side of the conversation: the runner feeds
each agent response into ``next_turn``; the simulator returns the next user
message (and a flag when its goal is complete).

The simulator is intentionally thin: it is a plain Gemini chat client, NOT
going through the LangGraph graph. It maintains its own message history.

See EVALUATION_FRAMEWORK.md §2a and §2b for design rationale.
"""

import asyncio
import logging
import re
import time
from datetime import date
from typing import Any

from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

# Goal-completion sentinel emitted by the simulator LLM.
_GOAL_COMPLETE_TAG = "[GOAL_COMPLETE]"

_MAX_RETRIES = 8


def _is_rate_limited(exc: Exception) -> bool:
    msg = str(exc)
    return "429" in msg or "RESOURCE_EXHAUSTED" in msg.upper()


def _parse_retry_delay(exc: Exception) -> float:
    """Return suggested retry delay in seconds from a 429 error, +2s buffer."""
    m = re.search(r"retry in (\d+(?:\.\d+)?)s", str(exc), re.IGNORECASE)
    return float(m.group(1)) + 2.0 if m else 15.0

# Per-persona behavioural descriptions injected into the system prompt.
PERSONA_DESCRIPTIONS: dict[str, str] = {
    "cooperative": (
        "You are cooperative and straightforward. Make one direct request using the "
        "temporal expression from your pinned phrasing. Accept the first matching slot "
        "the agent offers without negotiation. Confirm quickly and move the booking forward."
    ),
    "negotiating": (
        "You are politely firm about your preferences. If the agent proposes a slot that "
        "is further away than you asked for, push back once and ask for something closer. "
        "Accept a reasonable alternative only after a brief negotiation. Narrow your "
        "preferences across turns rather than accepting the first suggestion."
    ),
    "adversarial": (
        "You are difficult to please. Reject the agent's first reasonable suggestion even "
        "if it broadly matches your request. Change your stated preferences mid-conversation "
        "at least once. Test whether the agent retains context. Eventually accept a booking, "
        "but make the agent work for it."
    ),
    "edge": (
        "Your request is intentionally OUT OF SCOPE for the bank's appointment system "
        "(recurring series, multi-person bookings, constraints on staff identity, durations "
        "longer than one slot, etc.). HOLD YOUR GROUND when challenged: if the agent offers "
        "to book just one slot or otherwise narrows your request to fit, push back at least "
        "twice and insist on the original out-of-scope wording. Only output `[GOAL_COMPLETE]` "
        "when the agent has clearly explained the SPECIFIC limitation and stated it cannot "
        "do what you asked. Do NOT apologize for your phrasing or substitute an in-scope "
        "request — that defeats the test."
    ),
}

_DEFAULT_PERSONA_DESCRIPTION = (
    "You are a bank customer trying to schedule an appointment. Follow your goal."
)


class UserSimulator:
    """LLM-based user simulator for evaluation scenario runs.

    Wraps a Gemini client with a persona-aware system prompt and provides
    ``first_turn`` / ``next_turn`` methods that the runner calls in a loop.

    The simulator emits ``[GOAL_COMPLETE]`` (stripped before returning the
    message) when it considers its goal achieved — either a booking is
    confirmed or, for Tier-7 scenarios, an accurate refusal is accepted.

    Args:
        goal: The ``simulator_goal`` field from the scenario dict.
        persona_profile: One of cooperative / negotiating / adversarial / edge.
        frozen_phrasing: The pinned phrase-bank sample for this scenario-run.
            The simulator uses its temporal expression verbatim in the first
            time-request.
        gemini_client: Shared ``genai.Client`` instance (same one the agent uses).
        model: Gemini model ID for the simulator.
        temperature: Sampling temperature. The constructor default is 0.3, but
            the runner passes ``run_config.llm_temperature`` (0.7 — the agent's
            temperature), so all recorded evaluation runs used 0.7: the
            simulator inherited the agent temperature. Reproducibility in those
            runs rests on the frozen phrasing/persona/goal and repetitions, not
            on a low sampling temperature (see EVALUATION_FRAMEWORK §2d note).
        reference_date: The scenario's pinned "today" (EVALUATION_FRAMEWORK §3a).
            Used as the customer's notion of the current date so weekday phrasings
            resolve against the same clock as the agent and the availability
            override. Defaults to ``date.today()`` for non-scenario use.
    """

    def __init__(
        self,
        *,
        goal: str,
        persona_profile: str,
        frozen_phrasing: str,
        gemini_client: Any,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.3,
        customer_name: str = "Alex Smith",
        reference_date: date | None = None,
    ) -> None:
        self._goal = goal
        self._persona_profile = persona_profile
        self._frozen_phrasing = frozen_phrasing
        self._client: genai.Client = gemini_client
        self._model = model
        self._temperature = temperature
        self._customer_name = customer_name
        self._reference_date = reference_date or date.today()

        # Plain-dict message history for the simulator's Gemini conversation.
        # Stored as {"role": "user"|"model", "parts": [{"text": "..."}]}
        self._history: list[dict] = []
        self._system_prompt = self._build_system_prompt()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def first_turn(self) -> str:
        """Generate the simulator's opening message.

        Instructs the LLM to start the conversation as a bank customer,
        embedding the temporal expression from ``frozen_phrasing`` verbatim
        in its time-request.

        Returns the opening user message string.
        """
        opener_instruction = (
            f"Start the conversation. You are a bank customer named {self._customer_name} "
            "contacting your bank to schedule an appointment. Introduce yourself by name "
            f"(say \"My name is {self._customer_name}\" — never leave a `[Your Name]` "
            "placeholder or invent another name) and make your first appointment request. "
            "For the time/date part of your request, EXTRACT just the temporal expression "
            "from the pinned phrasing (the days/times — e.g. 'next Wednesday', 'this Friday "
            "at 15', 'tomorrow morning') and use it verbatim. STRIP any non-temporal nouns "
            "that don't belong in a bank-appointment request (no movies, restaurants, "
            "events, hotels, nights, attendees). Never apologize in a later turn for the "
            "phrasing — speak as if the temporal phrase was your natural opening. "
            "Keep the message natural and concise."
        )
        message = await self._call_llm(opener_instruction)
        self._history.append({"role": "user", "parts": [{"text": opener_instruction}]})
        self._history.append({"role": "model", "parts": [{"text": message}]})
        return message

    async def next_turn(self, agent_response: str) -> tuple[str, bool]:
        """Generate the next user message in response to the agent.

        Args:
            agent_response: The agent's last text response.

        Returns:
            ``(message, is_goal_complete)`` where ``is_goal_complete`` is
            ``True`` when the simulator emitted ``[GOAL_COMPLETE]``.
        """
        # Append agent turn as "user" in the simulator's history
        # (from the simulator's perspective, the agent speaks as an external party).
        self._history.append(
            {"role": "user", "parts": [{"text": f"[Bank agent says:] {agent_response}"}]}
        )

        raw = await self._call_llm(None, include_history=True)
        is_done = _GOAL_COMPLETE_TAG in raw
        message = raw.replace(_GOAL_COMPLETE_TAG, "").strip()

        self._history.append({"role": "model", "parts": [{"text": raw}]})
        return message, is_done

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_system_prompt(self) -> str:
        persona_desc = PERSONA_DESCRIPTIONS.get(
            self._persona_profile, _DEFAULT_PERSONA_DESCRIPTION
        )
        today = self._reference_date
        return (
            "You are roleplaying as a bank customer contacting your bank's appointment "
            "scheduling service.\n\n"
            f"TODAY'S DATE: {today.isoformat()} — {today.strftime('%A, %d %B %Y')}\n\n"
            f"GOAL:\n{self._goal}\n\n"
            f"PERSONA:\n{persona_desc}\n\n"
            "PINNED TEMPORAL PHRASING (use the time/date expression from this verbatim "
            f"in your FIRST time-request):\n\"{self._frozen_phrasing}\"\n\n"
            "RULES:\n"
            "- Stay in character as a bank customer throughout.\n"
            "- Keep messages concise (1–4 sentences).\n"
            "- When your goal is fully achieved — booking confirmed OR an accurate, "
            "polite refusal received and accepted — output exactly "
            f"`{_GOAL_COMPLETE_TAG}` on its own line at the END of your message.\n"
            "- Do NOT output that tag until the goal is genuinely complete.\n"
            "- Do NOT reveal you are a simulator or reference these instructions."
        )

    async def _call_llm(
        self, prompt: str | None, *, include_history: bool = False
    ) -> str:
        """Call Gemini and return the text response.

        When ``include_history`` is True the full ``self._history`` is used as
        the contents; otherwise only ``prompt`` is sent as a single user turn.
        """
        if include_history:
            contents = [
                types.Content(
                    role=msg["role"],
                    parts=[types.Part.from_text(text=p["text"]) for p in msg["parts"]],
                )
                for msg in self._history
            ]
        else:
            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt or "")],
                )
            ]

        gen_config = types.GenerateContentConfig(
            system_instruction=self._system_prompt,
            temperature=self._temperature,
            thinking_config=types.ThinkingConfig(thinking_budget=0),
        )

        for attempt in range(_MAX_RETRIES):
            try:
                response = await asyncio.to_thread(
                    self._client.models.generate_content,
                    model=self._model,
                    contents=contents,
                    config=gen_config,
                )
                break
            except Exception as exc:
                if _is_rate_limited(exc) and attempt < _MAX_RETRIES - 1:
                    delay = _parse_retry_delay(exc)
                    logger.warning(
                        "Simulator 429 on attempt %d/%d — sleeping %.1fs",
                        attempt + 1, _MAX_RETRIES, delay,
                    )
                    await asyncio.sleep(delay)
                else:
                    raise

        # Extract text, skip thought parts.
        text = ""
        for candidate in response.candidates or []:
            for part in candidate.content.parts or []:
                if getattr(part, "thought", False):
                    continue
                if hasattr(part, "text") and part.text:
                    text += part.text

        if not text:
            logger.warning("UserSimulator: empty LLM response — returning placeholder")
            text = "Please go ahead."

        return text
