from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.kuep import KuepParseResponse
from app.services.kuep_import_service import KuepImportService

router = APIRouter(prefix="/kuep", tags=["kuep"])


@router.post("/{dokument_id}/parse", response_model=KuepParseResponse)
def parse_kuep(
    dokument_id: UUID,
    db: Session = Depends(get_db),
) -> KuepParseResponse:
    result = KuepImportService(db).parse_dokument(dokument_id)
    return KuepParseResponse(
        dokument_id=UUID(result["dokument_id"]),
        status=result["status"],
        stats=result["stats"],
        warnings=result["warnings"],
        pages_processed=result["pages_processed"],
    )
