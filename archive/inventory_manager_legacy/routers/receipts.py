from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

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
receipts_db = []
receipt_id_counter = 1

@router.post("/", response_model=Receipt)
async def create_receipt(receipt: ReceiptCreate):
    global receipt_id_counter
    new_receipt = Receipt(
        **receipt.model_dump(),
        id=receipt_id_counter,
        created_at=datetime.now()
    )
    receipts_db.append(new_receipt)
    receipt_id_counter += 1
    return new_receipt

@router.get("/", response_model=List[Receipt])
async def get_receipts(
    store_name: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    filtered_receipts = receipts_db
    
    if store_name:
        filtered_receipts = [r for r in filtered_receipts if r.store_name == store_name]
    if start_date:
        filtered_receipts = [r for r in filtered_receipts if r.purchase_date >= start_date]
    if end_date:
        filtered_receipts = [r for r in filtered_receipts if r.purchase_date <= end_date]
    
    return filtered_receipts

@router.get("/{receipt_id}", response_model=Receipt)
async def get_receipt(receipt_id: int):
    for receipt in receipts_db:
        if receipt.id == receipt_id:
            return receipt
    raise HTTPException(status_code=404, detail="Receipt not found")

@router.delete("/{receipt_id}")
async def delete_receipt(receipt_id: int):
    for i, receipt in enumerate(receipts_db):
        if receipt.id == receipt_id:
            del receipts_db[i]
            return {"message": "Receipt deleted"}
    raise HTTPException(status_code=404, detail="Receipt not found")

@router.get("/stores")
async def get_stores():
    return list(set(receipt.store_name for receipt in receipts_db))

@router.get("/summary")
async def get_expense_summary(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    filtered_receipts = receipts_db
    
    if start_date:
        filtered_receipts = [r for r in filtered_receipts if r.purchase_date >= start_date]
    if end_date:
        filtered_receipts = [r for r in filtered_receipts if r.purchase_date <= end_date]
    
    total_spent = sum(r.total_amount for r in filtered_receipts)
    store_totals = {}
    for receipt in filtered_receipts:
        store_totals[receipt.store_name] = store_totals.get(receipt.store_name, 0) + receipt.total_amount
    
    return {
        "total_spent": total_spent,
        "receipt_count": len(filtered_receipts),
        "store_totals": store_totals
    } 