from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.enums import ObjektTyp
from app.models.element import Element
from app.models.historie import Historie
from app.models.kabel import Kabel
from app.models.objekt import Objekt
from app.models.verteiler import Verteiler
from app.schemas.objects import (
    ElementResponse,
    HistorieResponse,
    KabelResponse,
    ObjektResponse,
    VerteilerResponse,
)
from app.services.str_vererbung import StrVererbungService

router = APIRouter(tags=["objects"])


@router.get("/objects", response_model=list[ObjektResponse])
def list_objects(
    projekt_id: UUID,
    objekt_typ: ObjektTyp | None = None,
    db: Session = Depends(get_db),
) -> list[ObjektResponse]:
    stmt = select(Objekt).where(Objekt.projekt_id == projekt_id)
    if objekt_typ:
        stmt = stmt.where(Objekt.objekt_typ == objekt_typ)
    return [ObjektResponse.model_validate(o) for o in db.scalars(stmt).all()]


@router.get("/objects/{objekt_id}", response_model=ObjektResponse)
def get_object(objekt_id: UUID, db: Session = Depends(get_db)) -> ObjektResponse:
    obj = db.get(Objekt, objekt_id)
    if not obj:
        raise HTTPException(404, "Objekt nicht gefunden")
    return ObjektResponse.model_validate(obj)


@router.get("/cables", response_model=list[KabelResponse])
def list_cables(projekt_id: UUID, db: Session = Depends(get_db)) -> list[KabelResponse]:
    stmt = (
        select(Kabel)
        .join(Objekt, Kabel.id == Objekt.id)
        .where(Objekt.projekt_id == projekt_id)
        .order_by(Kabel.name)
    )
    return [KabelResponse.model_validate(k) for k in db.scalars(stmt).all()]


@router.get("/elements", response_model=list[ElementResponse])
def list_elements(projekt_id: UUID, db: Session = Depends(get_db)) -> list[ElementResponse]:
    stmt = (
        select(Element)
        .join(Objekt, Element.id == Objekt.id)
        .where(Objekt.projekt_id == projekt_id)
        .order_by(Element.name)
    )
    return [ElementResponse.model_validate(e) for e in db.scalars(stmt).all()]


@router.get("/distributors", response_model=list[VerteilerResponse])
def list_distributors(
    projekt_id: UUID, db: Session = Depends(get_db)
) -> list[VerteilerResponse]:
    stmt = (
        select(Verteiler)
        .join(Objekt, Verteiler.id == Objekt.id)
        .where(Objekt.projekt_id == projekt_id)
        .order_by(Verteiler.name)
    )
    return [VerteilerResponse.model_validate(v) for v in db.scalars(stmt).all()]


@router.get("/history/{objekt_id}", response_model=list[HistorieResponse])
def get_history(objekt_id: UUID, db: Session = Depends(get_db)) -> list[HistorieResponse]:
    stmt = (
        select(Historie)
        .where(Historie.objekt_id == objekt_id)
        .order_by(Historie.timestamp.desc())
    )
    return [HistorieResponse.model_validate(h) for h in db.scalars(stmt).all()]
