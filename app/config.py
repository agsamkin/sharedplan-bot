from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    TELEGRAM_BOT_TOKEN: str
    DATABASE_URL: str
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str
    NEXARA_API_KEY: str
    OWNER_TELEGRAM_ID: int

    TIMEZONE: str = "Europe/Moscow"
    REMINDER_CHECK_INTERVAL_SECONDS: int = 30

    MINI_APP_URL: str = ""
    MINI_APP_PORT: int = 8080


settings = Settings()
