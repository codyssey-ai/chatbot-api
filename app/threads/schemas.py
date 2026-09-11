"""채팅방 요청/응답 스키마."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ThreadCreateRequest(BaseModel):
    # 생략하면 DB 기본값('새 대화')을 쓴다.
    title: str | None = Field(default=None, max_length=100)


class ThreadUpdateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)


class ThreadResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
