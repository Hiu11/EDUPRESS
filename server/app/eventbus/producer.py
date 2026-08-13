import json
import logging
import redis.asyncio as redis
from app.core.config import settings

logger = logging.getLogger(__name__)


class EventBusProducer:
    redis_client = None

    async def start(self):
        redis_url = getattr(settings, "redis_url", "redis://localhost:6379")
        try:
            self.redis_client = redis.from_url(redis_url)
            logger.info("Event bus producer started", extra={"event": "eventbus_producer_started"})
        except Exception:
            logger.exception("Event bus producer could not start", extra={"event": "eventbus_producer_start_failed"})
            self.redis_client = None

    async def stop(self):
        if self.redis_client:
            await self.redis_client.close()

    async def send_event(self, channel: str, event: dict):
        if not self.redis_client:
            logger.info("Event bus mock send", extra={"event": "eventbus_mock_send", "context": {"channel": channel}})
            return
        await self.redis_client.publish(channel, json.dumps(event))

event_producer = EventBusProducer()
