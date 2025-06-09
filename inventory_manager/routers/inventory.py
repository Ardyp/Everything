from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from models import Item as ItemModel, get_db

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

@router.post("/items", response_model=Item)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = ItemModel(
        **item.model_dump(),
        last_updated=datetime.now(),
        needs_restock=item.min_quantity is not None and item.quantity <= (item.min_quantity or 0)
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return Item.model_validate(db_item)

@router.get("/items", response_model=List[Item])
async def get_items(
    category: Optional[str] = None,
    needs_restock: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ItemModel)
    if category:
        query = query.filter(ItemModel.category == category)
    if needs_restock is not None:
        query = query.filter(ItemModel.needs_restock == needs_restock)
    items = query.all()
    return [Item.model_validate(i) for i in items]

@router.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    item_obj = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not item_obj:
        raise HTTPException(status_code=404, detail="Item not found")
    return Item.model_validate(item_obj)

@router.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    for key, value in item.model_dump().items():
        setattr(db_item, key, value)
    db_item.last_updated = datetime.now()
    db_item.needs_restock = item.min_quantity is not None and item.quantity <= (item.min_quantity or 0)
    db.commit()
    db.refresh(db_item)
    return Item.model_validate(db_item)

@router.delete("/items/{item_id}")
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted"}

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(ItemModel.category).distinct().all()
    return [c[0] for c in categories]

@router.get("/low-stock", response_model=List[Item])
async def get_low_stock_items(db: Session = Depends(get_db)):
    items = db.query(ItemModel).filter(ItemModel.needs_restock == True).all()
    return [Item.model_validate(i) for i in items]
