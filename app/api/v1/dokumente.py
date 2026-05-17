import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.config import settings
from app.db.enums import DokumentStatus, DokumentTyp
from app.models.annotation import Annotation
from app.models.dokument import Dokument

router = APIRouter(prefix="/dokumente", tags=["dokumente"])


class DokumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    projekt_id: uuid.UUID
    dokumenttyp: DokumentTyp
    dateiname: str
    importdatum: datetime
    status: DokumentStatus


class AnnotationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    dokument_id: uuid.UUID
    objekt_id: uuid.UUID
    x: float
    y: float
    breite: float | None
    hoehe: float | None
    text: str | None
    farbe: str | None


@router.get("", response_model=list[DokumentResponse])
def list_dokumente(projekt_id: uuid.UUID, db: Session = Depends(get_db)):
    stmt = (
        select(Dokument)
        .where(Dokument.projekt_id == projekt_id)
        .order_by(Dokument.importdatum.desc())
    )
    return [DokumentResponse.model_validate(d) for d in db.scalars(stmt).all()]


@router.get("/{dokument_id}/annotations", response_model=list[AnnotationResponse])
def list_annotations(dokument_id: uuid.UUID, db: Session = Depends(get_db)):
    stmt = select(Annotation).where(Annotation.dokument_id == dokument_id)
    return [AnnotationResponse.model_validate(a) for a in db.scalars(stmt).all()]


@router.get("/{dokument_id}/file")
def get_dokument_file(dokument_id: uuid.UUID, db: Session = Depends(get_db)):
    dokument = db.get(Dokument, dokument_id)
    if not dokument:
        raise HTTPException(404, "Dokument nicht gefunden")
    path = Path(dokument.dateipfad).resolve()
    upload_root = Path(settings.upload_dir).resolve()
    if not str(path).startswith(str(upload_root)):
        raise HTTPException(403, "Zugriff verweigert")
    if not path.exists():
        raise HTTPException(404, "Datei nicht gefunden")
    media = "application/pdf" if path.suffix.lower() == ".pdf" else "application/octet-stream"
    return FileResponse(path, media_type=media, filename=dokument.dateiname)
