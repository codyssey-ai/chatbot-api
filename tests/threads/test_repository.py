from uuid import uuid4

import pytest

from app.threads import repository


class FakeCursor:
    def __init__(self, rows: list[dict]) -> None:
        self.rows = rows
        self.query = ""
        self.params: tuple | None = None
        self.row_factory = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def execute(self, query: str, params: tuple) -> None:
        self.query = query
        self.params = params

    async def fetchone(self):
        return self.rows[0]

    async def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self, cursor: FakeCursor) -> None:
        self.fake_cursor = cursor

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    def cursor(self, *, row_factory):
        self.fake_cursor.row_factory = row_factory
        return self.fake_cursor


class FakePool:
    def __init__(self, cursor: FakeCursor) -> None:
        self.connection_instance = FakeConnection(cursor)

    def connection(self):
        return self.connection_instance


@pytest.mark.asyncio
async def test_create_uses_database_uuid_and_default_title() -> None:
    user_id = uuid4()
    thread_id = uuid4()
    cursor = FakeCursor([{"id": thread_id, "title": "새 대화"}])

    thread = await repository.create(FakePool(cursor), user_id, None)

    assert thread["id"] == thread_id
    assert "(user_id)" in cursor.query
    assert "title" not in cursor.query.split("VALUES")[0]
    assert cursor.params == (user_id,)


@pytest.mark.asyncio
async def test_list_by_user_orders_threads_by_recent_activity() -> None:
    user_id = uuid4()
    rows = [{"id": uuid4(), "title": "최근 대화"}]
    cursor = FakeCursor(rows)

    threads = await repository.list_by_user(FakePool(cursor), user_id)

    assert threads == rows
    assert "WHERE user_id = %s ORDER BY updated_at DESC" in cursor.query
    assert cursor.params == (user_id,)
