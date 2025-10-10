"""
FastAPI Backend for Financial Analysis System
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict
import sys
from pathlib import Path
import uuid
import json

# Add agents to path
sys.path.append(str(Path(__file__).parent))

from agents.sql_generator import SQLGeneratorAgent
from agents.sql_executor import SQLExecutorAgent
from agents.insights_generator import InsightsGeneratorAgent
from agents.visualizer import VisualizerAgent

# Initialize FastAPI app
app = FastAPI(
    title="HUL Financial Analysis API",
    description="Multi-agent system for financial data analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agents
sql_generator = SQLGeneratorAgent()
sql_executor = SQLExecutorAgent()
insights_generator = InsightsGeneratorAgent()
visualizer = VisualizerAgent()

# In-memory storage for analysis results
analysis_cache = {}


# Pydantic models
class AnalysisRequest(BaseModel):
    question: str
    enable_visualization: bool = True


class AnalysisResponse(BaseModel):
    analysis_id: str
    question: str
    sql_query: Optional[str]
    results: Optional[List[Dict]]
    columns: Optional[List[str]]
    row_count: int
    insights: Optional[str]
    summary: Optional[str]
    visualizations: Optional[Dict]
    error: Optional[str]
    status: str  # "success", "error", "processing"


class HealthResponse(BaseModel):
    status: str
    agents: Dict[str, str]


# Routes

@app.get("/", response_model=Dict)
async def root():
    """Root endpoint"""
    return {
        "message": "HUL Financial Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "analyze": "/api/analyze",
            "sample_questions": "/api/sample-questions",
            "chart": "/api/chart/{filename}"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "agents": {
            "sql_generator": "active",
            "sql_executor": "active",
            "insights_generator": "active",
            "visualizer": "active"
        }
    }


@app.get("/api/sample-questions")
async def get_sample_questions():
    """Get sample questions"""
    return {
        "questions": [
            {
                "id": 1,
                "question": "What is the revenue variance between 2022 and 2023?",
                "category": "Revenue Analysis"
            },
            {
                "id": 2,
                "question": "Show me the net profit margin trend over all years",
                "category": "Profitability"
            },
            {
                "id": 3,
                "question": "How has total assets grown from 2021 to 2025?",
                "category": "Asset Management"
            },
            {
                "id": 4,
                "question": "Compare the current ratio and quick ratio across years",
                "category": "Liquidity"
            },
            {
                "id": 5,
                "question": "What are the key profitability metrics for 2024?",
                "category": "Profitability"
            },
            {
                "id": 6,
                "question": "Analyze working capital efficiency over time",
                "category": "Efficiency"
            },
            {
                "id": 7,
                "question": "Show me operating cash flow trends",
                "category": "Cash Flow"
            },
            {
                "id": 8,
                "question": "Compare debt equity ratio with return on net worth",
                "category": "Leverage"
            }
        ]
    }


@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_question(request: AnalysisRequest):
    """
    Main analysis endpoint - orchestrates all agents
    """
    analysis_id = str(uuid.uuid4())
    
    try:
        # Step 1: Generate SQL
        sql_result = sql_generator.generate(request.question)
        
        if sql_result["error"]:
            return AnalysisResponse(
                analysis_id=analysis_id,
                question=request.question,
                sql_query=None,
                results=None,
                columns=None,
                row_count=0,
                insights=None,
                summary=None,
                visualizations=None,
                error=f"SQL Generation Failed: {sql_result['error']}",
                status="error"
            )
        
        sql_query = sql_result["sql_query"]
        
        # Step 2: Execute SQL (with retry)
        max_retry = 2
        attempt = 0
        execution_result = None
        
        while attempt <= max_retry:
            execution_result = sql_executor.execute_with_validation(
                sql_query,
                return_df=True
            )
            
            if not execution_result["error"]:
                break
            
            if attempt < max_retry:
                # Try to fix SQL
                fix_result = sql_generator.fix_query(
                    question=request.question,
                    broken_sql=sql_query,
                    error=execution_result["error"]
                )
                
                if fix_result["error"]:
                    return AnalysisResponse(
                        analysis_id=analysis_id,
                        question=request.question,
                        sql_query=sql_query,
                        results=None,
                        columns=None,
                        row_count=0,
                        insights=None,
                        summary=None,
                        visualizations=None,
                        error=f"SQL Fix Failed: {fix_result['error']}",
                        status="error"
                    )
                
                sql_query = fix_result["sql_query"]
                attempt += 1
            else:
                return AnalysisResponse(
                    analysis_id=analysis_id,
                    question=request.question,
                    sql_query=sql_query,
                    results=None,
                    columns=None,
                    row_count=0,
                    insights=None,
                    summary=None,
                    visualizations=None,
                    error=f"SQL Execution Failed: {execution_result['error']}",
                    status="error"
                )
        
        # Check if we have results
        if execution_result["row_count"] == 0:
            return AnalysisResponse(
                analysis_id=analysis_id,
                question=request.question,
                sql_query=sql_query,
                results=None,
                columns=None,
                row_count=0,
                insights=None,
                summary=None,
                visualizations=None,
                error="Query returned no results",
                status="error"
            )
        
        # Convert DataFrame to list of dicts
        results_df = execution_result["results"]
        results_list = results_df.to_dict('records')
        columns = results_df.columns.tolist()
        
        # Step 3: Generate Insights
        insights_result = insights_generator.generate(
            question=request.question,
            sql_query=sql_query,
            results=results_df
        )
        
        insights = insights_result.get("insights")
        summary = insights_result.get("summary")
        
        # Step 4: Create Visualizations (if enabled)
        viz_result = None
        if request.enable_visualization:
            viz_result = visualizer.analyze_and_visualize(
                question=request.question,
                results=results_df,
                output_dir="output"
            )
        
        # Cache the result
        analysis_cache[analysis_id] = {
            "question": request.question,
            "sql_query": sql_query,
            "results": results_list,
            "insights": insights,
            "visualizations": viz_result
        }
        
        return AnalysisResponse(
            analysis_id=analysis_id,
            question=request.question,
            sql_query=sql_query,
            results=results_list,
            columns=columns,
            row_count=len(results_list),
            insights=insights,
            summary=summary,
            visualizations=viz_result,
            error=None,
            status="success"
        )
        
    except Exception as e:
        return AnalysisResponse(
            analysis_id=analysis_id,
            question=request.question,
            sql_query=None,
            results=None,
            columns=None,
            row_count=0,
            insights=None,
            summary=None,
            visualizations=None,
            error=f"Unexpected error: {str(e)}",
            status="error"
        )


@app.get("/api/chart/{filename}")
async def get_chart(filename: str):
    """Serve chart images"""
    file_path = Path("output") / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Chart not found")
    
    return FileResponse(file_path, media_type="image/png")


@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get cached analysis result"""
    if analysis_id not in analysis_cache:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_cache[analysis_id]


@app.delete("/api/analysis/{analysis_id}")
async def delete_analysis(analysis_id: str):
    """Delete cached analysis"""
    if analysis_id in analysis_cache:
        del analysis_cache[analysis_id]
        return {"message": "Analysis deleted"}
    
    raise HTTPException(status_code=404, detail="Analysis not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)