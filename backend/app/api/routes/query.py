from fastapi import APIRouter, HTTPException, Depends
from app.models import QueryExecuteRequest, QueryExecuteResponse
from app.services.query_service import QueryService
from app.middleware.auth_middleware import get_organization_id

router = APIRouter(prefix="/api/query", tags=["query"])


@router.post("/execute", response_model=QueryExecuteResponse)
async def execute_query(request: QueryExecuteRequest, organization_id: int = Depends(get_organization_id)):
    """Execute a SQL query (requires authentication)"""
    try:
        # Validate SQL
        QueryService.validate_sql(request.sql)

        # Execute with organization filter
        columns, rows, row_count, execution_time = QueryService.execute_sql(request.sql, organization_id)

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
