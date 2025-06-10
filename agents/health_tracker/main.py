"""Simple health tracking agent for gym check-ins."""
from fastapi import APIRouter, Depends
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.orm import Session
from datetime import datetime
from database.db import engine, get_db
from database.models import Base

router = APIRouter(prefix="/health", tags=["health"])


class GymCheckInDB(Base):
    __tablename__ = "gym_checkins"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


# Ensure table is created
Base.metadata.create_all(bind=engine)


@router.post("/gym/check-in")
async def gym_check_in(db: Session = Depends(get_db)):
    entry = GymCheckInDB()
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"message": "Checked in", "time": entry.timestamp.isoformat()}


@router.get("/gym/summary")
async def gym_summary(db: Session = Depends(get_db)):
    count = db.query(GymCheckInDB).count()
    return {"total_checkins": count}
