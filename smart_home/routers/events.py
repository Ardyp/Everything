from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(
    prefix="/events",
    tags=["home events"],
    responses={404: {"description": "Not found"}},
)

class EventBase(BaseModel):
    device_id: int
    event_type: str  # motion_detected, temperature_change, etc.
    description: str
    severity: str = "info"  # info, warning, critical
    metadata: dict = {}

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# Temporary in-memory storage
events_db = []
event_id_counter = 1

@router.post("/", response_model=Event)
async def create_event(event: EventCreate):
    global event_id_counter
    new_event = Event(
        **event.model_dump(),
        id=event_id_counter,
        timestamp=datetime.now()
    )
    events_db.append(new_event)
    event_id_counter += 1
    return new_event

@router.get("/", response_model=List[Event])
async def get_events(
    device_id: Optional[int] = None,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100
):
    filtered_events = events_db
    
    if device_id:
        filtered_events = [e for e in filtered_events if e.device_id == device_id]
    if event_type:
        filtered_events = [e for e in filtered_events if e.event_type == event_type]
    if severity:
        filtered_events = [e for e in filtered_events if e.severity == severity]
    
    return filtered_events[-limit:]

@router.get("/{event_id}", response_model=Event)
async def get_event(event_id: int):
    for event in events_db:
        if event.id == event_id:
            return event
    raise HTTPException(status_code=404, detail="Event not found")

@router.delete("/{event_id}")
async def delete_event(event_id: int):
    for i, event in enumerate(events_db):
        if event.id == event_id:
            del events_db[i]
            return {"message": "Event deleted"}
    raise HTTPException(status_code=404, detail="Event not found")

@router.get("/device/{device_id}", response_model=List[Event])
async def get_device_events(device_id: int, limit: int = 50):
    device_events = [e for e in events_db if e.device_id == device_id]
    return device_events[-limit:] 