from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    responses={404: {"description": "Not found"}},
)

class ItemBase(BaseModel):
    name: str
    category: str
    quantity: int
    unit: str = "pieces"  # pieces, kg, liters, etc.
    location: Optional[str] = None
    min_quantity: Optional[int] = None
    notes: Optional[str] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    last_updated: datetime
    needs_restock: bool = False

    class Config:
        from_attributes = True

# Temporary in-memory storage
items_db = []
item_id_counter = 1

@router.post("/items", response_model=Item)
async def create_item(item: ItemCreate):
    global item_id_counter
    new_item = Item(
        **item.model_dump(),
        id=item_id_counter,
        last_updated=datetime.now(),
        needs_restock=item.min_quantity is not None and item.quantity <= item.min_quantity
    )
    items_db.append(new_item)
    item_id_counter += 1
    return new_item

@router.get("/items", response_model=List[Item])
async def get_items(
    category: Optional[str] = None,
    needs_restock: Optional[bool] = None
):
    filtered_items = items_db
    
    if category:
        filtered_items = [i for i in filtered_items if i.category == category]
    if needs_restock is not None:
        filtered_items = [i for i in filtered_items if i.needs_restock == needs_restock]
    
    return filtered_items

@router.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int):
    for item in items_db:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")

@router.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemCreate):
    for i, existing_item in enumerate(items_db):
        if existing_item.id == item_id:
            updated_item = Item(
                **item.model_dump(),
                id=item_id,
                last_updated=datetime.now(),
                needs_restock=item.min_quantity is not None and item.quantity <= item.min_quantity
            )
            items_db[i] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")

@router.delete("/items/{item_id}")
async def delete_item(item_id: int):
    for i, item in enumerate(items_db):
        if item.id == item_id:
            del items_db[i]
            return {"message": "Item deleted"}
    raise HTTPException(status_code=404, detail="Item not found")

@router.get("/categories")
async def get_categories():
    return list(set(item.category for item in items_db))

@router.get("/low-stock", response_model=List[Item])
async def get_low_stock_items():
    return [item for item in items_db if item.needs_restock] 