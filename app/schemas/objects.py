from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.db.enums import ElementArt, ObjektTyp, VerteilerArt


class ObjektResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    projekt_id: UUID
    objekt_typ: ObjektTyp
    created_at: datetime
    updated_at: datetime


class VerteilerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    art: VerteilerArt
    name: str
    km: Decimal | None
    str: int | None = None
    bemerkungen: str | None


class KabelResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    typ: str | None
    index: str | None
    laenge_soll: Decimal | None
    laenge_ist: Decimal | None
    trommelnummer: str | None
    verlegeart: str | None
    vlp_nummer: str | None
    str: int | None
    streckenuebergreifend: bool
    von_ort_id: UUID | None
    bis_ort_id: UUID | None


class ElementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    elementart: ElementArt
    name: str
    kabel_id: UUID | None
    verteiler_id: UUID | None
    str: int | None


class HistorieResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    objekt_id: UUID
    feld: str
    alter_wert: str | None
    neuer_wert: str | None
    timestamp: datetime
    benutzer: str | None


class ObjektUpdate(BaseModel):
    bemerkungen: str | None = None
  km: Decimal | None = None
  str: int | None = None
  laenge_ist: Decimal | None = None
  trommelnummer: str | None = None
  verlegeart: str | None = None
  typ: str | None = None
