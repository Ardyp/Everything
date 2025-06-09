from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ItemCategory(str, Enum):
    SNACKS = "snacks"
    GROCERIES = "groceries"
    HOUSEHOLD = "household"
    OTHER = "other"

class ItemUnit(str, Enum):
    PIECES = "pieces"
    BAGS = "bags"
    BOXES = "boxes"
    BOTTLES = "bottles"
    CANS = "cans"
    POUNDS = "pounds"
    GALLONS = "gallons"
    GRAMS = "grams"
    LITERS = "liters"

class InventoryItem(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    category: ItemCategory
    quantity: float = Field(..., ge=0)
    unit: ItemUnit
    expiry_date: Optional[datetime] = None
    last_updated: datetime = Field(default_factory=datetime.now)
    low_stock_threshold: float = Field(default=2.0, ge=0.1)
    notes: Optional[str] = Field(None, max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Potato Chips",
                "category": "snacks",
                "quantity": 3,
                "unit": "bags",
                "expiry_date": "2024-06-21T00:00:00Z",
                "low_stock_threshold": 2
            }
        }
        from_attributes = True 