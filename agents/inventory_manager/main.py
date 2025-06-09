from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Depends
from typing import Dict, List, Optional, Set, Any
from datetime import datetime
from sqlalchemy.orm import Session
import pytesseract
from PIL import Image
import io
import re
from .database import get_db, InventoryItemDB
from .models import ItemCategory, ItemUnit, InventoryItem

router = APIRouter()

def normalize_item_name(name: str) -> str:
    """Normalize item name for consistent storage and retrieval."""
    return name.lower().strip()

def extract_items_from_receipt(text: str) -> List[dict]:
    """
    Extract items from receipt text using regex patterns.
    This is a basic implementation - can be enhanced with ML/AI for better accuracy.
    """
    # Example pattern: looking for quantity and item name
    # Pattern matches: "2 MILK", "1.5 LB APPLES", "3 BOXES CEREAL"
    pattern = r'(\d+\.?\d*)\s*(?:(?:' + '|'.join(unit.value for unit in ItemUnit) + r')\s+)?([A-Za-z\s]+)'
    matches = re.finditer(pattern, text)
    
    items = []
    for match in matches:
        quantity = float(match.group(1))
        name = match.group(2).strip()
        
        # Basic categorization - can be enhanced with ML/AI
        category = ItemCategory.OTHER
        if any(word in name.lower() for word in ["chips", "candy", "snack"]):
            category = ItemCategory.SNACKS
        elif any(word in name.lower() for word in ["milk", "bread", "fruit", "vegetable"]):
            category = ItemCategory.GROCERIES
        elif any(word in name.lower() for word in ["soap", "paper", "cleaner"]):
            category = ItemCategory.HOUSEHOLD
            
        items.append({
            "name": name,
            "quantity": quantity,
            "category": category,
            "unit": ItemUnit.PIECES  # Default unit - can be enhanced
        })
    
    return items

@router.post("/upload")
async def upload_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Upload and process a receipt image using OCR."""
    try:
        # Read and process image
        content = await file.read()
        image = Image.open(io.BytesIO(content))
        
        # Perform OCR
        text = pytesseract.image_to_string(image)
        
        # Extract items from OCR text
        extracted_items = extract_items_from_receipt(text)
        
        # Update inventory
        updated_items = []
        for item_data in extracted_items:
            normalized_name = normalize_item_name(item_data["name"])
            
            # Check if item exists
            db_item = db.query(InventoryItemDB).filter(
                InventoryItemDB.name == normalized_name
            ).first()
            
            if db_item:
                # Update existing item
                db_item.quantity += item_data["quantity"]
                db_item.last_updated = datetime.now()
            else:
                # Create new item
                db_item = InventoryItemDB(
                    name=normalized_name,
                    category=item_data["category"],
                    quantity=item_data["quantity"],
                    unit=item_data["unit"]
                )
                db.add(db_item)
            
            updated_items.append(item_data["name"])
        
        db.commit()
        
        return {
            "status": "success",
            "message": f"Receipt processed. Added/updated {len(updated_items)} items.",
            "processed_items": updated_items
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing receipt: {str(e)}")

@router.get("/snacks", response_model=List[InventoryItem])
async def get_snacks(
    min_quantity: Optional[float] = Query(None, ge=0),
    include_expired: bool = Query(False, description="Include expired items"),
    db: Session = Depends(get_db)
) -> List[InventoryItem]:
    """Get all snack items in inventory."""
    query = db.query(InventoryItemDB).filter(
        InventoryItemDB.category == ItemCategory.SNACKS
    )
    
    if not include_expired:
        query = query.filter(
            (InventoryItemDB.expiry_date is None) |
            (InventoryItemDB.expiry_date > datetime.now())
        )
    
    if min_quantity is not None:
        query = query.filter(InventoryItemDB.quantity >= min_quantity)
    
    items = query.order_by(
        InventoryItemDB.expiry_date.nullslast(),
        InventoryItemDB.name
    ).all()
    
    return [InventoryItem.from_orm(item) for item in items]

@router.post("/inventory/update", response_model=InventoryItem)
async def update_inventory(
    item: InventoryItem,
    db: Session = Depends(get_db)
) -> InventoryItem:
    """Update or add an item to inventory."""
    if item.expiry_date and item.expiry_date < datetime.now():
        raise HTTPException(
            status_code=400,
            detail="Cannot add item with past expiry date"
        )
    
    normalized_name = normalize_item_name(item.name)
    db_item = db.query(InventoryItemDB).filter(
        InventoryItemDB.name == normalized_name
    ).first()
    
    if db_item:
        # Update existing item
        for key, value in item.dict(exclude={"last_updated"}).items():
            setattr(db_item, key, value)
        db_item.last_updated = datetime.now()
    else:
        # Create new item
        db_item = InventoryItemDB(**item.dict())
        db.add(db_item)
    
    db.commit()
    db.refresh(db_item)
    return InventoryItem.from_orm(db_item)

@router.get("/inventory/low", response_model=List[InventoryItem])
async def get_low_inventory(
    categories: Optional[Set[ItemCategory]] = Query(None),
    exclude_expired: bool = Query(True, description="Exclude expired items"),
    db: Session = Depends(get_db)
) -> List[InventoryItem]:
    """Get items with quantity below their low stock threshold."""
    query = db.query(InventoryItemDB).filter(
        InventoryItemDB.quantity < InventoryItemDB.low_stock_threshold
    )
    
    if categories:
        query = query.filter(InventoryItemDB.category.in_(categories))
    
    if exclude_expired:
        query = query.filter(
            (InventoryItemDB.expiry_date is None) |
            (InventoryItemDB.expiry_date > datetime.now())
        )
    
    items = query.order_by(
        InventoryItemDB.quantity,
        InventoryItemDB.name
    ).all()
    
    return [InventoryItem.from_orm(item) for item in items]

@router.delete("/inventory/{item_name}")
async def delete_item(
    item_name: str,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Delete an item from inventory."""
    normalized_name = normalize_item_name(item_name)
    db_item = db.query(InventoryItemDB).filter(
        InventoryItemDB.name == normalized_name
    ).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()
    
    return {"message": f"Item '{item_name}' deleted successfully"}

# Stretch feature placeholders
"""
@router.post("/order")
async def place_order():
    # TODO: Integrate with grocery delivery APIs
    pass

@router.post("/barcode")
async def scan_barcode():
    # TODO: Integrate with barcode scanning and product database APIs
    pass
""" 