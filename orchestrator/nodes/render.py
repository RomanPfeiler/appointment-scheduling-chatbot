"""Render node — Step 4 (Planner/Renderer split). Currently a pass-through stub.

Future behavior: receive ONLY `information_to_convey` from the planner (never
raw tool output) and produce the user-facing text. This separation is the
project's main hallucination-mitigation strategy. For now the agent node
produces user text directly.

This file exists so the graph topology is final from day one. Not wired into
orchestrator/graph.py yet.
"""

import logging

from langchain_core.runnables import RunnableConfig

from orchestrator.state import ConversationState

logger = logging.getLogger(__name__)


async def render_node(state: ConversationState, config: RunnableConfig) -> dict:
    """Pass-through stub. Returns no state changes."""
    logger.debug("render_node (stub) — no-op")
    return {}
