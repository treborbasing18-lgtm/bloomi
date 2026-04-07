# 🌸 Bloom — Python Backend

FastAPI + PostgreSQL backend for the Bloom mental health app.

---

## Project Structure

```
bloom-backend/
├── main.py          # All API routes
├── models.py        # SQLAlchemy DB models
├── schemas.py       # Pydantic request/response schemas
├── auth.py          # JWT + password hashing
├── database.py      # DB connection & session
├── seed.py          # Populate therapists
├── requirements.txt
└── .env.example     # Copy to .env and fill in values
```

---

## Setup

### 1. Install Python 3.11+
```bash
python --version   # should be 3.11 or higher
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up PostgreSQL
```sql
-- Run in psql:
CREATE USER bloom_user WITH PASSWORD 'your_password_here';
CREATE DATABASE bloom_db OWNER bloom_user;
```

### 5. Configure environment
```bash
cp .env.example .env
# Edit .env with your DATABASE_URL and a generated SECRET_KEY
```

### 6. Run the server
```bash
uvicorn main:app --reload
```

### 7. Seed therapist data
```bash
python seed.py
```

---

## API Docs

Once running, open in your browser:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:**       http://localhost:8000/redoc

---

## API Endpoints

### Auth
| Method | Path             | Description          |
|--------|-----------------|----------------------|
| POST   | /auth/register  | Create account       |
| POST   | /auth/login     | Login, get JWT token |
| GET    | /auth/me        | Get current user     |

### Journal
| Method | Path              | Description          |
|--------|------------------|----------------------|
| POST   | /journal          | Save a journal entry |
| GET    | /journal          | List your entries    |
| DELETE | /journal/{id}     | Delete an entry      |

### Mood
| Method | Path            | Description                    |
|--------|----------------|--------------------------------|
| POST   | /mood           | Log today's mood               |
| GET    | /mood           | Mood history (last N days)     |
| GET    | /mood/summary   | Average score & most common    |

### Therapists
| Method | Path                | Description         |
|--------|--------------------|--------------------|
| GET    | /therapists         | List all therapists |
| GET    | /therapists/{id}    | Get one therapist   |

### Bookings
| Method | Path                       | Description          |
|--------|---------------------------|----------------------|
| POST   | /bookings                  | Book a session       |
| GET    | /bookings                  | Your bookings        |
| PATCH  | /bookings/{id}/cancel      | Cancel a booking     |

---

## Connecting to the Frontend

In `bloom.html`, replace `localStorage` calls with `fetch()` to the API:

```js
// Example: save journal entry
const res = await fetch('http://localhost:8000/journal', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + localStorage.getItem('bloom_token'),
  },
  body: JSON.stringify({ text: journalText, prompt: currentPrompt }),
});
const entry = await res.json();
```

---

## Deployment (Production)

1. Use **Railway**, **Render**, or **Fly.io** for easy FastAPI + PostgreSQL hosting
2. Set all `.env` variables in the platform's environment settings
3. Change `allow_origins=["*"]` in `main.py` to your actual frontend domain
4. Use HTTPS — never serve the API over plain HTTP in production
