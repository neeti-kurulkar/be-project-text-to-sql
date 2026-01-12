from fastapi import APIRouter, HTTPException, Depends
from app.models import QuickStatsResponse
from app.services.stats_service import StatsService
from app.middleware.auth_middleware import get_organization_id

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=QuickStatsResponse)
async def get_quick_stats(organization_id: int = Depends(get_organization_id)):
    """Get quick statistics for dashboard (requires authentication)"""
    try:
        stats = StatsService.get_quick_stats(organization_id=organization_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
