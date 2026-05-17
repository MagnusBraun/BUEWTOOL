# LST Bauüberwachung – Installation (Windows PowerShell)
# Einfach: INSTALL.bat doppelklicken
# Oder:   Set-Location C:\Users\magnu\lst-bauueberwachung
#         .\setup.ps1

$ErrorActionPreference = "Stop"
$ProjectRoot = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
Write-Host "Projektordner: $ProjectRoot" -ForegroundColor Gray
$Backend = Join-Path $ProjectRoot "backend"

Write-Host "=== 1/4 PostgreSQL (Docker) ===" -ForegroundColor Cyan
Set-Location $ProjectRoot

$dockerCmd = Get-Command docker -ErrorAction SilentlyContinue
if (-not $dockerCmd) {
    Write-Host "Docker nicht gefunden. Bitte Docker Desktop installieren und starten." -ForegroundColor Red
    Write-Host "Download: https://www.docker.com/products/docker-desktop/" -ForegroundColor Yellow
    Write-Host "Setup wird ohne Datenbank fortgesetzt (Schritt 3 schlaegt ggf. fehl)." -ForegroundColor Yellow
} else {
    docker compose up -d
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Hinweis: Docker Desktop laeuft? Alternativ: docker-compose up -d" -ForegroundColor Yellow
        docker-compose up -d 2>$null
    }
}

Write-Host "=== 2/4 Python venv + Pakete ===" -ForegroundColor Cyan
Set-Location $Backend

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    throw "Python nicht gefunden. Bitte Python 3.11+ installieren und PATH pruefen."
}

python -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\.venv\Scripts\pip.exe" install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host ".env aus .env.example erstellt." -ForegroundColor Green
}

Write-Host "=== 3/4 Datenbank-Migration ===" -ForegroundColor Cyan
& ".\.venv\Scripts\alembic.exe" upgrade head

Write-Host "=== 4/4 Fertig ===" -ForegroundColor Green
Write-Host ""
Write-Host "Server starten:" -ForegroundColor Yellow
Write-Host '  cd C:\Users\magnu\lst-bauueberwachung\backend'
Write-Host '  .\.venv\Scripts\Activate.ps1'
Write-Host '  uvicorn app.main:app --reload --host 127.0.0.1 --port 8000'
Write-Host ""
Write-Host "Dokumentation: http://127.0.0.1:8000/docs" -ForegroundColor Yellow
