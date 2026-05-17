# LST KÜP/VLP – Backend

FastAPI-Backend für das LST-Dokumentations- und Auswertungssystem (Deutsche Bahn Bauüberwachung).

## Voraussetzungen

- Python 3.11+
- Docker (für PostgreSQL) oder lokale PostgreSQL-Instanz

## Installation

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

## Datenbank starten

```bash
docker compose up -d
alembic upgrade head
```

## Server starten

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- API-Dokumentation: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Beispielaufrufe

```bash
# Projekt anlegen
curl -X POST http://localhost:8000/api/v1/projekte \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Bauabschnitt Nord\"}"

# KÜP hochladen (projekt_id aus Antwort einsetzen)
curl -X POST http://localhost:8000/api/v1/upload/kuep \
  -F "projekt_id=<UUID>" \
  -F "file=@./Beispiel_KUEP.pdf"

# VLP hochladen
curl -X POST http://localhost:8000/api/v1/upload/vlp \
  -F "projekt_id=<UUID>" \
  -F "file=@./Beispiel_VLP.xlsx"
```

## Projektstruktur

```
app/
  api/          # REST-Endpunkte
  core/         # Konfiguration, Logging
  db/           # SQLAlchemy Base, Session, Enums
  models/       # ORM-Modelle
  schemas/      # Pydantic-Schemas
  services/     # Geschäftslogik
  storage/      # Dateispeicher
alembic/        # Migrationen
```

## KÜP-Geometrieanalyse

Nach dem Upload wird standardmäßig eine geometrische Analyse gestartet (`parse=true`).

```bash
# KÜP mit Auto-Parse
curl -X POST http://localhost:8000/api/v1/upload/kuep \
  -F "projekt_id=<UUID>" \
  -F "file=@./plan.pdf" \
  -F "parse=true"

# Manuelle Analyse eines importierten Dokuments
curl -X POST http://localhost:8000/api/v1/kuep/<dokument_id>/parse
```

Erkennung:
- **Verteiler/Maste:** vertikale Rechtecke + Text (ESTW, RSTW, KS, MSTT)
- **Kabel:** horizontale Linien mit Mittellinie, Quadrantenlogik (Name, Typ, Länge, Index)
- **Elemente:** Beschriftungen (Hp, Vs, Az, …) mit Kabelnähe
- **Streckenvererbung:** dynamisch Verteiler → Kabel → Elemente

## VLP-Import und Matching

```bash
curl -X POST http://localhost:8000/api/v1/upload/vlp \
  -F "projekt_id=<UUID>" \
  -F "file=@./vlp.xlsx" \
  -F "import_data=true"

curl -X POST "http://localhost:8000/api/v1/vlp/<dokument_id>/import"
```

Matching: primär Kabelname, sekundär Name+SOLL-Länge-Kontext.

## Validierung

```bash
curl -X POST http://localhost:8000/api/v1/validate \
  -H "Content-Type: application/json" \
  -d "{\"projekt_id\": \"<UUID>\"}"
```

Regeln: **gelb** (fehlende Zuordnung/Vererbung), **rot** (Längenabweichung, doppelte Objekte, widersprüchliche Str.).

## Listen-Endpunkte

- `GET /api/v1/cables?projekt_id=`
- `GET /api/v1/elements?projekt_id=`
- `GET /api/v1/distributors?projekt_id=`
- `GET /api/v1/history/{objekt_id}`
- `PUT /api/v1/objects/{objekt_id}`

## Nächste Schritte

1. Frontend mit PDF-Overlay und Validierungsansicht
2. Kabelliste / Elementliste als Export
