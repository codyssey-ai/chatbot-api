"""인증 라우터.

TODO(인증 담당): signup / login 구현

동작 방식
    Jinja2 폼 → 여기 → Supabase Auth → JWT 수신 → HttpOnly 쿠키로 발급

주의
    - 토큰을 응답 본문에 담지 않는다. 쿠키에만 넣는다.
    - 배포 환경에서는 COOKIE_SECURE=true 로 두어 Secure 플래그를 켠다.
    - Supabase 대시보드에서 이메일 확인(Confirm email)을 꺼야 가입 즉시 로그인된다.
"""

from fastapi import APIRouter, Depends, Response

from app.dependencies import ACCESS_TOKEN_COOKIE, CurrentUser, get_current_user
from app.schemas import LoginRequest, SignupRequest, UserResponse

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/auth/signup", status_code=201)
async def signup(body: SignupRequest) -> UserResponse:
    # TODO: client.auth.sign_up({"email": ..., "password": ...})
    #       이미 가입된 이메일이면 409 로 안내한다.
    raise NotImplementedError


@router.post("/auth/login")
async def login(body: LoginRequest, response: Response) -> UserResponse:
    # TODO: client.auth.sign_in_with_password(...) 로 세션을 받고 아래처럼 쿠키를 심는다.
    #   response.set_cookie(
    #       ACCESS_TOKEN_COOKIE,
    #       session.access_token,
    #       httponly=True,
    #       secure=settings.cookie_secure,
    #       samesite="lax",
    #       max_age=session.expires_in,
    #   )
    raise NotImplementedError


@router.post("/auth/logout", status_code=204)
async def logout(response: Response) -> None:
    response.delete_cookie(ACCESS_TOKEN_COOKIE)


@router.get("/me")
async def me(user: CurrentUser = Depends(get_current_user)) -> UserResponse:
    return UserResponse(id=user.id, email=user.email)
