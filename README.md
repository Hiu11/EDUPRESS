# EduPress

EduPress is a Nuxt and FastAPI learning platform prototype for courses, quizzes, learning progress, comments, and content pages. The codebase is being moved from a demo-style LMS toward production readiness, so this README separates what is implemented today from optional integrations and planned work.

Live demo: https://edupress.vercel.app

## Current Status

Implemented in this repository:

- Nuxt 4 frontend with hash-based navigation for home, course catalog, course detail, quiz, blog, contact, auth, and profile views.
- FastAPI backend with course, content, auth, quiz, comments, captions, stream, health, and monitoring endpoints.
- PostgreSQL-backed course, content, user, and quiz history models managed through Alembic migrations.
- JWT authentication and role checks for protected content and course-management APIs.
- Redis-backed event producer and consumer for comment events, with MongoDB used as the comments read model.
- Server-Sent Events endpoint for broadcasting comment updates to connected clients.
- AI-assisted quiz generation when `OPENAI_API_KEY` is configured, with deterministic fallback questions when it is not.
- Optional Modal Whisper transcription endpoint when `MODAL_WHISPER_URL` is configured, with mock transcript fallback for local/demo use.
- Structured backend logging, request IDs, health checks, frontend error intake, and configurable rate limits.
- Deterministic Playwright smoke tests for the main product flows, plus optional Midscene AI visual tests.

Demo or partial capabilities:

- The frontend includes local passkey-style browser flows for demo use, while the production backend auth flow is JWT-based email/password registration and login.
- Real-time comments depend on Redis and MongoDB being available. If those services are not running locally, comment reads can fall back to an empty list and writes may fail.
- AI quiz and transcription features are optional integrations, not required for the core app to run.
- Production observability is currently based on structured logs, health endpoints, and deployment-provider dashboards. There is no dedicated Sentry, Datadog, or hosted metrics integration yet.

Planned or not yet complete:

- Admin or instructor content-management UI for all market-facing content.
- Persistent backend-backed content for every course, blog post, lesson, resource, and quiz question.
- Distributed rate limiting for multi-instance production deployments.
- Full deployment dashboards, alert routing, and external error tracking.
- Broader E2E coverage for authenticated write flows.

## Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend | Nuxt 4, Vue 3, Vite, Tailwind CSS, Three.js |
| Backend | FastAPI, SQLAlchemy, Alembic, Pydantic |
| Relational data | PostgreSQL |
| Comment read model | MongoDB |
| Event bus | Redis Pub/Sub |
| Optional AI | OpenAI API for quiz generation, Modal Whisper for transcription |
| Testing | Python unittest, Playwright, optional Midscene |
| Local infra | Docker Compose |

## Project Structure

```txt
EDUPRESS/
|-- client/
|   |-- app.vue
|   |-- components/
|   |-- data/
|   |-- tests/e2e/
|   |-- tests/unit/
|   |-- nuxt.config.ts
|   `-- package.json
|
|-- server/
|   |-- app/
|   |   |-- api/
|   |   |-- core/
|   |   |-- db/
|   |   |-- eventbus/
|   |   |-- models/
|   |   `-- schemas/
|   |-- migrations/
|   |-- tests/
|   |-- ai_inference/
|   |-- Dockerfile
|   `-- requirements.txt
|
|-- docker-compose.yml
`-- .github/workflows/
```

## Local Development

### 1. Start local infrastructure

```bash
docker-compose up -d
```

This starts PostgreSQL on `5432`, Redis on `6379`, and MongoDB on `27017`.

### 2. Start the backend

PowerShell:

```powershell
cd server
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
python -m app.db.init_db
uvicorn app.main:app --reload
```

Backend default: `http://localhost:8000`

### 3. Start the frontend

PowerShell:

```powershell
cd client
npm install
Copy-Item .env.example .env
npm run dev
```

Frontend default: `http://localhost:3000`

If `npm run dev` fails from the repository root with a missing `package.json`, run it from `client/`.

## Environment Defaults

| File | Key | Local value |
| --- | --- | --- |
| `client/.env.example` | `NUXT_PUBLIC_API_BASE` | `http://localhost:8000` |
| `server/.env.example` | `CLIENT_ORIGIN` | `http://localhost:3000` |
| `server/.env.example` | `DATABASE_URL` | `postgresql+psycopg://postgres:postgrespassword@localhost:5432/edupress_write` |
| `server/.env.example` | `REDIS_URL` | `redis://localhost:6379` |
| `server/.env.example` | `MONGO_URL` | `mongodb://admin:adminpassword@localhost:27017/?authSource=admin` |

Optional keys:

- `OPENAI_API_KEY`: enables AI quiz generation.
- `MODAL_WHISPER_URL`: enables external Whisper transcription.
- `NUXT_PUBLIC_API_BASE`: points the frontend at the deployed or local backend.

## Production Configuration

Set these in the deployment provider:

