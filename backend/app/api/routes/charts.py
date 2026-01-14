from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from app.services.charts_service import ChartsService
from app.middleware.auth_middleware import get_organization_id
from app.models import (
    RevenueByCountryResponse,
    RevenueTrendResponse,
    QuarterlyRevenueResponse,
    TopExpensesResponse,
    RegionalDistributionResponse,
    ProfitLossResponse,
    YoYGrowthResponse,
    ExpenseBreakdownResponse,
    AllChartsResponse
)

router = APIRouter(prefix="/api/charts", tags=["charts"])


@router.get("/all", response_model=AllChartsResponse)
async def get_all_charts(
    year: Optional[int] = Query(None, description="Filter by year"),
    organization_id: int = Depends(get_organization_id)
):
    """Get all chart data in a single request"""
    try:
        return ChartsService.get_all_charts(organization_id, year)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/revenue-by-country", response_model=RevenueByCountryResponse)
async def get_revenue_by_country(
    year: Optional[int] = Query(None, description="Filter by year"),
    organization_id: int = Depends(get_organization_id)
):
    """Revenue breakdown by country"""
    try:
        data = ChartsService.get_revenue_by_country(organization_id, year)
        return RevenueByCountryResponse(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/revenue-trend", response_model=RevenueTrendResponse)
async def get_revenue_trend(
    organization_id: int = Depends(get_organization_id)
):
    """Monthly revenue trend over time"""
    try:
        data = ChartsService.get_revenue_trend(organization_id)
        return RevenueTrendResponse(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/quarterly-revenue", response_model=QuarterlyRevenueResponse)
async def get_quarterly_revenue(
    organization_id: int = Depends(get_organization_id)
):
    """Quarterly revenue comparison across years"""
    try:
        data = ChartsService.get_quarterly_revenue(organization_id)
        return QuarterlyRevenueResponse(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-expenses", response_model=TopExpensesResponse)
async def get_top_expenses(
    limit: int = Query(5, ge=1, le=20, description="Number of top expenses to return"),
    year: Optional[int] = Query(None, description="Filter by year"),
    organization_id: int = Depends(get_organization_id)
):
    """Top expense accounts"""
    try:
        data = ChartsService.get_top_expenses(organization_id, limit, year)
        return TopExpensesResponse(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/regional-distribution", response_model=RegionalDistributionResponse)
async def get_regional_distribution(
    year: Optional[int] = Query(None, description="Filter by year"),
    organization_id: int = Depends(get_organization_id)
):
    """Revenue distribution by region"""
    try:
        data = ChartsService.get_regional_distribution(organization_id, year)
        return RegionalDistributionResponse(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profit-loss", response_model=ProfitLossResponse)
async def get_profit_loss(
    organization_id: int = Depends(get_organization_id)
):
    """Monthly profit/loss trend"""
    try:
        data = ChartsService.get_profit_loss_trend(organization_id)
        return ProfitLossResponse(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/yoy-growth", response_model=YoYGrowthResponse)
async def get_yoy_growth(
    organization_id: int = Depends(get_organization_id)
):
    """Year-over-year growth comparison"""
    try:
        data = ChartsService.get_yoy_growth(organization_id)
        return YoYGrowthResponse(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/expense-breakdown", response_model=ExpenseBreakdownResponse)
async def get_expense_breakdown(
    year: Optional[int] = Query(None, description="Filter by year"),
    organization_id: int = Depends(get_organization_id)
):
    """Monthly expense breakdown by category"""
    try:
        data = ChartsService.get_expense_breakdown(organization_id, year)
        return ExpenseBreakdownResponse(data=data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
