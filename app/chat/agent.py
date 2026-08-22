"""LangGraph 에이전트 구성.

컨텍스트 유지 전략의 핵심은 두 가지다.

1. FastAPI 는 과거 대화를 다시 조립하지 않는다. 현재 질문만 넘긴다.
2. 같은 thread_id 를 넘기면 체크포인터가 이전 State 를 복구한다.

자세한 내용은 docs/API_SPEC.md 5장 참고.
"""

from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from app.chat.prompts import SUMMARY_PROMPT, SYSTEM_PROMPT
from app.core.config import settings


def build_openai_model() -> ChatOpenAI:
    """기본 OpenAI 모델 인스턴스를 만든다.

    main과 summary는 같은 공급자를 쓰더라도 인스턴스를 공유하지 않는다.
    이후 한쪽만 다른 공급자로 전환해도 서로의 설정에 영향을 주지 않는다.
    """
    return ChatOpenAI(
        model=settings.openai_model_name,
        temperature=0,
        api_key=settings.openai_api_key,
        timeout=settings.openai_timeout_seconds,
        # 재시도 대신 명시적인 Gemini 폴백으로 장애를 처리한다.
        max_retries=0,
    )


def build_gemini_model() -> ChatGoogleGenerativeAI:
    """명시적으로 선택한 경우에만 Gemini 모델 인스턴스를 만든다."""
    if not settings.gemini_api_key:
        raise ValueError("GEMINI_API_KEY가 설정되어 있지 않습니다.")

    return ChatGoogleGenerativeAI(
        model=settings.gemini_model_name,
        temperature=0,
        api_key=settings.gemini_api_key,
        request_timeout=settings.gemini_timeout_seconds,
        retries=0,
    )


def build_model(provider: str):
    """설정에서 명시한 공급자의 역할별 모델을 만든다."""
    if provider == "openai":
        return build_openai_model()
    if provider == "gemini":
        return build_gemini_model()
    raise ValueError(f"지원하지 않는 모델 공급자입니다: {provider}")


def build_agent(checkpointer):
    """체크포인터를 물린 에이전트를 만든다. lifespan 에서 한 번만 호출한다."""
    # 기본 상태에서는 main과 summary 모두 OpenAI를 쓴다.
    # 환경 변수로 명시한 역할만 Gemini로 전환할 수 있다.
    main_model = build_model(settings.main_model_provider)
    summary_model = build_model(settings.summary_model_provider)

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
