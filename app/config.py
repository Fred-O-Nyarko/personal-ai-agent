from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path

# Always resolves to the project root regardless of where python is invoked
ROOT_DIR = Path(__file__).parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── App ───────────────────────────────────────────────────
    app_name: str = "Freddy AI"
    debug: bool = False
    log_level: str = "INFO"
    allowed_origins: list[str] = ["http://localhost", "http://localhost:3000"]

    # ── LLM ───────────────────────────────────────────────────
    llm_provider: str = "openai"
    openai_api_key: str
    openai_model:str = "gpt-4o"

    # ── Database ──────────────────────────────────────────────
    database_url:str

    # ── Tools ─────────────────────────────────────────────────
    max_content_tokens: int = 12000
    request_timeout_seconds: int = 15

@lru_cache
def get_settings() -> Settings:
    return Settings()


