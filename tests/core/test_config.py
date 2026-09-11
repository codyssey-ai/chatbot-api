from app.core.config import Settings


def make_settings(**overrides: object) -> Settings:
    values = {
        "openai_api_key": "test-openai-key",
        "database_url": "postgresql://test:test@localhost:5432/test",
        "supabase_url": "https://example.supabase.co",
        "supabase_anon_key": "test-anon-key",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_main_and_summary_models_default_to_openai() -> None:
    settings = make_settings()

    assert settings.main_model_provider == "openai"
    assert settings.summary_model_provider == "openai"


def test_gemini_is_selected_only_when_configured() -> None:
    settings = make_settings(
        gemini_api_key="test-gemini-key",
        main_model_provider="gemini",
        summary_model_provider="gemini",
    )

    assert settings.main_model_provider == "gemini"
    assert settings.summary_model_provider == "gemini"
