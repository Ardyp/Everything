from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy.orm import Session
from agents.smart_home.database import get_db, DeviceDB

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

# Database backed storage

@router.post("/devices", response_model=Device)
async def create_device(device: DeviceCreate, db: Session = Depends(get_db)):
    db_device = DeviceDB(
        name=device.name,
        type=device.type,
        location=device.location,
        status=device.status,
        settings=device.settings,
        last_updated=datetime.now(),
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return Device(
        id=db_device.id,
        last_updated=db_device.last_updated,
        **device.model_dump(),
    )

@router.get("/devices", response_model=List[Device])
async def get_devices(db: Session = Depends(get_db)):
    devices = db.query(DeviceDB).all()
    return [
        Device(
            id=d.id,
            name=d.name,
            type=d.type,
            location=d.location,
            status=d.status,
            settings=d.settings or {},
            last_updated=d.last_updated,
        )
        for d in devices
    ]

@router.get("/devices/{device_id}", response_model=Device)
async def get_device(device_id: int, db: Session = Depends(get_db)):
    d = db.query(DeviceDB).filter(DeviceDB.id == device_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Device not found")
    return Device(
        id=d.id,
        name=d.name,
        type=d.type,
        location=d.location,
        status=d.status,
        settings=d.settings or {},
        last_updated=d.last_updated,
    )

@router.put("/devices/{device_id}/status/{new_status}")
async def update_device_status(device_id: int, new_status: str, db: Session = Depends(get_db)):
    d = db.query(DeviceDB).filter(DeviceDB.id == device_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Device not found")
    d.status = new_status
    d.last_updated = datetime.now()
    db.commit()
    return {"message": f"Device status updated to {new_status}"}

@router.put("/devices/{device_id}/settings")
async def update_device_settings(device_id: int, settings: dict, db: Session = Depends(get_db)):
    d = db.query(DeviceDB).filter(DeviceDB.id == device_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Device not found")
    new_settings = d.settings or {}
    new_settings.update(settings)
    d.settings = new_settings
    d.last_updated = datetime.now()
    db.commit()
    return {"message": "Device settings updated"}

@router.delete("/devices/{device_id}")
async def delete_device(device_id: int, db: Session = Depends(get_db)):
    d = db.query(DeviceDB).filter(DeviceDB.id == device_id).first()
    if not d:
        raise HTTPException(status_code=404, detail="Device not found")
    db.delete(d)
    db.commit()
    return {"message": "Device deleted"}
