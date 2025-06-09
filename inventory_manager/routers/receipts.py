from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from models import Receipt as ReceiptModel, get_db

router = APIRouter(
    prefix="/receipts",
    tags=["receipts"],
    responses={404: {"description": "Not found"}},
)

class ReceiptItemBase(BaseModel):
    item_name: str
    quantity: float
    unit_price: float
    total_price: float
    category: Optional[str] = None

class ReceiptBase(BaseModel):
    store_name: str
    purchase_date: datetime
    items: List[ReceiptItemBase]
    total_amount: float
    payment_method: str
    notes: Optional[str] = None

class ReceiptCreate(ReceiptBase):
    pass

class Receipt(ReceiptBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Temporary in-memory storage

@router.post("/", response_model=Receipt)
async def create_receipt(receipt: ReceiptCreate, db: Session = Depends(get_db)):
    db_receipt = ReceiptModel(
        **receipt.model_dump(),
        created_at=datetime.now()
    )
    db.add(db_receipt)
    db.commit()
    db.refresh(db_receipt)
    return Receipt.model_validate(db_receipt)

@router.get("/", response_model=List[Receipt])
async def get_receipts(
    store_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ReceiptModel)
    if store_name:
        query = query.filter(ReceiptModel.store_name == store_name)
    if start_date:
        query = query.filter(ReceiptModel.purchase_date >= start_date)
    if end_date:
        query = query.filter(ReceiptModel.purchase_date <= end_date)
    receipts = query.all()
    return [Receipt.model_validate(r) for r in receipts]

@router.get("/{receipt_id}", response_model=Receipt)
async def get_receipt(receipt_id: int, db: Session = Depends(get_db)):
    db_receipt = db.query(ReceiptModel).filter(ReceiptModel.id == receipt_id).first()
    if not db_receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return Receipt.model_validate(db_receipt)

@router.delete("/{receipt_id}")
async def delete_receipt(receipt_id: int, db: Session = Depends(get_db)):
    db_receipt = db.query(ReceiptModel).filter(ReceiptModel.id == receipt_id).first()
    if not db_receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")
    db.delete(db_receipt)
    db.commit()
    return {"message": "Receipt deleted"}

@router.get("/stores")
async def get_stores(db: Session = Depends(get_db)):
    stores = db.query(ReceiptModel.store_name).distinct().all()
    return [s[0] for s in stores]

@router.get("/summary")
async def get_expense_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    query = db.query(ReceiptModel)
    if start_date:
        query = query.filter(ReceiptModel.purchase_date >= start_date)
    if end_date:
        query = query.filter(ReceiptModel.purchase_date <= end_date)
    receipts = query.all()
    total_spent = sum(r.total_amount for r in receipts)
    store_totals = {}
    for r in receipts:
        store_totals[r.store_name] = store_totals.get(r.store_name, 0) + r.total_amount
    return {
        "total_spent": total_spent,
        "receipt_count": len(receipts),
        "store_totals": store_totals,
    }

