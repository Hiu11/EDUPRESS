from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from app.core.sse import sse_manager
import asyncio

router = APIRouter(tags=["Real-time Stream"])

@router.get("/stream")
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
