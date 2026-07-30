@echo off
rem No ejecutar directamente -- este archivo lo usan los demas .bat de esta carpeta.
rem Fija SIEMPRE Python 3.12 (el que tiene sounddevice, mediapipe, numpy,
rem etc. instalados). El comando "python" o "py" sin version puede resolver
rem a otra instalacion del sistema sin esas librerias y romper la app
rem (paso real 2026-07: se instalo Python 3.14 nuevo y quedo como
rem predeterminado, dejando sin efecto "python script.py" en la terminal).
cd /d "%~dp0.."
py -3.12 -c "import numpy, sounddevice" 2>nul
if errorlevel 1 (
    echo.
    echo ================================================================
    echo   ERROR: Python 3.12 no responde o le faltan librerias.
    echo   Esto NO deberia pasar -- avisa a Claude con este mensaje.
    echo ================================================================
    echo.
    pause
    exit /b 1
)
