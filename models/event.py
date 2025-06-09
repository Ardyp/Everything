from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from .database import Base

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer)
    event_type = Column(String)
    description = Column(String)
    severity = Column(String, default="info")
    metadata = Column(JSON, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow)
