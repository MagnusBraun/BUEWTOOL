from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from app.parsing.vlp_types import ParsedVlpRow
from app.services.vlp_match_service import VlpMatchService


def test_match_by_exact_name():
    kid = uuid4()
    kabel = SimpleNamespace(id=kid, name="S400500", laenge_soll=Decimal("30"))
    by_name = {"S400500": kabel}
    row = ParsedVlpRow(kabel_name="S400500", laenge_ist=Decimal("29.5"))
    match, method = VlpMatchService().match_row(row, by_name, [kabel])
    assert match is kabel
    assert method == "name_exakt"
