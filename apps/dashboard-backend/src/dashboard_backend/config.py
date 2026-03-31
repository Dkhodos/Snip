"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://shortener_app:localdev@localhost:5432/shortener"
    clerk_publishable_key: str = ""
    clerk_secret_key: str = ""
    environment: str = "development"

    email_provider: str = "mailpit"
    resend_api_key: str = ""
    email_from: str = "Snip <noreply@snip.dev>"
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    click_threshold: int = 100

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
