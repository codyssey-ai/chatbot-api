"""LangGraph 에이전트 구성.

컨텍스트 유지 전략의 핵심은 두 가지다.

1. FastAPI 는 과거 대화를 다시 조립하지 않는다. 현재 질문만 넘긴다.
2. 같은 thread_id 를 넘기면 체크포인터가 이전 State 를 복구한다.

자세한 내용은 docs/API_SPEC.md 5장 참고.
"""

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain.chat_models import init_chat_model

from app.config import settings

SYSTEM_PROMPT = (
    "너는 간결하고 정확한 AI 어시스턴트다. "
    "이전 대화의 결정사항과 제약조건을 일관되게 유지한다."
)

# {messages} 플레이스홀더와 <messages> 블록은 반드시 유지해야 한다.
SUMMARY_PROMPT = """
<role>
Conversation Context Compressor
</role>

<instructions>
아래 과거 대화를 이후 대화를 이어가는 데 필요한 정보만 남기도록 압축하라.

반드시 보존:
- 사용자의 현재 목표
- 이미 결정된 사항
- 사용자가 명시한 제약조건
- 중요한 기술명, 수치, 고유명사
- 현재 진행 중인 작업
- 아직 해결되지 않은 질문

제외:
- 인사말
- 반복 설명
- 이미 의미가 없어진 중간 대화
- 불필요한 표현

가능하면 아래 형식을 사용하라.

## GOAL
...

## DECISIONS
...

## CONSTRAINTS
...

## OPEN ITEMS
...

요약 결과만 반환하라.
</instructions>

<messages>
{messages}
</messages>
"""


def build_agent(checkpointer):
    """체크포인터를 물린 에이전트를 만든다. lifespan 에서 한 번만 호출한다."""
    main_model = init_chat_model(settings.model_name, temperature=0)
    summary_model = init_chat_model(settings.model_name, temperature=0)

    return create_agent(
        model=main_model,
        tools=[],
        system_prompt=SYSTEM_PROMPT,
        middleware=[
            SummarizationMiddleware(
                model=summary_model,
                # 메시지 수가 아니라 토큰 기준으로 잡는다. tool call 이 늘어나면
                # "최근 N개 메시지 = N/2 턴" 이 성립하지 않기 때문이다.
                trigger=("tokens", settings.summary_trigger_tokens),
                keep=("tokens", settings.summary_keep_tokens),
                summary_prompt=SUMMARY_PROMPT,
            )
        ],
        checkpointer=checkpointer,
        name="main_agent",
    )
