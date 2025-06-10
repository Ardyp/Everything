from fastapi import APIRouter, HTTPException, Query
from google.transit import gtfs_realtime_pb2
import requests
import os
from typing import List, Dict
from datetime import datetime

router = APIRouter(prefix="/commute", tags=["commute monitor"])

GTFS_FEED_URL = os.getenv("GTFS_FEED_URL", "")


def _load_feed() -> gtfs_realtime_pb2.FeedMessage:
    if not GTFS_FEED_URL:
        raise HTTPException(status_code=500, detail="GTFS_FEED_URL not configured")
    try:
        response = requests.get(GTFS_FEED_URL, timeout=10)
        response.raise_for_status()
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        return feed
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch feed: {e}")


@router.get("/status")
async def get_status() -> Dict[str, int]:
    """Return count of current delays in the feed."""
    feed = _load_feed()
    delays = 0
    for entity in feed.entity:
        if entity.trip_update:
            for stop_update in entity.trip_update.stop_time_update:
                if stop_update.HasField("arrival") and stop_update.arrival.delay > 0:
                    delays += 1
    return {"delay_events": delays}


@router.get("/next-train")
async def next_train(stop_id: str = Query(..., description="Stop ID")) -> List[Dict[str, str]]:
    """Return next departure times for a stop."""
    feed = _load_feed()
    departures: List[Dict[str, str]] = []
    for entity in feed.entity:
        if entity.trip_update:
            for stop_update in entity.trip_update.stop_time_update:
                if stop_update.stop_id == stop_id:
                    arrival_time = stop_update.arrival.time
                    departures.append({
                        "trip_id": entity.trip_update.trip.trip_id,
                        "arrival": datetime.fromtimestamp(arrival_time).isoformat()
                    })
    departures.sort(key=lambda d: d["arrival"])
    return departures[:3]
