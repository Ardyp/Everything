from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
import os
from dotenv import load_dotenv

from agents.smart_home.main import router as smart_home_router
from agents.life_organizer.main import router as organizer_router
from agents.inventory_manager.main import router as inventory_router
from agents.commute_monitor.main import router as commute_router
from agents.health_tracker.main import router as health_router
from voice.voice_router import router as voice_router
from os_manager.routers import system_info, file_system, process_mgmt

# Load environment variables at startup
load_dotenv()

app = FastAPI(
    title="Everything App",
    description="A modular FastAPI application for managing your life, home, inventory, and health",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for each agent
app.include_router(smart_home_router)
app.include_router(organizer_router)
app.include_router(inventory_router)
app.include_router(commute_router)
app.include_router(health_router)
app.include_router(voice_router)

# Existing OS management utilities
app.include_router(system_info)
app.include_router(file_system)
app.include_router(process_mgmt)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Everything App",
        "docs_url": "/docs",
    }


if __name__ == "__main__":
    Path("mock_data").mkdir(exist_ok=True)
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True,
    )
