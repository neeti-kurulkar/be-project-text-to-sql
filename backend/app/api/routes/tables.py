from fastapi import APIRouter, HTTPException, Query
from typing import List
from app.models import TableListResponse, TableDataResponse
from app.services.table_service import TableService

router = APIRouter(prefix="/api/tables", tags=["tables"])


@router.get("", response_model=List[TableListResponse])
async def list_tables():
    """Get list of all available tables"""
    try:
        tables = TableService.list_tables()
        return tables
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{table_name}", response_model=TableDataResponse)
async def get_table_data(
    table_name: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    """Get paginated data from a specific table"""
    try:
        data = TableService.get_table_data(table_name, page, page_size)
        return data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
