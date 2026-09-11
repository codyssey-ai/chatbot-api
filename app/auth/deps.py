"""인증 의존성. 로그인이 필요한 엔드포인트에 Depends 로 건다."""

from dataclasses import dataclass
from uuid import UUID

from fastapi import Depends, Request

from app.auth import service
from app.core.deps import get_supabase
from app.core.errors import Unauthorized

ACCESS_TOKEN_COOKIE = "access_token"


@dataclass
class CurrentUser:
    id: UUID
    email: str


async def get_current_user(
    request: Request,
    client=Depends(get_supabase),
) -> CurrentUser:
    token = request.cookies.get(ACCESS_TOKEN_COOKIE)
    if not token:
        raise Unauthorized()

    user = await service.verify_token(client, token)
    if user is None:
        raise Unauthorized("세션이 만료되었습니다. 다시 로그인해 주세요.")

    return CurrentUser(id=user.id, email=user.email)
