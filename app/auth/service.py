"""Supabase Auth 호출 계층.

TODO(인증 담당): 전체 구현

자격 증명 관리만 Supabase 에 위임하고, 세션 유지와 접근 제어는 우리가 담당한다.
라우터는 이 모듈만 호출하고 supabase 클라이언트를 직접 다루지 않는다.

주의
    - Supabase 대시보드에서 이메일 확인(Confirm email)을 꺼야 가입 즉시 로그인된다.
    - 실패 원문을 그대로 사용자에게 돌려주지 않는다. AppError 로 감싼다.
"""

from dataclasses import dataclass
from uuid import UUID


@dataclass
class AuthUser:
    id: UUID
    email: str


@dataclass
class AuthSession:
    user: AuthUser
    access_token: str
    expires_in: int


async def sign_up(client, email: str, password: str) -> AuthUser:
    """계정을 만든다. 이미 가입된 이메일이면 409 로 안내한다."""
    # TODO: response = client.auth.sign_up({"email": email, "password": password})
    #       return AuthUser(id=UUID(response.user.id), email=response.user.email)
    raise NotImplementedError


async def sign_in(client, email: str, password: str) -> AuthSession:
    """로그인해 세션을 받는다. 실패하면 401 로 안내한다."""
    # TODO: response = client.auth.sign_in_with_password(
    #           {"email": email, "password": password}
    #       )
    #       session, user = response.session, response.user
    #       return AuthSession(
    #           user=AuthUser(id=UUID(user.id), email=user.email),
    #           access_token=session.access_token,
    #           expires_in=session.expires_in,
    #       )
    raise NotImplementedError


async def verify_token(client, token: str) -> AuthUser | None:
    """액세스 토큰을 검증한다. 유효하지 않으면 None 을 돌려준다.

    초기 구현은 Supabase 에 조회하는 방식으로 단순하게 간다.
    요청마다 외부 왕복이 생기므로, 지연이 문제가 되면 로컬 JWT 검증으로 바꾼다.
    docs/API_SPEC.md 8.2 참고.
    """
    # TODO: response = client.auth.get_user(token)
    #       if response is None or response.user is None:
    #           return None
    #       return AuthUser(id=UUID(response.user.id), email=response.user.email)
    raise NotImplementedError
