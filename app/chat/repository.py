"""chat_logs 테이블 접근 계층.

TODO(챗 담당): 전체 구현

chat_logs 는 LangGraph 컨텍스트 관리용이 아니다.
미들웨어가 오래된 대화를 요약해도 여기 원본은 그대로 유지된다.
"""

from uuid import UUID

from psycopg_pool import AsyncConnectionPool


async def save_success(
    pool: AsyncConnectionPool,
    *,
    thread_id: UUID,
    user_id: UUID,
    question: str,
    answer: str,
    latency_ms: int,
) -> int:
    """성공한 문답을 기록하고 id 를 돌려준다."""
    async with pool.connection() as conn:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "INSERT INTO chat_logs "
                "(thread_id, user_id, question, answer, status, latency_ms) "
                "VALUES (%s, %s, %s, %s, 'success', %s) RETURNING id",
                (thread_id, user_id, question, answer, latency_ms),
            )
            row = await cursor.fetchone()
            return row[0]


async def save_error(
    pool: AsyncConnectionPool,
    *,
    thread_id: UUID,
    user_id: UUID,
    question: str,
    error_message: str,
) -> int:
    """실패한 호출도 기록한다. answer 는 NULL 로 둔다."""
    # TODO: INSERT INTO chat_logs
    #         (thread_id, user_id, question, answer, status, error_message)
    #       VALUES (%s, %s, %s, NULL, 'error', %s) RETURNING id
    raise NotImplementedError


async def list_by_thread(pool: AsyncConnectionPool, thread_id: UUID) -> list[dict]:
    """대화 내역을 시간순으로 돌려준다. 화면 복구에 쓴다."""
    # TODO: WHERE thread_id = %s ORDER BY created_at
    raise NotImplementedError