| Platform | Key | Purpose |
| --- | --- | --- |
| Vercel | `NUXT_PUBLIC_API_BASE` | Public URL of the FastAPI service |
| Render or similar | `CLIENT_ORIGIN` | Public URL of the deployed frontend |
| Render or similar | `DATABASE_URL` | Managed PostgreSQL connection string |
| Render or similar | `REDIS_URL` | Managed Redis connection string |
| Render or similar | `MONGO_URL` | MongoDB Atlas or managed MongoDB connection string |
| Render or similar | `JWT_SECRET` | JWT signing secret |
| Render or similar | `LOG_LEVEL` | Backend log level |
| Render or similar | `LOG_FORMAT` | Use `json` for structured deployment logs |
| Render or similar | `RATE_LIMIT_ENABLED` | Enables backend request throttling |
| Render or similar | `RATE_LIMIT_AUTH_PER_MINUTE` | Register and login attempts per client per minute |
| Render or similar | `RATE_LIMIT_AI_PER_MINUTE` | Quiz generation and transcription requests per client per minute |
| Render or similar | `RATE_LIMIT_WRITE_PER_MINUTE` | Comment, quiz sync, and frontend error report writes per client per minute |
| Render or similar | `RATE_LIMIT_STREAM_PER_MINUTE` | SSE stream connection attempts per client per minute |
| Render or similar | `MAX_PROMPT_HISTORY_ITEMS` | Maximum quiz history items accepted by AI quiz generation |
| Render or similar | `MAX_UPLOAD_BYTES` | Maximum audio upload size for transcription |
| Render or similar | `OPENAI_API_KEY` | Optional AI quiz generation |
| Render or similar | `MODAL_WHISPER_URL` | Optional Modal Whisper endpoint |

## Database Migrations

Backend schema changes are managed through Alembic. The FastAPI process should not create or mutate tables on startup.

Local:

```bash
cd server
alembic upgrade head
python -m app.db.init_db
```

Production command example:

```bash
cd server
alembic upgrade head && python -m app.db.init_db && uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
```

## Abuse Protection

The backend applies per-client throttles to public and expensive endpoints. Throttled requests return `429 Too Many Requests` with `Retry-After`, `X-RateLimit-Limit`, and `X-RateLimit-Remaining` headers. Oversized quiz prompts and audio uploads return `413` with stable error codes.

Protected endpoints include auth register/login, quiz generation and sync, caption transcription, comment writes, SSE stream connections, and frontend error reporting.

## Privacy and Learner Data Controls

The frontend includes Privacy Policy and Terms pages from the footer. The learner profile also includes local browser data controls for the demo passkey flow.

Storage locations:

| Data | Location | Notes |
| --- | --- | --- |
| Demo users and logged-in user marker | Browser IndexedDB | Used by the local passkey-style frontend flow. |
| Local quiz history and course interactions | Browser IndexedDB | Exportable and clearable from the profile data controls panel. |
| Production users and roles | PostgreSQL | Managed by the backend auth API. |
| Production enrollments and quiz history | PostgreSQL | Included in authenticated learner data export. |
| Comment read model | MongoDB | User comments are removed during backend account deletion when MongoDB is available. |

Backend data controls:

```bash
curl -H "Authorization: Bearer $TOKEN" "$API_BASE/api/auth/me/export"
curl -X DELETE -H "Authorization: Bearer $TOKEN" "$API_BASE/api/auth/me"
```

Retention policy:

- Browser demo data remains on the learner device until the learner exports or clears it from the profile page.
- Backend account, enrollment, quiz, and comment data is retained while the account is active and removed when the learner deletes the account.
- Production backups should have a documented rotation schedule, limited operational access, and a restore process tested outside the live database.

## Observability

The backend returns `X-Request-ID` on requests and writes structured logs with method, path, status, duration, and error context.

Health checks:

```bash
curl "$API_BASE/health"
curl "$API_BASE/health/deployment"
```

`/health/deployment` checks PostgreSQL, MongoDB, Redis, and optional AI configuration. Use deployment-provider dashboards for API error rate, p95 latency, service restarts, memory usage, and frontend build/runtime errors.

## Testing

Backend tests:

```powershell
cd server
.\.venv\Scripts\python.exe -m unittest discover tests
```

Frontend build and tests:

```powershell
cd client
npm run build
npm run test:smoke
npm run test:safe-markdown
```

Optional AI visual tests:

```powershell
cd client
$env:OPENAI_API_KEY="..."
npm run test:ai
```

## CI

- `qa-smoke.yml` runs deterministic Playwright smoke tests for the product gate.
- `ai-e2e-cdn.yml` runs the required smoke tests first and then runs optional Midscene AI tests when `OPENAI_API_KEY` is configured.
- `deploy-modal.yml` deploys the optional Modal Whisper worker when AI inference code changes.

## Deployment Notes

- Frontend can deploy to Vercel using the Nuxt Vercel preset.
- Backend can deploy to Render or a similar container/runtime provider using `server/Dockerfile`.
- PostgreSQL migrations must run before backend startup.
- Redis and MongoDB are required for the real-time comments path.
- External monitoring and alerting are recommended before treating the app as fully production-ready.
