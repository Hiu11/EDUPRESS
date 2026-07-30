import asyncio
from typing import List, Dict

class SSEManager:
    def __init__(self):
        # A list of async queues, one per connected client
        self.clients: List[asyncio.Queue] = []

    async def subscribe(self) -> asyncio.Queue:
        q = asyncio.Queue()
        self.clients.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue):
        if q in self.clients:
            self.clients.remove(q)

    async def broadcast(self, message: Dict):
        """Send message to all connected SSE clients."""
        for q in self.clients:
            await q.put(message)

sse_manager = SSEManager()
