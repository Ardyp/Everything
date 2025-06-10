from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .database import get_db, ReminderDB, AppointmentDB
from .models import ReminderPriority, Reminder, Appointment

router = APIRouter(prefix="/organizer", tags=["life organizer"])

@router.post("/reminder", response_model=Reminder)
async def create_reminder(
    reminder: Reminder,
    db: Session = Depends(get_db)
) -> Reminder:
    """Create a new reminder."""
    if reminder.due_date < datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Due date cannot be in the past"
        )
    
    db_reminder = ReminderDB(**reminder.dict())
    db.add(db_reminder)
    db.commit()
    db.refresh(db_reminder)
    return Reminder.from_orm(db_reminder)

@router.get("/reminder", response_model=List[Reminder])
async def get_reminders(
    completed: Optional[bool] = None,
    priority: Optional[ReminderPriority] = None,
    limit: int = Query(default=50, gt=0, le=100),
    db: Session = Depends(get_db)
) -> List[Reminder]:
    """Get all reminders, optionally filtered by completion status and priority."""
    query = db.query(ReminderDB)
    
    if completed is not None:
        query = query.filter(ReminderDB.completed == completed)
    
    if priority:
        query = query.filter(ReminderDB.priority == priority)
    
    # Sort by due date and priority
    query = query.order_by(ReminderDB.due_date, ReminderDB.priority)
    
    reminders = query.limit(limit).all()
    return [Reminder.from_orm(r) for r in reminders]

@router.post("/appointment", response_model=Appointment)
async def book_appointment(
    appointment: Appointment,
    db: Session = Depends(get_db)
) -> Appointment:
    """Book a new appointment."""
    if appointment.date < datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Appointment date cannot be in the past"
        )
    
    # Check for conflicts with more precise timing
    appointment_end = appointment.date.replace(
        minute=appointment.date.minute + appointment.duration_minutes
    )
    
    # Query for conflicting appointments
    conflicts = db.query(AppointmentDB).filter(
        (
            (AppointmentDB.date <= appointment.date) &
            (AppointmentDB.date.op('+').__call__(AppointmentDB.duration_minutes * 60) > appointment.date)
        ) |
        (
            (AppointmentDB.date < appointment_end) &
            (AppointmentDB.date.op('+').__call__(AppointmentDB.duration_minutes * 60) >= appointment_end)
        )
    ).first()
    
    if conflicts:
        raise HTTPException(
            status_code=400,
            detail="Scheduling conflict: Another appointment exists during this time"
        )
    
    db_appointment = AppointmentDB(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return Appointment.from_orm(db_appointment)

@router.get("/summary")
async def get_summary(db: Session = Depends(get_db)) -> dict:
    """Get a summary of current tasks and appointments."""
    now = datetime.now()
    
    # Get pending reminders
    pending_reminders = db.query(ReminderDB).filter(
        ReminderDB.completed == False
    ).order_by(ReminderDB.due_date).all()
    
    # Get upcoming appointments
    upcoming_appointments = db.query(AppointmentDB).filter(
        AppointmentDB.date >= now
    ).order_by(AppointmentDB.date).all()
    
    return {
        "pending_reminders_count": len(pending_reminders),
        "upcoming_appointments_count": len(upcoming_appointments),
        "high_priority_reminders": len([r for r in pending_reminders if r.priority == ReminderPriority.HIGH]),
        "next_reminder": Reminder.from_orm(pending_reminders[0]).dict() if pending_reminders else None,
        "next_appointment": Appointment.from_orm(upcoming_appointments[0]).dict() if upcoming_appointments else None,
        "overdue_reminders": len([r for r in pending_reminders if r.due_date < now])
    }

@router.get("/calendar", response_model=List[Appointment])
async def get_calendar(
    view: str = Query("day", pattern="^(day|week)$"),
    db: Session = Depends(get_db)
) -> List[Appointment]:
    """Return appointments for today or the next 7 days."""
    now = datetime.now()
    end = now + (timedelta(days=7) if view == "week" else timedelta(days=1))
    appointments = db.query(AppointmentDB).filter(
        AppointmentDB.date >= now,
        AppointmentDB.date < end
    ).order_by(AppointmentDB.date).all()
    return [Appointment.from_orm(a) for a in appointments]

@router.put("/reminder/{reminder_id}/complete")
async def complete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """Mark a reminder as completed."""
    reminder = db.query(ReminderDB).filter(ReminderDB.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    reminder.completed = True
    db.commit()
    return {"message": "Reminder marked as completed"}

@router.delete("/reminder/{reminder_id}")
async def delete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """Delete a reminder."""
    reminder = db.query(ReminderDB).filter(ReminderDB.id == reminder_id).first()
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    
    db.delete(reminder)
    db.commit()
    return {"message": "Reminder deleted"}

@router.delete("/appointment/{appointment_id}")
async def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db)
) -> dict:
    """Cancel an appointment."""
    appointment = db.query(AppointmentDB).filter(AppointmentDB.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    if appointment.date < datetime.now():
        raise HTTPException(status_code=400, detail="Cannot cancel past appointments")
    
    db.delete(appointment)
    db.commit()
    return {"message": "Appointment cancelled"}

# Stretch feature placeholders
"""
@router.post("/calendar/sync")
async def sync_with_google_calendar():
    # TODO: Implement Google Calendar integration
    # from google.oauth2.credentials import Credentials
    # from googleapiclient.discovery import build
    pass

@router.post("/reminder/natural")
async def create_natural_language_reminder():
    # TODO: Implement OpenAI integration for natural language processing
    pass
""" 