import logging
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.enums import DokumentTyp
from app.schemas.upload import UploadResponse
from app.services.kuep_import_service import KuepImportService
from app.services.upload_service import ALLOWED_KUEP, ALLOWED_VLP, UploadService
from app.services.vlp_import_service import VlpImportService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload")


@router.post("/kuep", response_model=UploadResponse)
async def upload_kuep(
    projekt_id: UUID = Form(...),
    file: UploadFile = File(...),
    parse: bool = Form(True),
    db: Session = Depends(get_db),
) -> UploadResponse:
    service = UploadService()
    dokument = await service.upload(
        db,
        projekt_id=projekt_id,
        dokumenttyp=DokumentTyp.KUEP,
        file=file,
        allowed_suffixes=ALLOWED_KUEP,
        subdir="kuep",
    )
    message = "KÜP erfolgreich importiert."
    if parse:
        try:
            result = KuepImportService(db).parse_dokument(dokument.id)
            stats = result["stats"]
            message = (
                f"KÜP analysiert: {stats['verteiler']} Verteiler, "
                f"{stats['kabel']} Kabel, {stats['elemente']} Elemente."
            )
            db.refresh(dokument)
        except Exception as exc:
            logger.warning("KÜP Auto-Parse fehlgeschlagen: %s", exc)
            message = "KÜP importiert, automatische Analyse fehlgeschlagen – POST /api/v1/kuep/{id}/parse aufrufen."
    return UploadResponse(
        dokument_id=dokument.id,
        projekt_id=dokument.projekt_id,
        dateiname=dokument.dateiname,
        dokumenttyp=dokument.dokumenttyp,
        status=dokument.status,
        message=message,
    )


@router.post("/vlp", response_model=UploadResponse)
async def upload_vlp(
    projekt_id: UUID = Form(...),
    file: UploadFile = File(...),
    import_data: bool = Form(True),
    db: Session = Depends(get_db),
) -> UploadResponse:
    service = UploadService()
    dokument = await service.upload(
        db,
        projekt_id=projekt_id,
        dokumenttyp=DokumentTyp.VLP,
        file=file,
        allowed_suffixes=ALLOWED_VLP,
        subdir="vlp",
    )
    message = "VLP erfolgreich importiert."
    if import_data:
        try:
            result = VlpImportService(db).import_dokument(dokument.id)
            stats = result["stats"]
            message = (
                f"VLP importiert: {stats['matched']}/{stats['rows_total']} Kabel gematcht, "
                f"{stats['updated']} aktualisiert."
            )
            db.refresh(dokument)
        except Exception as exc:
            logger.warning("VLP Auto-Import fehlgeschlagen: %s", exc)
            message = "VLP importiert – POST /api/v1/vlp/{id}/import manuell aufrufen."
    return UploadResponse(
        dokument_id=dokument.id,
        projekt_id=dokument.projekt_id,
        dateiname=dokument.dateiname,
        dokumenttyp=dokument.dokumenttyp,
        status=dokument.status,
        message=message,
    )
