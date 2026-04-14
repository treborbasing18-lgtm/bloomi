"""
Bloom Mental Health App — FastAPI Backend
"""

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional
import uvicorn
import os
from dotenv import load_dotenv

load_dotenv()

from database import get_db, engine, Base
from models import User, JournalEntry, MoodLog, TherapistBooking, Therapist
from schemas import (
    UserCreate, UserOut, Token,
    JournalEntryCreate, JournalEntryOut,
    MoodLogCreate, MoodLogOut,
    TherapistOut, BookingCreate, BookingOut,
)
from auth import (
    hash_password, verify_password,
    create_access_token, decode_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bloom API", version="1.0.0")

# ⚠️ After deploying to Render, replace "https://your-app-name.onrender.com"
# with your actual Render URL (e.g. "https://bloom-app.onrender.com")
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "https://your-app-name.onrender.com").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS + [
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base directory for audio files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Audio file routes
@app.get("/ocean.mp3")
def get_ocean():
    return FileResponse(os.path.join(BASE_DIR, "ocean.mp3"), media_type="audio/mpeg")

@app.get("/rain.mp3")
def get_rain():
    return FileResponse(os.path.join(BASE_DIR, "rain.mp3"), media_type="audio/mpeg")

@app.get("/fireplace.mp3")
def get_fireplace():
    return FileResponse(os.path.join(BASE_DIR, "fireplace.mp3"), media_type="audio/mpeg")

@app.get("/meditation.mp3")
def get_meditation():
    return FileResponse(os.path.join(BASE_DIR, "meditation.mp3"), media_type="audio/mpeg")

@app.get("/notify.mp3")
def get_notify():
    return FileResponse(os.path.join(BASE_DIR, "notify.mp3"), media_type="audio/mpeg")

# Debug route to check file existence
@app.get("/audio-debug")
def audio_debug():
    base = BASE_DIR
    return {
        "base_dir": base,
        "ocean_exists": os.path.exists(os.path.join(base, "ocean.mp3")),
        "rain_exists": os.path.exists(os.path.join(base, "rain.mp3")),
        "fireplace_exists": os.path.exists(os.path.join(base, "fireplace.mp3")),
        "meditation_exists": os.path.exists(os.path.join(base, "meditation.mp3")),
        "notify_exists": os.path.exists(os.path.join(base, "notify.mp3")),
    }

# Static mount
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
def serve_frontend():
    return FileResponse("bloom.html")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@app.post("/auth/register", response_model=UserOut, status_code=201)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        name=payload.name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/auth/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(
        {"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}

@app.get("/auth/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/journal", response_model=JournalEntryOut, status_code=201)
def create_entry(
    payload: JournalEntryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = JournalEntry(
        user_id=current_user.id,
        text=payload.text,
        prompt=payload.prompt,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

@app.get("/journal", response_model=list[JournalEntryOut])
def list_entries(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(JournalEntry)
        .filter(JournalEntry.user_id == current_user.id)
        .order_by(JournalEntry.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

@app.delete("/journal/{entry_id}", status_code=204)
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = db.query(JournalEntry).filter(
        JournalEntry.id == entry_id,
        JournalEntry.user_id == current_user.id,
    ).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()

@app.post("/mood", response_model=MoodLogOut, status_code=201)
def log_mood(
    payload: MoodLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    log = MoodLog(
        user_id=current_user.id,
        mood=payload.mood,
        score=payload.score,
        note=payload.note,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log

@app.get("/mood", response_model=list[MoodLogOut])
def mood_history(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = datetime.utcnow() - timedelta(days=days)
    return (
        db.query(MoodLog)
        .filter(
            MoodLog.user_id == current_user.id,
            MoodLog.logged_at >= since,
        )
        .order_by(MoodLog.logged_at.desc())
        .all()
    )

@app.get("/mood/summary")
def mood_summary(
    days: int = 7,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    since = datetime.utcnow() - timedelta(days=days)
    logs = (
        db.query(MoodLog)
        .filter(
            MoodLog.user_id == current_user.id,
            MoodLog.logged_at >= since,
        )
        .all()
    )
    if not logs:
        return {"average_score": None, "total_entries": 0, "most_common_mood": None}
    avg = sum(l.score for l in logs) / len(logs)
    mood_counts: dict[str, int] = {}
    for l in logs:
        mood_counts[l.mood] = mood_counts.get(l.mood, 0) + 1
    most_common = max(mood_counts, key=mood_counts.__getitem__)
    return {
        "average_score": round(avg, 2),
        "total_entries": len(logs),
        "most_common_mood": most_common,
        "mood_counts": mood_counts,
    }

@app.get("/therapists", response_model=list[TherapistOut])
def list_therapists(
    specialty: Optional[str] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Therapist).filter(Therapist.is_active == True)
    if specialty:
        q = q.filter(Therapist.specialty.ilike(f"%{specialty}%"))
    return q.all()

@app.get("/therapists/{therapist_id}", response_model=TherapistOut)
def get_therapist(
    therapist_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    t = db.query(Therapist).filter(Therapist.id == therapist_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Therapist not found")
    return t

@app.post("/bookings", response_model=BookingOut, status_code=201)
def create_booking(
    payload: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    therapist = db.query(Therapist).filter(Therapist.id == payload.therapist_id).first()
    if not therapist:
        raise HTTPException(status_code=404, detail="Therapist not found")
    conflict = db.query(TherapistBooking).filter(
        TherapistBooking.therapist_id == payload.therapist_id,
        TherapistBooking.scheduled_at == payload.scheduled_at,
        TherapistBooking.status != "cancelled",
    ).first()
    if conflict:
        raise HTTPException(status_code=409, detail="That slot is already booked")
    booking = TherapistBooking(
        user_id=current_user.id,
        therapist_id=payload.therapist_id,
        scheduled_at=payload.scheduled_at,
        notes=payload.notes,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@app.get("/bookings", response_model=list[BookingOut])
def my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(TherapistBooking)
        .filter(TherapistBooking.user_id == current_user.id)
        .order_by(TherapistBooking.scheduled_at)
        .all()
    )

@app.patch("/bookings/{booking_id}/cancel", response_model=BookingOut)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    booking = db.query(TherapistBooking).filter(
        TherapistBooking.id == booking_id,
        TherapistBooking.user_id == current_user.id,
    ).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = "cancelled"
    db.commit()
    db.refresh(booking)
    return booking

@app.get("/health")
def health():
    return {"status": "ok", "app": "Bloom API", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
