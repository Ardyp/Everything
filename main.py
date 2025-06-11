from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import os
from dotenv import load_dotenv
from agents.life_organizer.main import router as life_organizer_router
from agents.smart_home.main import router as smart_home_router
from agents.inventory_manager.main import router as inventory_router
from life_organizer.routers import location
from os_manager.routers import system_info, file_system, process_mgmt
from voice_assistant import router as voice_router

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
app.include_router(life_organizer_router, prefix="/organizer")
app.include_router(location)  # Location features remain standalone

# Smart Home
app.include_router(smart_home_router, prefix="/smart-home")

# Inventory Manager
app.include_router(inventory_router, prefix="/inventory")

# OS Manager
app.include_router(system_info)
app.include_router(file_system)
app.include_router(process_mgmt)

# Voice Assistant
app.include_router(voice_router)

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
