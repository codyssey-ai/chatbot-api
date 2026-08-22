"""Supabase PostgreSQL 커넥션 풀.

풀은 lifespan 에서 한 번만 열고 애플리케이션 전체가 공유한다.
LangGraph 체크포인터도 같은 풀을 사용한다.
"""

from psycopg_pool import AsyncConnectionPool

from app.config import settings


def create_pool() -> AsyncConnectionPool:
    return AsyncConnectionPool(
        conninfo=settings.database_url,
        min_size=1,
        # Supabase 무료 플랜은 동시 연결 수가 제한적이라 작게 잡는다.
        max_size=5,
        kwargs={
            # checkpointer.setup() 이 DDL 을 실행하므로 필요하다.
            "autocommit": True,
            # Transaction 모드 풀러(6543)는 prepared statement 를 지원하지 않는다.
            # Session 모드(5432)를 쓰더라도 켜 두면 안전하다.
            "prepare_threshold": None,
        },
        open=False,
    )


async def ping(pool: AsyncConnectionPool) -> None:
    """DB 가 살아 있는지 확인한다. /health 가 호출한다.

    Supabase 무료 플랜은 7일 무활동 시 프로젝트가 일시정지되므로,
    이 질의가 유휴 방지 역할도 겸한다.
    """
    async with pool.connection() as conn:
        await conn.execute("SELECT 1")
