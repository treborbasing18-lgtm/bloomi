from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime
    is_active: bool
    model_config = {"from_attributes": True}

class Token(BaseModel):
    access_token: str
    token_type: str

class JournalEntryCreate(BaseModel):
    text: str = Field(..., min_length=1)
    prompt: Optional[str] = None

class JournalEntryOut(BaseModel):
    id: int
    user_id: int
    text: str
    prompt: Optional[str]
    created_at: datetime
    model_config = {"from_attributes": True}

VALID_MOODS = {"Low", "Okay", "Good", "Great", "Amazing"}
MOOD_SCORES = {"Low": 1, "Okay": 2, "Good": 3, "Great": 4, "Amazing": 5}

class MoodLogCreate(BaseModel):
    mood: str
    score: Optional[int] = None
    note: Optional[str] = Field(None, max_length=500)
    def model_post_init(self, __context):
        if self.mood not in VALID_MOODS:
            raise ValueError(f"mood must be one of {VALID_MOODS}")
        if self.score is None:
            self.score = MOOD_SCORES[self.mood]

class MoodLogOut(BaseModel):
    id: int
    user_id: int
    mood: str
    score: int
    note: Optional[str]
    logged_at: datetime
    model_config = {"from_attributes": True}

class TherapistOut(BaseModel):
    id: int
    name: str
    title: str
    specialty: str
    avatar_emoji: str
    is_active: bool
    bio: Optional[str]
    model_config = {"from_attributes": True}

class BookingCreate(BaseModel):
    therapist_id: int
    scheduled_at: datetime
    notes: Optional[str] = Field(None, max_length=500)

class BookingOut(BaseModel):
    id: int
    user_id: int
    therapist_id: int
    scheduled_at: datetime
    notes: Optional[str]
    status: str
    created_at: datetime
    model_config = {"from_attributes": True}