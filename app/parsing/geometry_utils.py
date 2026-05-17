import math
import re
from decimal import Decimal, InvalidOperation

from app.parsing.types import BBox, LineSegment, Point, TextSpan


def distance(p1: Point, p2: Point) -> float:
    return math.hypot(p1.x - p2.x, p1.y - p2.y)


def bbox_contains_point(bbox: BBox, p: Point, margin: float = 2.0) -> bool:
    return (
        bbox.x0 - margin <= p.x <= bbox.x1 + margin
        and bbox.y0 - margin <= p.y <= bbox.y1 + margin
    )


def bbox_union(a: BBox, b: BBox) -> BBox:
    return BBox(min(a.x0, b.x0), min(a.y0, b.y0), max(a.x1, b.x1), max(a.y1, b.y1))


def texts_near_bbox(
    texts: list[TextSpan],
    bbox: BBox,
    margin: float = 25.0,
    page: int | None = None,
) -> list[TextSpan]:
    expanded = BBox(bbox.x0 - margin, bbox.y0 - margin, bbox.x1 + margin, bbox.y1 + margin)
    result: list[TextSpan] = []
    for t in texts:
        if page is not None and t.page != page:
            continue
        if bbox_intersects(expanded, t.bbox):
            result.append(t)
    return sorted(result, key=lambda s: (s.bbox.y0, s.bbox.x0))


def bbox_intersects(a: BBox, b: BBox) -> bool:
    return not (a.x1 < b.x0 or b.x1 < a.x0 or a.y1 < b.y0 or b.y1 < a.y0)


def merge_text_lines(spans: list[TextSpan]) -> str:
    if not spans:
        return ""
    return " ".join(s.text.strip() for s in spans if s.text.strip())


def parse_km_value(text: str) -> Decimal | None:
    match = re.search(r"km\s*([0-9]+)[,.]([0-9]+)", text, re.IGNORECASE)
    if not match:
        return None
    try:
        return Decimal(f"{match.group(1)}.{match.group(2)}")
    except InvalidOperation:
        return None


def parse_str_num(text: str) -> int | None:
    match = re.search(r"Str\.?\s*(\d+)", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    match = re.search(r"\(\s*Str\.?\s*(\d+)\s*\)", text, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None


def parse_laenge_soll(text: str) -> Decimal | None:
    match = re.search(r"(\d+(?:[,.]\d+)?)\s*m\b", text, re.IGNORECASE)
    if not match:
        return None
    try:
        return Decimal(match.group(1).replace(",", "."))
    except InvalidOperation:
        return None


def lines_overlap_parallel(a: LineSegment, b: LineSegment, y_tol: float = 3.0) -> bool:
    if not a.is_horizontal or not b.is_horizontal:
        return False
    ay = (a.y0 + a.y1) / 2
    by = (b.y0 + b.y1) / 2
    if abs(ay - by) > y_tol:
        return False
    ax0, ax1 = sorted((a.x0, a.x1))
    bx0, bx1 = sorted((b.x0, b.x1))
    return not (ax1 < bx0 or bx1 < ax0)


def find_vertical_midline(
    cable: LineSegment, verticals: list[LineSegment], x_tol: float = 8.0
) -> float | None:
    cx0, cx1 = sorted((cable.x0, cable.x1))
    cy = cable.midpoint.y
    candidates: list[float] = []
    for v in verticals:
        if not v.is_vertical:
            continue
        vx = (v.x0 + v.x1) / 2
        vy0, vy1 = sorted((v.y0, v.y1))
        if cx0 - x_tol <= vx <= cx1 + x_tol and vy0 - 5 <= cy <= vy1 + 5:
            candidates.append(vx)
    if not candidates:
        return cable.midpoint.x
    return sum(candidates) / len(candidates)


def assign_quadrant(span: TextSpan, mid_x: float, mid_y: float) -> str:
    cx, cy = span.bbox.cx, span.bbox.cy
    if cx <= mid_x and cy <= mid_y:
        return "oben_links"
    if cx <= mid_x and cy > mid_y:
        return "unten_links"
    if cx > mid_x and cy <= mid_y:
        return "oben_rechts"
    return "unten_rechts"


def nearest_endpoint_connections(
    line: LineSegment, node_bboxes: list[BBox], max_dist: float = 40.0
) -> tuple[int | None, int | None]:
    p_start = Point(line.x0, line.y0)
    p_end = Point(line.x1, line.y1)
    start_idx: int | None = None
    end_idx: int | None = None
    start_d = max_dist
    end_d = max_dist
    for i, bb in enumerate(node_bboxes):
        center = Point(bb.cx, bb.cy)
        ds = distance(p_start, center)
        de = distance(p_end, center)
        if ds < start_d:
            start_d = ds
            start_idx = i
        if de < end_d:
            end_d = de
            end_idx = i
    return start_idx, end_idx
