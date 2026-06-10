"""Plan node — Step 4 (Planner/Renderer split). Currently a pass-through stub.

Future behavior: emit a structured ResponsePlan (tool_requests, question_for_user,
information_to_convey, phase_transition) consumed by execute and render. For now
the agent node calls Gemini/Claude directly, which both plans and renders in one
shot.

This file exists so the graph topology is final from day one. Not wired into
orchestrator/graph.py yet.
"""

import logging

from langchain_core.runnables import RunnableConfig

from orchestrator.state import ConversationState

logger = logging.getLogger(__name__)


async def plan_node(state: ConversationState, config: RunnableConfig) -> dict:
    """Pass-through stub. Returns no state changes."""
    logger.debug("plan_node (stub) — no-op")
    return {}
