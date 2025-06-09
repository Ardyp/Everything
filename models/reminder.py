from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from .database import Base

class Reminder(Base):
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String, nullable=True)
    due_date = Column(DateTime)
    priority = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed = Column(Boolean, default=False)
