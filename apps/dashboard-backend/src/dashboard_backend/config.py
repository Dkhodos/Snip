"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = ""
    db_host: str = ""
    db_port: int = 5432
    db_name: str = ""
    db_user: str = ""
    db_password: str = ""

    clerk_publishable_key: str = ""
    clerk_secret_key: str = ""
    environment: str = "development"

    email_provider: str = "mailpit"
    resend_api_key: str = ""
    email_from: str = "Snip <noreply@snip.dev>"
    smtp_host: str = "localhost"
    smtp_port: int = 1025
    click_threshold: int = 100
    allowed_origins: str = "http://localhost:5173"

    # Storage (OG image generation)
    storage_provider: str = ""
    storage_endpoint: str = ""
    storage_access_key: str = ""
    storage_secret_key: str = ""
    gcp_project_id: str = ""
    og_image_bucket: str = ""
    og_image_public_url_base: str = ""
    redirect_base_url: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def effective_database_url(self) -> str:
        """Return DATABASE_URL if set, otherwise construct from individual components."""
        if self.database_url:
            return self.database_url
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
