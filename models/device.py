from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from .database import Base

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    type = Column(String)
    location = Column(String)
    status = Column(String, default="off")
    settings = Column(JSON, default=dict)
    last_updated = Column(DateTime, default=datetime.utcnow)
