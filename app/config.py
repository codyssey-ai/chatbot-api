"""환경 변수 로딩. 값은 .env 에서 읽고, 키 목록은 .env.example 을 기준으로 한다."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # model_ 로 시작하는 필드가 pydantic 예약어와 충돌하지 않도록 보호를 해제한다.
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        protected_namespaces=(),
    )

    # LLM
    openai_api_key: str
    model_name: str = "openai:gpt-4.1-mini"
    ai_timeout_seconds: int = 60
    summary_trigger_tokens: int = 8000
    summary_keep_tokens: int = 4000

    # Supabase
    database_url: str
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str

    # 애플리케이션
    log_level: str = "INFO"
    max_message_length: int = 2000
    cookie_secure: bool = False


settings = Settings()  # type: ignore[call-arg]
