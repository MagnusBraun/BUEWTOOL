from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from app.services.validation_service import ValidationService, ValidationSeverity


def test_laenge_abweichung_rot():
    k = SimpleNamespace(
        id=uuid4(),
        name="S1",
        laenge_soll=Decimal("100"),
        laenge_ist=Decimal("50"),
        str=1,
        streckenuebergreifend=False,
        von_ort_id=None,
        bis_ort_id=None,
        vlp_nummer="VLP1",
    )

    class FakeDb:
        def get(self, *a):
            return None

        def scalars(self, stmt):
            return []

    svc = ValidationService(FakeDb(), uuid4())  # type: ignore
    issues = svc._check_kabel_soll_ist([k])
    assert any(i["severity"] == ValidationSeverity.ROT.value for i in issues)
