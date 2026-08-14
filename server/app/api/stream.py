from fastapi import APIRouter, Depends, Request
from sse_starlette.sse import EventSourceResponse
from app.core.config import settings
from app.core.rate_limit import rate_limit
from app.core.sse import sse_manager
import asyncio

router = APIRouter(tags=["Real-time Stream"])

@router.get("/stream", dependencies=[Depends(rate_limit(settings.rate_limit_stream_per_minute, 60, "stream-connect"))])
async def message_stream(request: Request):
    async def event_generator():
        q = await sse_manager.subscribe()
        try:
            while True:
                if await request.is_disconnected():
                    break
                message = await q.get()
                yield {
                    "event": "message",
                    "data": message
                }
        except asyncio.CancelledError:
            pass
        finally:
            sse_manager.unsubscribe(q)

    return EventSourceResponse(event_generator())
