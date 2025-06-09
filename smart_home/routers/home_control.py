from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from models import Device as DeviceModel, get_db

router = APIRouter(
    prefix="/home",
    tags=["home control"],
    responses={404: {"description": "Not found"}},
)

class DeviceBase(BaseModel):
    name: str
    type: str  # light, thermostat, camera, etc.
    location: str  # room or area
    status: str = "off"  # on/off/other states
    settings: dict = {}  # flexible settings storage

class DeviceCreate(DeviceBase):
    pass

class Device(DeviceBase):
    id: int
    last_updated: datetime

    class Config:
        from_attributes = True

# Temporary in-memory storage

@router.post("/devices", response_model=Device)
async def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    db_device = DeviceModel(
        **device.model_dump(),
        last_updated=datetime.now()
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return Device.model_validate(db_device)

@router.get("/devices", response_model=List[Device])
async def get_devices(db: Session = Depends(get_db)):
    devices = db.query(DeviceModel).all()
    return [Device.model_validate(d) for d in devices]

@router.get("/devices/{device_id}", response_model=Device)
async def get_device(device_id: int, db: Session = Depends(get_db)):
    dev = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    return Device.model_validate(dev)

@router.put("/devices/{device_id}/status/{new_status}")
async def update_device_status(device_id: int, new_status: str, db: Session = Depends(get_db)):
    dev = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    dev.status = new_status
    dev.last_updated = datetime.now()
    db.commit()
    return {"message": f"Device status updated to {new_status}"}

@router.put("/devices/{device_id}/settings")
async def update_device_settings(device_id: int, settings: dict, db: Session = Depends(get_db)):
    dev = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    dev.settings.update(settings)
    dev.last_updated = datetime.now()
    db.commit()
    return {"message": "Device settings updated"}

@router.delete("/devices/{device_id}")
async def delete_device(device_id: int, db: Session = Depends(get_db)):
    dev = db.query(DeviceModel).filter(DeviceModel.id == device_id).first()
    if not dev:
        raise HTTPException(status_code=404, detail="Device not found")
    db.delete(dev)
    db.commit()
    return {"message": "Device deleted"}
