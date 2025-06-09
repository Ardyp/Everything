from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

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
appointments_db = []
appointment_id_counter = 1

@router.post("/", response_model=Appointment)
async def create_appointment(appointment: AppointmentCreate):
    global appointment_id_counter
    new_appointment = Appointment(
        **appointment.model_dump(),
        id=appointment_id_counter,
        created_at=datetime.now()
    )
    appointments_db.append(new_appointment)
    appointment_id_counter += 1
    return new_appointment

@router.get("/", response_model=List[Appointment])
async def get_appointments():
    return appointments_db

@router.get("/{appointment_id}", response_model=Appointment)
async def get_appointment(appointment_id: int):
    for appointment in appointments_db:
        if appointment.id == appointment_id:
            return appointment
    raise HTTPException(status_code=404, detail="Appointment not found")

@router.put("/{appointment_id}", response_model=Appointment)
async def update_appointment(appointment_id: int, appointment: AppointmentCreate):
    for i, existing_appointment in enumerate(appointments_db):
        if existing_appointment.id == appointment_id:
            updated_appointment = Appointment(
                **appointment.model_dump(),
                id=appointment_id,
                created_at=existing_appointment.created_at,
                status=existing_appointment.status
            )
            appointments_db[i] = updated_appointment
            return updated_appointment
    raise HTTPException(status_code=404, detail="Appointment not found")

@router.delete("/{appointment_id}")
async def delete_appointment(appointment_id: int):
    for i, appointment in enumerate(appointments_db):
        if appointment.id == appointment_id:
            del appointments_db[i]
            return {"message": "Appointment deleted"}
    raise HTTPException(status_code=404, detail="Appointment not found")

@router.post("/{appointment_id}/status/{new_status}")
async def update_appointment_status(appointment_id: int, new_status: str):
    valid_statuses = ["scheduled", "completed", "cancelled"]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )
    
    for appointment in appointments_db:
        if appointment.id == appointment_id:
            appointment.status = new_status
            return {"message": f"Appointment status updated to {new_status}"}
    raise HTTPException(status_code=404, detail="Appointment not found") 