from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql://monitoring:monitoring@localhost:5432/monitoring",
        alias="DATABASE_URL",
    )
    check_interval_seconds: int = Field(default=10, alias="CHECK_INTERVAL_SECONDS")
    default_timeout_ms: int = Field(default=3000, alias="DEFAULT_TIMEOUT_MS")
    default_sla_target: float = Field(default=99.9, alias="DEFAULT_SLA_TARGET")
    smtp_host: str = Field(default="localhost", alias="SMTP_HOST")
    smtp_port: int = Field(default=1025, alias="SMTP_PORT")
    smtp_username: Optional[str] = Field(default=None, alias="SMTP_USERNAME")
    smtp_password: Optional[str] = Field(default=None, alias="SMTP_PASSWORD")
    smtp_from: str = Field(default="monitoring@example.com", alias="SMTP_FROM")
    smtp_use_tls: bool = Field(default=False, alias="SMTP_USE_TLS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
