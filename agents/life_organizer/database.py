from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
from typing import Optional
from .models import ReminderPriority

# Create database engine
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./life_organizer.db")
engine = create_engine(DATABASE_URL)

# Create declarative base
Base = declarative_base()

class ReminderDB(Base):
    """Database model for reminders"""
    __tablename__ = "reminders"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    description = Column(String(500), nullable=True)
    due_date = Column(DateTime, index=True)
    priority = Column(SQLEnum(ReminderPriority))
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

class AppointmentDB(Base):
    """Database model for appointments"""
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), index=True)
    date = Column(DateTime, index=True)
    duration_minutes = Column(Integer)
    location = Column(String(200), nullable=True)
    notes = Column(String(500), nullable=True)

# Create tables
Base.metadata.create_all(bind=engine)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 