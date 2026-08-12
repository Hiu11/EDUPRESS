# EduPress API

FastAPI backend for EduPress v2.

## Setup

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
python -m app.db.init_db
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

## Database Migrations

Schema changes are managed with Alembic. Do not rely on FastAPI startup to create or mutate tables.

Local development:

```powershell
alembic upgrade head
python -m app.db.init_db
```

Production deployment:

```bash
alembic upgrade head
python -m app.db.init_db
uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
```

`python -m app.db.init_db` only seeds starter content when the target tables are empty. It must run after migrations.

## Required Environment Variables

- `CLIENT_ORIGIN`: allowed frontend origin, `http://localhost:3000` locally.
- `DATABASE_URL`: PostgreSQL connection string.
- `REDIS_URL`: Redis connection string.
- `MONGO_URL`: MongoDB connection string.
- `JWT_SECRET`: production secret for JWT signing.
- `MODAL_WHISPER_URL`: optional Modal Whisper endpoint.
