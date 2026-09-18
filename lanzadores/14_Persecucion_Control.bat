@echo off
rem Sesion de CONTROL del investigador (alias CTRL1): nunca se mezcla con YP.
call "%~dp0_base.bat" || exit /b 1
cd /d "%~dp0.."
echo.
echo   SESION DE CONTROL  (alias CTRL1, NO es YP)
echo   1 = cabeza
echo   2 = ojos (mueve solo los ojos, cabeza quieta)
echo.
set /p op="  Elige 1 o 2 y pulsa ENTER: "
if "%op%"=="2" (
    py -3.12 src\persecucion_mirada.py --ojos --alias CTRL1 %*
) else (
    py -3.12 src\persecucion_mirada.py --alias CTRL1 %*
)
if errorlevel 1 (
    echo.
    echo Hubo un error al ejecutar. Revisa el mensaje de arriba.
    pause
)
