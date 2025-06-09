from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/commute", tags=["commute"])

@router.get("/status")
async def status():
    """Return mock commute status."""
    return {"message": "Trains running on time", "timestamp": datetime.now().isoformat()}

@router.get("/summary")
async def summary():
    return {
        "route": "NJ Transit Northeast Corridor",
        "duration": "45 minutes",
        "advice": "Leave by 8 AM to arrive on time"
    }
