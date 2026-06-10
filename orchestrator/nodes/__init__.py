"""LangGraph node implementations for the appointment scheduling orchestrator.

Active nodes (wired into the graph):
- agent_node        — calls the active LLM provider, routes to execute or end
- execute_node      — calls MCP tools via MCPBridge

Stub nodes (defined so the graph topology is final, not yet wired):
- annotate_node     — Step 2 (NLP pipeline)
- plan_node         — Step 4 (Planner)
- render_node       — Step 4 (Renderer)
"""

from orchestrator.nodes.agent import agent_node, should_continue
from orchestrator.nodes.annotate import annotate_node
from orchestrator.nodes.execute import execute_node
from orchestrator.nodes.plan import plan_node
from orchestrator.nodes.render import render_node

__all__ = [
    "agent_node",
    "annotate_node",
    "execute_node",
    "plan_node",
    "render_node",
    "should_continue",
]
