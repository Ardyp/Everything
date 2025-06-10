"""Commute monitoring agent using GTFS realtime feeds."""
from fastapi import APIRouter
from typing import Dict
import os
import logging
import requests
from gtfs_realtime_bindings import feedmessage_pb2

router = APIRouter(prefix="/commute", tags=["commute"])
FEED_URL = os.getenv("GTFS_FEED_URL")


@router.get("/status")
async def get_train_status(stop_id: str) -> Dict[str, str]:
    """Return basic status information for a stop."""
    if not FEED_URL:
        return {"error": "GTFS_FEED_URL not configured"}
    try:
        resp = requests.get(FEED_URL, timeout=10)
        feed = feedmessage_pb2.FeedMessage()
        feed.ParseFromString(resp.content)
        return {"stop_id": stop_id, "entities": len(feed.entity)}
    except Exception as e:
        logging.exception("Failed to fetch feed")
        return {"error": str(e)}
