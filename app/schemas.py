"""요청/응답 스키마. 입력 검증도 여기서 처리한다."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.config import settings


# --- 인증 --------------------------------------------------------------------


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str


# --- 채팅방 ------------------------------------------------------------------


class ThreadCreateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=100)


class ThreadUpdateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=100)


class ThreadResponse(BaseModel):
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


# --- 메시지 ------------------------------------------------------------------


class MessageRequest(BaseModel):
    message: str

    @field_validator("message")
    @classmethod
    def not_blank(cls, value: str) -> str:
        # 공백만 입력하는 경우를 막는다. 과제 요구사항의 입력 검증에 해당한다.
        stripped = value.strip()
        if not stripped:
            raise ValueError("메시지를 입력해 주세요.")
        if len(stripped) > settings.max_message_length:
            raise ValueError(
                f"메시지는 {settings.max_message_length}자를 넘을 수 없습니다."
            )
        return stripped


class MessageResponse(BaseModel):
    thread_id: UUID
    answer: str


class ChatLogResponse(BaseModel):
    id: int
    question: str
    answer: str | None
    status: str
    created_at: datetime
