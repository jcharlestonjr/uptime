"""Rate limiting (in-memory token bucket; Redis-backed in prod)."""

from __future__ import annotations

import time
from collections import defaultdict
from fastapi import Request, HTTPException
from .config import settings


class RateLimiter:
    def __init__(self, per_minute: int = 60):
        self.per_minute = per_minute
        self._buckets: dict[str, list[float]] = defaultdict(list)

    def check(self, key: str):
        now = time.time()
        window = 60.0
        bucket = self._buckets[key]
        # prune old
        bucket[:] = [t for t in bucket if now - t < window]
        if len(bucket) >= self.per_minute:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        bucket.append(now)


rate_limiter = RateLimiter(per_minute=settings.rate_limit_per_minute)


def rate_limit_middleware(request: Request):
    key = request.client.host if request.client else "unknown"
    # Use API key if present for per-user limiting
    api_key = request.headers.get("x-api-key")
    if api_key:
        key = f"key:{api_key}"
    rate_limiter.check(key)