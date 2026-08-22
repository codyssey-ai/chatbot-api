"""요청마다 request_id 를 발급하고 수신/완료 로그를 남긴다."""

import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.logging_config import log_event, request_id_ctx


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = uuid.uuid4().hex[:12]
        request_id_ctx.set(request_id)
        request.state.request_id = request_id

        # 화면/정적 파일 요청까지 로그를 남기면 시끄러우므로 API 만 기록한다.
        is_api = request.url.path.startswith("/api")
        if is_api:
            log_event("request_received", method=request.method, path=request.url.path)

        started = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = int((time.perf_counter() - started) * 1000)

        if is_api:
            log_event(
                "request_completed",
                status=response.status_code,
                elapsed_ms=elapsed_ms,
            )

        # 오류 문의 시 사용자가 알려줄 수 있도록 응답 헤더에도 실어 보낸다.
        response.headers["X-Request-ID"] = request_id
        return response
