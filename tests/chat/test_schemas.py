import pytest
from pydantic import ValidationError

from app.chat.schemas import MessageRequest


def test_message_request_strips_surrounding_whitespace() -> None:
    request = MessageRequest(message="  이전 대화를 기억해?  ")

    assert request.message == "이전 대화를 기억해?"


@pytest.mark.parametrize("message", ["", "   ", "\n\t"])
def test_message_request_rejects_blank_input(message: str) -> None:
    with pytest.raises(ValidationError):
        MessageRequest(message=message)
