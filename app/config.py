from typing import Optional
from urllib.parse import quote_plus

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    TELEGRAM_BOT_TOKEN: str
    DATABASE_URL: Optional[str] = None
    OWNER_TELEGRAM_ID: int

    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "sharedplan"

    OPENROUTER_API_KEY: Optional[str] = None
    OPENROUTER_MODEL: Optional[str] = None
    NEXARA_API_KEY: Optional[str] = None

    TIMEZONE: str = "Europe/Moscow"
    REMINDER_CHECK_INTERVAL_SECONDS: int = 30

    MINI_APP_URL: str = ""
    MINI_APP_PORT: int = 8080

    @model_validator(mode="after")
    def build_database_url(self) -> "Settings":
        if self.DATABASE_URL:
            return self
        if self.DB_USER and self.DB_PASSWORD:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{quote_plus(self.DB_USER)}:{quote_plus(self.DB_PASSWORD)}"
                f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            )
            return self
        raise ValueError(
            "Необходимо задать DATABASE_URL или DB_USER + DB_PASSWORD"
        )


settings = Settings()
