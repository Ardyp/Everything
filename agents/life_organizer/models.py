from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ReminderPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Reminder(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    due_date: datetime
    priority: ReminderPriority = ReminderPriority.MEDIUM
    completed: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Get milk, bread, and eggs",
                "due_date": "2024-03-22T15:00:00Z",
                "priority": "medium"
            }
        }
        from_attributes = True

class Appointment(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    date: datetime
    duration_minutes: int = Field(..., gt=0, le=480)  # Max 8 hours
    location: Optional[str] = Field(None, max_length=200)
    notes: Optional[str] = Field(None, max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Haircut",
                "date": "2024-03-22T14:00:00Z",
                "duration_minutes": 30,
                "location": "123 Main St"
            }
        }
        from_attributes = True 