import logging
from pathlib import Path

import cv2
import fitz
import numpy as np
import pdfplumber

from app.parsing.types import BBox, LineSegment, PageGeometry, RectShape, TextSpan

logger = logging.getLogger(__name__)

MIN_LINE_LENGTH = 15.0
HORIZONTAL_RATIO = 3.0


class PdfGeometryExtractor:
    """Extrahiert Vektorlinien und Text mit Koordinaten aus KÜP-PDFs."""

    def __init__(self, pdf_path: str | Path) -> None:
        self.pdf_path = Path(pdf_path)

    def extract_all_pages(self) -> list[PageGeometry]:
        pages: list[PageGeometry] = []
        with fitz.open(self.pdf_path) as doc:
            for page_num, page in enumerate(doc):
                width, height = page.rect.width, page.rect.height
                texts = self._extract_text_spans(page, page_num)
                lines, rects = self._extract_drawings(page, page_num)
                cv_lines = self._extract_lines_opencv(page, page_num)
                lines = self._merge_lines(lines, cv_lines)
                pages.append(
                    PageGeometry(
                        page=page_num,
                        width=width,
                        height=height,
                        texts=texts,
                        lines=lines,
                        rects=rects,
                    )
                )
        pages = self._supplement_with_pdfplumber(pages)
        return pages

    def _extract_text_spans(self, page: fitz.Page, page_num: int) -> list[TextSpan]:
        spans: list[TextSpan] = []
        data = page.get_text("dict")
        for block in data.get("blocks", []):
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    text = (span.get("text") or "").strip()
                    if not text:
                        continue
                    x0, y0, x1, y1 = span["bbox"]
                    spans.append(
                        TextSpan(text=text, bbox=BBox(x0, y0, x1, y1), page=page_num)
                    )
        return spans

    def _extract_drawings(
        self, page: fitz.Page, page_num: int
    ) -> tuple[list[LineSegment], list[RectShape]]:
        lines: list[LineSegment] = []
        rects: list[RectShape] = []
        for drawing in page.get_drawings():
            fill = drawing.get("fill") is not None
            for item in drawing.get("items", []):
                op = item[0]
                if op == "l" and len(item) >= 3:
                    p1, p2 = item[1], item[2]
                    seg = LineSegment(
                        p1.x, p1.y, p2.x, p2.y, page=page_num, width=drawing.get("width", 1) or 1
                    )
                    if seg.length >= MIN_LINE_LENGTH:
                        lines.append(seg)
                elif op == "re" and len(item) >= 2:
                    r = item[1]
                    rects.append(
                        RectShape(
                            bbox=BBox(r.x0, r.y0, r.x1, r.y1),
                            page=page_num,
                            filled=fill,
                        )
                    )
        return lines, rects

    def _extract_lines_opencv(self, page: fitz.Page, page_num: int) -> list[LineSegment]:
        lines: list[LineSegment] = []
        try:
            mat = page.get_pixmap(dpi=150)
            img = np.frombuffer(mat.samples, dtype=np.uint8).reshape(mat.height, mat.width, mat.n)
            if mat.n >= 3:
                gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            else:
                gray = img
            scale_x = page.rect.width / mat.width
            scale_y = page.rect.height / mat.height
            edges = cv2.Canny(gray, 50, 150)
            detected = cv2.HoughLinesP(
                edges, 1, np.pi / 180, threshold=80, minLineLength=30, maxLineGap=5
            )
            if detected is not None:
                for seg in detected[:, 0]:
                    x0, y0, x1, y1 = seg
                    lines.append(
                        LineSegment(
                            x0 * scale_x,
                            y0 * scale_y,
                            x1 * scale_x,
                            y1 * scale_y,
                            page=page_num,
                        )
                    )
        except Exception as exc:
            logger.warning("OpenCV-Linienerkennung Seite %s: %s", page_num, exc)
        return lines

    def _merge_lines(
        self, primary: list[LineSegment], secondary: list[LineSegment]
    ) -> list[LineSegment]:
        merged = list(primary)
        for s in secondary:
            if not any(self._same_line(s, m) for m in merged):
                merged.append(s)
        return merged

    @staticmethod
    def _same_line(a: LineSegment, b: LineSegment, tol: float = 4.0) -> bool:
        return (
            abs(a.x0 - b.x0) < tol
            and abs(a.y0 - b.y0) < tol
            and abs(a.x1 - b.x1) < tol
            and abs(a.y1 - b.y1) < tol
        )

    def _supplement_with_pdfplumber(self, pages: list[PageGeometry]) -> list[PageGeometry]:
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                for i, pl_page in enumerate(pdf.pages):
                    if i >= len(pages):
                        break
                    for edge in pl_page.edges:
                        if edge.get("orientation") == "h":
                            x0 = edge["x0"]
                            x1 = edge["x1"]
                            y = edge["top"]
                            seg = LineSegment(x0, y, x1, y, page=i)
                            if seg.length >= MIN_LINE_LENGTH and not any(
                                PdfGeometryExtractor._same_line(seg, l) for l in pages[i].lines
                            ):
                                pages[i].lines.append(seg)
        except Exception as exc:
            logger.warning("pdfplumber-Ergänzung fehlgeschlagen: %s", exc)
        return pages
