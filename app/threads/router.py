"""채팅방 CRUD 라우터.

메시지 전송과 조회는 app/chat/router.py 에 있다.

모든 엔드포인트는 로그인 사용자 기준으로 동작하며,
thread_id 를 받는 요청은 반드시 소유권을 먼저 확인한다.
"""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.auth.deps import CurrentUser, get_current_user
from app.core.deps import get_checkpointer, get_pool
from app.threads import service
from app.threads.schemas import (
    ThreadCreateRequest,
    ThreadResponse,
    ThreadUpdateRequest,
)

router = APIRouter(prefix="/api/threads", tags=["threads"])


@router.post("", status_code=201)
async def create_thread(
    body: ThreadCreateRequest,
    user: CurrentUser = Depends(get_current_user),
    pool=Depends(get_pool),
) -> ThreadResponse:
    thread = await service.create_thread(pool, user.id, body.title)
    return ThreadResponse(**thread)


@router.get("")
async def list_threads(
    user: CurrentUser = Depends(get_current_user),
    pool=Depends(get_pool),
) -> list[ThreadResponse]:
    threads = await service.list_threads(pool, user.id)
    return [ThreadResponse(**t) for t in threads]


@router.patch("/{thread_id}")
async def rename_thread(
    thread_id: UUID,
    body: ThreadUpdateRequest,
    user: CurrentUser = Depends(get_current_user),
    pool=Depends(get_pool),
) -> ThreadResponse:
    thread = await service.rename_thread(pool, thread_id, user.id, body.title)
    return ThreadResponse(**thread)


@router.delete("/{thread_id}", status_code=204)
async def delete_thread(
    thread_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    pool=Depends(get_pool),
    checkpointer=Depends(get_checkpointer),
) -> None:
    await service.delete_thread(pool, checkpointer, thread_id, user.id)
