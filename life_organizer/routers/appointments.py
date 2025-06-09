from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy.orm import Session
from agents.life_organizer.database import get_db, AppointmentDB

router = APIRouter(
    prefix="/appointments",
    tags=["appointments"],
    responses={404: {"description": "Not found"}},
)

class AppointmentBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: int
    created_at: datetime
    status: str = "scheduled"  # scheduled, completed, cancelled

    class Config:
        from_attributes = True

# Database backed storage

@router.post("/", response_model=Appointment)
async def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    db_appointment = AppointmentDB(
        title=appointment.title,
        description=appointment.description,
        date=appointment.start_time,
        duration_minutes=int((appointment.end_time - appointment.start_time).total_seconds() / 60),
        location=appointment.location,
        notes=None,
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return Appointment(
        id=db_appointment.id,
        created_at=db_appointment.date,
        status="scheduled",
        **appointment.model_dump(),
    )

@router.get("/", response_model=List[Appointment])
async def get_appointments(db: Session = Depends(get_db)):
    records = db.query(AppointmentDB).all()
    return [
        Appointment(
            id=r.id,
            title=r.title,
            description=r.notes,
            start_time=r.date,
            end_time=r.date + timedelta(minutes=r.duration_minutes),
            location=r.location,
            created_at=r.date,
            status="scheduled",
        )
        for r in records
    ]

@router.get("/{appointment_id}", response_model=Appointment)
async def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    r = db.query(AppointmentDB).filter(AppointmentDB.id == appointment_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return Appointment(
        id=r.id,
        title=r.title,
        description=r.notes,
        start_time=r.date,
        end_time=r.date + timedelta(minutes=r.duration_minutes),
        location=r.location,
        created_at=r.date,
        status="scheduled",
    )

@router.put("/{appointment_id}", response_model=Appointment)
async def update_appointment(appointment_id: int, appointment: AppointmentCreate, db: Session = Depends(get_db)):
    db_app = db.query(AppointmentDB).filter(AppointmentDB.id == appointment_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db_app.title = appointment.title
    db_app.description = appointment.description
    db_app.date = appointment.start_time
    db_app.duration_minutes = int((appointment.end_time - appointment.start_time).total_seconds() / 60)
    db_app.location = appointment.location
    db.commit()
    db.refresh(db_app)
    return Appointment(
        id=db_app.id,
        title=db_app.title,
        description=db_app.description,
        start_time=db_app.date,
        end_time=db_app.date + timedelta(minutes=db_app.duration_minutes),
        location=db_app.location,
        created_at=db_app.date,
        status="scheduled",
    )

@router.delete("/{appointment_id}")
async def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db_app = db.query(AppointmentDB).filter(AppointmentDB.id == appointment_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(db_app)
    db.commit()
    return {"message": "Appointment deleted"}

@router.post("/{appointment_id}/status/{new_status}")
async def update_appointment_status(appointment_id: int, new_status: str, db: Session = Depends(get_db)):
    valid_statuses = ["scheduled", "completed", "cancelled"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    db_app = db.query(AppointmentDB).filter(AppointmentDB.id == appointment_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return {"message": f"Appointment status updated to {new_status}"}
