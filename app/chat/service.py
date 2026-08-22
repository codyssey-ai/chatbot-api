"""메시지 전송 파이프라인.

TODO(챗 담당): 전체 구현

처리 순서 (docs/API_SPEC.md 7.5)
    1. thread 소유권 확인      threads.service.require_owned
    2. LangGraph 호출          현재 질문만 넘긴다. 과거 대화는 넘기지 않는다
    3. 응답 반환
    4. chat_logs 저장          실패도 status='error' 로 기록
    5. updated_at 갱신         DB 트리거가 처리

로그 이벤트: ai_call_start / ai_call_success / ai_call_failed / db_save_success
"""

import logging
import time
from uuid import UUID

from app.chat import repository
from app.core.logging import log_event
from app.threads import service as threads_service


async def send_message(
    *,
    pool,
    agent,
    thread_id: UUID,
    user_id: UUID,
    question: str,
) -> str:
    await threads_service.require_owned(pool, thread_id, user_id)

    log_event("ai_call_start", thread_id=thread_id)
    started = time.perf_counter()

    # TODO: 아래 호출을 감싸 타임아웃과 예외를 처리한다.
    #
    #   result = await agent.ainvoke(
    #       {"messages": [{"role": "user", "content": question}]},
    #       config={"configurable": {"thread_id": str(thread_id)}},
    #   )
    #   answer = result["messages"][-1].content
    #
    # 실패 시 repository.save_error() 로 기록한 뒤
    # AITimeout / AIUpstreamError 를 던진다.
    #
    # 주의: 요약이 트리거된 턴은 LLM 을 두 번 호출한다(요약 + 본 응답).
    # 전체를 단일 타임아웃으로 묶으면 그 턴마다 실패할 수 있다.
    # docs/API_SPEC.md 12.1 참고.
    raise NotImplementedError

    latency_ms = int((time.perf_counter() - started) * 1000)
    log_event("ai_call_success", latency_ms=latency_ms)

    # DB 저장에 실패해도 이미 받은 답변은 사용자에게 돌려준다.
    try:
        chat_id = await repository.save_success(
            pool,
            thread_id=thread_id,
            user_id=user_id,
            question=question,
            answer=answer,
            latency_ms=latency_ms,
        )
        log_event("db_save_success", chat_id=chat_id)
    except Exception as exc:
        log_event("db_save_failed", level=logging.ERROR, error=type(exc).__name__)

    return answer


async def list_messages(*, pool, thread_id: UUID, user_id: UUID) -> list[dict]:
    await threads_service.require_owned(pool, thread_id, user_id)
    return await repository.list_by_thread(pool, thread_id)
