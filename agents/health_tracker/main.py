from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/health", tags=["health"])

gym_visits = []

@router.post("/gym")
async def log_gym_visit():
    visit = {"visited_at": datetime.now().isoformat()}
    gym_visits.append(visit)
    return {"message": "Gym visit logged", **visit}

@router.get("/status")
async def status():
    return {"visits": len(gym_visits)}
