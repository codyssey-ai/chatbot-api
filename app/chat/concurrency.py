"""같은 채팅방의 동시 Agent 실행을 막는 프로세스 내 가드."""

import asyncio
from contextlib import asynccontextmanager
from uuid import UUID

from app.core.errors import Conflict


class ThreadRunGuard:
    """thread_id별로 하나의 AI 실행만 허용한다.

    현재 배포는 단일 애플리케이션 프로세스를 전제로 한다. 다중 워커/인스턴스로
    확장하면 PostgreSQL advisory lock 또는 별도 락 테이블로 대체해야 한다.
    """

    def __init__(self) -> None:
        self._locks: dict[str, asyncio.Lock] = {}

    @asynccontextmanager
    async def acquire(self, thread_id: UUID):
        key = str(thread_id)
        lock = self._locks.setdefault(key, asyncio.Lock())
        if lock.locked():
            raise Conflict(
                "이 대화는 현재 응답을 생성 중입니다. 잠시 후 다시 시도해 주세요.",
                detail=f"thread_id={key}",
            )

        await lock.acquire()
        try:
            yield
        finally:
            lock.release()
            if not lock.locked():
                self._locks.pop(key, None)


thread_run_guard = ThreadRunGuard()
