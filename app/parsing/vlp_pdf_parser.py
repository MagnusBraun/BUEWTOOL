import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pdfplumber

from app.parsing.vlp_types import ParsedVlpRow, VlpParseResult

CABLE_RE = re.compile(r"\b(S\d[\w.]*)\b", re.IGNORECASE)
LAENGE_RE = re.compile(r"(\d+(?:[,.]\d+)?)\s*m\b", re.IGNORECASE)
VLP_NR_RE = re.compile(r"VLP[\s\-/]*(\d+[\w\-/]*)", re.IGNORECASE)


class VlpPdfParser:
    def parse(self, path: str | Path) -> VlpParseResult:
        result = VlpParseResult()
        with pdfplumber.open(path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                tables = page.extract_tables() or []
                if tables:
                    for table in tables:
                        result.rows.extend(self._parse_table(table, page_num))
                else:
                    text = page.extract_text() or ""
                    result.rows.extend(self._parse_text_lines(text, page_num))
                    vlp_match = VLP_NR_RE.search(text)
                    if vlp_match and not result.vlp_nummer_global:
                        result.vlp_nummer_global = vlp_match.group(0).strip()

        result.rows = self._deduplicate_rows(result.rows)
        if not result.rows:
            result.warnings.append("Keine VLP-Zeilen im PDF erkannt")
        return result

    def _parse_table(self, table: list[list], page: int) -> list[ParsedVlpRow]:
        if not table or len(table) < 2:
            return []
        header = [self._norm(c) for c in table[0]]
        col_map = self._header_map(header)
        rows: list[ParsedVlpRow] = []
        for i, row in enumerate(table[1:], start=1):
            if not row:
                continue
            name = self._cell(row, col_map.get("kabel"))
            if not name:
                continue
            kabel = self._extract_kabel_name(name)
            if not kabel:
                continue
            rows.append(
                ParsedVlpRow(
                    kabel_name=kabel,
                    laenge_ist=self._parse_laenge(self._cell(row, col_map.get("laenge"))),
                    trommelnummer=self._cell(row, col_map.get("trommel")),
                    verlegeart=self._cell(row, col_map.get("verlegeart")),
                    vlp_nummer=self._cell(row, col_map.get("vlp")),
                    rohdaten={"source": "pdf_table", "page": page, "row": i},
                    row_index=i,
                )
            )
        return rows

    def _parse_text_lines(self, text: str, page: int) -> list[ParsedVlpRow]:
        rows: list[ParsedVlpRow] = []
        for i, line in enumerate(text.splitlines()):
            cable = CABLE_RE.search(line)
            if not cable:
                continue
            laenge = LAENGE_RE.search(line)
            rows.append(
                ParsedVlpRow(
                    kabel_name=cable.group(1).upper(),
                    laenge_ist=self._parse_laenge(laenge.group(1)) if laenge else None,
                    trommelnummer=None,
                    verlegeart=None,
                    vlp_nummer=None,
                    rohdaten={"source": "pdf_text", "page": page, "line": i, "raw": line},
                    row_index=i,
                )
            )
        return rows

    def _header_map(self, header: list[str]) -> dict[str, int]:
        mapping: dict[str, int] = {}
        for i, h in enumerate(header):
            if "kabel" in h or "leitung" in h or h == "name":
                mapping["kabel"] = i
            elif "ist" in h and ("laeng" in h or "länge" in h or "m" in h):
                mapping["laenge"] = i
            elif "trommel" in h:
                mapping["trommel"] = i
            elif "verleg" in h:
                mapping["verlegeart"] = i
            elif "vlp" in h:
                mapping["vlp"] = i
        return mapping

    @staticmethod
    def _norm(cell) -> str:
        if cell is None:
            return ""
        t = str(cell).lower().replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
        return re.sub(r"\s+", " ", t).strip()

    @staticmethod
    def _cell(row: list, idx: int | None) -> str | None:
        if idx is None or idx >= len(row) or row[idx] is None:
            return None
        s = str(row[idx]).strip()
        return s or None

    @staticmethod
    def _extract_kabel_name(text: str) -> str | None:
        m = CABLE_RE.search(text)
        return m.group(1).upper() if m else None

    @staticmethod
    def _parse_laenge(text: str | None) -> Decimal | None:
        if not text:
            return None
        s = str(text).replace(",", ".").replace("m", "").strip()
        try:
            return Decimal(s)
        except InvalidOperation:
            return None

    @staticmethod
    def _deduplicate_rows(rows: list[ParsedVlpRow]) -> list[ParsedVlpRow]:
        seen: dict[str, ParsedVlpRow] = {}
        for r in rows:
            if r.kabel_name and r.kabel_name not in seen:
                seen[r.kabel_name] = r
        return list(seen.values())
