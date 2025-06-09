from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from .database import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String, nullable=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    location = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="scheduled")
