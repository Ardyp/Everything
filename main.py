from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from agents.smart_home.main import router as smart_home_router
from agents.life_organizer.main import router as life_organizer_router
from agents.inventory_manager.main import router as inventory_router
from agents.commute_monitor.main import router as commute_router
from agents.health_tracker.main import router as health_router
from voice.voice_router import router as voice_router

load_dotenv()

app = FastAPI(title="Everything App", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(smart_home_router)
app.include_router(life_organizer_router)
app.include_router(inventory_router)
app.include_router(commute_router)
app.include_router(health_router)
app.include_router(voice_router, prefix="/voice")

@app.get("/")
async def root():
    return {"message": "Everything App running"}
