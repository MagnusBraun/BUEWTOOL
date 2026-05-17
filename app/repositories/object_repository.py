import uuid
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.enums import ObjektTyp, VerteilerArt
from app.models.annotation import Annotation
from app.models.element import Element
from app.models.kabel import Kabel
from app.models.objekt import Objekt
from app.models.verteiler import Verteiler
from app.parsing.types import ParsedElement, ParsedKabel, ParsedVerteiler


class ObjectRepository:
    """Zentrale Objektverwaltung – keine redundanten Kopien pro Projekt."""

    def __init__(self, db: Session, projekt_id: uuid.UUID) -> None:
        self.db = db
        self.projekt_id = projekt_id

    def get_or_create_verteiler(self, parsed: ParsedVerteiler) -> Verteiler:
        existing = self._find_verteiler_by_name(parsed.name)
        if existing:
            self._update_verteiler(existing, parsed)
            return existing
        obj = Objekt(projekt_id=self.projekt_id, objekt_typ=ObjektTyp.VERTEILER)
        self.db.add(obj)
        self.db.flush()
        verteiler = Verteiler(
            id=obj.id,
            art=parsed.art,
            name=parsed.name,
            km=parsed.km,
            str=parsed.str_num,
            bbox_x=parsed.bbox.x0,
            bbox_y=parsed.bbox.y0,
            bbox_breite=parsed.bbox.width,
            bbox_hoehe=parsed.bbox.height,
        )
        self.db.add(verteiler)
        self.db.flush()
        return verteiler

    def get_or_create_kabel(self, parsed: ParsedKabel, von_id: uuid.UUID | None, bis_id: uuid.UUID | None) -> Kabel:
        existing = self._find_kabel_by_name(parsed.name)
        if existing:
            self._update_kabel(existing, parsed, von_id, bis_id)
            return existing
        obj = Objekt(projekt_id=self.projekt_id, objekt_typ=ObjektTyp.KABEL)
        self.db.add(obj)
        self.db.flush()
        kabel = Kabel(
            id=obj.id,
            name=parsed.name,
            typ=parsed.typ,
            index=parsed.index,
            laenge_soll=parsed.laenge_soll,
            von_ort_id=von_id,
            bis_ort_id=bis_id,
            geom_line=parsed.geom_line,
            str=self._resolve_kabel_str(von_id, bis_id),
            streckenuebergreifend=self._is_streckenuebergreifend(von_id, bis_id),
        )
        self.db.add(kabel)
        self.db.flush()
        return kabel

    def get_or_create_element(
        self,
        parsed: ParsedElement,
        kabel_id: uuid.UUID | None,
        verteiler_id: uuid.UUID | None,
    ) -> Element:
        existing = self._find_element(parsed.elementart.value, parsed.name)
        if existing:
            existing.kabel_id = kabel_id or existing.kabel_id
            existing.verteiler_id = verteiler_id or existing.verteiler_id
            if kabel_id:
                kabel = self.db.get(Kabel, kabel_id)
                if kabel and kabel.str is not None:
                    existing.str = kabel.str
            return existing
        obj = Objekt(projekt_id=self.projekt_id, objekt_typ=ObjektTyp.ELEMENT)
        self.db.add(obj)
        self.db.flush()
        str_val = None
        if kabel_id:
            kabel = self.db.get(Kabel, kabel_id)
            str_val = kabel.str if kabel else None
        element = Element(
            id=obj.id,
            elementart=parsed.elementart,
            name=parsed.name,
            kabel_id=kabel_id,
            verteiler_id=verteiler_id,
            str=str_val,
            bbox_x=parsed.bbox.x0,
            bbox_y=parsed.bbox.y0,
        )
        self.db.add(element)
        self.db.flush()
        return element

    def create_annotation(
        self,
        dokument_id: uuid.UUID,
        objekt_id: uuid.UUID,
        bbox_x: float,
        bbox_y: float,
        breite: float,
        hoehe: float,
        text: str | None = None,
    ) -> Annotation:
        ann = Annotation(
            dokument_id=dokument_id,
            objekt_id=objekt_id,
            x=bbox_x,
            y=bbox_y,
            breite=breite,
            hoehe=hoehe,
            text=text,
            farbe="#000000",
        )
        self.db.add(ann)
        return ann

    def _find_verteiler_by_name(self, name: str) -> Verteiler | None:
        stmt = (
            select(Verteiler)
            .join(Objekt, Verteiler.id == Objekt.id)
            .where(Objekt.projekt_id == self.projekt_id, Verteiler.name == name)
        )
        return self.db.scalars(stmt).first()

    def _find_kabel_by_name(self, name: str) -> Kabel | None:
        stmt = (
            select(Kabel)
            .join(Objekt, Kabel.id == Objekt.id)
            .where(Objekt.projekt_id == self.projekt_id, Kabel.name == name)
        )
        return self.db.scalars(stmt).first()

    def _find_element(self, elementart: str, name: str) -> Element | None:
        stmt = (
            select(Element)
            .join(Objekt, Element.id == Objekt.id)
            .where(
                Objekt.projekt_id == self.projekt_id,
                Element.name == name,
            )
        )
        return self.db.scalars(stmt).first()

    def _update_verteiler(self, v: Verteiler, parsed: ParsedVerteiler) -> None:
        v.art = parsed.art
        v.km = parsed.km or v.km
        if parsed.str_num is not None:
            v.str = parsed.str_num
        v.bbox_x = parsed.bbox.x0
        v.bbox_y = parsed.bbox.y0
        v.bbox_breite = parsed.bbox.width
        v.bbox_hoehe = parsed.bbox.height

    def _update_kabel(
        self,
        k: Kabel,
        parsed: ParsedKabel,
        von_id: uuid.UUID | None,
        bis_id: uuid.UUID | None,
    ) -> None:
        k.typ = parsed.typ or k.typ
        k.index = parsed.index or k.index
        k.laenge_soll = parsed.laenge_soll or k.laenge_soll
        k.geom_line = parsed.geom_line or k.geom_line
        if von_id:
            k.von_ort_id = von_id
        if bis_id:
            k.bis_ort_id = bis_id
        k.str = self._resolve_kabel_str(k.von_ort_id, k.bis_ort_id)
        k.streckenuebergreifend = self._is_streckenuebergreifend(k.von_ort_id, k.bis_ort_id)

    def _resolve_kabel_str(
        self, von_id: uuid.UUID | None, bis_id: uuid.UUID | None
    ) -> int | None:
        if von_id:
            von = self.db.get(Verteiler, von_id)
            if von and von.str is not None:
                return von.str
        if bis_id:
            bis_v = self.db.get(Verteiler, bis_id)
            if bis_v and bis_v.str is not None:
                return bis_v.str
        return None

    def _is_streckenuebergreifend(
        self, von_id: uuid.UUID | None, bis_id: uuid.UUID | None
    ) -> bool:
        if not von_id or not bis_id:
            return False
        von = self.db.get(Verteiler, von_id)
        bis_v = self.db.get(Verteiler, bis_id)
        if not von or not bis_v:
            return False
        if von.str is None or bis_v.str is None:
            return False
        return von.str != bis_v.str

    def find_verteiler_map(self) -> dict[str, Verteiler]:
        stmt = (
            select(Verteiler)
            .join(Objekt, Verteiler.id == Objekt.id)
            .where(Objekt.projekt_id == self.projekt_id)
        )
        return {v.name.upper(): v for v in self.db.scalars(stmt).all()}

    def find_kabel_map(self) -> dict[str, Kabel]:
        stmt = (
            select(Kabel)
            .join(Objekt, Kabel.id == Objekt.id)
            .where(Objekt.projekt_id == self.projekt_id)
        )
        return {k.name.upper(): k for k in self.db.scalars(stmt).all()}
