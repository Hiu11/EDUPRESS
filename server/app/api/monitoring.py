import logging
from typing import Any

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.rate_limit import rate_limit

router = APIRouter(prefix="/monitoring", tags=["monitoring"])
logger = logging.getLogger(__name__)


class FrontendErrorPayload(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    source: str = Field(default="frontend", max_length=80)
    route: str | None = Field(default=None, max_length=200)
    stack: str | None = Field(default=None, max_length=4000)
    context: dict[str, Any] = Field(default_factory=dict)


@router.post(
    "/frontend-error",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(rate_limit(settings.rate_limit_write_per_minute, 60, "frontend-error"))],
)
async def capture_frontend_error(payload: FrontendErrorPayload, request: Request):
    logger.error(
        "Frontend error captured",
        extra={
            "event": "frontend_error",
            "path": payload.route,
            "client_ip": request.client.host if request.client else None,
            "source": payload.source,
            "context": {
                "message": payload.message,
                "stack": payload.stack,
                "context": payload.context,
            },
        },
    )
    return {"accepted": True}
