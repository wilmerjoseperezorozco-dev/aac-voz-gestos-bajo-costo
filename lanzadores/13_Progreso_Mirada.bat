@echo off
call "%~dp0_base.bat" || exit /b 1
cd /d "%~dp0.."
py -3.12 src\mirada_progreso.py
pause
