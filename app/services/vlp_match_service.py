import logging
import re
from decimal import Decimal
from difflib import SequenceMatcher

from app.models.kabel import Kabel
from app.parsing.vlp_types import ParsedVlpRow

logger = logging.getLogger(__name__)


class VlpMatchService:
    """Matching VLP-Zeilen auf zentrale Kabelobjekte."""

    def match_row(
        self,
        row: ParsedVlpRow,
        kabel_by_name: dict[str, Kabel],
        kabel_list: list[Kabel],
    ) -> tuple[Kabel | None, str]:
        if not row.kabel_name:
            return None, "kein_kabelname"

        key = row.kabel_name.upper()
        if key in kabel_by_name:
            return kabel_by_name[key], "name_exakt"

        # Varianten: S30435.1 vs S30435
        base = re.sub(r"[.\s].*$", "", key)
        for name, kabel in kabel_by_name.items():
            if name.startswith(base) or base.startswith(re.sub(r"[.\s].*$", "", name)):
                return kabel, "name_variante"

        # Sekundär: ähnlicher Name + ähnliche SOLL-Länge
        if row.laenge_ist is not None:
            for kabel in kabel_list:
                if kabel.laenge_soll is None:
                    continue
                name_sim = SequenceMatcher(None, key, kabel.name.upper()).ratio()
                len_diff = abs(float(kabel.laenge_soll) - float(row.laenge_ist))
                if name_sim >= 0.75 and len_diff <= max(5.0, float(kabel.laenge_soll) * 0.15):
                    return kabel, "kontext_laenge"

        # Fuzzy Name
        best: Kabel | None = None
        best_score = 0.0
        for kabel in kabel_list:
            score = SequenceMatcher(None, key, kabel.name.upper()).ratio()
            if score > best_score and score >= 0.85:
                best_score = score
                best = kabel
        if best:
            return best, "name_fuzzy"

        return None, "kein_treffer"
