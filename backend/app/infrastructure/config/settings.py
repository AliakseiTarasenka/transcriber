"""Typed application settings loaded from environment / .env."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = Field(default="transcriber")
    app_env: str = Field(default="development")
    log_level: str = Field(default="INFO")

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)

    # CORS
    cors_origins: str = Field(default="http://localhost:3000")

    # Anthropic
    anthropic_api_key: str = Field(default="")
    anthropic_model: str = Field(default="claude-sonnet-4-5-20250929")
    # Sampling temperature for Claude. Low values (0.0-0.3) keep summaries
    # faithful to the transcript; higher values introduce creative phrasing.
    anthropic_temperature: float = Field(default=0.3, ge=0.0, le=1.0)

    # Limits
    #
    # Claude Sonnet/Opus 4.x context window = 200_000 tokens (~600_000 chars).
    # We reserve room for the system prompt + user prompt + completion, so the
    # transcript itself is capped at ~200k chars (≈50k tokens). This comfortably
    # fits a ~3-hour video; longer ones fall back to smart truncation.
    max_transcript_chars: int = Field(default=200_000, ge=1_000, le=600_000)
    # Output cap. Sonnet 4.5 / Haiku 4.5 support up to 64k output tokens; Opus
    # 4.5 supports 32k. 8k is a sane default for summaries.
    max_output_tokens: int = Field(default=8_192, ge=128, le=64_000)
    default_lang: str = Field(default="ru")

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings accessor."""
    return Settings()
