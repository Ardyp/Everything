from enum import Enum
from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime

class DeviceStatus(str, Enum):
    ON = "on"
    OFF = "off"

class SecurityStatus(str, Enum):
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    ARMED = "armed"
    DISARMED = "disarmed"
    OPEN = "open"
    CLOSED = "closed"

class PlantStatus(str, Enum):
    GOOD = "good"
    LOW = "low"
    CRITICAL = "critical"

class Plant(BaseModel):
    last_watered: datetime
    moisture_level: PlantStatus
    needs_water: bool
    notes: Optional[str] = Field(None, max_length=500)

class HomeStatus(BaseModel):
    temperature: Dict[str, float] = Field(..., description="Temperature by room in Fahrenheit")
    lights: Dict[str, DeviceStatus]
    security: Dict[str, SecurityStatus]
    plants: Dict[str, Plant]
    last_updated: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True 