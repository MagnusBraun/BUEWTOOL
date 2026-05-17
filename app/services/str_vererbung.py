import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.element import Element
from app.models.kabel import Kabel
from app.models.objekt import Objekt
from app.models.verteiler import Verteiler


class StrVererbungService:
    """Dynamische Streckennummern-Vererbung: Verteiler → Kabel → Elemente."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def recompute_from_verteiler(self, verteiler_id: uuid.UUID) -> int:
        verteiler = self.db.get(Verteiler, verteiler_id)
        if verteiler is None:
            return 0
        updated = 0
        for kabel in self._kabel_for_verteiler(verteiler_id):
            new_str = self._kabel_str(kabel)
            if kabel.str != new_str or kabel.streckenuebergreifend != self._is_cross(kabel):
                kabel.str = new_str
                kabel.streckenuebergreifend = self._is_cross(kabel)
                updated += 1
            for element in kabel.elemente:
                if element.str != kabel.str:
                    element.str = kabel.str
                    updated += 1
        return updated

    def recompute_projekt(self, projekt_id: uuid.UUID) -> int:
        stmt = (
            select(Verteiler)
            .join(Objekt, Verteiler.id == Objekt.id)
            .where(Objekt.projekt_id == projekt_id)
        )
        total = 0
        for v in self.db.scalars(stmt).all():
            total += self.recompute_from_verteiler(v.id)
        return total

    def _kabel_for_verteiler(self, verteiler_id: uuid.UUID) -> list[Kabel]:
        stmt = select(Kabel).where(
            (Kabel.von_ort_id == verteiler_id) | (Kabel.bis_ort_id == verteiler_id)
        )
        return list(self.db.scalars(stmt).all())

    def _kabel_str(self, kabel: Kabel) -> int | None:
        von = self.db.get(Verteiler, kabel.von_ort_id) if kabel.von_ort_id else None
        if von and von.str is not None:
            return von.str
        bis_v = self.db.get(Verteiler, kabel.bis_ort_id) if kabel.bis_ort_id else None
        return bis_v.str if bis_v else None

    def _is_cross(self, kabel: Kabel) -> bool:
        von = self.db.get(Verteiler, kabel.von_ort_id) if kabel.von_ort_id else None
        bis_v = self.db.get(Verteiler, kabel.bis_ort_id) if kabel.bis_ort_id else None
        if not von or not bis_v or von.str is None or bis_v.str is None:
            return False
        return von.str != bis_v.str
