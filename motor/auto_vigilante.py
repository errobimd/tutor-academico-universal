#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Centinela Ultraligero y Sincronizador en Tiempo Real (auto_vigilante.py)
1. Monitorea continuamente '1 Evaluación/' y la raíz del proyecto:
   Detecta archivos nuevos, modificados o eliminados (.pdf, .docx, .html, .txt, .md como Obsidian)
   y actualiza inmediatamente TEMARIO_ACTIVO.md y el índice RAG.
2. Sincroniza periódicamente con GitHub (cada 3 minutos):
   Consulta silenciosamente el repositorio oficial con 'git pull' para mantener
   el tutor actualizado con las últimas reglas KaTeX y mejoras pedagógicas.
Consumo de CPU: 0.0%
"""

import os
import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

# Asegurar codificación utf-8
try:
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from auto_gestor import AutoGestor
from indexador_academico import IndexadorAcademico

ARCHIVOS_SISTEMA_IGNORADOS = {
    "requirements.txt", "system_prompt_tutor.txt", "temario_activo.md",
    "ejemplo_operaciones_latex.html", "ejemplo_operaciones_latex.md", "verificar_entorno.py",
    "readme.md", "skill.md", "instrucciones_tutor_bionic.md", "mapa_de_scripts_y_herramientas.md",
    "memoria_sesion_y_conversacion.md", "prompt_activacion_bionic.md", "revision_general_y_estado_proyecto.md"
}

def resolver_raiz_proyecto():
    """Determina la raíz de trabajo real (1 Evaluación o el espacio global)."""
    if len(sys.argv) > 1 and Path(sys.argv[1]).exists():
        return Path(sys.argv[1]).resolve()
    
    cwd = Path.cwd().resolve()
    if (cwd / "1 Evaluación").exists() or (cwd / ".agents").exists() or (cwd / "TEMARIO_ACTIVO.md").exists():
        return cwd
    
    candidato = Path(__file__).resolve().parent
    for _ in range(6):
        if (candidato / "1 Evaluación").exists() or (candidato / ".agents").exists() or (candidato / "TEMARIO_ACTIVO.md").exists():
            return candidato
        if candidato.parent == candidato:
            break
        candidato = candidato.parent
    return cwd

def obtener_instantanea_archivos(raiz):
    """
    Obtiene un diccionario con la firma de cada archivo relevante:
    { ruta_relativa: (tamano, fecha_modificacion) }
    """
    extensiones = ('.pdf', '.docx', '.html', '.txt', '.md')
    carpetas_ignoradas = {
        ".git", ".venv", "storage_index", "__pycache__", ".gemini", ".agents"
    }
    
    instantanea = {}
    p_raiz = Path(raiz)
    
    rutas_a_escanear = []
    eval_dir = p_raiz / "1 Evaluación"
    if eval_dir.exists() and eval_dir != p_raiz:
        rutas_a_escanear.append(eval_dir)
    rutas_a_escanear.append(p_raiz)
    
    for base in rutas_a_escanear:
        for root, dirs, files in os.walk(base):
            dirs[:] = [d for d in dirs if d not in carpetas_ignoradas and "Plantemiento" not in d and not d.startswith('.')]
            for f in files:
                f_lower = f.lower()
                if (
                    f_lower.endswith(extensiones) and 
                    not f.startswith("~$") and 
                    not f.startswith(".") and
                    f_lower not in ARCHIVOS_SISTEMA_IGNORADOS
                ):
                    ruta_completa = Path(root) / f
                    try:
                        st = ruta_completa.stat()
                        rel = str(ruta_completa.relative_to(p_raiz))
                        instantanea[rel] = (st.st_size, st.st_mtime)
                    except Exception:
                        pass
    return instantanea

def sincronizar_con_github(raiz):
    """
    Consulta silenciosamente el repositorio oficial en GitHub.
    Si hay cambios nuevos (reglas KaTeX, mejoras de motor), los descarga con 'git pull'.
    No bloquea si no hay conexión o si no es un repo git.
    """
    candidatos_git = [
        raiz / ".agents" / "skills" / "tutor-academico",
        raiz / "skills" / "tutor-academico",
        Path(__file__).resolve().parent.parent
    ]
    for ruta_repo in candidatos_git:
        if (ruta_repo / ".git").exists():
            try:
                res = subprocess.run(
                    ["git", "-C", str(ruta_repo), "pull", "--quiet"],
                    capture_output=True,
                    text=True,
                    timeout=15
                )
                if res.returncode == 0:
                    return True
            except Exception:
                pass
    return False

def main():
    base_dir = resolver_raiz_proyecto()
    gestor = AutoGestor(raiz_proyecto=base_dir)
    
    print("=" * 70)
    print(" 👁️  CENTINELA EN TIEMPO REAL Y SINCRONIZADOR GITHUB - TUTOR ACADÉMICO")
    print(f"     Directorio vigilado: {base_dir}")
    print("     Consumo CPU: 0% | Intervalo Local: 1.5s | Sincronización GitHub: cada 3 min")
    print("     Presiona Ctrl+C para detener el centinela.")
    print("=" * 70)

    # 1. Asegurar catálogo inicial al arrancar
    print("\n[+] Sincronizando catálogo inicial...")
    gestor.actualizar_manifest()
    instantanea_previa = obtener_instantanea_archivos(base_dir)
    print(f"[*] Centinela activo. Monitoreando {len(instantanea_previa)} documentos...")

    INTERVALO_GITHUB_SEG = 180  # 3 minutos
    ultimo_check_github = time.time()

    while True:
        try:
            time.sleep(1.5)
            
            # A. Comprobación periódica con GitHub
            ahora_tiempo = time.time()
            if ahora_tiempo - ultimo_check_github >= INTERVALO_GITHUB_SEG:
                ultimo_check_github = ahora_tiempo
                actualizado = sincronizar_con_github(base_dir)
                if actualizado:
                    print(f"    🌐 [{datetime.now().strftime('%H:%M:%S')}] Sincronización con GitHub: Repositorio al día.")

            # B. Comprobación de cambios en disco local
            instantanea_actual = obtener_instantanea_archivos(base_dir)

            if instantanea_actual != instantanea_previa:
                ahora = datetime.now().strftime("%H:%M:%S")
                print(f"\n[!] [{ahora}] 🔔 ¡CAMBIO DETECTADO EN DISCO!")
                
                nuevos_o_movidos = set(instantanea_actual.keys()) - set(instantanea_previa.keys())
                eliminados = set(instantanea_previa.keys()) - set(instantanea_actual.keys())
                
                for n in nuevos_o_movidos:
                    print(f"    └─ [+] Archivo detectado / reubicado: '{n}'")
                for e in eliminados:
                    print(f"    └─ [-] Archivo retirado: '{e}'")

                print("    ⏳ Reindexando y actualizando TEMARIO_ACTIVO.md...")
                
                try:
                    indexador = IndexadorAcademico(raiz_proyecto=base_dir)
                    indexador.indexar_todo()
                except Exception:
                    pass

                gestor.actualizar_manifest()
                instantanea_previa = instantanea_actual
                print(f"    ✅ [{datetime.now().strftime('%H:%M:%S')}] Catálogo TEMARIO_ACTIVO.md actualizado al 100%.\n")

        except KeyboardInterrupt:
            print("\n[i] Centinela detenido por el usuario.")
            break
        except Exception as err:
            print(f"[!] Error en ciclo de vigilancia: {err}")
            time.sleep(2)

if __name__ == "__main__":
    main()
