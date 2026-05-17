@echo off
cd /d "%~dp0"
echo Projektordner: %CD%
echo.
if not exist "setup.ps1" (
    echo FEHLER: setup.ps1 nicht gefunden.
    echo Bitte dieses Fenster im Ordner lst-bauueberwachung starten.
    pause
    exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0setup.ps1"
echo.
pause
