from dataclasses import dataclass, field
from decimal import Decimal

from app.db.enums import ElementArt, VerteilerArt


@dataclass(frozen=True)
class Point:
    x: float
    y: float


@dataclass(frozen=True)
class BBox:
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def cx(self) -> float:
        return (self.x0 + self.x1) / 2

    @property
    def cy(self) -> float:
        return (self.y0 + self.y1) / 2

    @property
    def width(self) -> float:
        return abs(self.x1 - self.x0)

    @property
    def height(self) -> float:
        return abs(self.y1 - self.y0)


@dataclass
class TextSpan:
    text: str
    bbox: BBox
    page: int


@dataclass
class LineSegment:
    x0: float
    y0: float
    x1: float
    y1: float
    page: int
    width: float = 1.0

    @property
    def is_horizontal(self) -> bool:
        return abs(self.y1 - self.y0) < abs(self.x1 - self.x0) * 0.15

    @property
    def is_vertical(self) -> bool:
        return abs(self.x1 - self.x0) < abs(self.y1 - self.y0) * 0.15

    @property
    def length(self) -> float:
        return ((self.x1 - self.x0) ** 2 + (self.y1 - self.y0) ** 2) ** 0.5

    @property
    def midpoint(self) -> Point:
        return Point((self.x0 + self.x1) / 2, (self.y0 + self.y1) / 2)


@dataclass
class RectShape:
    bbox: BBox
    page: int
    filled: bool = False


@dataclass
class ParsedVerteiler:
    art: VerteilerArt
    name: str
    km: Decimal | None
    str_num: int | None
    bbox: BBox
    page: int
    raw_labels: list[str] = field(default_factory=list)


@dataclass
class ParsedKabel:
    name: str
    typ: str | None
    index: str | None
    laenge_soll: Decimal | None
    bbox: BBox
    page: int
    line: LineSegment
    midline_x: float
    geom_line: list[list[float]]
    quadrant_texts: dict[str, list[str]] = field(default_factory=dict)


@dataclass
class ParsedElement:
    elementart: ElementArt
    name: str
    bbox: BBox
    page: int
    kabel_name: str | None = None


@dataclass
class PageGeometry:
    page: int
    width: float
    height: float
    texts: list[TextSpan]
    lines: list[LineSegment]
    rects: list[RectShape]


@dataclass
class KuepParseResult:
    verteiler: list[ParsedVerteiler] = field(default_factory=list)
    kabel: list[ParsedKabel] = field(default_factory=list)
    elemente: list[ParsedElement] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    pages_processed: int = 0
