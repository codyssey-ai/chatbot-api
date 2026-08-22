"""인증 라우터.

TODO(인증 담당): signup / login 본문 구현. 실제 호출은 service.py 에 있다.

동작 방식
    Jinja2 폼 → 여기 → Supabase Auth → JWT 수신 → HttpOnly 쿠키로 발급

주의
    - 토큰을 응답 본문에 담지 않는다. 쿠키에만 넣는다.
    - 배포 환경에서는 COOKIE_SECURE=true 로 두어 Secure 플래그를 켠다.
"""

from fastapi import APIRouter, Depends, Response

from app.auth.deps import ACCESS_TOKEN_COOKIE, CurrentUser, get_current_user
from app.auth.schemas import LoginRequest, SignupRequest, UserResponse
from app.core.deps import get_supabase

router = APIRouter(prefix="/api", tags=["auth"])


@router.post("/auth/signup", status_code=201)
async def signup(
    body: SignupRequest,
    client=Depends(get_supabase),
) -> UserResponse:
    # TODO: user = await service.sign_up(client, body.email, body.password)
    #       return UserResponse(id=user.id, email=user.email)
    raise NotImplementedError


@router.post("/auth/login")
async def login(
    body: LoginRequest,
    response: Response,
    client=Depends(get_supabase),
) -> UserResponse:
    # TODO: session = await service.sign_in(client, body.email, body.password)
    #       response.set_cookie(
    #           ACCESS_TOKEN_COOKIE,
    #           session.access_token,
    #           httponly=True,
    #           secure=settings.cookie_secure,
    #           samesite="lax",
    #           max_age=session.expires_in,
    #       )
    #       return UserResponse(id=session.user.id, email=session.user.email)
    raise NotImplementedError


@router.post("/auth/logout", status_code=204)
async def logout(response: Response) -> None:
    response.delete_cookie(ACCESS_TOKEN_COOKIE)


@router.get("/me")
async def me(user: CurrentUser = Depends(get_current_user)) -> UserResponse:
    return UserResponse(id=user.id, email=user.email)
