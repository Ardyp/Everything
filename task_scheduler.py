from fastapi import APIRouter, HTTPException
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
from typing import List, Dict, Any
from datetime import datetime
import os

from life_organizer.routers import reminders
from inventory_manager.routers import inventory
from shared.location_service import LocationService

logger = logging.getLogger(__name__)

# Scheduler instance
scheduler = AsyncIOScheduler()

router = APIRouter(prefix="/schedule", tags=["scheduler"])


def send_due_reminders() -> None:
    """Log reminders that are due."""
    now = datetime.now()
    due = [r for r in reminders.reminders_db if not r.completed and r.due_date <= now]
    for r in due:
        logger.info("Reminder due: %s", r.title)


def check_low_stock() -> None:
    """Log items that need restocking."""
    items = inventory.get_low_stock_items()
    if items:
        names = ", ".join(item.name for item in items)
        logger.info("Low stock items: %s", names)


def update_commute_info() -> None:
    """Retrieve commute info and log the duration."""
    origin = os.getenv("COMMUTE_ORIGIN")
    destination = os.getenv("COMMUTE_DESTINATION")
    if not origin or not destination:
        logger.warning("COMMUTE_ORIGIN or COMMUTE_DESTINATION not set")
        return

    service = LocationService()
    info = service.get_commute_info(origin, destination)
    if "error" in info:
        logger.error("Commute update error: %s", info["error"])
        return

    duration = info.get("best_route", {}).get("duration", {}).get("text")
    logger.info("Commute from %s to %s: %s", origin, destination, duration)


def add_scheduled_jobs() -> None:
    """Register default scheduled jobs if not already present."""
    jobs = [
        ("due_reminders", send_due_reminders, 60),
        ("low_stock", check_low_stock, 300),
        ("commute_update", update_commute_info, 600),
    ]
    for job_id, func, interval in jobs:
        if not scheduler.get_job(job_id):
            scheduler.add_job(func, "interval", seconds=interval, id=job_id)


@router.get("/tasks")
async def list_tasks() -> List[Dict[str, Any]]:
    """List current scheduled tasks."""
    result = []
    for job in scheduler.get_jobs():
        result.append({
            "id": job.id,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "paused": job.next_run_time is None,
        })
    return result


@router.post("/enable/{task_id}")
async def enable_task(task_id: str) -> Dict[str, str]:
    """Resume a paused task."""
    try:
        scheduler.resume_job(task_id)
        return {"message": f"{task_id} resumed"}
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.post("/disable/{task_id}")
async def disable_task(task_id: str) -> Dict[str, str]:
    """Pause a scheduled task."""
    try:
        scheduler.pause_job(task_id)
        return {"message": f"{task_id} paused"}
    except Exception as exc:
        raise HTTPException(status_code=404, detail=str(exc))
