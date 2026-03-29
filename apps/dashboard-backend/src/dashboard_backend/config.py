"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://shortener_app:localdev@localhost:5432/shortener"
    clerk_publishable_key: str = ""
    clerk_secret_key: str = ""
    environment: str = "development"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
