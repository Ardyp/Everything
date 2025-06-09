from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Dict, Any, Optional, List
import pyttsx3
from datetime import datetime
from sqlalchemy.orm import Session
from .database import get_db, HomeStateDB, EventLogDB, log_event
from .models import DeviceStatus, SecurityStatus, PlantStatus, Plant, HomeStatus

router = APIRouter()

# Initialize text-to-speech engine
try:
    engine = pyttsx3.init()
except Exception as e:
    print(f"Warning: TTS engine initialization failed: {e}")
    engine = None

def play_welcome_message(message: str) -> None:
    """Play welcome message using text-to-speech or fall back to print."""
    print(f"Welcome message: {message}")  # Fallback/logging
    if engine:
        try:
            engine.say(message)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS playback failed: {e}")

def get_current_home_status(db: Session) -> HomeStatus:
    """Load and validate current home status."""
    home_state = db.query(HomeStateDB).order_by(HomeStateDB.id.desc()).first()
    
    if not home_state:
        # Initialize with default values if no state exists
        home_state = HomeStateDB(
            temperature={"living_room": 72.0, "bedroom": 70.0, "kitchen": 73.0},
            lights={"living_room": "off", "bedroom": "off", "kitchen": "off"},
            security={"front_door": "locked", "back_door": "locked", "alarm_system": "armed"},
            plants={
                "living_room_fern": {
                    "last_watered": datetime.now().isoformat(),
                    "moisture_level": "good",
                    "needs_water": False,
                    "notes": None
                }
            },
            last_updated=datetime.now()
        )
        db.add(home_state)
        db.commit()
        db.refresh(home_state)
    
    return HomeStatus(
        temperature=home_state.temperature_dict,
        lights=home_state.lights_dict,
        security=home_state.security_dict,
        plants={
            name: Plant(**data)
            for name, data in home_state.plants_dict.items()
        },
        last_updated=home_state.last_updated
    )

@router.post("/arrive")
async def user_arrived(
    auto_lights: bool = Query(True, description="Automatically turn on lights"),
    disarm_security: bool = Query(True, description="Automatically disarm security system"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Handle user arrival at home."""
    try:
        # Load and validate current status
        home_status = get_current_home_status(db)
        
        # Update home state
        updates_made = []
        
        if auto_lights and all(status == DeviceStatus.OFF for status in home_status.lights.values()):
            # Turn on main lights if all are off
            home_status.lights["living_room"] = DeviceStatus.ON
            home_status.lights["kitchen"] = DeviceStatus.ON
            updates_made.append("turned on main lights")
        
        if disarm_security and home_status.security["alarm_system"] == SecurityStatus.ARMED:
            home_status.security["alarm_system"] = SecurityStatus.DISARMED
            updates_made.append("disarmed security system")
        
        # Check for items needing attention
        attention_items = []
        
        # Check plants
        for plant_name, plant in home_status.plants.items():
            if plant.needs_water:
                attention_items.append(f"{plant_name.replace('_', ' ')} needs water")
        
        # Check security
        if any(status == SecurityStatus.UNLOCKED for status in home_status.security.values()):
            attention_items.append("some doors are unlocked")
        
        # Generate welcome message
        welcome_msg = "Welcome home!"
        if updates_made:
            welcome_msg += f" I've {' and '.join(updates_made)}."
        if attention_items:
            welcome_msg += f" Please note: {', '.join(attention_items)}."
        
        # Save updated status
        home_status.last_updated = datetime.now()
        new_state = HomeStateDB(
            temperature=home_status.temperature,
            lights={k: v.value for k, v in home_status.lights.items()},
            security={k: v.value for k, v in home_status.security.items()},
            plants={
                name: {
                    "last_watered": plant.last_watered.isoformat(),
                    "moisture_level": plant.moisture_level.value,
                    "needs_water": plant.needs_water,
                    "notes": plant.notes
                }
                for name, plant in home_status.plants.items()
            },
            last_updated=home_status.last_updated
        )
        db.add(new_state)
        
        # Log the arrival event
        log_event(db, "arrival", {
            "updates": updates_made,
            "attention_needed": attention_items,
            "auto_lights": auto_lights,
            "disarm_security": disarm_security
        })
        
        db.commit()
        
        # Play welcome message
        play_welcome_message(welcome_msg)
        
        return {
            "message": "Welcome sequence completed",
            "welcome_message": welcome_msg,
            "updates": updates_made,
            "attention_needed": attention_items,
            "arrival_time": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing arrival: {str(e)}")

@router.get("/status")
async def get_home_status(
    include_temps: bool = Query(True, description="Include temperature readings"),
    include_security: bool = Query(True, description="Include security status"),
    include_plants: bool = Query(True, description="Include plant status"),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get current home status with optional filters."""
    try:
        home_status = get_current_home_status(db)
        response = {"last_updated": home_status.last_updated}
        
        if include_temps:
            response["temperature"] = home_status.temperature
        
        response["lights"] = home_status.lights
        
        if include_security:
            response["security"] = home_status.security
        
        if include_plants:
            response["plants"] = {
                name: plant.dict() 
                for name, plant in home_status.plants.items()
            }
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving home status: {str(e)}")

@router.post("/lights/{room}")
async def control_lights(
    room: str,
    status: DeviceStatus,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Control lights in a specific room."""
    try:
        home_status = get_current_home_status(db)
        
        if room not in home_status.lights:
            raise HTTPException(status_code=404, detail=f"Room '{room}' not found")
        
        home_status.lights[room] = status
        home_status.last_updated = datetime.now()
        
        # Save updated status
        new_state = HomeStateDB(
            temperature=home_status.temperature,
            lights={k: v.value for k, v in home_status.lights.items()},
            security={k: v.value for k, v in home_status.security.items()},
            plants={
                name: {
                    "last_watered": plant.last_watered.isoformat(),
                    "moisture_level": plant.moisture_level.value,
                    "needs_water": plant.needs_water,
                    "notes": plant.notes
                }
                for name, plant in home_status.plants.items()
            },
            last_updated=home_status.last_updated
        )
        db.add(new_state)
        
        # Log the light control event
        log_event(db, "light_control", {
            "room": room,
            "status": status.value,
            "previous_status": home_status.lights[room].value
        })
        
        db.commit()
        
        return {
            "message": f"Lights in {room} turned {status}",
            "room": room,
            "status": status
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error controlling lights: {str(e)}")

@router.get("/events")
async def get_events(
    event_type: Optional[str] = None,
    limit: int = Query(default=50, gt=0, le=100),
    db: Session = Depends(get_db)
) -> List[Dict[str, Any]]:
    """Get event history with optional filtering."""
    query = db.query(EventLogDB).order_by(EventLogDB.timestamp.desc())
    
    if event_type:
        query = query.filter(EventLogDB.event_type == event_type)
    
    events = query.limit(limit).all()
    return [
        {
            "id": event.id,
            "timestamp": event.timestamp,
            "event_type": event.event_type,
            "details": event.details
        }
        for event in events
    ]

# Stretch feature placeholders
"""
@router.post("/voice-command")
async def process_voice_command():
    # TODO: Integrate with OpenAI Whisper for voice processing
    pass

@router.get("/commute")
async def get_commute_status():
    # TODO: Integrate with NJ Transit + Google Maps APIs
    pass
""" 