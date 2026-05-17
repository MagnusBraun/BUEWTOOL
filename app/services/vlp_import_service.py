import logging
import uuid
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.enums import DokumentStatus, DokumentTyp
from app.models.dokument import Dokument
from app.models.historie import Historie
from app.models.kabel import Kabel
from app.models.vlp_import import VlpImportZeile
from app.parsing.vlp_excel_parser import VlpExcelParser
from app.parsing.vlp_pdf_parser import VlpPdfParser
from app.parsing.vlp_types import ParsedVlpRow, VlpParseResult
from app.repositories.object_repository import ObjectRepository
from app.services.vlp_match_service import VlpMatchService

logger = logging.getLogger(__name__)


class VlpImportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.matcher = VlpMatchService()

    def import_dokument(self, dokument_id: uuid.UUID, benutzer: str | None = None) -> dict:
        dokument = self.db.get(Dokument, dokument_id)
        if dokument is None:
            raise HTTPException(status_code=404, detail="Dokument nicht gefunden")
        if dokument.dokumenttyp != DokumentTyp.VLP:
            raise HTTPException(status_code=400, detail="Nur VLP-Dokumente")

        path = Path(dokument.dateipfad)
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"Datei nicht gefunden: {path}")

        parsed = self._parse_file(path)
        repo = ObjectRepository(self.db, dokument.projekt_id)
        kabel_map = repo.find_kabel_map()
        kabel_list = list(kabel_map.values())

        stats = {
            "rows_total": len(parsed.rows),
            "matched": 0,
            "unmatched": 0,
            "updated": 0,
        }
        unmatched_names: list[str] = []

        global_vlp = parsed.vlp_nummer_global

        for row in parsed.rows:
            kabel, match_method = self.matcher.match_row(row, kabel_map, kabel_list)
            vlp_nr = row.vlp_nummer or global_vlp

            zeile = VlpImportZeile(
                dokument_id=dokument.id,
                kabel_name=row.kabel_name,
                laenge_ist=row.laenge_ist,
                trommelnummer=row.trommelnummer,
                verlegeart=row.verlegeart,
                vlp_nummer=vlp_nr,
                rohdaten={**row.rohdaten, "match_method": match_method},
                matched_kabel_id=kabel.id if kabel else None,
            )
            self.db.add(zeile)

            if kabel:
                stats["matched"] += 1
                if self._apply_to_kabel(kabel, row, vlp_nr, benutzer):
                    stats["updated"] += 1
            else:
                stats["unmatched"] += 1
                if row.kabel_name:
                    unmatched_names.append(row.kabel_name)

        dokument.status = DokumentStatus.ANALYSIERT
        dokument.metadaten = {
            **(dokument.metadaten or {}),
            "vlp_import": stats,
            "unmatched_names": unmatched_names[:50],
            "warnings": parsed.warnings,
        }
        self.db.commit()

        return {
            "dokument_id": str(dokument.id),
            "status": dokument.status.value,
            "stats": stats,
            "unmatched_names": unmatched_names,
            "warnings": parsed.warnings,
        }

    def _parse_file(self, path: Path) -> VlpParseResult:
        suffix = path.suffix.lower()
        try:
            if suffix in (".xlsx", ".xls"):
                return VlpExcelParser().parse(path)
            if suffix == ".pdf":
                return VlpPdfParser().parse(path)
        except Exception as exc:
            logger.exception("VLP-Parsing fehlgeschlagen: %s", exc)
            raise HTTPException(
                status_code=422,
                detail=f"VLP-Parsing fehlgeschlagen: {exc}",
            ) from exc
        raise HTTPException(status_code=400, detail=f"Unbekanntes VLP-Format: {suffix}")

    def _apply_to_kabel(
        self,
        kabel: Kabel,
        row: ParsedVlpRow,
        vlp_nr: str | None,
        benutzer: str | None,
    ) -> bool:
        changed = False
        if row.laenge_ist is not None and kabel.laenge_ist != row.laenge_ist:
            self._historie(kabel.id, "laenge_ist", kabel.laenge_ist, row.laenge_ist, benutzer)
            kabel.laenge_ist = row.laenge_ist
            changed = True
        if row.trommelnummer and kabel.trommelnummer != row.trommelnummer:
            self._historie(kabel.id, "trommelnummer", kabel.trommelnummer, row.trommelnummer, benutzer)
            kabel.trommelnummer = row.trommelnummer
            changed = True
        if row.verlegeart and kabel.verlegeart != row.verlegeart:
            self._historie(kabel.id, "verlegeart", kabel.verlegeart, row.verlegeart, benutzer)
            kabel.verlegeart = row.verlegeart
            changed = True
        if vlp_nr and kabel.vlp_nummer != vlp_nr:
            self._historie(kabel.id, "vlp_nummer", kabel.vlp_nummer, vlp_nr, benutzer)
            kabel.vlp_nummer = vlp_nr
            changed = True
        return changed

    def _historie(
        self,
        objekt_id: uuid.UUID,
        feld: str,
        alt,
        neu,
        benutzer: str | None,
    ) -> None:
        self.db.add(
            Historie(
                objekt_id=objekt_id,
                feld=feld,
                alter_wert=str(alt) if alt is not None else None,
                neuer_wert=str(neu) if neu is not None else None,
                benutzer=benutzer,
            )
        )
