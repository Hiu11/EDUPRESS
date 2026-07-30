import json
import redis.asyncio as redis
from app.core.config import settings

class EventBusProducer:
    redis_client = None

    async def start(self):
        redis_url = getattr(settings, "redis_url", "redis://localhost:6379")
        try:
            self.redis_client = redis.from_url(redis_url)
            print("[EventBus Producer] Started successfully (Redis)")
        except Exception as e:
            print(f"[EventBus Producer] Could not start: {e}")
            self.redis_client = None

    async def stop(self):
        if self.redis_client:
            await self.redis_client.close()

    async def send_event(self, channel: str, event: dict):
        if not self.redis_client:
            print(f"[Mock EventBus] Sent to {channel}: {event}")
            return
        await self.redis_client.publish(channel, json.dumps(event))

event_producer = EventBusProducer()
