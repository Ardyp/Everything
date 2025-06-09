from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session
from agents.life_organizer.database import get_db, ReminderDB

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

# Database backed storage

@router.post("/", response_model=Reminder)
async def create_reminder(reminder: ReminderCreate, db: Session = Depends(get_db)):
    db_reminder = ReminderDB(
        title=reminder.title,
        description=reminder.description,
        due_date=reminder.due_date,
        priority=reminder.priority,
        completed=False,
        created_at=datetime.now(),
    )
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return Reminder(**reminder.model_dump(), id=db_reminder.id, created_at=db_reminder.created_at)

@router.get("/", response_model=List[Reminder])
async def get_reminders(db: Session = Depends(get_db)):
    reminders = db.query(ReminderDB).all()
    return [
        Reminder(
            id=r.id,
            title=r.title,
            description=r.description,
            due_date=r.due_date,
            priority=r.priority,
            created_at=r.created_at,
            completed=r.completed,
        )
        for r in reminders
    ]

@router.get("/{reminder_id}", response_model=Reminder)
async def get_reminder(reminder_id: int, db: Session = Depends(get_db)):
    r = db.query(ReminderDB).filter(ReminderDB.id == reminder_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return Reminder(
        id=r.id,
        title=r.title,
        description=r.description,
        due_date=r.due_date,
        priority=r.priority,
        created_at=r.created_at,
        completed=r.completed,
    )

@router.put("/{reminder_id}", response_model=Reminder)
async def update_reminder(reminder_id: int, reminder: ReminderCreate, db: Session = Depends(get_db)):
    db_reminder = db.query(ReminderDB).filter(ReminderDB.id == reminder_id).first()
    if not db_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")

    for field, value in reminder.model_dump().items():
        setattr(db_reminder, field, value)
    db.commit()
    db.refresh(db_reminder)
    return Reminder(
        id=db_reminder.id,
        title=db_reminder.title,
        description=db_reminder.description,
        due_date=db_reminder.due_date,
        priority=db_reminder.priority,
        created_at=db_reminder.created_at,
        completed=db_reminder.completed,
    )

@router.delete("/{reminder_id}")
async def delete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    db_reminder = db.query(ReminderDB).filter(ReminderDB.id == reminder_id).first()
    if not db_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    db.delete(db_reminder)
    db.commit()
    return {"message": "Reminder deleted"}

@router.post("/{reminder_id}/complete")
async def complete_reminder(reminder_id: int, db: Session = Depends(get_db)):
    db_reminder = db.query(ReminderDB).filter(ReminderDB.id == reminder_id).first()
    if not db_reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    db_reminder.completed = True
    db.commit()
    return {"message": "Reminder marked as completed"}
