from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


class FileStorage:
    def __init__(self, base_dir: str | None = None) -> None:
        self.base = Path(base_dir or settings.upload_dir)
        self.base.mkdir(parents=True, exist_ok=True)

    async def save(self, file: UploadFile, subdir: str) -> tuple[str, str]:
        original = file.filename or "upload"
        suffix = Path(original).suffix.lower()
        stored_name = f"{uuid4().hex}{suffix}"
        target_dir = self.base / subdir
        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / stored_name
        content = await file.read()
        path.write_bytes(content)
        return str(path.resolve()), stored_name
