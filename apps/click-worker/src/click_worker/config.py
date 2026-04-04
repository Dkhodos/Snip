"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    environment: str = "development"

    # Analytics
    analytics_provider: str = "dev"
    gcp_project_id: str = ""
    bq_dataset: str = ""
    bq_table: str = "click_events"

    # Pub/Sub push authentication
    # Set to the full HTTPS URL of the /ingest endpoint (the push subscription audience).
    # Leave empty to disable verification (dev/test only).
    pubsub_audience: str = ""
    enable_pubsub_auth: bool = True

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
