# API starten (nach setup.ps1)
$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "backend")
& ".\.venv\Scripts\Activate.ps1"
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
