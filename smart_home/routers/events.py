from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from models import Event as EventModel, get_db

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

@router.post("/", response_model=Event)
async def create_event(event: EventCreate, db: Session = Depends(get_db)):
    db_event = EventModel(
        **event.model_dump(),
        timestamp=datetime.now()
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return Event.model_validate(db_event)

@router.get("/", response_model=List[Event])
async def get_events(
    device_id: Optional[int] = None,
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(EventModel)
    if device_id:
        query = query.filter(EventModel.device_id == device_id)
    if event_type:
        query = query.filter(EventModel.event_type == event_type)
    if severity:
        query = query.filter(EventModel.severity == severity)
    events = query.order_by(EventModel.timestamp.desc()).limit(limit).all()
    return [Event.model_validate(e) for e in events]

@router.get("/{event_id}", response_model=Event)
async def get_event(event_id: int, db: Session = Depends(get_db)):
    ev = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    return Event.model_validate(ev)

@router.delete("/{event_id}")
async def delete_event(event_id: int, db: Session = Depends(get_db)):
    ev = db.query(EventModel).filter(EventModel.id == event_id).first()
    if not ev:
        raise HTTPException(status_code=404, detail="Event not found")
    db.delete(ev)
    db.commit()
    return {"message": "Event deleted"}

@router.get("/device/{device_id}", response_model=List[Event])
async def get_device_events(device_id: int, limit: int = 50, db: Session = Depends(get_db)):
    events = (
        db.query(EventModel)
        .filter(EventModel.device_id == device_id)
        .order_by(EventModel.timestamp.desc())
        .limit(limit)
        .all()
    )
    return [Event.model_validate(e) for e in events]
