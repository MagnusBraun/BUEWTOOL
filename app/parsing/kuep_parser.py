import logging
from pathlib import Path

from app.parsing.detectors.cable_detector import CableDetector
from app.parsing.detectors.element_detector import ElementDetector
from app.parsing.detectors.verteiler_detector import VerteilerDetector
from app.parsing.pdf_extractor import PdfGeometryExtractor
from app.parsing.geometry_utils import nearest_endpoint_connections
from app.parsing.types import KuepParseResult, ParsedKabel, ParsedVerteiler

logger = logging.getLogger(__name__)


class KuepParser:
    """Orchestriert geometriebasierte KÜP-Analyse über alle Seiten."""

    def __init__(self) -> None:
        self._verteiler_detector = VerteilerDetector()
        self._cable_detector = CableDetector()
        self._element_detector = ElementDetector()

    def parse(self, pdf_path: str | Path) -> KuepParseResult:
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF nicht gefunden: {path}")

        extractor = PdfGeometryExtractor(path)
        pages = extractor.extract_all_pages()

        result = KuepParseResult(pages_processed=len(pages))
        all_verteiler: list[ParsedVerteiler] = []
        all_kabel: list[ParsedKabel] = []

        for page in pages:
            v = self._verteiler_detector.detect(page)
            k = self._cable_detector.detect(page)
            all_verteiler.extend(v)
            all_kabel.extend(k)
            result.verteiler.extend(v)
            result.kabel.extend(k)

        for page in pages:
            page_v = [x for x in all_verteiler if x.page == page.page]
            page_k = [x for x in all_kabel if x.page == page.page]
            result.elemente.extend(self._element_detector.detect(page, page_v, page_k))

        self._link_cable_endpoints(result)
        result.verteiler = self._global_deduplicate_verteiler(result.verteiler)
        result.kabel = self._global_deduplicate_kabel(result.kabel)

        if not result.verteiler and not result.kabel:
            result.warnings.append(
                "Keine Verteiler oder Kabel erkannt – PDF-Qualität oder Skalierung prüfen."
            )

        logger.info(
            "KÜP geparst: %d Verteiler, %d Kabel, %d Elemente, %d Seiten",
            len(result.verteiler),
            len(result.kabel),
            len(result.elemente),
            result.pages_processed,
        )
        return result

    def _link_cable_endpoints(self, result: KuepParseResult) -> None:
        if not result.verteiler:
            return
        node_bboxes = [v.bbox for v in result.verteiler]
        for kabel in result.kabel:
            start_i, end_i = nearest_endpoint_connections(kabel.line, node_bboxes)
            if start_i is not None:
                kabel.quadrant_texts["_von"] = [result.verteiler[start_i].name]
            if end_i is not None:
                kabel.quadrant_texts["_bis"] = [result.verteiler[end_i].name]

    @staticmethod
    def _global_deduplicate_verteiler(items: list[ParsedVerteiler]) -> list[ParsedVerteiler]:
        seen: dict[str, ParsedVerteiler] = {}
        for item in items:
            key = item.name.strip().upper()
            if key not in seen:
                seen[key] = item
        return list(seen.values())

    @staticmethod
    def _global_deduplicate_kabel(items: list[ParsedKabel]) -> list[ParsedKabel]:
        seen: dict[str, ParsedKabel] = {}
        for item in items:
            if item.name not in seen:
                seen[item.name] = item
        return list(seen.values())
