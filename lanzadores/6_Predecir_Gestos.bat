@echo off
call "%~dp0_base.bat" || exit /b 1
cd /d "%~dp0.."
py -3.12 src\gestos_predecir.py
if errorlevel 1 (
    echo.
    echo Hubo un error al ejecutar. Revisa el mensaje de arriba.
    pause
)
