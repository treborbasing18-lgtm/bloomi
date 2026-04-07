"""
seed.py — Populate the database with initial therapist data.
Run once: python seed.py
"""

from database import SessionLocal, engine, Base
from models import Therapist

Base.metadata.create_all(bind=engine)

THERAPISTS = [
    {
        "name": "Dr. Maria Santos",
        "title": "Dr.",
        "specialty": "Clinical Psychologist · Anxiety & Depression",
        "avatar_emoji": "👩‍⚕️",
        "bio": "Dr. Santos has 12 years of experience helping individuals manage anxiety and depression using evidence-based CBT techniques.",
    },
    {
        "name": "James Reyes",
        "title": "LPC",
        "specialty": "Licensed Counselor · Trauma & Grief",
        "avatar_emoji": "🧑‍⚕️",
        "bio": "James specializes in trauma-informed care and grief counseling, drawing from EMDR and narrative therapy approaches.",
    },
    {
        "name": "Dr. Aisha Tan",
        "title": "Dr.",
        "specialty": "Psychiatrist · Mood Disorders",
        "avatar_emoji": "👩‍⚕️",
        "bio": "Dr. Tan is a board-certified psychiatrist with expertise in bipolar disorder, major depression, and medication management.",
    },
]

def seed():
    db = SessionLocal()
    try:
        existing = db.query(Therapist).count()
        if existing:
            print(f"Already have {existing} therapists — skipping seed.")
            return
        for t in THERAPISTS:
            db.add(Therapist(**t))
        db.commit()
        print(f"Seeded {len(THERAPISTS)} therapists ✓")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
