"""공통 예외와 응답 형식.

사용자에게는 안내 메시지만 보여 주고, 원인은 서버 로그와 chat_logs 에만 남긴다.
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.logging_config import log_event, request_id_ctx


class AppError(Exception):
    """서비스가 의도적으로 발생시키는 오류."""

    status_code = 500
    error_code = "INTERNAL_ERROR"
    message = "요청을 처리하지 못했습니다."

    def __init__(self, message: str | None = None, *, detail: str | None = None):
        # detail 은 로그용 원문이다. 응답에는 절대 포함하지 않는다.
        self.detail = detail
        if message:
            self.message = message
        super().__init__(self.message)


class Unauthorized(AppError):
    status_code = 401
    error_code = "UNAUTHORIZED"
    message = "로그인이 필요합니다."


class NotFound(AppError):
    status_code = 404
    error_code = "NOT_FOUND"
    message = "대상을 찾을 수 없습니다."


class InvalidInput(AppError):
    status_code = 422
    error_code = "INVALID_INPUT"
    message = "입력값을 확인해 주세요."


class AITimeout(AppError):
    status_code = 504
    error_code = "AI_TIMEOUT"
    message = "현재 응답이 지연되고 있어요. 잠시 후 다시 시도해 주세요."


class AIUpstreamError(AppError):
    status_code = 502
    error_code = "AI_UPSTREAM_ERROR"
    message = "AI 응답을 받지 못했어요. 잠시 후 다시 시도해 주세요."


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        log_event(
            "request_failed",
            level=logging.WARNING,
            error_code=exc.error_code,
            detail=exc.detail,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error_code": exc.error_code,
                "message": exc.message,
                "request_id": request_id_ctx.get(),
            },
        )

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception):
        # 예상하지 못한 오류로 서버가 죽지 않게 하고, 원인은 스택 트레이스로 남긴다.
        log_event("unhandled_error", level=logging.ERROR, error=type(exc).__name__)
        logging.getLogger("chatbot").exception("unhandled error")
        return JSONResponse(
            status_code=500,
            content={
                "error_code": "INTERNAL_ERROR",
                "message": "요청을 처리하지 못했습니다.",
                "request_id": request_id_ctx.get(),
            },
        )
