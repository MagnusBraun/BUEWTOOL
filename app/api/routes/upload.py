import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_upload_service
from app.db.session import get_db
from app.schemas.document import DocumentResponse, UploadResponse
from app.schemas.errors import ErrorResponse
from app.services.upload import DocumentUploadService, UploadValidationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post(
    "/kuep",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Kabelübersichtsplan (KÜP) hochladen",
    responses={
        400: {"model": ErrorResponse, "description": "Ungültige Datei"},
        413: {"model": ErrorResponse, "description": "Datei zu groß"},
    },
)
def upload_kuep(
    file: UploadFile = File(..., description="KÜP als PDF"),
    db: Session = Depends(get_db),
    upload_service: DocumentUploadService = Depends(get_upload_service),
) -> UploadResponse:
    try:
        document = upload_service.upload_kuep(db, file)
    except UploadValidationError as exc:
        status_code = (
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            if exc.code == "file_too_large"
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("KÜP-Upload fehlgeschlagen")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Interner Fehler beim Speichern des KÜP.",
        ) from exc
    finally:
        file.file.close()

    return UploadResponse(
        message="KÜP erfolgreich hochgeladen. Verarbeitung folgt in Schritt 5–7.",
        document=DocumentResponse.model_validate(document),
    )


@router.post(
    "/vlp",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Kabelverlegeprotokoll (VLP) hochladen",
    responses={
        400: {"model": ErrorResponse, "description": "Ungültige Datei"},
        413: {"model": ErrorResponse, "description": "Datei zu groß"},
    },
)
def upload_vlp(
    file: UploadFile = File(..., description="VLP als PDF oder Excel"),
    db: Session = Depends(get_db),
    upload_service: DocumentUploadService = Depends(get_upload_service),
) -> UploadResponse:
    try:
        document = upload_service.upload_vlp(db, file)
    except UploadValidationError as exc:
        status_code = (
            status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            if exc.code == "file_too_large"
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("VLP-Upload fehlgeschlagen")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Interner Fehler beim Speichern des VLP.",
        ) from exc
    finally:
        file.file.close()

    return UploadResponse(
        message="VLP erfolgreich hochgeladen. Import der Verlegedaten folgt in Schritt 17.",
        document=DocumentResponse.model_validate(document),
    )
