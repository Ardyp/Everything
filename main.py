from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
import uvicorn
from pathlib import Path
import os
from dotenv import load_dotenv
from life_organizer.routers import reminders, appointments, location
from smart_home.routers import home_control, events
from inventory_manager.routers import inventory, receipts
from os_manager.routers import system_info, file_system, process_mgmt
from auth import router as auth_router

# Load environment variables at startup
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Everything App",
    description="A modular FastAPI application for managing your life, home, inventory, and system",
    version="1.0.0"
)

# Configure CORS and HTTPS
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if os.getenv("ENV", "development").lower() == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

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

# Auth
app.include_router(auth_router)

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
