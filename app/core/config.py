from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    app_name: str = "LST Bauüberwachung API"
    app_version: str = "0.1.0"
    debug: bool = False

    database_url: str = Field(
        default="postgresql+psycopg2://lst:lst@localhost:5432/lst_bauueberwachung",
        description="SQLAlchemy-Datenbank-URL",
    )

    upload_dir: Path = Field(default=Path("uploads"))
    max_upload_size_mb: int = 50
    allowed_kuep_extensions: set[str] = {".pdf"}
    allowed_vlp_extensions: set[str] = {".pdf", ".xlsx", ".xls"}

    cors_origins: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()
