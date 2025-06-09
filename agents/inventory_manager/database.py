from sqlalchemy import create_engine, Column, Integer, String, DateTime, Enum as SQLEnum, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
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