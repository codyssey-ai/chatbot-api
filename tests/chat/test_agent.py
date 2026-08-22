from types import SimpleNamespace

from app.chat import agent


class FakeChatOpenAI:
    def __init__(self, **kwargs: object) -> None:
        self.kwargs = kwargs


def test_openai_model_uses_configured_timeout_without_sdk_retry(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        agent,
        "settings",
        SimpleNamespace(
            openai_model_name="gpt-4.1-mini",
            openai_api_key="test-openai-key",
            openai_timeout_seconds=18,
        ),
    )
    monkeypatch.setattr(agent, "ChatOpenAI", FakeChatOpenAI)

    model = agent.build_openai_model()

    assert model.kwargs == {
        "model": "gpt-4.1-mini",
        "temperature": 0,
        "api_key": "test-openai-key",
        "timeout": 18,
        "max_retries": 0,
    }
