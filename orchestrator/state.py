"""Conversation state for the LangGraph orchestrator."""

import operator
from typing import Annotated, TypedDict


class ConversationState(TypedDict):
    """LangGraph state for a single appointment-booking conversation.

    The ``messages`` field stores the Gemini conversation history as a list of
    ``google.genai.types.Content`` objects (role="user" or role="model", each
    with a ``parts`` list).  Using ``Annotated[list, operator.add]`` tells
    LangGraph to *append* new messages rather than replace the list on every
    node return.
    """

    # Gemini conversation history — list of google.genai.types.Content objects
    messages: Annotated[list, operator.add]

    # --- Booking state fields ---
    topic_id: str | None            # e.g. "investing"
    topic_name: str | None          # e.g. "Investing"
    contact_medium_id: str | None   # e.g. "online"
    contact_medium_name: str | None # e.g. "Online Meeting"

    # Conversation phase — valid values:
    #   intent | topic | medium | datetime | availability | confirm | booked
    phase: str

    # How many user turns have elapsed
    turn_count: int

    # Set by the agent node when Gemini emits a function_call.
    # Cleared by the execute node after the MCP call completes.
    # Schema: {"name": str, "args": dict}
    pending_tool_call: dict | None

    # Written by the execute node with the raw MCP response dict.
    # Read by the agent node on the next loop iteration.
    tool_result: dict | None

    # Structured debug records accumulated across nodes.
    # Each record: {"node": str, "timestamp": str, "action": str, "details": dict}
    # Uses operator.add so every node can append without overwriting prior records.
    debug_log: Annotated[list, operator.add]

    # NLP annotation output for the latest user message — written by the
    # annotate node when nlp_datetime_enabled or nlp_entity_enabled is True,
    # consumed by the agent node to build the per-turn system prompt's NLP HINTS
    # block. Stored as a plain dict (the JSON form of nlp.schemas.AnnotatedMessage,
    # via model_dump(mode="json")) so LangGraph state validation doesn't trip on
    # the Pydantic model. None means "baseline mode" — agent prompt is unchanged.
    last_annotation: dict | None


def default_state() -> ConversationState:
    """Return a fresh ConversationState with all defaults applied."""
    return ConversationState(
        messages=[],
        topic_id=None,
        topic_name=None,
        contact_medium_id=None,
        contact_medium_name=None,
        phase="intent",
        turn_count=0,
        pending_tool_call=None,
        tool_result=None,
        debug_log=[],
        last_annotation=None,
    )
