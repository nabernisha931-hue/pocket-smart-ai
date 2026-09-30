from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PocketSmart AI"

    environment: str = "development"

    debug: bool = True

    database_url: str = "sqlite:///./pocketsmart.db"

    jwt_secret_key: str = "change-me-in-production"

    jwt_algorithm: str = "HS256"

    access_token_expire_minutes: int = 120

    gemini_api_key: str = ""

    gemini_model: str = "gemini-2.5-flash"

    allowed_origins: str = (
        "http://127.0.0.1:8000,http://localhost:8000"
    )

    max_upload_mb: int = 5

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origins(self) -> list[str]:
        return [
            item.strip()
            for item in self.allowed_origins.split(",")
            if item.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()