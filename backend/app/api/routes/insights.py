"""
Insights API Routes - Automated AI-powered insights
"""
from fastapi import APIRouter, Depends, HTTPException
from app.middleware.auth_middleware import get_current_user
from app.services.insights_service import InsightsService

router = APIRouter(prefix="/api/insights", tags=["insights"])


@router.get("/automated")
async def get_automated_insights(current_user: dict = Depends(get_current_user)):
    """
    Get automated AI-powered insights for the organization.
    Analyzes revenue concentration, growth trends, seasonality,
    and generates actionable recommendations.
    """
    try:
        organization_id = current_user.get("organization_id", 1)
        insights = InsightsService.get_automated_insights(organization_id)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
