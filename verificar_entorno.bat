@echo off
chcp 65001 > nul
title Verificador de Salud del Entorno - Tutor Academico
cls
echo ======================================================================
echo  Iniciando comprobacion automatica del entorno...
echo ======================================================================

if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0verificar_entorno.py"
) else (
    python "%~dp0verificar_entorno.py"
)

echo.
pause
