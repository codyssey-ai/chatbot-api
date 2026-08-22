"""chat_threads 테이블 접근 계층.

TODO(챗 담당): 전체 구현

SQL 은 여기에만 둔다. 라우터와 서비스는 이 모듈을 통해서만 DB 에 닿는다.
스키마는 scripts/schema.sql 참고.
"""

from uuid import UUID

from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

# updated_at 은 DB 트리거가 갱신하므로 UPDATE 문에 직접 넣지 않는다.
COLUMNS = "id, title, created_at, updated_at"


async def create(pool: AsyncConnectionPool, user_id: UUID, title: str | None) -> dict:
    # TODO: title 이 None 이면 컬럼을 생략해 DB 기본값('새 대화')이 들어가게 한다.
    #   INSERT INTO chat_threads (user_id, title) VALUES (%s, %s) RETURNING ...
    raise NotImplementedError


async def list_by_user(pool: AsyncConnectionPool, user_id: UUID) -> list[dict]:
    # TODO: WHERE user_id = %s ORDER BY updated_at DESC
    #       idx_chat_threads_user_updated 인덱스가 이 질의를 커버한다.
    raise NotImplementedError


async def get_owned(
    pool: AsyncConnectionPool, thread_id: UUID, user_id: UUID
) -> dict | None:
    """소유권까지 함께 확인한다. 없거나 남의 것이면 None.

    라우터는 None 을 받으면 403 이 아니라 404 로 응답한다.
    403 을 주면 그 ID 의 thread 가 존재한다는 사실이 노출된다.
    """
    # TODO: WHERE id = %s AND user_id = %s
    raise NotImplementedError


async def update_title(
    pool: AsyncConnectionPool, thread_id: UUID, user_id: UUID, title: str
) -> dict | None:
    # TODO: UPDATE ... WHERE id = %s AND user_id = %s RETURNING ...
    raise NotImplementedError


async def delete(pool: AsyncConnectionPool, thread_id: UUID, user_id: UUID) -> bool:
    """삭제되면 True. chat_logs 는 ON DELETE CASCADE 로 함께 지워진다.

    LangGraph 체크포인트는 CASCADE 대상이 아니다. 서비스 계층에서 따로 지운다.
    """
    # TODO: DELETE FROM chat_threads WHERE id = %s AND user_id = %s
    raise NotImplementedError
