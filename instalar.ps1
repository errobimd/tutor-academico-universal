# ======================================================================
#  Tutor Académico Universal - Instalador Automatizado y Blindado
# ======================================================================
$ErrorActionPreference = "SilentlyContinue"

# Detección dinámica y robusta de rutas relativas
$SkillRoot = $PSScriptRoot
$SkillsDir = Split-Path $SkillRoot -Parent
$AgentsDir = Split-Path $SkillsDir -Parent
$ProjectRoot = Split-Path $AgentsDir -Parent

$VenvDir = Join-Path $AgentsDir ".venv"
$PipExe = Join-Path $VenvDir "Scripts\pip.exe"
$PythonExe = Join-Path $VenvDir "Scripts\python.exe"
$PythonwExe = Join-Path $VenvDir "Scripts\pythonw.exe"
$ReqFile = Join-Path $SkillRoot "requirements.txt"
$VigilanteScript = Join-Path $SkillRoot "motor\auto_vigilante.py"
$GestorScript = Join-Path $SkillRoot "motor\auto_gestor.py"

# 1. Crear entorno virtual si no existe
if (!(Test-Path $PipExe)) {
    Write-Host "[1/4] Creando entorno virtual aislado (.agents/.venv)..."
    python -m venv $VenvDir
} else {
    Write-Host "[1/4] Entorno virtual existente detectado (.agents/.venv)."
}

# 2. Instalar dependencias requeridas
if (Test-Path $PipExe) {
    Write-Host "[2/4] Verificando dependencias del sistema..."
    & $PipExe install -r $ReqFile --quiet --no-warn-script-location
}

# 3. Arrancar centinela en segundo plano con pythonw (sin consola)
if (Test-Path $PythonwExe) {
    Write-Host "[3/4] Activando centinela permanente en segundo plano..."
    Start-Process -FilePath $PythonwExe -ArgumentList $VigilanteScript -WindowStyle Hidden
}

# 4. Generación inicial rápida del catálogo TEMARIO_ACTIVO.md
if (Test-Path $PythonExe) {
    Write-Host "[4/4] Sincronizando catálogo TEMARIO_ACTIVO.md..."
    & $PythonExe $GestorScript
}

Write-Host "======================================================================"
Write-Host "  ✅ TUTOR ACADÉMICO LISTO: Entorno, centinela y catálogo activos."
Write-Host "======================================================================"
