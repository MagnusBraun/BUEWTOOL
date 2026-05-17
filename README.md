# LST Bauüberwachung

Modulare Webanwendung zur Digitalisierung der Bauüberwachung im Bereich Leit- und Sicherungstechnik (LST).

## Projektstruktur

```
lst-bauueberwachung/
├── database/schema.sql      # PostgreSQL-Referenzschema
├── docker-compose.yml       # PostgreSQL 16
└── backend/
    ├── alembic/             # Migrationen
    ├── app/
    │   ├── api/routes/      # FastAPI-Routen
    │   ├── core/            # Konfiguration, Logging
    │   ├── db/              # SQLAlchemy Session
    │   ├── models/          # ORM-Modelle
    │   ├── schemas/         # Pydantic-Schemas
    │   └── services/        # Geschäftslogik
    └── requirements.txt
```

## Installation

### Windows (PowerShell) – empfohlen

**Nicht** den Bash-Block unten in PowerShell kopieren (`source`, `cp` und `&&` funktionieren dort nicht).

Einmal im Projektordner:

```powershell
Set-Location C:\Users\magnu\lst-bauueberwachung
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\setup.ps1
```

Falls die Aktivierung der venv blockiert wird (einmalig):

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

Server starten:

```powershell
.\start.ps1
```

Oder manuell, **jede Zeile einzeln**:

```powershell
Set-Location C:\Users\magnu\lst-bauueberwachung
docker compose up -d
Set-Location backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Linux / macOS

```bash
cd lst-bauueberwachung
docker compose up -d
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API-Dokumentation: [http://localhost:8000/docs](http://localhost:8000/docs)

## Beispielaufrufe

### Health Check

PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

### KÜP hochladen

PowerShell (Pfad anpassen):

```powershell
curl.exe -X POST "http://127.0.0.1:8000/upload/kuep" -F "file=@C:\pfad\zum\kuep.pdf"
```

### VLP hochladen

```powershell
curl.exe -X POST "http://127.0.0.1:8000/upload/vlp" -F "file=@C:\pfad\zum\vlp.xlsx"
```

## Entwicklungsstand


| Schritt                  | Status |
| ------------------------ | ------ |
| 1. PostgreSQL-Schema     | ✅      |
| 2. SQLAlchemy-Modelle    | ✅      |
| 3. FastAPI-Grundstruktur | ✅      |
| 4. Upload-Endpunkte      | ✅      |
| 5. PDF-Parsing           | ⏳      |
| 6. Geometrieerkennung    | ⏳      |


