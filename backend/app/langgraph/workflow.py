"""
LangGraph workflow for the multi-agent NL2SQL pipeline.
Orchestrates the flow between all 6 agents with conditional routing.
"""

from langgraph.graph import StateGraph, END
from app.langgraph.state import QueryState
from app.agents import (
    Agent1Understanding,
    Agent2Schema,
    Agent3SQLGeneration,
    Agent4Validation,
    Agent5Insights,
    Agent6Visualization
)


def create_workflow():
    """
    Create and compile the LangGraph workflow.

    Returns:
        Compiled workflow that can be invoked with a QueryState
    """
    # Initialize all agents
    agent_1 = Agent1Understanding()
    agent_2 = Agent2Schema()
    agent_3 = Agent3SQLGeneration()
    agent_4 = Agent4Validation()

    # Create the graph
    workflow = StateGraph(QueryState)

    # Define a node that increments retry count before regenerating SQL
    def increment_retry_and_generate(state: QueryState) -> QueryState:
        state["retry_count"] = state.get("retry_count", 0) + 1
        return agent_3.execute(state)

    # Add nodes
    workflow.add_node("understand", agent_1.execute)
    workflow.add_node("navigate_schema", agent_2.execute)
    workflow.add_node("generate_sql", agent_3.execute)
    workflow.add_node("validate", agent_4.execute)
    workflow.add_node("retry_sql", increment_retry_and_generate)

    # Set entry point
    workflow.set_entry_point("understand")

    # Add linear edges
    workflow.add_edge("understand", "navigate_schema")
    workflow.add_edge("navigate_schema", "generate_sql")
    workflow.add_edge("generate_sql", "validate")
    workflow.add_edge("retry_sql", "validate")

    # Add conditional edge from validate
    workflow.add_conditional_edges(
        "validate",
        decide_after_validation,
        {
            "proceed": END,
            "retry": "retry_sql",
            "fail": END
        }
    )

    # Compile the workflow
    compiled = workflow.compile()

    return compiled


def decide_after_validation(state: QueryState) -> str:
    """
    Decide what to do after validation.

    Args:
        state: Current pipeline state

    Returns:
        Next node to route to: "proceed", "retry", or "fail"
    """
    validation_result = state.get("validation_result", {})
    retry_count = state.get("retry_count", 0)

    if validation_result.get("is_valid", False):
        return "proceed"

    # Allow one retry (retry_count starts at 0, incremented before retry)
    if retry_count < 1:
        return "retry"

    return "fail"
