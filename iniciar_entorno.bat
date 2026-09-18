@echo off
chcp 65001 > nul
title Instalador y Verificador del Entorno - Tutor Académico
cls

echo ======================================================================
echo   TUTOR ACADEMICO UNIVERSAL - INICIALIZACION DEL ENTORNO AISLADO
echo ======================================================================
echo.

:: 1. Comprobar si Python está instalado
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] No se ha encontrado Python en tu sistema.
    echo Por favor instala Python 3.8 o superior desde python.org
    echo IMPORTANTE: Marca la casilla "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

:: 2. Crear entorno virtual .venv si no existe
if not exist "%~dp0.venv\Scripts\python.exe" (
    echo [+] Creando entorno virtual aislado (.venv)...
    python -m venv "%~dp0.venv"
    if %errorlevel% neq 0 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo [OK] Entorno virtual creado con exito.
    echo.
) else (
    echo [i] Entorno virtual (.venv) ya existente.
)

:: 3. Instalar/Actualizar dependencias en el .venv
echo [+] Comprobando e instalando dependencias (pypdf, python-docx, beautifulsoup4)...
"%~dp0.venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
"%~dp0.venv\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt" --quiet
if %errorlevel% neq 0 (
    echo [AVISO] Hubo alguna advertencia al instalar paquetes. Continuando con la verificacion...
) else (
    echo [OK] Dependencias instaladas y actualizadas correctamente.
)
echo.

:: 4. Ejecutar auditoría de salud con el Python aislado
echo [+] Ejecutando auditoria automatizada de salud...
echo.
"%~dp0.venv\Scripts\python.exe" "%~dp0verificar_entorno.py"

echo.
echo ======================================================================
echo  Todo listo. Ya puedes abrir Bionic y comenzar con @tutor-academico
echo ======================================================================
echo.
pause
