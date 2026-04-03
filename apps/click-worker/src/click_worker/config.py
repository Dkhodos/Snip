"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"

    # Analytics
    analytics_provider: str = "dev"
    gcp_project_id: str = ""
    bq_dataset: str = ""
    bq_table: str = "click_events"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
