"""LangGraph graph definition for the appointment scheduling orchestrator."""

from langgraph.graph import END, StateGraph

from orchestrator.nodes.agent import agent_node, should_continue
from orchestrator.nodes.annotate import annotate_node
from orchestrator.nodes.execute import execute_node
from orchestrator.state import ConversationState


def build_graph():
    """Build the appointment scheduling graph.

    Flow:
        START → annotate → agent → (has tool call?) → execute → agent (loop)
                                                     → END (text response)

    The annotate node runs the NLP pipeline on the latest user message when
    the ``nlp_datetime_enabled`` / ``nlp_entity_enabled`` flags are set
    (IMPROVEMENT_PLAN.md §5). With all flags off it is a no-op and the
    baseline behavior is byte-identical to the pre-NLP graph.

    The agent node calls the active LLM provider with function declarations.
    The provider either requests a tool call or generates a text response.
    The execute node calls the MCP server and returns the result; control
    flows back to the agent (NOT to annotate — annotate only runs once per
    user turn at the start of the invocation).
    """
    graph = StateGraph(ConversationState)

    graph.add_node("annotate", annotate_node)
    graph.add_node("agent", agent_node)
    graph.add_node("execute", execute_node)

    graph.set_entry_point("annotate")
    graph.add_edge("annotate", "agent")

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "execute": "execute",
            "end": END,
        },
    )

    graph.add_edge("execute", "agent")

    return graph.compile()


appointment_graph = build_graph()
