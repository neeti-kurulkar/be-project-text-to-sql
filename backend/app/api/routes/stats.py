from fastapi import APIRouter, HTTPException
from app.models import QuickStatsResponse
from app.services.stats_service import StatsService

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("", response_model=QuickStatsResponse)
async def get_quick_stats():
    """Get quick statistics for dashboard"""
    try:
        stats = StatsService.get_quick_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
