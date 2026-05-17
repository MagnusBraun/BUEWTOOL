from decimal import Decimal

from app.parsing.geometry_utils import (
    assign_quadrant,
    parse_km_value,
    parse_laenge_soll,
    parse_str_num,
)
from app.parsing.types import BBox, TextSpan


def test_parse_km():
    assert parse_km_value("km 57,000 (Str. 1120)") == Decimal("57.000")


def test_parse_str():
    assert parse_str_num("km 57,000 (Str. 1120)") == 1120


def test_parse_laenge():
    assert parse_laenge_soll("30m") == Decimal("30")


def test_quadrant_assignment():
    mid_x, mid_y = 100.0, 50.0
    span = TextSpan("S400500", BBox(10, 10, 40, 30), page=0)
    assert assign_quadrant(span, mid_x, mid_y) == "oben_links"
