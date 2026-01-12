from pydantic import BaseModel
from typing import List, Any, Optional, Dict
from datetime import datetime


class QueryExecuteRequest(BaseModel):
    sql: str


class QueryExecuteResponse(BaseModel):
    columns: List[str]
    rows: List[Dict[str, Any]]
    row_count: int
    execution_time: float


class TableListResponse(BaseModel):
    name: str
    display_name: str
    row_count: int


class TableDataRequest(BaseModel):
    table_name: str
    page: int = 1
    page_size: int = 50


class TableDataResponse(BaseModel):
    table_name: str
    columns: List[str]
    rows: List[Dict[str, Any]]
    total_rows: int
    page: int
    page_size: int
    total_pages: int


class QuickStatsResponse(BaseModel):
    total_revenue: float
    total_transactions: int
    countries_count: int
    date_range: str


class QueryHistoryItem(BaseModel):
    id: int
    question: str
    sql: str
    timestamp: datetime
    execution_time: float
    row_count: int


class QueryHistoryResponse(BaseModel):
    history: List[QueryHistoryItem]
    total: int
