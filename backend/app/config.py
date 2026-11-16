"""App settings, read from environment variables (or a local .env file).

DevOps rule (12-factor app): config lives in the ENVIRONMENT, not in code.
The same code/image runs in dev, staging and prod; only env vars change.
"""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "NotesHub"
    app_version: str = "0.1.0"       # CI will set this to the release tag later
    environment: str = "dev"         # dev | staging | prod
    log_level: str = "INFO"
    database_url: str = "postgresql+psycopg://noteshub:noteshub@127.0.0.1:5432/noteshub"
    cors_origins: list[str] = ["http://localhost:8080"]  # frontend URL(s), JSON list in env


@lru_cache
def get_settings() -> Settings:
    return Settings()
