from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from .database import Base

class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    store_name = Column(String)
    purchase_date = Column(DateTime)
    items = Column(JSON)
    total_amount = Column(Float)
    payment_method = Column(String)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
