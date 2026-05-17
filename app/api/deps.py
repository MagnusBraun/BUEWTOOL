from functools import lru_cache

from app.core.config import Settings, get_settings
from app.services.upload import DocumentUploadService


@lru_cache
def get_upload_service() -> DocumentUploadService:
    return DocumentUploadService(get_settings())


def get_settings_dep() -> Settings:
    return get_settings()
