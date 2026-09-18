#!/usr/bin/env bash
# Instalador y Verificador del Entorno - Tutor Académico (Linux / macOS)

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

echo "======================================================================"
echo "  TUTOR ACADEMICO UNIVERSAL - INICIALIZACION DEL ENTORNO AISLADO"
echo "======================================================================"
echo ""

if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 no está instalado en el sistema."
    exit 1
fi

if [ ! -f "$DIR/.venv/bin/python" ]; then
    echo "[+] Creando entorno virtual aislado (.venv)..."
    python3 -m venv "$DIR/.venv"
    echo "[OK] Entorno virtual creado con éxito."
else
    echo "[i] Entorno virtual (.venv) ya existente."
fi

echo "[+] Comprobando e instalando dependencias (pypdf, python-docx, beautifulsoup4)..."
"$DIR/.venv/bin/python" -m pip install --upgrade pip --quiet
"$DIR/.venv/bin/python" -m pip install -r "$DIR/requirements.txt" --quiet
echo "[OK] Dependencias instaladas y actualizadas correctamente."
echo ""

echo "[+] Ejecutando auditoría automatizada de salud..."
"$DIR/.venv/bin/python" "$DIR/verificar_entorno.py"

echo ""
echo "======================================================================"
echo " Todo listo. Ya puedes abrir Bionic y comenzar con @tutor-academico"
echo "======================================================================"
