from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import Reminder as ReminderModel, get_db

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

@router.post("/", response_model=Reminder)
async def create_reminder(reminder: ReminderCreate, db: Session = Depends(get_db)):
    db_reminder = ReminderModel(
        **reminder.model_dump(),
        created_at=datetime.now()
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return Reminder.model_validate(db_reminder)

@router.get("/", response_model=List[Reminder])
async def get_reminders(db: Session = Depends(get_db)):
    reminders = db.query(ReminderModel).all()
    return [Reminder.model_validate(r) for r in reminders]

@router.get("/{reminder_id}", response_model=Reminder)
async def get_reminder(reminder_id: int, db: Session = Depends(get_db)):
    reminder_obj = db.query(ReminderModel).filter(ReminderModel.id == reminder_id).first()
    if not reminder_obj:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return Reminder.model_validate(reminder_obj)

@router.put("/{reminder_id}", response_model=Reminder)
async def update_reminder(reminder_id: int, reminder: ReminderCreate, db: Session = Depends(get_db)):
    db_reminder = db.query(ReminderModel).filter(ReminderModel.id == reminder_id).first()
    if not db_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    for key, value in reminder.model_dump().items():
        setattr(db_reminder, key, value)
    db.commit()
    db.refresh(db_reminder)
    return Reminder.model_validate(db_reminder)

@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    db_reminder = db.query(ReminderModel).filter(ReminderModel.id == reminder_id).first()
    if not db_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    db.delete(db_reminder)
    db.commit()
    return {"message": "Reminder deleted"}

@router.post("/{reminder_id}/complete")
async def complete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    reminder_obj = db.query(ReminderModel).filter(ReminderModel.id == reminder_id).first()
    if not reminder_obj:
        raise HTTPException(status_code=404, detail="Reminder not found")
    reminder_obj.completed = True
    db.commit()
    return {"message": "Reminder marked as completed"}
