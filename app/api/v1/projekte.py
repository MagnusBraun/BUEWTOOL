from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.projekt import ProjektCreate, ProjektResponse
from app.services.projekt_service import ProjektService

router = APIRouter(prefix="/projekte", tags=["projekte"])


@router.post("", response_model=ProjektResponse, status_code=201)
def create_projekt(
    body: ProjektCreate,
    db: Session = Depends(get_db),
) -> ProjektResponse:
    projekt = ProjektService().create(db, body.name)
    return ProjektResponse.model_validate(projekt)


@router.get("", response_model=list[ProjektResponse])
def list_projekte(db: Session = Depends(get_db)) -> list[ProjektResponse]:
    projekte = ProjektService().list_all(db)
    return [ProjektResponse.model_validate(p) for p in projekte]
