from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

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
devices_db = []
device_id_counter = 1

@router.post("/devices", response_model=Device)
async def create_device(device: DeviceCreate):
    global device_id_counter
    new_device = Device(
        **device.model_dump(),
        id=device_id_counter,
        last_updated=datetime.now()
    )
    devices_db.append(new_device)
    device_id_counter += 1
    return new_device

@router.get("/devices", response_model=List[Device])
async def get_devices():
    return devices_db

@router.get("/devices/{device_id}", response_model=Device)
async def get_device(device_id: int):
    for device in devices_db:
        if device.id == device_id:
            return device
    raise HTTPException(status_code=404, detail="Device not found")

@router.put("/devices/{device_id}/status/{new_status}")
async def update_device_status(device_id: int, new_status: str):
    for device in devices_db:
        if device.id == device_id:
            device.status = new_status
            device.last_updated = datetime.now()
            return {"message": f"Device status updated to {new_status}"}
    raise HTTPException(status_code=404, detail="Device not found")

@router.put("/devices/{device_id}/settings")
async def update_device_settings(device_id: int, settings: dict):
    for device in devices_db:
        if device.id == device_id:
            device.settings.update(settings)
            device.last_updated = datetime.now()
            return {"message": "Device settings updated"}
    raise HTTPException(status_code=404, detail="Device not found")

@router.delete("/devices/{device_id}")
async def delete_device(device_id: int):
    for i, device in enumerate(devices_db):
        if device.id == device_id:
            del devices_db[i]
            return {"message": "Device deleted"}
    raise HTTPException(status_code=404, detail="Device not found") 