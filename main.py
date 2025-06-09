from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import os
from dotenv import load_dotenv
from life_organizer.routers import (
    reminders,
    appointments,
    location,
    calendar,
    notifications,
)
from life_organizer import scheduler as organizer_scheduler
from smart_home.routers import home_control, events
from inventory_manager.routers import inventory, receipts
from os_manager.routers import system_info, file_system, process_mgmt

# Load environment variables at startup
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Everything App",
    description="A modular FastAPI application for managing your life, home, inventory, and system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
# Life Organizer
app.include_router(reminders)
app.include_router(appointments)
app.include_router(location)  # New location router
app.include_router(calendar)
app.include_router(notifications)

# Start background scheduler for notifications
organizer_scheduler.start()
# Smart Home
app.include_router(home_control)
app.include_router(events)

# Inventory Manager
app.include_router(inventory)
app.include_router(receipts)

# OS Manager
app.include_router(system_info)
app.include_router(file_system)
app.include_router(process_mgmt)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Everything App",
        "docs_url": "/docs",
        "modules": [
            "Life Organizer (reminders, appointments, location, calendar, notifications)",
            "Smart Home (home control, events)",
            "Inventory Manager (inventory, receipts)",
            "OS Manager (system info, file system, process management)"
        ]
    }

if __name__ == "__main__":
    # Ensure required directories exist
    Path("mock_data").mkdir(exist_ok=True)
    
    # Start the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )
