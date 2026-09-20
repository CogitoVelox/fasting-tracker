from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import settings
from app.db import Base, engine, get_db
from app.models import Fast
from app.schemas import FastEnd, FastRead
from app.streak import compute_streak


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Fasting Tracker", lifespan=lifespan)


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        raise HTTPException(status_code=503, detail="database unavoidable")
    return {"status": "ready"}


@app.get("/fasts/current", response_model=FastRead)
def current_fast(db: Session = Depends(get_db)):
    fast = db.query(Fast).filter(Fast.ended_at.is_(None)).first()
    if fast is None:
        raise HTTPException(status_code=404, detail="no fast in progress")
    return fast


@app.get("/fasts", response_model=list[FastRead])
def list_fasts(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Fast).order_by(Fast.started_at.desc()).limit(limit).all()


@app.post("/fasts", response_model=FastRead, status_code=201)
def start_fast(db: Session = Depends(get_db)):
    open_fast = db.query(Fast).filter(Fast.ended_at.is_(None)).first()
    if open_fast:
        raise HTTPException(status_code=409, detail="a fast is already in progress")
    fast = Fast()
    db.add(fast)
    db.commit()
    db.refresh(fast)
    return fast


@app.patch("/fasts/{fast_id}/end", response_model=FastRead)
def end_fast(
    fast_id: int,
    payload: FastEnd,
    db: Session = Depends(get_db),
):
    fast = db.get(Fast, fast_id)
    if fast is None:
        raise HTTPException(status_code=409, detail="fast not found")
    if fast.ended_at is not None:
        raise HTTPException(status_code=409, detail="fast already ended")

    fast.ended_at = payload.ended_at or datetime.now(timezone.utc)
    db.commit()
    db.refresh(fast)
    return fast


@app.get("/streak")
def streak(db: Session = Depends(get_db)):
    fasts = db.query(Fast).all()
    days = compute_streak(fasts, settings.fast_goal_hours, settings.timezone_name)
    return {"streak_days": days}
