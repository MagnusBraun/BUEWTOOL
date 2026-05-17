import logging
import shutil
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.models.document import Document
from app.models.enums import DocumentStatus, DocumentType

logger = logging.getLogger(__name__)


class UploadValidationError(ValueError):
    def __init__(self, message: str, code: str) -> None:
        super().__init__(message)
        self.code = code


class DocumentUploadService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.kuep_dir = settings.upload_dir / "kuep"
        self.vlp_dir = settings.upload_dir / "vlp"
        self.kuep_dir.mkdir(parents=True, exist_ok=True)
        self.vlp_dir.mkdir(parents=True, exist_ok=True)

    def _validate_file(self, file: UploadFile, allowed_extensions: set[str]) -> str:
        if not file.filename:
            raise UploadValidationError("Dateiname fehlt.", "missing_filename")

        suffix = Path(file.filename).suffix.lower()
        if suffix not in allowed_extensions:
            allowed = ", ".join(sorted(allowed_extensions))
            raise UploadValidationError(
                f"Dateityp '{suffix}' nicht erlaubt. Erlaubt: {allowed}",
                "invalid_extension",
            )
        return suffix

    def _validate_size(self, file: UploadFile) -> None:
        file.file.seek(0, 2)
        size_bytes = file.file.tell()
        file.file.seek(0)
        max_bytes = self.settings.max_upload_size_mb * 1024 * 1024
        if size_bytes > max_bytes:
            raise UploadValidationError(
                f"Datei zu groß ({size_bytes} Bytes). Maximum: {self.settings.max_upload_size_mb} MB",
                "file_too_large",
            )

    def _store_file(self, file: UploadFile, target_dir: Path, suffix: str) -> Path:
        stored_name = f"{uuid4()}{suffix}"
        destination = target_dir / stored_name
        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info("Datei gespeichert: %s", destination)
        return destination

    def upload_kuep(self, db: Session, file: UploadFile) -> Document:
        suffix = self._validate_file(file, self.settings.allowed_kuep_extensions)
        self._validate_size(file)
        path = self._store_file(file, self.kuep_dir, suffix)
        return self._create_document_record(
            db=db,
            dokumenttyp=DocumentType.KUEP,
            dateiname=file.filename or stored_name_from(path),
            dateipfad=str(path.resolve()),
        )

    def upload_vlp(self, db: Session, file: UploadFile) -> Document:
        suffix = self._validate_file(file, self.settings.allowed_vlp_extensions)
        self._validate_size(file)
        path = self._store_file(file, self.vlp_dir, suffix)
        return self._create_document_record(
            db=db,
            dokumenttyp=DocumentType.VLP,
            dateiname=file.filename or stored_name_from(path),
            dateipfad=str(path.resolve()),
        )

    def _create_document_record(
        self,
        db: Session,
        dokumenttyp: DocumentType,
        dateiname: str,
        dateipfad: str,
    ) -> Document:
        document = Document(
            dokumenttyp=dokumenttyp,
            dateiname=dateiname,
            dateipfad=dateipfad,
            status=DocumentStatus.HOCHGELADEN,
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        logger.info(
            "Dokument registriert: id=%s typ=%s datei=%s",
            document.id,
            dokumenttyp.value,
            dateiname,
        )
        return document


def stored_name_from(path: Path) -> str:
    return path.name
