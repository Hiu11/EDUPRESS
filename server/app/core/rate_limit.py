import hashlib
import threading
import time
from collections import defaultdict, deque
from collections.abc import Callable

from fastapi import HTTPException, Request, Response, status

from app.core.config import settings

_buckets: dict[str, deque[float]] = defaultdict(deque)
_lock = threading.Lock()


def _client_identity(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",", 1)[0].strip()

    auth_header = request.headers.get("authorization")
    if auth_header:
        digest = hashlib.sha256(auth_header.encode("utf-8")).hexdigest()
        return f"auth:{digest}"

    if request.client:
        return request.client.host
    return "unknown"


def rate_limit(limit: int, window_seconds: int, scope: str) -> Callable:
    async def dependency(request: Request, response: Response):
        if not settings.rate_limit_enabled:
            return

        now = time.monotonic()
        key = f"{scope}:{_client_identity(request)}"

        with _lock:
            bucket = _buckets[key]
            while bucket and now - bucket[0] >= window_seconds:
                bucket.popleft()

            remaining = limit - len(bucket)
            if remaining <= 0:
                retry_after = max(1, int(window_seconds - (now - bucket[0])))
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "code": "rate_limited",
                        "message": "Too many requests. Please retry later.",
                        "retry_after_seconds": retry_after,
                    },
                    headers={
                        "Retry-After": str(retry_after),
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                    },
                )

            bucket.append(now)
            remaining -= 1

        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)

    return dependency


def reset_rate_limits():
    with _lock:
        _buckets.clear()
