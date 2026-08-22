"""공통 의존성.

TODO(인증 담당): verify_token 구현 — 이슈 참조

세션 유지는 HttpOnly 쿠키로 하고, 자격 증명 검증만 Supabase Auth 에 위임한다.
초기 구현은 supabase.auth.get_user(token) 호출로 단순하게 간다.
지연이 문제가 되면 로컬 JWT 검증으로 바꾼다. docs/API_SPEC.md 8.2 참고.
"""

from dataclasses import dataclass
from uuid import UUID

from fastapi import Request
from psycopg_pool import AsyncConnectionPool

from app.errors import Unauthorized

ACCESS_TOKEN_COOKIE = "access_token"


@dataclass
class CurrentUser:
    id: UUID
    email: str


def get_pool(request: Request) -> AsyncConnectionPool:
    return request.app.state.pool


def get_agent(request: Request):
    return request.app.state.agent


def get_checkpointer(request: Request):
    return request.app.state.checkpointer


async def get_current_user(request: Request) -> CurrentUser:
    """쿠키의 액세스 토큰을 검증해 사용자를 돌려준다.

    로그인이 필요한 모든 엔드포인트에 Depends 로 건다.
    """
    token = request.cookies.get(ACCESS_TOKEN_COOKIE)
    if not token:
        raise Unauthorized()

    # TODO(인증 담당): Supabase Auth 로 토큰을 검증하고 CurrentUser 를 만든다.
    #   client = request.app.state.supabase
    #   response = client.auth.get_user(token)
    #   if response is None or response.user is None:
    #       raise Unauthorized("세션이 만료되었습니다. 다시 로그인해 주세요.")
    #   return CurrentUser(id=UUID(response.user.id), email=response.user.email)
    raise NotImplementedError("get_current_user 미구현")
