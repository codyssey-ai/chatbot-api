"""애플리케이션 진입점.

실행
    uvicorn app.main:app --reload
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# 체크포인트 역직렬화 시 허용되지 않은 타입을 제한한다.
# LangGraph import 전에 설정해야 한다.
os.environ.setdefault("LANGGRAPH_STRICT_MSGPACK", "true")

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver  # noqa: E402
from supabase import create_client  # noqa: E402

from app.agent import build_agent  # noqa: E402
from app.config import settings  # noqa: E402
from app.db import create_pool, ping, secure_checkpoint_tables  # noqa: E402
from app.errors import register_error_handlers  # noqa: E402
from app.logging_config import log_event, setup_logging  # noqa: E402
from app.middleware import RequestContextMiddleware  # noqa: E402
from app.routers import auth, pages, threads  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.log_level)

    pool = create_pool()
    await pool.open()

    checkpointer = AsyncPostgresSaver(pool)
    # 체크포인트 테이블을 만든다. 이미 있으면 아무 일도 하지 않는다.
    await checkpointer.setup()
    # 방금 만들어진 테이블은 RLS 가 꺼진 상태다. 바로 막는다.
    await secure_checkpoint_tables(pool)

    app.state.pool = pool
    app.state.checkpointer = checkpointer
    app.state.agent = build_agent(checkpointer)
    app.state.supabase = create_client(
        settings.supabase_url,
        settings.supabase_anon_key,
    )

    log_event("startup_complete", model=settings.model_name)
    try:
        yield
    finally:
        await pool.close()
        log_event("shutdown_complete")


app = FastAPI(title="Chatbot API", lifespan=lifespan)

app.add_middleware(RequestContextMiddleware)
register_error_handlers(app)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(pages.router)
app.include_router(auth.router)
app.include_router(threads.router)


@app.get("/health", tags=["ops"])
async def health():
    """서버와 DB 상태 확인.

    GitHub Actions cron 이 매일 호출해 Render 와 Supabase 의 유휴 정지를 막는다.
    """
    await ping(app.state.pool)
    return {"status": "ok"}
