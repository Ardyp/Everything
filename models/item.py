from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from .database import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, index=True)
    quantity = Column(Float)
    unit = Column(String)
    location = Column(String, nullable=True)
    min_quantity = Column(Float, nullable=True)
    notes = Column(String, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    needs_restock = Column(Boolean, default=False)
