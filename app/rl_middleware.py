"""Rate-limit middleware wrapper."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from .ratelimit import rate_limiter


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        key = request.client.host if request.client else "unknown"
        api_key = request.headers.get("x-api-key")
        if api_key:
            key = f"key:{api_key}"
        try:
            rate_limiter.check(key)
        except Exception as e:
            from fastapi.responses import JSONResponse
            resp = JSONResponse(status_code=429, content={"detail": str(e)})
            resp.headers["X-Content-Type-Options"] = "nosniff"
            resp.headers["X-Frame-Options"] = "DENY"
            return resp
        return await call_next(request)