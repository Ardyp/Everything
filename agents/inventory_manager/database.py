from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Enum as SQLEnum,
    Float, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
from datetime import datetime
from typing import Optional
from .models import ItemCategory, ItemUnit

# Create database engine
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./inventory.db")
engine = create_engine(DATABASE_URL)

# Create declarative base
Base = declarative_base()

class InventoryItemDB(Base):
    """Database model for inventory items"""
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    category = Column(SQLEnum(ItemCategory))
    quantity = Column(Float)
    unit = Column(SQLEnum(ItemUnit))
    expiry_date = Column(DateTime, nullable=True)
    last_updated = Column(DateTime, default=datetime.now)
    low_stock_threshold = Column(Float, default=2.0)
    notes = Column(String(500), nullable=True)

class ReceiptDB(Base):
    """Database model for purchase receipts"""
    __tablename__ = "receipts"

    id = Column(Integer, primary_key=True, index=True)
    store_name = Column(String(100))
    purchase_date = Column(DateTime)
    total_amount = Column(Float)
    payment_method = Column(String(50))
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    items = relationship("ReceiptItemDB", back_populates="receipt", cascade="all, delete-orphan")


class ReceiptItemDB(Base):
    """Database model for receipt line items"""
    __tablename__ = "receipt_items"

    id = Column(Integer, primary_key=True, index=True)
    receipt_id = Column(Integer, ForeignKey("receipts.id"))
    item_name = Column(String(100))
    quantity = Column(Float)
    unit_price = Column(Float)
    total_price = Column(Float)
    category = Column(String(50), nullable=True)

    receipt = relationship("ReceiptDB", back_populates="items")

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