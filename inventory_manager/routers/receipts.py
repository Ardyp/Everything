from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from agents.inventory_manager.database import get_db, ReceiptDB, ReceiptItemDB

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

# Database backed storage

@router.post("/", response_model=Receipt)
async def create_receipt(receipt: ReceiptCreate, db: Session = Depends(get_db)):
    db_receipt = ReceiptDB(
        store_name=receipt.store_name,
        purchase_date=receipt.purchase_date,
        total_amount=receipt.total_amount,
        payment_method=receipt.payment_method,
        notes=receipt.notes,
        created_at=datetime.now(),
    )
    db.add(db_receipt)
    db.commit()
    db.refresh(db_receipt)

    for item in receipt.items:
        db_item = ReceiptItemDB(
            receipt_id=db_receipt.id,
            item_name=item.item_name,
            quantity=item.quantity,
            unit_price=item.unit_price,
            total_price=item.total_price,
            category=item.category,
        )
        db.add(db_item)
    db.commit()

    return Receipt(
        id=db_receipt.id,
        created_at=db_receipt.created_at,
        **receipt.model_dump(),
    )

@router.get("/", response_model=List[Receipt])
async def get_receipts(
    store_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    query = db.query(ReceiptDB)

    if store_name:
        query = query.filter(ReceiptDB.store_name == store_name)
    if start_date:
        query = query.filter(ReceiptDB.purchase_date >= start_date)
    if end_date:
        query = query.filter(ReceiptDB.purchase_date <= end_date)

    receipts = query.all()
    results = []
    for r in receipts:
        items = db.query(ReceiptItemDB).filter(ReceiptItemDB.receipt_id == r.id).all()
        results.append(
            Receipt(
                id=r.id,
                store_name=r.store_name,
                purchase_date=r.purchase_date,
                total_amount=r.total_amount,
                payment_method=r.payment_method,
                notes=r.notes,
                created_at=r.created_at,
                items=[
                    ReceiptItemBase(
                        item_name=i.item_name,
                        quantity=i.quantity,
                        unit_price=i.unit_price,
                        total_price=i.total_price,
                        category=i.category,
                    )
                    for i in items
                ],
            )
        )
    return results

@router.get("/{receipt_id}", response_model=Receipt)
async def get_receipt(receipt_id: int, db: Session = Depends(get_db)):
    r = db.query(ReceiptDB).filter(ReceiptDB.id == receipt_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Receipt not found")
    items = db.query(ReceiptItemDB).filter(ReceiptItemDB.receipt_id == r.id).all()
    return Receipt(
        id=r.id,
        store_name=r.store_name,
        purchase_date=r.purchase_date,
        total_amount=r.total_amount,
        payment_method=r.payment_method,
        notes=r.notes,
        created_at=r.created_at,
        items=[
            ReceiptItemBase(
                item_name=i.item_name,
                quantity=i.quantity,
                unit_price=i.unit_price,
                total_price=i.total_price,
                category=i.category,
            )
            for i in items
        ],
    )

@router.delete("/{receipt_id}")
async def delete_receipt(receipt_id: int, db: Session = Depends(get_db)):
    r = db.query(ReceiptDB).filter(ReceiptDB.id == receipt_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Receipt not found")
    db.query(ReceiptItemDB).filter(ReceiptItemDB.receipt_id == receipt_id).delete()
    db.delete(r)
    db.commit()
    return {"message": "Receipt deleted"}

@router.get("/stores")
async def get_stores(db: Session = Depends(get_db)):
    stores = db.query(ReceiptDB.store_name).distinct().all()
    return [s[0] for s in stores]

@router.get("/summary")
async def get_expense_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    query = db.query(ReceiptDB)

    if start_date:
        query = query.filter(ReceiptDB.purchase_date >= start_date)
    if end_date:
        query = query.filter(ReceiptDB.purchase_date <= end_date)

    receipts = query.all()
    total_spent = sum(r.total_amount for r in receipts)
    store_totals = {}
    for r in receipts:
        store_totals[r.store_name] = store_totals.get(r.store_name, 0) + r.total_amount

    return {
        "total_spent": total_spent,
        "receipt_count": len(receipts),
        "store_totals": store_totals
    }
