import re

from app.db.enums import ElementArt
from app.parsing.geometry_utils import texts_near_bbox
from app.parsing.types import BBox, PageGeometry, ParsedElement, ParsedKabel, ParsedVerteiler, TextSpan

ELEMENT_PATTERNS: list[tuple[ElementArt, re.Pattern[str]]] = [
    (ElementArt.Hp, re.compile(r"\bHp\b", re.IGNORECASE)),
    (ElementArt.Vs, re.compile(r"\bVs\b", re.IGNORECASE)),
    (ElementArt.VW, re.compile(r"\bVW\b", re.IGNORECASE)),
    (ElementArt.Ls, re.compile(r"\bLs\b", re.IGNORECASE)),
    (ElementArt.Az, re.compile(r"\bAz\b", re.IGNORECASE)),
    (ElementArt.PZB, re.compile(r"\bPZB\b", re.IGNORECASE)),
    (ElementArt.GU, re.compile(r"\bGÜ\b|\bGU\b", re.IGNORECASE)),
]


class ElementDetector:
    """Erkennt LST-Elemente anhand Beschriftung und räumlicher Nähe."""

    def detect(
        self,
        page: PageGeometry,
        verteiler: list[ParsedVerteiler],
        kabel: list[ParsedKabel],
    ) -> list[ParsedElement]:
        results: list[ParsedElement] = []
        used: set[str] = set()

        for span in page.texts:
            art, name = self._match_element(span.text)
            if art is None:
                continue
            key = f"{art.value}:{name}"
            if key in used:
                continue
            kabel_name = self._nearest_kabel(span, kabel)
            results.append(
                ParsedElement(
                    elementart=art,
                    name=name,
                    bbox=span.bbox,
                    page=page.page,
                    kabel_name=kabel_name,
                )
            )
            used.add(key)

        for rect in page.rects:
            if rect.bbox.width > 30 and rect.bbox.height > 30:
                nearby = texts_near_bbox(page.texts, rect.bbox, margin=15, page=page.page)
                label = " ".join(t.text for t in nearby)
                art, name = self._match_element(label)
                if art and name:
                    key = f"{art.value}:{name}"
                    if key not in used:
                        results.append(
                            ParsedElement(
                                elementart=art,
                                name=name,
                                bbox=rect.bbox,
                                page=page.page,
                                kabel_name=self._nearest_kabel_from_bbox(rect.bbox, kabel),
                            )
                        )
                        used.add(key)

        return results

    def _match_element(self, text: str) -> tuple[ElementArt | None, str | None]:
        for art, pattern in ELEMENT_PATTERNS:
            if pattern.search(text):
                name = text.strip() or art.value
                return art, name
        return None, None

    @staticmethod
    def _nearest_kabel(span: TextSpan, kabel: list[ParsedKabel]) -> str | None:
        return ElementDetector._nearest_kabel_from_bbox(span.bbox, kabel)

    @staticmethod
    def _nearest_kabel_from_bbox(bbox: BBox, kabel: list[ParsedKabel]) -> str | None:
        if not kabel:
            return None
        best: ParsedKabel | None = None
        best_dist = float("inf")
        for k in kabel:
            dist = abs(bbox.cy - k.line.midpoint.y) + abs(bbox.cx - k.line.midpoint.x) * 0.3
            if dist < best_dist:
                best_dist = dist
                best = k
        return best.name if best and best_dist < 80 else None
