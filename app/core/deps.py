"""애플리케이션 전역 자원 의존성.

lifespan 에서 만들어 app.state 에 올려둔 것들을 라우터로 꺼내 준다.
"""

from fastapi import Request
from psycopg_pool import AsyncConnectionPool


def get_pool(request: Request) -> AsyncConnectionPool:
    return request.app.state.pool


def get_agent(request: Request):
    return request.app.state.agent


def get_checkpointer(request: Request):
    return request.app.state.checkpointer


def get_supabase(request: Request):
    return request.app.state.supabase
