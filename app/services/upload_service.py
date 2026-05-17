import logging
from pathlib import Path
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.enums import DokumentStatus, DokumentTyp
from app.models.dokument import Dokument
from app.models.projekt import Projekt
from app.storage.file_storage import FileStorage

logger = logging.getLogger(__name__)

ALLOWED_KUEP = {".pdf"}
ALLOWED_VLP = {".pdf", ".xlsx", ".xls"}


class UploadService:
    def __init__(self, storage: FileStorage | None = None) -> None:
        self.storage = storage or FileStorage()

    def _validate_size(self, content: bytes) -> None:
        max_bytes = settings.max_upload_mb * 1024 * 1024
        if len(content) > max_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Datei überschreitet {settings.max_upload_mb} MB",
            )

    def _get_suffix(self, filename: str) -> str:
        return Path(filename).suffix.lower()

    def _ensure_projekt(self, db: Session, projekt_id: UUID) -> Projekt:
        projekt = db.get(Projekt, projekt_id)
        if projekt is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Projekt {projekt_id} nicht gefunden",
            )
        return projekt

    async def upload(
        self,
        db: Session,
        *,
        projekt_id: UUID,
        dokumenttyp: DokumentTyp,
        file: UploadFile,
        allowed_suffixes: set[str],
        subdir: str,
    ) -> Dokument:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Dateiname fehlt",
            )

        suffix = self._get_suffix(file.filename)
        if suffix not in allowed_suffixes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Format '{suffix}' nicht erlaubt. Erlaubt: {sorted(allowed_suffixes)}",
            )

        self._ensure_projekt(db, projekt_id)

        content = await file.read()
        self._validate_size(content)
        await file.seek(0)

        path, stored_name = await self.storage.save(file, subdir)
        logger.info(
            "Datei gespeichert: %s -> %s (Projekt %s, Typ %s)",
            file.filename,
            stored_name,
            projekt_id,
            dokumenttyp.value,
        )

        dokument = Dokument(
            projekt_id=projekt_id,
            dokumenttyp=dokumenttyp,
            dateiname=file.filename,
            dateipfad=path,
            status=DokumentStatus.IMPORTIERT,
            metadaten={"stored_name": stored_name, "suffix": suffix},
        )
        db.add(dokument)
        db.commit()
        db.refresh(dokument)
        return dokument
