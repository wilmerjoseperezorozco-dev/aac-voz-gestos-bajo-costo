@echo off
rem Lanzador directo del tablero de comunicacion -- doble clic para abrir.
cd /d "%~dp0"
py -3.12 src\tablero_escaneo.py
if errorlevel 1 (
    echo.
    echo Hubo un error al iniciar. Revisa el mensaje de arriba.
    pause
)
