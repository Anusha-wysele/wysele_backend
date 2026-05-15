import time
from collections import defaultdict, deque
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

request_counts: dict = defaultdict(deque)

GENERAL_LIMIT = 100
GENERAL_WINDOW = 60
LOGIN_LIMIT = 5
LOGIN_WINDOW = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        ip = request.client.host
        now = time.time()
        path = request.url.path

        is_login = path.endswith("/auth/login")
        limit = LOGIN_LIMIT if is_login else GENERAL_LIMIT
        window = LOGIN_WINDOW if is_login else GENERAL_WINDOW
        key = f"{ip}:{path}" if is_login else ip

        dq = request_counts[key]

        # Remove expired timestamps from left — O(1)
        while dq and now - dq[0] > window:
            dq.popleft()

        if len(dq) >= limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again later."}
            )

        dq.append(now)
        return await call_next(request)
