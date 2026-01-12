from fastapi import APIRouter, HTTPException
from app.models import QueryExecuteRequest, QueryExecuteResponse
from app.services.query_service import QueryService

router = APIRouter(prefix="/api/query", tags=["query"])


@router.post("/execute", response_model=QueryExecuteResponse)
async def execute_query(request: QueryExecuteRequest):
    """Execute a SQL query"""
    try:
        # Validate SQL
        QueryService.validate_sql(request.sql)

        # Execute
        columns, rows, row_count, execution_time = QueryService.execute_sql(request.sql)

        return QueryExecuteResponse(
            columns=columns,
            rows=rows,
            row_count=row_count,
            execution_time=execution_time
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
