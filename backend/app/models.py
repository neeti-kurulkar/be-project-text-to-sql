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


# Chart data models
class RevenueByCountryItem(BaseModel):
    country: str
    revenue: float


class RevenueTrendItem(BaseModel):
    month: str
    revenue: float


class QuarterlyRevenueItem(BaseModel):
    quarter: str


class TopExpenseItem(BaseModel):
    account: str
    amount: float


class RegionalDistributionItem(BaseModel):
    region: str
    value: float
    percentage: int


class ProfitLossItem(BaseModel):
    month: str
    revenue: float
    expenses: float
    net: float


class YoYGrowthItem(BaseModel):
    year: int
    revenue: float
    prevRevenue: Optional[float] = None
    growthRate: Optional[float] = None


# Chart response models
class RevenueByCountryResponse(BaseModel):
    data: List[RevenueByCountryItem]


class RevenueTrendResponse(BaseModel):
    data: List[RevenueTrendItem]


class QuarterlyRevenueResponse(BaseModel):
    data: List[Dict[str, Any]]


class TopExpensesResponse(BaseModel):
    data: List[TopExpenseItem]


class RegionalDistributionResponse(BaseModel):
    data: List[RegionalDistributionItem]


class ProfitLossResponse(BaseModel):
    data: List[ProfitLossItem]


class YoYGrowthResponse(BaseModel):
    data: List[YoYGrowthItem]


class ExpenseBreakdownResponse(BaseModel):
    data: List[Dict[str, Any]]


class AllChartsResponse(BaseModel):
    revenueByCountry: List[RevenueByCountryItem]
    revenueTrend: List[RevenueTrendItem]
    quarterlyRevenue: List[Dict[str, Any]]
    topExpenses: List[TopExpenseItem]
    regionalDistribution: List[RegionalDistributionItem]
    profitLoss: List[ProfitLossItem]
    yoyGrowth: List[YoYGrowthItem]
    expenseBreakdown: List[Dict[str, Any]]
