import re
from decimal import Decimal

from app.db.enums import VerteilerArt
from app.parsing.geometry_utils import merge_text_lines, parse_km_value, parse_str_num, texts_near_bbox
from app.parsing.types import BBox, PageGeometry, ParsedVerteiler, RectShape, TextSpan

VERTEILER_PREFIXES = ("ESTW", "RSTW", "KS")
MAST_PREFIX = "MSTT"


class VerteilerDetector:
    """Erkennt Verteiler (ESTW/RSTW/KS) und Signalmaste (MSTT) geometrisch."""

    def detect(self, page: PageGeometry) -> list[ParsedVerteiler]:
        results: list[ParsedVerteiler] = []
        used_texts: set[int] = set()

        for rect in page.rects:
            if not self._is_vertical_frame(rect):
                continue
            nearby = texts_near_bbox(page.texts, rect.bbox, margin=35, page=page.page)
            label = merge_text_lines(nearby)
            parsed = self._parse_from_rect(rect, nearby, label)
            if parsed:
                results.append(parsed)
                for t in nearby:
                    used_texts.add(id(t))

        for span in page.texts:
            if id(span) in used_texts:
                continue
            parsed = self._parse_from_text_anchor(span, page)
            if parsed:
                results.append(parsed)

        return self._deduplicate(results)

    def _is_vertical_frame(self, rect: RectShape) -> bool:
        w, h = rect.bbox.width, rect.bbox.height
        if h < 20 or w < 3:
            return False
        return h > w * 1.5

    def _parse_from_rect(
        self, rect: RectShape, nearby: list[TextSpan], label: str
    ) -> ParsedVerteiler | None:
        art, name = self._resolve_art_name(label, nearby)
        if art is None or not name:
            return None
        km = parse_km_value(label)
        str_num = parse_str_num(label) if art != VerteilerArt.MST else None
        return ParsedVerteiler(
            art=art,
            name=name,
            km=km,
            str_num=str_num,
            bbox=rect.bbox,
            page=rect.page,
            raw_labels=[t.text for t in nearby],
        )

    def _parse_from_text_anchor(self, span: TextSpan, page: PageGeometry) -> ParsedVerteiler | None:
        text = span.text.strip()
        art, name = self._resolve_art_name(text, [span])
        if art is None:
            return None
        block = texts_near_bbox(page.texts, span.bbox, margin=30, page=page.page)
        label = merge_text_lines(block)
        km = parse_km_value(label)
        str_num = parse_str_num(label) if art != VerteilerArt.MST else None
        bbox = span.bbox
        for r in page.rects:
            if self._is_vertical_frame(r) and abs(r.bbox.cx - span.bbox.cx) < 40:
                bbox = r.bbox
                break
        return ParsedVerteiler(
            art=art,
            name=name or text,
            km=km,
            str_num=str_num,
            bbox=bbox,
            page=page.page,
            raw_labels=[t.text for t in block],
        )

    def _resolve_art_name(
        self, label: str, spans: list[TextSpan]
    ) -> tuple[VerteilerArt | None, str | None]:
        upper = label.upper()
        for prefix in VERTEILER_PREFIXES:
            if prefix in upper:
                name = self._extract_name(label, prefix)
                return VerteilerArt[prefix], name
        if MAST_PREFIX in upper or any(s.text.upper().startswith(MAST_PREFIX) for s in spans):
            name = self._extract_mast_name(label, spans)
            return VerteilerArt.MST, name
        return None, None

    @staticmethod
    def _extract_name(label: str, prefix: str) -> str | None:
        match = re.search(rf"({prefix}\s*\S+)", label, re.IGNORECASE)
        return match.group(1).strip() if match else None

    @staticmethod
    def _extract_mast_name(label: str, spans: list[TextSpan]) -> str | None:
        for s in spans:
            if s.text.upper().startswith(MAST_PREFIX):
                return s.text.strip()
        match = re.search(r"(MSTT\s*\S+)", label, re.IGNORECASE)
        return match.group(1).strip() if match else None

    @staticmethod
    def _deduplicate(items: list[ParsedVerteiler]) -> list[ParsedVerteiler]:
        unique: list[ParsedVerteiler] = []
        for item in items:
            if not any(
                u.name == item.name and abs(u.bbox.cx - item.bbox.cx) < 20 for u in unique
            ):
                unique.append(item)
        return unique
