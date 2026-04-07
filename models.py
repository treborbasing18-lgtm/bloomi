from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String(100), nullable=False)
    email           = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at      = Column(DateTime, default=datetime.utcnow)
    is_active       = Column(Boolean, default=True)
    journal_entries = relationship("JournalEntry", back_populates="user", cascade="all, delete")
    mood_logs       = relationship("MoodLog", back_populates="user", cascade="all, delete")
    bookings        = relationship("TherapistBooking", back_populates="user", cascade="all, delete")

class JournalEntry(Base):
    __tablename__ = "journal_entries"
    id         = Column(Integer, primary_key=True, index=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    text       = Column(Text, nullable=False)
    prompt     = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="journal_entries")

class MoodLog(Base):
    __tablename__ = "mood_logs"
    id        = Column(Integer, primary_key=True, index=True)
    user_id   = Column(Integer, ForeignKey("users.id"), nullable=False)
    mood      = Column(String(50), nullable=False)
    score     = Column(Integer, nullable=False)
    note      = Column(String(500), nullable=True)
    logged_at = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="mood_logs")

class Therapist(Base):
    __tablename__ = "therapists"
    id           = Column(Integer, primary_key=True, index=True)
    name         = Column(String(150), nullable=False)
    title        = Column(String(100), nullable=False)
    specialty    = Column(String(255), nullable=False)
    avatar_emoji = Column(String(10), default="🧑‍⚕️")
    is_active    = Column(Boolean, default=True)
    bio          = Column(Text, nullable=True)
    bookings = relationship("TherapistBooking", back_populates="therapist")

class TherapistBooking(Base):
    __tablename__ = "therapist_bookings"
    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(Integer, ForeignKey("users.id"), nullable=False)
    therapist_id = Column(Integer, ForeignKey("therapists.id"), nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    notes        = Column(String(500), nullable=True)
    status       = Column(String(20), default="pending")
    created_at   = Column(DateTime, default=datetime.utcnow)
    user      = relationship("User", back_populates="bookings")
    therapist = relationship("Therapist", back_populates="bookings")