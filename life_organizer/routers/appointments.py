from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import Appointment as AppointmentModel, get_db

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

# Temporary in-memory storage

@router.post("/", response_model=Appointment)
async def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db)):
    db_appointment = AppointmentModel(
        **appointment.model_dump(),
        created_at=datetime.now()
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return Appointment.model_validate(db_appointment)

@router.get("/", response_model=List[Appointment])
async def get_appointments(db: Session = Depends(get_db)):
    apps = db.query(AppointmentModel).all()
    return [Appointment.model_validate(a) for a in apps]

@router.get("/{appointment_id}", response_model=Appointment)
async def get_appointment(appointment_id: int, db: Session = Depends(get_db)):
    app = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return Appointment.model_validate(app)

@router.put("/{appointment_id}", response_model=Appointment)
async def update_appointment(appointment_id: int, appointment: AppointmentCreate, db: Session = Depends(get_db)):
    db_app = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()
    if not db_app:
        raise HTTPException(status_code=404, detail="Appointment not found")
    for key, value in appointment.model_dump().items():
        setattr(db_app, key, value)
    db.commit()
    db.refresh(db_app)
    return Appointment.model_validate(db_app)

@router.delete("/{appointment_id}")
async def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    app = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(app)
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
    
    app = db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Appointment not found")
    app.status = new_status
    db.commit()
    return {"message": f"Appointment status updated to {new_status}"}
