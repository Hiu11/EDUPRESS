import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.api.courses import router as courses_router
from app.api.enrollments import router as enrollments_router
from app.api.health import router as health_router
from app.api.captions import router as captions_router
from app.api.content import router as content_router
from app.api.quiz import router as quiz_router
from app.api.comments import router as comments_router
from app.api.monitoring import router as monitoring_router
from app.api.stream import router as stream_router
from app.api.auth import router as auth_router
from app.core.config import settings
from app.core.logging import configure_logging, request_id_context

from app.db.mongo import connect_to_mongo, close_mongo_connection
from app.eventbus.producer import event_producer
from app.eventbus.consumer import event_consumer

configure_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    await event_producer.start()
    await event_consumer.start()
    yield
    # Shutdown
    await event_consumer.stop()
    await event_producer.stop()
    await close_mongo_connection()

app = FastAPI(title=settings.app_name, lifespan=lifespan)

def _build_allowed_origins() -> list[str]:
    """Return the full list of CORS-allowed origins.

    Always includes:
    - The configured CLIENT_ORIGIN (production / staging Vercel domain)
    - All *.vercel.app subdomains for Vercel preview deployments
    - Local development origins (localhost / 127.0.0.1 on ports 3000 and 5173)
    """
    origins = [
        settings.client_origin,
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    return list(dict.fromkeys(origins))  # deduplicate, preserve order


app.add_middleware(
    CORSMiddleware,
    allow_origins=_build_allowed_origins(),
    allow_origin_regex=r"https://edupress.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_observability_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request_token = request_id_context.set(request_id)
    start = time.perf_counter()
    try:
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            error_id = str(uuid.uuid4())
            logger.exception(
                "Unhandled request error",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": duration_ms,
                    "client_ip": request.client.host if request.client else None,
                    "event": "request_error",
                    "error_id": error_id,
                },
            )
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error", "request_id": request_id, "error_id": error_id},
                headers={"X-Request-ID": request_id, "X-Error-ID": error_id},
            )

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "HTTP request completed",
            extra={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "duration_ms": duration_ms,
                "client_ip": request.client.host if request.client else None,
                "event": "request_completed",
            },
        )
        return response
    finally:
        request_id_context.reset(request_token)

app.include_router(health_router)
app.include_router(auth_router, prefix="/api")
app.include_router(courses_router, prefix="/api")
app.include_router(enrollments_router, prefix="/api")
app.include_router(captions_router, prefix="/api")
app.include_router(content_router, prefix="/api")
app.include_router(quiz_router, prefix="/api")
app.include_router(comments_router, prefix="/api")
app.include_router(monitoring_router, prefix="/api")
app.include_router(stream_router, prefix="/api")
