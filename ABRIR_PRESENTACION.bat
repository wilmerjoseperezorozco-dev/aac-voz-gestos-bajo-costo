@echo off
rem Lanzador para demos/presentaciones -- abre el menu central SIN mostrar
rem ninguna ventana de consola (usa pythonw en vez de python). Si algo
rem falla, no se ve ningun error en pantalla -- para depurar antes de una
rem presentacion, usa INICIAR.bat en su lugar (ese si muestra errores).
set PYTHONW="C:\Users\HP\AppData\Local\Microsoft\WindowsApps\PythonSoftwareFoundation.Python.3.12_qbz5n2kfra8p0\pythonw.exe"
cd /d "%~dp0"
start "" %PYTHONW% src\centro_comunicacion.py
