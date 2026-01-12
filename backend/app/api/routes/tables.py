from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List
from app.models import TableListResponse, TableDataResponse
from app.services.table_service import TableService
from app.middleware.auth_middleware import get_organization_id

router = APIRouter(prefix="/api/tables", tags=["tables"])


@router.get("", response_model=List[TableListResponse])
async def list_tables(organization_id: int = Depends(get_organization_id)):
    """Get list of all available tables (requires authentication)"""
    try:
        tables = TableService.list_tables(organization_id)
        return tables
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{table_name}", response_model=TableDataResponse)
async def get_table_data(
    table_name: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    organization_id: int = Depends(get_organization_id)
):
    """Get paginated data from a specific table (requires authentication)"""
    try:
        data = TableService.get_table_data(table_name, page, page_size, organization_id)
        return data
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
