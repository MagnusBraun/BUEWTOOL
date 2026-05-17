from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+psycopg://lst:lst@localhost:5432/lst_kuep"
    upload_dir: str = "./data/uploads"
    max_upload_mb: int = 50
    api_v1_prefix: str = "/api/v1"


settings = Settings()
