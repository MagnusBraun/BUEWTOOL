import re
from decimal import Decimal

from app.parsing.geometry_utils import (
    assign_quadrant,
    find_vertical_midline,
    parse_laenge_soll,
    texts_near_bbox,
)
from app.parsing.types import BBox, LineSegment, PageGeometry, ParsedKabel, TextSpan

CABLE_NAME_RE = re.compile(r"^S\d[\w.]*$", re.IGNORECASE)
CABLE_INDEX_RE = re.compile(r"^\(\d+\)$")
CABLE_TYP_RE = re.compile(r"\d+x\d+x[\d,.]+", re.IGNORECASE)


class CableDetector:
    """Erkennt horizontale Kabel mit Mittellinie und Quadrantenlogik."""

    MIN_CABLE_LENGTH = 40.0

    def detect(self, page: PageGeometry) -> list[ParsedKabel]:
        horizontals = [
            ln
            for ln in page.lines
            if ln.is_horizontal and ln.length >= self.MIN_CABLE_LENGTH
        ]
        verticals = [ln for ln in page.lines if ln.is_vertical]
        results: list[ParsedKabel] = []

        for cable_line in horizontals:
            if not self._has_midline_indicator(cable_line, verticals):
                continue
            mid_x = find_vertical_midline(cable_line, verticals)
            if mid_x is None:
                continue
            mid_y = cable_line.midpoint.y
            cable_bbox = self._cable_text_region(cable_line, mid_x, mid_y)
            nearby = texts_near_bbox(page.texts, cable_bbox, margin=5, page=page.page)
            quadrants = self._assign_quadrant_texts(nearby, mid_x, mid_y)
            parsed = self._build_kabel(cable_line, mid_x, quadrants, page.page)
            if parsed and parsed.name:
                results.append(parsed)

        return self._deduplicate_by_name(results)

    def _has_midline_indicator(
        self, cable: LineSegment, verticals: list[LineSegment]
    ) -> bool:
        mid_x = find_vertical_midline(cable, verticals)
        x0, x1 = sorted((cable.x0, cable.x1))
        return x0 <= mid_x <= x1

    def _cable_text_region(
        self, cable: LineSegment, mid_x: float, mid_y: float
    ) -> BBox:
        x0, x1 = sorted((cable.x0, cable.x1))
        pad_y = 18
        pad_x = 8
        return BBox(x0 - pad_x, mid_y - pad_y, x1 + pad_x, mid_y + pad_y)

    def _assign_quadrant_texts(
        self, spans: list[TextSpan], mid_x: float, mid_y: float
    ) -> dict[str, list[str]]:
        quadrants: dict[str, list[str]] = {
            "oben_links": [],
            "unten_links": [],
            "oben_rechts": [],
            "unten_rechts": [],
        }
        for span in spans:
            q = assign_quadrant(span, mid_x, mid_y)
            quadrants[q].append(span.text.strip())
        return quadrants

    def _build_kabel(
        self,
        line: LineSegment,
        mid_x: float,
        quadrants: dict[str, list[str]],
        page: int,
    ) -> ParsedKabel | None:
        name = self._pick_name(quadrants.get("oben_links", []))
        typ = self._pick_typ(quadrants.get("unten_links", []))
        laenge = self._pick_laenge(quadrants.get("oben_rechts", []))
        index = self._pick_index(quadrants.get("unten_rechts", []))

        if not name:
            all_text = " ".join(sum(quadrants.values(), []))
            match = re.search(r"S\d[\w.]*", all_text, re.IGNORECASE)
            name = match.group(0) if match else ""

        if not name:
            return None

        x0, x1 = sorted((line.x0, line.x1))
        y = line.midpoint.y
        bbox = BBox(x0, y - 15, x1, y + 15)
        geom = [[line.x0, line.y0], [line.x1, line.y1]]

        return ParsedKabel(
            name=name.upper(),
            typ=typ,
            index=index,
            laenge_soll=laenge,
            bbox=bbox,
            page=page,
            line=line,
            midline_x=mid_x,
            geom_line=geom,
            quadrant_texts=quadrants,
        )

    @staticmethod
    def _pick_name(texts: list[str]) -> str:
        for t in texts:
            cleaned = t.strip()
            if CABLE_NAME_RE.match(cleaned):
                return cleaned.upper()
        for t in texts:
            match = re.search(r"S\d[\w.]*", t, re.IGNORECASE)
            if match:
                return match.group(0).upper()
        return texts[0].strip().upper() if texts else ""

    @staticmethod
    def _pick_typ(texts: list[str]) -> str | None:
        for t in texts:
            if CABLE_TYP_RE.search(t):
                return t.strip()
        return " ".join(texts).strip() or None

    @staticmethod
    def _pick_laenge(texts: list[str]) -> Decimal | None:
        for t in texts:
            val = parse_laenge_soll(t)
            if val is not None:
                return val
        return None

    @staticmethod
    def _pick_index(texts: list[str]) -> str | None:
        for t in texts:
            if CABLE_INDEX_RE.match(t.strip()):
                return t.strip()
        return texts[0].strip() if texts else None

    @staticmethod
    def _deduplicate_by_name(items: list[ParsedKabel]) -> list[ParsedKabel]:
        seen: dict[str, ParsedKabel] = {}
        for item in items:
            if item.name not in seen or item.line.length > seen[item.name].line.length:
                seen[item.name] = item
        return list(seen.values())
