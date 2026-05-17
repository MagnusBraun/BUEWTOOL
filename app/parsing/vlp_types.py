from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class ParsedVlpRow:
    kabel_name: str | None
    laenge_ist: Decimal | None
    trommelnummer: str | None
    verlegeart: str | None
    vlp_nummer: str | None
    rohdaten: dict = field(default_factory=dict)
    row_index: int = 0


@dataclass
class VlpParseResult:
    rows: list[ParsedVlpRow] = field(default_factory=list)
    vlp_nummer_global: str | None = None
    warnings: list[str] = field(default_factory=list)
