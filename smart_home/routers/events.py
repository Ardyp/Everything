from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from agents.smart_home.database import get_db, EventLogDB

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

# Database backed storage

@router.post("/", response_model=Event)
async def create_event(event: EventCreate, db: Session = Depends(get_db)):
    db_event = EventLogDB(
        event_type=event.event_type,
        details={
            "device_id": event.device_id,
            "description": event.description,
            "severity": event.severity,
            "metadata": event.metadata,
        },
        timestamp=datetime.now(),
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return Event(
        id=db_event.id,
        device_id=event.device_id,
        event_type=event.event_type,
        description=event.description,
        severity=event.severity,
        metadata=event.metadata,
        timestamp=db_event.timestamp,
    )

@router.get("/", response_model=List[Event])
async def get_events(
    device_id: Optional[int] = None,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(EventLogDB)
    if device_id is not None:
        query = query.filter(EventLogDB.details["device_id"].as_integer() == device_id)
    if event_type:
        query = query.filter(EventLogDB.event_type == event_type)
    if severity:
        query = query.filter(EventLogDB.details["severity"] == severity)

    results = query.order_by(EventLogDB.timestamp.desc()).limit(limit).all()
    return [
        Event(
            id=e.id,
            device_id=e.details.get("device_id"),
            event_type=e.event_type,
            description=e.details.get("description", ""),
            severity=e.details.get("severity", "info"),
            metadata=e.details.get("metadata", {}),
            timestamp=e.timestamp,
        )
        for e in results
    ]

@router.get("/{event_id}", response_model=Event)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    e = db.query(EventLogDB).filter(EventLogDB.id == event_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Event not found")
    return Event(
        id=e.id,
        device_id=e.details.get("device_id"),
        event_type=e.event_type,
        description=e.details.get("description", ""),
        severity=e.details.get("severity", "info"),
        metadata=e.details.get("metadata", {}),
        timestamp=e.timestamp,
    )

@router.delete("/{event_id}")
async def delete_event(event_id: int, db: Session = Depends(get_db)):
    e = db.query(EventLogDB).filter(EventLogDB.id == event_id).first()
    if not e:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(e)
    db.commit()
    return {"message": "Event deleted"}

@router.get("/device/{device_id}", response_model=List[Event])
async def get_device_events(device_id: int, limit: int = 50, db: Session = Depends(get_db)):
    events = db.query(EventLogDB).filter(EventLogDB.details["device_id"].as_integer() == device_id).order_by(EventLogDB.timestamp.desc()).limit(limit).all()
    return [
        Event(
            id=e.id,
            device_id=device_id,
            event_type=e.event_type,
            description=e.details.get("description", ""),
            severity=e.details.get("severity", "info"),
            metadata=e.details.get("metadata", {}),
            timestamp=e.timestamp,
        )
        for e in events
    ]
