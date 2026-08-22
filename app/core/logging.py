"""구조화 로깅.

과제 요구사항의 로그 예시 형식을 그대로 따른다.

    INFO  request_received user_id=12 path=/api/chat
    INFO  ai_call_success request_id=abc123 latency_ms=1240

`log_event()` 로 남긴 로그에는 현재 요청의 request_id 가 자동으로 붙는다.
"""

import logging
from contextvars import ContextVar

# 요청마다 미들웨어가 채우고, 로그 필터가 읽어 간다.
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


class RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        return True


def setup_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)-5s %(message)s"))
    handler.addFilter(RequestIdFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())

    # 요청 로그는 미들웨어가 직접 남기므로 uvicorn 기본 액세스 로그는 끈다.
    logging.getLogger("uvicorn.access").disabled = True


logger = logging.getLogger("chatbot")


def log_event(event: str, level: int = logging.INFO, **fields: object) -> None:
    """`event key=value ...` 형태로 남긴다.

    사용 예:
        log_event("ai_call_success", latency_ms=1240)
        log_event("ai_call_failed", level=logging.ERROR, error_code="AI_TIMEOUT")
    """
    parts = [f"request_id={request_id_ctx.get()}"]
    parts += [f"{key}={value}" for key, value in fields.items() if value is not None]
    logger.log(level, "%s %s", event, " ".join(parts))
