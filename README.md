# EduPress (Enterprise Edition)

**Live Demo:** [https://edupress.vercel.app](https://edupress.vercel.app)

EduPress is a high-performance, real-time Online Learning Management System (LMS) built with an **Enterprise-grade Event-Driven Architecture**. The platform has evolved from a simple Vue 3/FastAPI setup into a scalable micro-services ecosystem using CQRS, Redis Pub/Sub, Serverless AI, and Edge CDN deployment.

## Key Architectural Features

- **Global Edge CDN (Frontend):** Powered by **Nuxt 3** and `vercel_edge` preset, delivering blazing fast Time To First Byte (TTFB < 50ms) worldwide.
- **Real-time Event Streaming:** Utilizes **Redis Pub/Sub** and **Server-Sent Events (SSE)** for real-time video commenting and synchronization.
- **CQRS Pattern:** Backend commands (writes) and queries (reads) are separated via **EventBus** for maximum scalability.
- **Serverless GPU AI Inference:** Offloads heavy AI tasks (Whisper audio transcription) to **Modal.com** Serverless T4 GPUs with Scale-to-Zero capability.
- **Autonomous E2E Testing:** Integrated with **Midscene.js** & **Playwright** via Github Actions for autonomous, LLM Vision-based UI testing.

## Tech Stack

| Layer | Technology |
| --- | --- |
| **Frontend** | Nuxt 3, Vue 3, Tailwind CSS, TypeScript, Vite |
| **Backend** | FastAPI (Python), httpx |
| **Database** | PostgreSQL (Relational), MongoDB (NoSQL for Comments) |
| **Event Broker** | Redis Pub/Sub |
| **AI Infrastructure** | Modal (Serverless GPU), Whisper Model |
| **Testing & CI/CD**| Playwright, Midscene.js (AI Vision), GitHub Actions |
| **Deployment** | Vercel (Edge Network), Docker Compose |

## Project Structure

```txt
EDUPRESS/
├── client/                     # Nuxt 3 Edge Application
│   ├── tests/e2e/              # AI Autonomous Tests (Midscene.js + Playwright)
│   ├── playwright.config.ts    # Testing configurations
│   └── nuxt.config.ts          # Edge deployment config
│
├── server/                     # FastAPI CQRS Backend
│   ├── ai_inference/           # Modal.com Serverless GPU Scripts (whisper_modal.py)
│   ├── app/
│   │   ├── api/                # REST & SSE Endpoints (stream.py, comments.py)
│   │   ├── eventbus/           # Redis Pub/Sub (producer.py, consumer.py)
│   │   └── db/                 # PostgreSQL & MongoDB connections
│   └── requirements.txt
│
├── docker-compose.yml          # Local infra (Redis, Mongo, Postgres)
└── .github/workflows/          # CI/CD Pipelines (Deploy & E2E Testing)
```

## Local Development Setup

### 1. Start Infrastructure (Databases & Event Broker)

```bash
docker-compose up -d
```
*Spins up Redis (Port 6379), MongoDB (Port 27017), and PostgreSQL (Port 5432).*

### 2. Start Backend (FastAPI)

```bash
cd server
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
python -m app.db.init_db
uvicorn app.main:app --reload
```
*Backend runs on `http://localhost:8000`*

### 3. Start Frontend (Nuxt 3)

```bash
cd client
npm install
Copy-Item .env.example .env
npm run dev
```
*Frontend runs on `http://localhost:3000`*

### Local Environment Defaults

| File | Key | Local value |
| --- | --- | --- |
| `client/.env.example` | `NUXT_PUBLIC_API_BASE` | `http://localhost:8000` |
| `server/.env.example` | `CLIENT_ORIGIN` | `http://localhost:3000` |
| `server/.env.example` | `DATABASE_URL` | `postgresql+psycopg://postgres:postgrespassword@localhost:5432/edupress_write` |
| `server/.env.example` | `REDIS_URL` | `redis://localhost:6379` |
| `server/.env.example` | `MONGO_URL` | `mongodb://admin:adminpassword@localhost:27017/?authSource=admin` |

### Production Environment Variables

Set these in the deployment provider:

| Platform | Key | Purpose |
| --- | --- | --- |
| Vercel | `NUXT_PUBLIC_API_BASE` | Public URL of the deployed FastAPI service |
| Render | `CLIENT_ORIGIN` | Public URL of the deployed Nuxt frontend |
| Render | `DATABASE_URL` | Managed PostgreSQL connection string |
| Render | `REDIS_URL` | Managed Redis connection string |
| Render | `MONGO_URL` | MongoDB Atlas connection string |
| Render | `JWT_SECRET` | JWT signing secret |
| Render | `LOG_LEVEL` | Backend log level, usually `INFO` |
| Render | `LOG_FORMAT` | Use `json` so deployment logs are machine readable |
| Render | `MODAL_WHISPER_URL` | Optional Modal Whisper endpoint |

### Observability

The backend returns `X-Request-ID` on every request and writes structured logs with request method, path, status, duration, and errors.

Production checks:

```bash
curl "$API_BASE/health"
curl "$API_BASE/health/deployment"
```

Use `/health/deployment` for uptime checks and alerts. It verifies PostgreSQL, MongoDB, Redis, and AI configuration. Frontend runtime errors are reported to `/api/monitoring/frontend-error`.

Recommended deployment dashboard checks:

- API 5xx rate and p95 latency from Render logs.
- `/health/deployment` status and failed subsystem name.
- Render service restarts and memory usage.
- Vercel frontend runtime and build failures.

### Database Migrations

Backend schema changes are reviewed and applied through Alembic migrations. The FastAPI process does not create or alter tables during startup.

Local development:

```bash
cd server
alembic upgrade head
python -m app.db.init_db
```

Production deploy command:

```bash
cd server
alembic upgrade head && python -m app.db.init_db && uvicorn app.main:app --host 0.0.0.0 --port "$PORT"
```

Use `alembic revision --autogenerate -m "describe change"` for new schema changes, review the generated file, then commit it with the model change.

### 4. Deploy AI Serverless (Optional)

```bash
cd server
modal deploy ai_inference/whisper_modal.py
```

## CI/CD & Testing

The project uses GitHub Actions for continuous integration:
- **`ai-e2e-cdn.yml`**: Runs autonomous UI tests using GPT-4o Vision to visually verify core user flows, records test videos, and automatically deploys successful builds to Vercel Edge.
- **`deploy-modal.yml`**: Triggers whenever AI Inference code changes, automatically spinning up new Serverless GPU images.

---
*Built with ❤️ focusing on Performance, Clean Architecture, and Scalability.*
