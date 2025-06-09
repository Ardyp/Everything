from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, JSON, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
from typing import Dict, Any
from .models import DeviceStatus, SecurityStatus, PlantStatus

# Create database engine
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smart_home.db")
engine = create_engine(DATABASE_URL)

# Create declarative base
Base = declarative_base()

class HomeStateDB(Base):
    """Database model for home state"""
    __tablename__ = "home_state"

    id = Column(Integer, primary_key=True, index=True)
    temperature = Column(JSON)  # Store temperature readings as JSON
    lights = Column(JSON)  # Store light statuses as JSON
    security = Column(JSON)  # Store security statuses as JSON
    plants = Column(JSON)  # Store plant data as JSON
    last_updated = Column(DateTime, default=datetime.now)

    @property
    def temperature_dict(self) -> Dict[str, float]:
        return self.temperature or {}

    @property
    def lights_dict(self) -> Dict[str, DeviceStatus]:
        return {k: DeviceStatus(v) for k, v in (self.lights or {}).items()}

    @property
    def security_dict(self) -> Dict[str, SecurityStatus]:
        return {k: SecurityStatus(v) for k, v in (self.security or {}).items()}

    @property
    def plants_dict(self) -> Dict[str, Dict[str, Any]]:
        plants_data = self.plants or {}
        return {
            name: {
                "last_watered": datetime.fromisoformat(data["last_watered"]),
                "moisture_level": PlantStatus(data["moisture_level"]),
                "needs_water": data["needs_water"],
                "notes": data.get("notes")
            }
            for name, data in plants_data.items()
        }

class EventLogDB(Base):
    """Database model for event logging"""
    __tablename__ = "event_log"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    event_type = Column(String(50))  # e.g., "arrival", "light_control", "security_change"
    details = Column(JSON)  # Store event details as JSON


class DeviceDB(Base):
    """Database model for smart home devices"""
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    type = Column(String(50))
    location = Column(String(100))
    status = Column(SQLEnum(DeviceStatus), default=DeviceStatus.OFF)
    settings = Column(JSON, default={})
    last_updated = Column(DateTime, default=datetime.now)

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

def log_event(db, event_type: str, details: Dict[str, Any]) -> None:
    """Log an event to the database"""
    event = EventLogDB(
        event_type=event_type,
        details=details
    )
    db.add(event)
    db.commit() 