"""
NL2SQL API routes for natural language to SQL processing.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from app.middleware.auth_middleware import get_current_user
from app.services.nl2sql_service import nl2sql_service


router = APIRouter(
    prefix="/api/nl2sql",
    tags=["nl2sql"]
)


# Request/Response Models

class NL2SQLRequest(BaseModel):
    """Request model for natural language query."""
    question: str = Field(..., min_length=5, max_length=1000)

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What was our total revenue in 2020?"
            }
        }


class SQLInfo(BaseModel):
    """SQL query information."""
    query: str
    execution_time: float


class ResultsInfo(BaseModel):
    """Query results information."""
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int


class InsightsInfo(BaseModel):
    """Insights generated from results."""
    summary: str = ""
    key_insights: List[str] = []
    trends: List[str] = []
    anomalies: List[str] = []
    metrics: Dict[str, Any] = {}


class VisualizationInfo(BaseModel):
    """Visualization recommendation."""
    should_visualize: bool = False
    chart_type: Optional[str] = None
    chart_config: Optional[Dict[str, Any]] = None
    reason: Optional[str] = None


class AgentTraceInfo(BaseModel):
    """Agent execution trace."""
    agent: str
    duration: float
    status: str
    details: Optional[Dict[str, Any]] = None


class NL2SQLResponse(BaseModel):
    """Response model for natural language query."""
    success: bool
    query_id: str
    original_question: str
    sql: Optional[SQLInfo] = None
    results: Optional[ResultsInfo] = None
    insights: Optional[InsightsInfo] = None
    visualization: Optional[VisualizationInfo] = None
    intent: Optional[Dict[str, Any]] = None
    agent_trace: List[AgentTraceInfo] = []
    total_time: float
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    agents: List[str]
    examples_loaded: bool


# Routes

@router.post("/query", response_model=NL2SQLResponse)
async def process_query(
    request: NL2SQLRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Process a natural language query and return SQL results with insights.

    The query goes through 6 agents:
    1. Understanding - Extracts intent from the question
    2. Schema - Selects relevant database tables
    3. SQL Generation - Generates the SQL query
    4. Validation - Validates SQL for security and correctness
    5. Insights - Generates natural language insights from results
    6. Visualization - Recommends appropriate chart types
    """
    try:
        organization_id = current_user["organization_id"]
        user_id = current_user["user_id"]

        result = nl2sql_service.process_query(
            question=request.question,
            organization_id=organization_id,
            user_id=user_id
        )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing query: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check the health of the NL2SQL service.
    """
    from app.retrieval import ExampleLoader

    loader = ExampleLoader()
    stats = loader.get_example_stats()

    examples_loaded = all(count > 0 for count in stats.values())

    return {
        "status": "healthy",
        "agents": [
            "Agent1Understanding",
            "Agent2Schema",
            "Agent3SQLGeneration",
            "Agent4Validation",
            "Agent5Insights",
            "Agent6Visualization"
        ],
        "examples_loaded": examples_loaded
    }


@router.get("/examples/stats")
async def get_example_stats(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get statistics about loaded examples.
    """
    from app.retrieval import ExampleLoader

    loader = ExampleLoader()
    stats = loader.get_example_stats()

    return {
        "success": True,
        "stats": stats
    }


@router.post("/examples/reload")
async def reload_examples(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Force reload all examples into ChromaDB.
    Admin only.
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    from app.retrieval import ExampleLoader

    loader = ExampleLoader()
    stats = loader.load_all_examples(force_reload=True)

    return {
        "success": True,
        "message": "Examples reloaded successfully",
        "stats": stats
    }
