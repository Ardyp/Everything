from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

router = APIRouter(
    prefix="/reminders",
    tags=["reminders"],
    responses={404: {"description": "Not found"}},
)

class ReminderBase(BaseModel):
    title: str
    description: Optional[str] = None
    due_date: datetime
    priority: Optional[int] = 1  # 1 (low) to 5 (high)

class ReminderCreate(ReminderBase):
    pass

class Reminder(ReminderBase):
    id: int
    created_at: datetime
    completed: bool = False

    class Config:
        from_attributes = True

# Temporary in-memory storage
reminders_db = []
reminder_id_counter = 1

@router.post("/", response_model=Reminder)
async def create_reminder(reminder: ReminderCreate):
    global reminder_id_counter
    new_reminder = Reminder(
        **reminder.model_dump(),
        id=reminder_id_counter,
        created_at=datetime.now()
    )
    reminders_db.append(new_reminder)
    reminder_id_counter += 1
    return new_reminder

@router.get("/", response_model=List[Reminder])
async def get_reminders():
    return reminders_db

@router.get("/{reminder_id}", response_model=Reminder)
async def get_reminder(reminder_id: int):
    for reminder in reminders_db:
        if reminder.id == reminder_id:
            return reminder
    raise HTTPException(status_code=404, detail="Reminder not found")

@router.put("/{reminder_id}", response_model=Reminder)
async def update_reminder(reminder_id: int, reminder: ReminderCreate):
    for i, existing_reminder in enumerate(reminders_db):
        if existing_reminder.id == reminder_id:
            updated_reminder = Reminder(
                **reminder.model_dump(),
                id=reminder_id,
                created_at=existing_reminder.created_at,
                completed=existing_reminder.completed
            )
            reminders_db[i] = updated_reminder
            return updated_reminder
    raise HTTPException(status_code=404, detail="Reminder not found")

@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: int):
    for i, reminder in enumerate(reminders_db):
        if reminder.id == reminder_id:
            del reminders_db[i]
            return {"message": "Reminder deleted"}
    raise HTTPException(status_code=404, detail="Reminder not found")

@router.post("/{reminder_id}/complete")
async def complete_reminder(reminder_id: int):
    for reminder in reminders_db:
        if reminder.id == reminder_id:
            reminder.completed = True
            return {"message": "Reminder marked as completed"}
    raise HTTPException(status_code=404, detail="Reminder not found") 