from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from agents.inventory_manager.database import get_db, InventoryItemDB
from agents.inventory_manager.models import ItemCategory, ItemUnit

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    responses={404: {"description": "Not found"}},
)

class ItemBase(BaseModel):
    name: str
    category: ItemCategory
    quantity: int
    unit: ItemUnit = ItemUnit.PIECES  # pieces, kg, liters, etc.
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

# Database interactions via SQLAlchemy

@router.post("/items", response_model=Item)
async def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = InventoryItemDB(
        name=item.name,
        category=item.category,
        quantity=item.quantity,
        unit=item.unit,
        notes=item.notes,
        low_stock_threshold=item.min_quantity or 0,
        last_updated=datetime.now(),
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return Item(
        **item.model_dump(),
        id=db_item.id,
        last_updated=db_item.last_updated,
        needs_restock=db_item.quantity <= db_item.low_stock_threshold if db_item.low_stock_threshold else False,
    )

@router.get("/items", response_model=List[Item])
async def get_items(
    category: Optional[ItemCategory] = None,
    needs_restock: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    query = db.query(InventoryItemDB)

    if category:
        query = query.filter(InventoryItemDB.category == category)
    items = query.all()

    results = []
    for db_item in items:
        restock = (
            db_item.low_stock_threshold is not None
            and db_item.quantity <= db_item.low_stock_threshold
        )
        if needs_restock is None or restock == needs_restock:
            results.append(
                Item(
                    id=db_item.id,
                    name=db_item.name,
                    category=db_item.category,
                    quantity=db_item.quantity,
                    unit=db_item.unit,
                    notes=db_item.notes,
                    min_quantity=db_item.low_stock_threshold,
                    last_updated=db_item.last_updated,
                    needs_restock=restock,
                )
            )

    return results

@router.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(InventoryItemDB).filter(InventoryItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    restock = (
        db_item.low_stock_threshold is not None
        and db_item.quantity <= db_item.low_stock_threshold
    )
    return Item(
        id=db_item.id,
        name=db_item.name,
        category=db_item.category,
        quantity=db_item.quantity,
        unit=db_item.unit,
        notes=db_item.notes,
        min_quantity=db_item.low_stock_threshold,
        last_updated=db_item.last_updated,
        needs_restock=restock,
    )

@router.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: ItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(InventoryItemDB).filter(InventoryItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    for field, value in item.model_dump().items():
        if field == "min_quantity":
            setattr(db_item, "low_stock_threshold", value)
        else:
            setattr(db_item, field, value)
    db_item.last_updated = datetime.now()
    db.commit()
    db.refresh(db_item)

    restock = (
        db_item.low_stock_threshold is not None
        and db_item.quantity <= db_item.low_stock_threshold
    )

    return Item(
        id=db_item.id,
        name=db_item.name,
        category=db_item.category,
        quantity=db_item.quantity,
        unit=db_item.unit,
        notes=db_item.notes,
        min_quantity=db_item.low_stock_threshold,
        last_updated=db_item.last_updated,
        needs_restock=restock,
    )

@router.delete("/items/{item_id}")
async def delete_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(InventoryItemDB).filter(InventoryItemDB.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(db_item)
    db.commit()
    return {"message": "Item deleted"}

@router.get("/categories")
async def get_categories(db: Session = Depends(get_db)):
    categories = db.query(InventoryItemDB.category).distinct().all()
    return [c[0] for c in categories]

@router.get("/low-stock", response_model=List[Item])
async def get_low_stock_items(db: Session = Depends(get_db)):
    items = db.query(InventoryItemDB).all()
    results = []
    for db_item in items:
        restock = (
            db_item.low_stock_threshold is not None
            and db_item.quantity <= db_item.low_stock_threshold
        )
        if restock:
            results.append(
                Item(
                    id=db_item.id,
                    name=db_item.name,
                    category=db_item.category,
                    quantity=db_item.quantity,
                    unit=db_item.unit,
                    notes=db_item.notes,
                    min_quantity=db_item.low_stock_threshold,
                    last_updated=db_item.last_updated,
                    needs_restock=restock,
                )
            )
    return results
