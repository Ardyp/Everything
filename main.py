from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import os
from dotenv import load_dotenv
from task_scheduler import router as scheduler_router, scheduler, add_scheduled_jobs
from life_organizer.routers import reminders, appointments, location
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
app.include_router(scheduler_router)

@app.get("/")
async def root():
    return {
        "message": "Welcome to Everything App",
        "docs_url": "/docs",
        "modules": [
            "Life Organizer (reminders, appointments, location)",
            "Smart Home (home control, events)",
            "Inventory Manager (inventory, receipts)",
            "OS Manager (system info, file system, process management)"
        ]
    }


@app.on_event("startup")
async def start_scheduler():
    add_scheduled_jobs()
    scheduler.start()


@app.on_event("shutdown")
async def stop_scheduler():
    scheduler.shutdown()

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
