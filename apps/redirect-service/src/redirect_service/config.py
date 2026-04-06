"""Application configuration."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = ""
    db_host: str = ""
    db_port: int = 5432
    db_name: str = ""
    db_user: str = ""
    db_password: str = ""

    environment: str = "development"

    # Queue
    queue_provider: str = "dev"
    gcp_project_id: str = ""
    click_topic: str = "click-events"

    # OG image
    og_image_base_url: str = ""
    redirect_base_url: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}

    @property
    def effective_database_url(self) -> str:
        """Return DATABASE_URL if set, otherwise construct from individual components."""
        if self.database_url:
            return self.database_url
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


settings = Settings()
