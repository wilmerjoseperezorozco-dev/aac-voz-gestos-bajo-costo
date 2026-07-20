@echo off
rem Lanzador del Centro de comunicacion -- doble clic para abrir.
rem Usa explicitamente Python 3.12 (el que tiene todas las dependencias
rem instaladas); el comando "python" a secas puede apuntar a otra version
rem del sistema sin las librerias del proyecto.
cd /d "%~dp0"
py -3.12 src\centro_comunicacion.py
if errorlevel 1 (
    echo.
    echo Hubo un error al iniciar. Revisa el mensaje de arriba.
    pause
)
