from __future__ import annotations

from pathlib import Path
from zoneinfo import ZoneInfo

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str = Field(..., alias="BOT_TOKEN")

    database_url: str = Field("postgres://bot:bot@localhost:5432/anti_sedentary", alias="DATABASE_URL")

    timezone: str = Field("Europe/Amsterdam", alias="TIMEZONE")
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    # LLM provider — pick any OpenAI-compatible endpoint via LLM_BASE_URL + LLM_MODEL.
    # Common providers (set LLM_BASE_URL and LLM_MODEL accordingly):
    #   Groq:       https://api.groq.com/openai/v1            llama-3.3-70b-versatile
    #   OpenAI:     https://api.openai.com/v1                  gpt-4o-mini
    #   Together:   https://api.together.xyz/v1                meta-llama/Llama-3.3-70B-Instruct-Turbo
    #   OpenRouter: https://openrouter.ai/api/v1               anthropic/claude-haiku-4.5
    #   Local Ollama: http://localhost:11434/v1                llama3.2
    # The API key is read from LLM_API_KEY first, with GROQ_API_KEY as a back-compat fallback.
    llm_enabled: bool = Field(True, alias="LLM_ENABLED")
    llm_provider: str = Field("groq", alias="LLM_PROVIDER")  # label only — for diagnostics
    llm_base_url: str = Field("https://api.groq.com/openai/v1", alias="LLM_BASE_URL")
    llm_model: str = Field("groq/compound-mini", alias="LLM_MODEL")
    llm_api_key: str = Field("", alias="LLM_API_KEY")
    groq_api_key: str = Field("", alias="GROQ_API_KEY")  # legacy fallback
    llm_max_history_messages: int = 24
    llm_timeout_seconds: int = 15

    # Comma-separated list of Telegram user_ids with admin powers
    admin_user_ids: str = Field("", alias="ADMIN_USER_IDS")

    default_day_start: str = "11:00"
    default_day_end: str = "18:00"
    default_break_every_minutes: int = 45

    scheduler_tick_seconds: int = 30
    nudge_after_minutes: int = 5
    fail_after_minutes: int = 15
    max_nudges_before_penalty: int = 2

    min_unlock_seconds: int = 35
    max_unlock_seconds: int = 8 * 60

    check_question_probability: float = 0.65

    throttle_rate_seconds: float = 0.7
    scheduler_concurrency: int = 20
    health_tick_seconds: int = 60

    # Message retention
    message_retention_days: int = 30
    cleanup_hour: int = 4

    # DB connection pool
    db_pool_minsize: int = 1
    db_pool_maxsize: int = 20
    db_connect_timeout: int = 10

    # Weekly summary
    weekly_summary_day_of_week: str = "mon"
    weekly_summary_hour: int = 9

    # Healthcheck HTTP server
    health_host: str = "0.0.0.0"
    health_port: int = 8080
    health_enabled: bool = True

    # Exercises YAML path (None = auto-resolve to config/exercises.yaml)
    exercises_path: Path | None = None

    @property
    def tz(self) -> ZoneInfo:
        return ZoneInfo(self.timezone)

    @property
    def llm_effective_api_key(self) -> str:
        return self.llm_api_key or self.groq_api_key

    @property
    def admin_ids(self) -> set[int]:
        if not self.admin_user_ids:
            return set()
        out: set[int] = set()
        for chunk in self.admin_user_ids.split(","):
            chunk = chunk.strip()
            if chunk.isdigit():
                out.add(int(chunk))
        return out

    @property
    def resolved_exercises_path(self) -> Path:
        if self.exercises_path is not None:
            return Path(self.exercises_path)
        # Walk up from this file: config.py → anti_sedentary_bot → src → repo root
        return Path(__file__).resolve().parents[2] / "config" / "exercises.yaml"


settings = Settings()  # type: ignore[call-arg]
