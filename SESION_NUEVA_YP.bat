@echo off
rem Sesion nueva unificada con YP: voz (si/no/ayuda) y luego gestos + cara.
rem Canales en SECUENCIA, nunca simultaneos (hallazgo de interferencia
rem cognitivo-motora en doble tarea, ver RESEARCH_LOG.md).
rem Cambia N para mas o menos muestras nuevas por palabra/gesto.
set N=5
cd /d "%~dp0"
py -3.12 -c "import numpy, sounddevice, mediapipe" 2>nul
if errorlevel 1 (
    echo ERROR: Python 3.12 no responde o le faltan librerias.
    pause
    exit /b 1
)

echo ============================================================
echo   SESION NUEVA CON YP  -  %N% muestras nuevas por palabra/gesto
echo   PASO 1 de 2: VOZ (si, no, ayuda)
echo ============================================================
py -3.12 src\grabar.py --nuevas %N% si no ayuda
if errorlevel 1 goto error

echo.
echo ============================================================
echo   Descanso. Cuando YP este lista, pulsa una tecla.
echo   PASO 2 de 2: GESTOS + CARA (si, no, ayuda)
echo ============================================================
pause
py -3.12 src\gestos_cara_grabar.py %N%
if errorlevel 1 goto error

echo.
echo Sesion terminada. Para ver las senales oculares:
echo   py -3.12 src\cara_analizar.py
pause
exit /b 0

:error
echo.
echo Hubo un error. Revisa el mensaje de arriba.
pause
exit /b 1
