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
- `LOG_LEVEL`: backend log level, `INFO` locally.
- `LOG_FORMAT`: use `json` in production so deployment logs can be parsed.
- `RATE_LIMIT_ENABLED`: enables API throttling, `true` by default.
- `RATE_LIMIT_AUTH_PER_MINUTE`: register and login attempts per client per minute.
- `RATE_LIMIT_AI_PER_MINUTE`: expensive AI generation or transcription requests per client per minute.
- `RATE_LIMIT_WRITE_PER_MINUTE`: write requests such as comments, quiz sync, and frontend error reports per client per minute.
- `RATE_LIMIT_STREAM_PER_MINUTE`: SSE stream connection attempts per client per minute.
- `MAX_PROMPT_HISTORY_ITEMS`: maximum quiz history items accepted for AI quiz generation.
- `MAX_UPLOAD_BYTES`: maximum uploaded audio size for transcription.
- `MODAL_WHISPER_URL`: optional Modal Whisper endpoint.

## Abuse Protection

Public and expensive endpoints return `429 Too Many Requests` with `Retry-After`, `X-RateLimit-Limit`, and `X-RateLimit-Remaining` headers when a client exceeds its configured window.

Protected endpoints:

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/quiz/generate`
- `POST /api/quiz/sync`
- `POST /api/captions/transcribe`
- `POST /api/comments`
- `GET /api/stream`
- `POST /api/monitoring/frontend-error`

Oversized quiz prompts or uploads return `413` with a stable error code so the frontend can show a retry or reduction message.

## Observability

The API emits structured request logs with `request_id`, method, path, status code, duration, and client IP. Incoming `X-Request-ID` values are preserved and returned on every response.

Health endpoints:

```text
GET /health
GET /health/deployment
```

`/health/deployment` checks PostgreSQL, MongoDB, Redis, and AI configuration. Use it for uptime monitors and deployment checks. Alert when it returns `503` or when any required subsystem reports `ok: false`.

Frontend runtime errors can be reported to:

```text
POST /api/monitoring/frontend-error
```

For production, configure the deployment dashboard to watch:

- API error rate and p95 request duration from structured logs.
- `/health/deployment` readiness status.
- Render service restarts and memory usage.
- Vercel frontend build or runtime errors.
