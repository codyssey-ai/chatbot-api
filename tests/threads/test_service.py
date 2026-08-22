from uuid import uuid4

import pytest

from app.threads import service


class FakeCheckpointer:
    def __init__(self) -> None:
        self.deleted_thread_id: str | None = None

    async def adelete_thread(self, thread_id: str) -> None:
        self.deleted_thread_id = thread_id


@pytest.mark.asyncio
async def test_delete_thread_removes_langgraph_state(monkeypatch) -> None:
    thread_id = uuid4()
    user_id = uuid4()
    checkpointer = FakeCheckpointer()

    async def delete_owned_thread(*args, **kwargs) -> bool:
        return True

    monkeypatch.setattr(service.repository, "delete", delete_owned_thread)

    await service.delete_thread(None, checkpointer, thread_id, user_id)

    assert checkpointer.deleted_thread_id == str(thread_id)
