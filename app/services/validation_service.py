import uuid
from decimal import Decimal
from enum import Enum

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.enums import ObjektTyp
from app.models.element import Element
from app.models.kabel import Kabel
from app.models.objekt import Objekt
from app.models.verteiler import Verteiler


class ValidationSeverity(str, Enum):
    GELB = "gelb"
    ROT = "rot"


class ValidationService:
    """Vergleicht SOLL (KÜP) mit IST (VLP) und prüft Datenkonsistenz."""

    LAENGE_TOLERANZ_PROZENT = Decimal("0.10")
    LAENGE_TOLERANZ_MIN_M = Decimal("2")

    def __init__(self, db: Session, projekt_id: uuid.UUID) -> None:
        self.db = db
        self.projekt_id = projekt_id

    def validate(self) -> dict:
        issues: list[dict] = []
        kabel_list = self._kabel_list()
        element_list = self._element_list()
        verteiler_list = self._verteiler_list()

        issues.extend(self._check_duplicate_kabel(kabel_list))
        issues.extend(self._check_kabel_soll_ist(kabel_list))
        issues.extend(self._check_str_vererbung(kabel_list, element_list))
        issues.extend(self._check_unmatched_vlp(kabel_list))
        issues.extend(self._check_widerspruechliche_str(kabel_list))
        issues.extend(self._check_missing_assignment(element_list))

        summary = {
            "gelb": sum(1 for i in issues if i["severity"] == ValidationSeverity.GELB.value),
            "rot": sum(1 for i in issues if i["severity"] == ValidationSeverity.ROT.value),
            "gesamt": len(issues),
        }
        return {"projekt_id": str(self.projekt_id), "summary": summary, "issues": issues}

    def _kabel_list(self) -> list[Kabel]:
        stmt = (
            select(Kabel)
            .join(Objekt, Kabel.id == Objekt.id)
            .where(Objekt.projekt_id == self.projekt_id)
        )
        return list(self.db.scalars(stmt).all())

    def _element_list(self) -> list[Element]:
        stmt = (
            select(Element)
            .join(Objekt, Element.id == Objekt.id)
            .where(Objekt.projekt_id == self.projekt_id)
        )
        return list(self.db.scalars(stmt).all())

    def _verteiler_list(self) -> list[Verteiler]:
        stmt = (
            select(Verteiler)
            .join(Objekt, Verteiler.id == Objekt.id)
            .where(Objekt.projekt_id == self.projekt_id)
        )
        return list(self.db.scalars(stmt).all())

    def _check_duplicate_kabel(self, kabel_list: list[Kabel]) -> list[dict]:
        issues = []
        names = [k.name.upper() for k in kabel_list]
        for name in set(names):
            if names.count(name) > 1:
                issues.append(
                    self._issue(
                        ValidationSeverity.ROT,
                        "doppelte_objekte",
                        f"Doppeltes Kabel '{name}' im Projekt",
                        objekt_typ="kabel",
                        referenz=name,
                    )
                )
        return issues

    def _check_kabel_soll_ist(self, kabel_list: list[Kabel]) -> list[dict]:
        issues = []
        for k in kabel_list:
            if k.laenge_soll is None:
                continue
            if k.laenge_ist is None:
                issues.append(
                    self._issue(
                        ValidationSeverity.GELB,
                        "fehlende_zuordnung",
                        f"Kabel '{k.name}': IST-Länge aus VLP fehlt",
                        objekt_id=str(k.id),
                        feld="laenge_ist",
                    )
                )
                continue
            diff = abs(k.laenge_soll - k.laenge_ist)
            tol = max(
                self.LAENGE_TOLERANZ_MIN_M,
                k.laenge_soll * self.LAENGE_TOLERANZ_PROZENT,
            )
            if diff > tol:
                issues.append(
                    self._issue(
                        ValidationSeverity.ROT,
                        "widerspruechliche_laenge",
                        f"Kabel '{k.name}': SOLL {k.laenge_soll}m vs IST {k.laenge_ist}m (Δ {diff}m)",
                        objekt_id=str(k.id),
                        feld="laenge_ist",
                    )
                )
        return issues

    def _check_str_vererbung(
        self, kabel_list: list[Kabel], element_list: list[Element]
    ) -> list[dict]:
        issues = []
        for k in kabel_list:
            if k.str is None and (k.von_ort_id or k.bis_ort_id):
                issues.append(
                    self._issue(
                        ValidationSeverity.GELB,
                        "fehlende_vererbung",
                        f"Kabel '{k.name}': Streckennummer nicht vererbt",
                        objekt_id=str(k.id),
                        feld="str",
                    )
                )
            if k.streckenuebergreifend and k.str is not None:
                von = self.db.get(Verteiler, k.von_ort_id) if k.von_ort_id else None
                bis_v = self.db.get(Verteiler, k.bis_ort_id) if k.bis_ort_id else None
                if von and bis_v and von.str and bis_v.str and von.str != bis_v.str:
                    pass  # erwartet bei streckenübergreifend
        for el in element_list:
            if el.str is None and el.kabel_id:
                issues.append(
                    self._issue(
                        ValidationSeverity.GELB,
                        "fehlende_vererbung",
                        f"Element '{el.name}': Streckennummer nicht vererbt",
                        objekt_id=str(el.id),
                        feld="str",
                    )
                )
        return issues

    def _check_unmatched_vlp(self, kabel_list: list[Kabel]) -> list[dict]:
        issues = []
        for k in kabel_list:
            if k.laenge_soll and not k.vlp_nummer and k.laenge_ist is None:
                issues.append(
                    self._issue(
                        ValidationSeverity.GELB,
                        "fehlende_zuordnung",
                        f"Kabel '{k.name}': kein VLP-Bezug",
                        objekt_id=str(k.id),
                    )
                )
        return issues

    def _check_widerspruechliche_str(self, kabel_list: list[Kabel]) -> list[dict]:
        issues = []
        for k in kabel_list:
            von = self.db.get(Verteiler, k.von_ort_id) if k.von_ort_id else None
            bis_v = self.db.get(Verteiler, k.bis_ort_id) if k.bis_ort_id else None
            if (
                von
                and bis_v
                and von.str
                and bis_v.str
                and von.str != bis_v.str
                and k.str
                and k.str not in (von.str, bis_v.str)
            ):
                issues.append(
                    self._issue(
                        ValidationSeverity.ROT,
                        "widerspruechliche_streckennummer",
                        f"Kabel '{k.name}': str={k.str} widerspricht Endpunkten {von.str}/{bis_v.str}",
                        objekt_id=str(k.id),
                        feld="str",
                    )
                )
        return issues

    def _check_missing_assignment(self, element_list: list[Element]) -> list[dict]:
        issues = []
        for el in element_list:
            if not el.kabel_id and not el.verteiler_id:
                issues.append(
                    self._issue(
                        ValidationSeverity.GELB,
                        "fehlende_zuordnung",
                        f"Element '{el.name}': weder Kabel noch Verteiler zugeordnet",
                        objekt_id=str(el.id),
                    )
                )
        return issues

    @staticmethod
    def _issue(
        severity: ValidationSeverity,
        regel: str,
        message: str,
        **extra,
    ) -> dict:
        return {
            "severity": severity.value,
            "regel": regel,
            "message": message,
            **extra,
        }
