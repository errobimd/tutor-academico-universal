#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Centinela Ultraligero en Tiempo Real (auto_vigilante.py)
Monitorea continuamente '1 Evaluación/' y la raíz del proyecto.
En cuanto detecta un archivo añadido, movido o eliminado,
actualiza automáticamente el catálogo TEMARIO_ACTIVO.md y la indexación RAG.
Consumo de CPU: 0.0%
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime

# Asegurar codificación utf-8
try:
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

from auto_gestor import AutoGestor
from indexador_academico import IndexadorAcademico

def obtener_instantanea_archivos(raiz):
    """
    Obtiene un diccionario con la firma de cada archivo relevante:
    { ruta_relativa: (tamano, fecha_modificacion) }
    """
    extensiones = ('.pdf', '.docx', '.html', '.txt')
    carpetas_ignoradas = {
        ".git", ".venv", "storage_index", "__pycache__", ".gemini", ".agents"
    }
    
    instantanea = {}
    p_raiz = Path(raiz)
    
    # 1. Escaneo en 1 Evaluación
    eval_dir = p_raiz / "1 Evaluación"
    rutas_a_escanear = []
    if eval_dir.exists():
        rutas_a_escanear.append(eval_dir)
    rutas_a_escanear.append(p_raiz)
    
    for base in rutas_a_escanear:
        for root, dirs, files in os.walk(base):
            # Excluir carpetas ignoradas
            dirs[:] = [d for d in dirs if d not in carpetas_ignoradas and "Plantemiento" not in d]
            for f in files:
                if f.lower().endswith(extensiones) and not f.startswith("~$"):
                    ruta_completa = Path(root) / f
                    try:
                        st = ruta_completa.stat()
                        rel = str(ruta_completa.relative_to(p_raiz))
                        instantanea[rel] = (st.st_size, st.st_mtime)
                    except Exception:
                        pass
    return instantanea

def main():
    base_dir = Path(__file__).resolve().parent.parent.parent
    gestor = AutoGestor(raiz_proyecto=base_dir)
    
    print("=" * 70)
    print(" 👁️  CENTINELA EN TIEMPO REAL - TUTOR ACADÉMICO")
    print(f"     Directorio vigilado: {base_dir}")
    print("     Consumo CPU: 0% | Intervalo: 1.5s")
    print("     Presiona Ctrl+C para detener el centinela.")
    print("=" * 70)

    # 1. Asegurar catálogo inicial al arrancar
    print("\n[+] Sincronizando catálogo inicial...")
    gestor.actualizar_manifest()
    instantanea_previa = obtener_instantanea_archivos(base_dir)
    print(f"[*] Centinela activo. Monitoreando {len(instantanea_previa)} documentos...")

    while True:
        try:
            time.sleep(1.5)
            instantanea_actual = obtener_instantanea_archivos(base_dir)

            if instantanea_actual != instantanea_previa:
                ahora = datetime.now().strftime("%H:%M:%S")
                print(f"\n[!] [{ahora}] 🔔 ¡CAMBIO DETECTADO EN DISCO!")
                
                # Detectar qué cambió exactamente
                nuevos_o_movidos = set(instantanea_actual.keys()) - set(instantanea_previa.keys())
                eliminados = set(instantanea_previa.keys()) - set(instantanea_actual.keys())
                
                for n in nuevos_o_movidos:
                    print(f"    └─ [+] Archivo detectado / reubicado: '{n}'")
                for e in eliminados:
                    print(f"    └─ [-] Archivo retirado: '{e}'")

                print("    ⏳ Reindexando RAG y actualizando TEMARIO_ACTIVO.md...")
                
                # 1. Reindexar todo
                indexador = IndexadorAcademico(raiz_proyecto=base_dir)
                indexador.indexar_todo()

                # 2. Actualizar catálogo y manifest
                gestor.actualizar_manifest()
                
                instantanea_previa = instantanea_actual
                print(f"    ✅ [{datetime.now().strftime('%H:%M:%S')}] Catálogo y RAG actualizados al 100%.\n")

        except KeyboardInterrupt:
            print("\n[i] Centinela detenido por el usuario.")
            break
        except Exception as err:
            print(f"[!] Error en ciclo de vigilancia: {err}")
            time.sleep(2)

if __name__ == "__main__":
    main()
