"""채팅방 및 메시지 라우터.

TODO(챗 담당): 전체 구현

모든 엔드포인트는 로그인 사용자 기준으로 동작한다.
thread_id 를 받는 요청은 반드시 소유권을 먼저 확인한다.
타인의 thread 이면 403 이 아니라 404 를 돌려준다. 존재 여부를 노출하지 않기 위해서다.

메시지 전송 처리 순서 (docs/API_SPEC.md 7.5)
    1. 로그인 확인            get_current_user
    2. thread 소유권 확인
    3. 입력 검증              MessageRequest 가 처리
    4. LangGraph 호출         현재 질문만 넘긴다. 과거 대화는 넘기지 않는다
    5. 응답 반환
    6. chat_logs 저장         실패도 status='error' 로 기록
    7. updated_at 갱신        DB 트리거가 처리
"""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.dependencies import CurrentUser, get_agent, get_current_user, get_pool
from app.schemas import (
    ChatLogResponse,
    MessageRequest,
    MessageResponse,
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
    # TODO: INSERT INTO chat_threads (user_id, title) ... RETURNING *
    #       title 이 없으면 DB 기본값('새 대화')을 그대로 쓴다.
    raise NotImplementedError


@router.get("")
async def list_threads(
    user: CurrentUser = Depends(get_current_user),
    pool=Depends(get_pool),
) -> list[ThreadResponse]:
    # TODO: WHERE user_id = %s ORDER BY updated_at DESC
    raise NotImplementedError


@router.patch("/{thread_id}")
async def rename_thread(
    thread_id: UUID,
    body: ThreadUpdateRequest,
    user: CurrentUser = Depends(get_current_user),
    pool=Depends(get_pool),
) -> ThreadResponse:
    # TODO: 소유권 확인 후 UPDATE. updated_at 은 트리거가 갱신한다.
    raise NotImplementedError


@router.delete("/{thread_id}", status_code=204)
async def delete_thread(
    thread_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    pool=Depends(get_pool),
) -> None:
    # TODO: 소유권 확인 후 DELETE. chat_logs 는 CASCADE 로 함께 지워진다.
    #
    # 주의: LangGraph 체크포인트는 CASCADE 대상이 아니다. 반드시 별도로 지운다.
    #   await checkpointer.adelete_thread(str(thread_id))
    # 빠뜨리면 삭제한 대화의 State 가 계속 남아 500MB 한도를 잠식한다.
    raise NotImplementedError


@router.get("/{thread_id}/messages")
async def list_messages(
    thread_id: UUID,
    user: CurrentUser = Depends(get_current_user),
    pool=Depends(get_pool),
) -> list[ChatLogResponse]:
    # TODO: 소유권 확인 후 chat_logs 를 created_at ASC 로 조회한다.
    #       체크포인트가 아니라 chat_logs 를 읽는다. 요약되지 않은 원본이 필요하다.
    raise NotImplementedError


@router.post("/{thread_id}/messages")
async def send_message(
    thread_id: UUID,
    body: MessageRequest,
    user: CurrentUser = Depends(get_current_user),
    pool=Depends(get_pool),
    agent=Depends(get_agent),
) -> MessageResponse:
    # TODO: 위 주석의 처리 순서대로 구현한다.
    #
    #   result = await agent.ainvoke(
    #       {"messages": [{"role": "user", "content": body.message}]},
    #       config={"configurable": {"thread_id": str(thread_id)}},
    #   )
    #   answer = result["messages"][-1].content
    #
    # 실패 시 AITimeout / AIUpstreamError 를 던지고, chat_logs 에는
    # status='error', error_message=원문 으로 남긴다.
    # 로그 이벤트: ai_call_start / ai_call_success / ai_call_failed / db_save_success
    raise NotImplementedError
