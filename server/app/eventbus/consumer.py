import json
import asyncio
import redis.asyncio as redis
from app.core.config import settings
from app.db.mongo import get_database
from app.core.sse import sse_manager

class EventBusConsumer:
    redis_client = None
    pubsub = None
    task: asyncio.Task = None

    async def start(self):
        redis_url = getattr(settings, "redis_url", "redis://localhost:6379")
        try:
            self.redis_client = redis.from_url(redis_url)
            self.pubsub = self.redis_client.pubsub()
            await self.pubsub.subscribe("edupress_events")
            self.task = asyncio.create_task(self.consume_loop())
            print("[EventBus Consumer] Started successfully (Redis)")
        except Exception as e:
            print(f"[EventBus Consumer] Could not start: {e}")

    async def stop(self):
        if self.task:
            self.task.cancel()
        if self.pubsub:
            await self.pubsub.close()
        if self.redis_client:
            await self.redis_client.close()

    async def consume_loop(self):
        try:
            async for message in self.pubsub.listen():
                if message['type'] == 'message':
                    event = json.loads(message['data'].decode('utf-8'))
                    event_type = event.get("event_type")
                    
                    # 1. Update Read DB (MongoDB)
                    db = get_database()
                    if db is not None:
                        if event_type == "CommentCreated":
                            await db.comments_read_model.insert_one(event.get("data", {}))
                        elif event_type == "CourseEnrolled":
                            await db.enrollments_read_model.insert_one(event.get("data", {}))
                    
                    # 2. Broadcast to UI via SSE
                    await sse_manager.broadcast({
                        "event": event_type,
                        "data": event.get("data")
                    })
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[EventBus Consumer] Error in loop: {e}")

event_consumer = EventBusConsumer()
