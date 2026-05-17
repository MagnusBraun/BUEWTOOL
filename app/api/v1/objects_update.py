from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.enums import ObjektTyp
from app.models.element import Element
from app.models.historie import Historie
from app.models.kabel import Kabel
from app.models.objekt import Objekt
from app.models.verteiler import Verteiler
from app.schemas.objects import ObjektUpdate
from app.services.str_vererbung import StrVererbungService

router = APIRouter(tags=["objects"])


@router.put("/objects/{objekt_id}")
def update_object(
    objekt_id: UUID,
    body: ObjektUpdate,
    benutzer: str | None = None,
    db: Session = Depends(get_db),
) -> dict:
    obj = db.get(Objekt, objekt_id)
    if not obj:
        raise HTTPException(404, "Objekt nicht gefunden")

    updated_fields: list[str] = []

    if obj.objekt_typ == ObjektTyp.VERTEILER:
        v = db.get(Verteiler, objekt_id)
        if not v:
            raise HTTPException(404, "Verteiler nicht gefunden")
        if body.km is not None and v.km != body.km:
            _hist(db, objekt_id, "km", v.km, body.km, benutzer)
            v.km = body.km
            updated_fields.append("km")
        if body.str is not None and v.str != body.str:
            _hist(db, objekt_id, "str", v.str, body.str, benutzer)
            v.str = body.str
            updated_fields.append("str")
            StrVererbungService(db).recompute_from_verteiler(v.id)
        if body.bemerkungen is not None:
            v.bemerkungen = body.bemerkungen
            updated_fields.append("bemerkungen")

    elif obj.objekt_typ == ObjektTyp.KABEL:
        k = db.get(Kabel, objekt_id)
        if not k:
            raise HTTPException(404, "Kabel nicht gefunden")
        for field, val in [
            ("laenge_ist", body.laenge_ist),
            ("trommelnummer", body.trommelnummer),
            ("verlegeart", body.verlegeart),
            ("typ", body.typ),
        ]:
            if val is not None and getattr(k, field) != val:
                _hist(db, objekt_id, field, getattr(k, field), val, benutzer)
                setattr(k, field, val)
                updated_fields.append(field)
        if body.bemerkungen is not None:
            k.bemerkungen = body.bemerkungen
            updated_fields.append("bemerkungen")

    elif obj.objekt_typ == ObjektTyp.ELEMENT:
        e = db.get(Element, objekt_id)
        if not e:
            raise HTTPException(404, "Element nicht gefunden")
        if body.bemerkungen is not None:
            e.bemerkungen = body.bemerkungen
            updated_fields.append("bemerkungen")

    db.commit()
    return {"objekt_id": str(objekt_id), "updated_fields": updated_fields}


def _hist(db, objekt_id, feld, alt, neu, benutzer):
    db.add(
        Historie(
            objekt_id=objekt_id,
            feld=feld,
            alter_wert=str(alt) if alt is not None else None,
            neuer_wert=str(neu) if neu is not None else None,
            benutzer=benutzer,
        )
    )
