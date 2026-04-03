"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://shortener_app:localdev@localhost:5432/shortener"
    environment: str = "development"

    # Queue
    queue_provider: str = "dev"
    gcp_project_id: str = ""
    click_topic: str = "click-events"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
