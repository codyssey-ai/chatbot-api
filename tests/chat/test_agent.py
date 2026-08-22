from types import SimpleNamespace

import pytest

from app.chat import agent


class FakeChatOpenAI:
    def __init__(self, **kwargs: object) -> None:
        self.kwargs = kwargs


class FakeChatGoogleGenerativeAI:
    def __init__(self, **kwargs: object) -> None:
        self.kwargs = kwargs


def model_settings(**overrides: object) -> SimpleNamespace:
    values = {
        "openai_model_name": "gpt-4.1-mini",
        "openai_api_key": "test-openai-key",
        "openai_timeout_seconds": 18,
        "gemini_model_name": "gemini-2.5-flash",
        "gemini_api_key": "test-gemini-key",
        "gemini_timeout_seconds": 20,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_openai_model_uses_configured_timeout_without_sdk_retry(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        agent,
        "settings",
        model_settings(),
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


def test_gemini_model_is_built_only_when_explicitly_selected(monkeypatch) -> None:
    monkeypatch.setattr(agent, "settings", model_settings())
    monkeypatch.setattr(agent, "ChatGoogleGenerativeAI", FakeChatGoogleGenerativeAI)

    model = agent.build_model("gemini")

    assert model.kwargs == {
        "model": "gemini-2.5-flash",
        "temperature": 0,
        "api_key": "test-gemini-key",
        "request_timeout": 20,
        "retries": 0,
    }


def test_gemini_model_requires_api_key(monkeypatch) -> None:
    monkeypatch.setattr(agent, "settings", model_settings(gemini_api_key=""))

    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        agent.build_model("gemini")
