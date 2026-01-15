"""
LangGraph state definition for the NL2SQL pipeline.
"""

from typing import TypedDict, List, Dict, Any, Optional


class AgentTrace(TypedDict):
    """Trace information for a single agent execution."""
    agent: str
    duration: float
    status: str
    details: Optional[Dict[str, Any]]


class ValidationResult(TypedDict):
    """Result from SQL validation."""
    is_valid: bool
    errors: List[str]


class Intent(TypedDict, total=False):
    """Extracted intent from user question."""
    intent_type: str
    metric: str
    aggregation: Optional[str]
    group_by: List[str]
    filters: Dict[str, Any]
    order: Optional[str]
    limit: Optional[int]
    comparison: Optional[str]
    visualization_suitable: bool


class Schema(TypedDict):
    """Selected database schema."""
    tables: List[str]
    joins: List[Dict[str, Any]]


class Insights(TypedDict, total=False):
    """Generated insights from query results."""
    summary: str
    key_insights: List[str]
    trends: Optional[List[str]]
    anomalies: Optional[List[str]]
    metrics: Optional[Dict[str, Any]]


class Visualization(TypedDict, total=False):
    """Visualization recommendation."""
    should_visualize: bool
    chart_type: Optional[str]
    chart_config: Optional[Dict[str, Any]]
    reason: Optional[str]


class QueryState(TypedDict, total=False):
    """
    State object that flows through the LangGraph workflow.

    Contains all inputs, intermediate results, and outputs from each agent.
    """
    # Input fields
    organization_id: int
    user_id: int
    question: str

    # Context (fetched before agents)
    org_context: str
    org_context_raw: Dict[str, Any]

    # Agent 1 output
    intent: Intent

    # Agent 2 output
    schema: Schema

    # Agent 3 output
    sql: str

    # Agent 4 output
    validation_result: ValidationResult
    error_feedback: Optional[str]
    retry_count: int

    # SQL execution results
    execution_success: bool
    results: List[Dict[str, Any]]
    result_columns: List[str]
    row_count: int
    execution_time: float
    execution_error: Optional[str]

    # Agent 5 output
    insights: Insights

    # Agent 6 output
    visualization: Visualization

    # Tracing
    agent_trace: List[AgentTrace]

    # Final response
    final_response: Optional[Dict[str, Any]]
