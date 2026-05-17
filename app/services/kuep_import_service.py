import logging
import uuid
from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.db.enums import DokumentStatus, DokumentTyp
from app.models.dokument import Dokument
from app.parsing.geometry_utils import nearest_endpoint_connections
from app.parsing.kuep_parser import KuepParser
from app.parsing.types import ParsedKabel, ParsedVerteiler
from app.repositories.object_repository import ObjectRepository
from app.services.str_vererbung import StrVererbungService

logger = logging.getLogger(__name__)


class KuepImportService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.parser = KuepParser()

    def parse_dokument(self, dokument_id: uuid.UUID) -> dict:
        dokument = self.db.get(Dokument, dokument_id)
        if dokument is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dokument nicht gefunden")
        if dokument.dokumenttyp != DokumentTyp.KUEP:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nur KÜP-Dokumente können geometrisch analysiert werden",
            )
        path = Path(dokument.dateipfad)
        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Datei nicht gefunden: {path}",
            )

        try:
            result = self.parser.parse(path)
        except Exception as exc:
            logger.exception("KÜP-Parsing fehlgeschlagen: %s", exc)
            dokument.status = DokumentStatus.FEHLER
            dokument.metadaten = {**(dokument.metadaten or {}), "error": str(exc)}
            self.db.commit()
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"KÜP-Analyse fehlgeschlagen: {exc}",
            ) from exc

        repo = ObjectRepository(self.db, dokument.projekt_id)
        verteiler_map: dict[str, uuid.UUID] = {}

        stats = {"verteiler": 0, "kabel": 0, "elemente": 0, "annotationen": 0}

        for pv in result.verteiler:
            v = repo.get_or_create_verteiler(pv)
            verteiler_map[pv.name.upper()] = v.id
            repo.create_annotation(
                dokument.id, v.id, pv.bbox.x0, pv.bbox.y0, pv.bbox.width, pv.bbox.height, pv.name
            )
            stats["verteiler"] += 1
            stats["annotationen"] += 1

        verteiler_list = list(result.verteiler)
        node_bboxes = [v.bbox for v in verteiler_list]

        for pk in result.kabel:
            von_id, bis_id = self._resolve_endpoints(pk, verteiler_list, node_bboxes, verteiler_map)
            k = repo.get_or_create_kabel(pk, von_id, bis_id)
            repo.create_annotation(
                dokument.id, k.id, pk.bbox.x0, pk.bbox.y0, pk.bbox.width, pk.bbox.height, pk.name
            )
            stats["kabel"] += 1
            stats["annotationen"] += 1

        kabel_map = repo.find_kabel_map()
        for pe in result.elemente:
            kabel_id = None
            if pe.kabel_name:
                k = kabel_map.get(pe.kabel_name.upper())
                kabel_id = k.id if k else None
            el = repo.get_or_create_element(pe, kabel_id, None)
            repo.create_annotation(
                dokument.id, el.id, pe.bbox.x0, pe.bbox.y0, pe.bbox.width, pe.bbox.height, pe.name
            )
            stats["elemente"] += 1
            stats["annotationen"] += 1

        StrVererbungService(self.db).recompute_projekt(dokument.projekt_id)

        dokument.status = DokumentStatus.ANALYSIERT
        dokument.metadaten = {
            **(dokument.metadaten or {}),
            "parse_stats": stats,
            "warnings": result.warnings,
            "pages_processed": result.pages_processed,
        }
        self.db.commit()

        return {
            "dokument_id": str(dokument.id),
            "status": dokument.status.value,
            "stats": stats,
            "warnings": result.warnings,
            "pages_processed": result.pages_processed,
        }

    def _resolve_endpoints(
        self,
        pk: ParsedKabel,
        verteiler_list: list[ParsedVerteiler],
        node_bboxes: list,
        verteiler_map: dict[str, uuid.UUID],
    ) -> tuple[uuid.UUID | None, uuid.UUID | None]:
        von_name = (pk.quadrant_texts.get("_von") or [None])[0]
        bis_name = (pk.quadrant_texts.get("_bis") or [None])[0]
        von_id = verteiler_map.get(von_name.upper()) if von_name else None
        bis_id = verteiler_map.get(bis_name.upper()) if bis_name else None

        if von_id is None or bis_id is None:
            start_i, end_i = nearest_endpoint_connections(pk.line, node_bboxes)
            if von_id is None and start_i is not None and start_i < len(verteiler_list):
                von_id = verteiler_map.get(verteiler_list[start_i].name.upper())
            if bis_id is None and end_i is not None and end_i < len(verteiler_list):
                bis_id = verteiler_map.get(verteiler_list[end_i].name.upper())
        return von_id, bis_id
