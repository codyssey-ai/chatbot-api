"""LangGraph 에이전트 구성.

컨텍스트 유지 전략의 핵심은 두 가지다.

1. FastAPI 는 과거 대화를 다시 조립하지 않는다. 현재 질문만 넘긴다.
2. 같은 thread_id 를 넘기면 체크포인터가 이전 State 를 복구한다.

자세한 내용은 docs/API_SPEC.md 5장 참고.
"""

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain.chat_models import init_chat_model

from app.chat.prompts import SUMMARY_PROMPT, SYSTEM_PROMPT
from app.core.config import settings


def build_agent(checkpointer):
    """체크포인터를 물린 에이전트를 만든다. lifespan 에서 한 번만 호출한다."""
    # api_key 를 명시적으로 넘긴다.
    # pydantic-settings 는 .env 를 Settings 객체로만 읽고 os.environ 에 넣지 않는데,
    # langchain_openai 는 환경 변수를 직접 읽기 때문에 그냥 두면 인증에 실패한다.
    model_kwargs = {"temperature": 0, "api_key": settings.openai_api_key}

    main_model = init_chat_model(settings.model_name, **model_kwargs)
    summary_model = init_chat_model(settings.model_name, **model_kwargs)

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
