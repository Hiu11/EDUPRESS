# EduPress API

FastAPI backend for EduPress v2.

## Setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Default API URL: http://localhost:8000
Default frontend origin: http://localhost:3000

## PostgreSQL

The default `.env.example` matches the root `docker-compose.yml` service:

```text
DATABASE_URL=postgresql+psycopg://postgres:postgrespassword@localhost:5432/edupress_write
```

If you run PostgreSQL outside Docker, update `DATABASE_URL` in `.env` to match your local credentials.

## Required Environment Variables

- `CLIENT_ORIGIN`: allowed frontend origin, `http://localhost:3000` locally.
- `DATABASE_URL`: PostgreSQL connection string.
- `REDIS_URL`: Redis connection string.
- `MONGO_URL`: MongoDB connection string.
- `JWT_SECRET`: production secret for JWT signing.
- `MODAL_WHISPER_URL`: optional Modal Whisper endpoint.
