from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.vlp import VlpImportResponse
from app.services.vlp_import_service import VlpImportService

router = APIRouter(prefix="/vlp", tags=["vlp"])


@router.post("/{dokument_id}/import", response_model=VlpImportResponse)
def import_vlp(
    dokument_id: UUID,
    benutzer: str | None = Query(None),
    db: Session = Depends(get_db),
) -> VlpImportResponse:
    result = VlpImportService(db).import_dokument(dokument_id, benutzer=benutzer)
    return VlpImportResponse(
        dokument_id=UUID(result["dokument_id"]),
        status=result["status"],
        stats=result["stats"],
        unmatched_names=result["unmatched_names"],
        warnings=result["warnings"],
    )
