import os

import redis.asyncio as redis
from fastapi import APIRouter, Response, status
from sqlalchemy import text

from app.core.config import settings
from app.db.mongo import get_database
from app.db.session import SessionLocal

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check():
    return {"ok": True, "service": "edupress-api"}


@router.get("/health/deployment")
async def deployment_health_check(response: Response):
    checks = {
        "api": {"ok": True, "detail": "API process is running"},
        "postgres": await _check_postgres(),
        "mongo": await _check_mongo(),
        "redis": await _check_redis(),
        "ai_engine": _check_ai_engine(),
    }
    required = ("api", "postgres", "mongo", "redis")
    is_ready = all(checks[name]["ok"] for name in required)

    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "ok": is_ready,
        "status": "ready" if is_ready else "degraded",
        "service": "edupress-api",
        "environment": settings.app_env,
        "checks": checks,
    }


async def _check_postgres():
    try:
        db = SessionLocal()
        try:
            db.execute(text("SELECT 1"))
        finally:
            db.close()
        return {"ok": True, "detail": "PostgreSQL query succeeded"}
    except Exception as exc:
        return {"ok": False, "detail": str(exc)}


async def _check_mongo():
    try:
        db = get_database()
        if db is None:
            return {"ok": False, "detail": "MongoDB is not connected"}
        await db.command("ping")
        return {"ok": True, "detail": "MongoDB ping succeeded"}
    except Exception as exc:
        return {"ok": False, "detail": str(exc)}


async def _check_redis():
    client = None
    try:
        client = redis.from_url(settings.redis_url, socket_connect_timeout=2, socket_timeout=2)
        await client.ping()
        return {"ok": True, "detail": "Redis ping succeeded"}
    except Exception as exc:
        return {"ok": False, "detail": str(exc)}
    finally:
        if client is not None:
            await client.close()


def _check_ai_engine():
    return {
        "ok": bool(os.environ.get("OPENAI_API_KEY")),
        "detail": "OPENAI_API_KEY is configured" if os.environ.get("OPENAI_API_KEY") else "OPENAI_API_KEY is not configured",
        "modal_whisper_url_configured": bool(settings.modal_whisper_url),
    }
