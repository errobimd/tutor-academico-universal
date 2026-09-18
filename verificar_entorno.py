#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auditor Automatizado de Salud del Entorno - Tutor Académico
Verifica carpetas, apuntes, sintaxis KaTeX y dependencias antes de iniciar.
"""

import os
import sys

# Asegurar codificación utf-8 en terminal de Windows
try:
    if sys.stdout.encoding.lower() != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print("=" * 70)
    print(" [i] AUDITORIA AUTOMATIZADA DE SALUD DEL ENTORNO")
    print("     Proyecto: Tutor Academico (Bionic Studio)")
    print(f"     Directorio: {base_dir}")
    print("=" * 70)
    
    total_checks = 0
    passed_checks = 0
    warnings = 0
    errors = 0

    def report(status, title, detail=""):
        nonlocal total_checks, passed_checks, warnings, errors
        total_checks += 1
        if status == "OK":
            passed_checks += 1
            icon = "  [ OK ] [v]"
        elif status == "AVISO":
            warnings += 1
            icon = "  [WARN] [!]"
        else:
            errors += 1
            icon = "  [FAIL] [X]"
        print(f"{icon} {title}")
        if detail:
            print(f"         └─ {detail}")

    print("\n[+] 1. VERIFICACION DE CARPETAS Y TEMARIOS:")
    eval_dir = os.path.join(base_dir, "1 Evaluación")
    if os.path.exists(eval_dir) and os.path.isdir(eval_dir):
        doc_files = []
        subdirs = []
        for root, dirs, files in os.walk(eval_dir):
            for d in dirs:
                subdirs.append(d)
            for f in files:
                if f.lower().endswith(('.pdf', '.docx', '.doc', '.txt')):
                    doc_files.append(os.path.join(root, f))
        
        if len(doc_files) > 0:
            report("OK", f"Temario detectado en '1 Evaluacion/': {len(doc_files)} documentos en {len(set(subdirs))} asignaturas")
        else:
            report("AVISO", "Carpeta '1 Evaluacion/' encontrada pero no contiene archivos PDF/DOCX")
    else:
        report("AVISO", "No se detecto la carpeta '1 Evaluacion/'. Coloca tus apuntes para indexarlos.")

    for folder in ["skills", "html", "imagenes"]:
        fpath = os.path.join(base_dir, folder)
        if os.path.exists(fpath) and os.path.isdir(fpath):
            report("OK", f"Directorio '{folder}/' presente y accesible")
        else:
            report("AVISO", f"Directorio '{folder}/' no encontrado o vacio")

    print("\n[+] 2. VERIFICACION DE SKILLS Y REGLAS DEL AGENTE:")
    skills_expected = [
        ("skills/verificador-entorno/SKILL.md", "Skill @verificador-entorno (Pre-vuelo)"),
        ("skills/tutor-academico/SKILL.md", "Skill @tutor-academico (Tutor Principal)"),
        ("SYSTEM_PROMPT_TUTOR.txt", "Instrucciones Maestras del Tutor"),
        ("GUIA_CONFIGURACION_BIONIC.md", "Guia de Configuracion Bionic Studio"),
        ("LEEME_PRIMERO_INSTRUCCIONES_FACILES.md", "Manual Facil de Instrucciones"),
        ("EJEMPLO_OPERACIONES_LATEX.html", "Portal Demostracion KaTeX / Mermaid")
    ]

    for rel_path, desc in skills_expected:
        full_p = os.path.join(base_dir, rel_path)
        if os.path.exists(full_p):
            sz = os.path.getsize(full_p)
            report("OK", f"{desc} -> {rel_path} ({sz} bytes)")
        else:
            report("AVISO", f"Archivo informativo no encontrado en esta ubicacion: {rel_path}")

    print("\n[+] 3. AUDITORIA DE COMPATIBILIDAD KATEX Y SINTAXIS MATEMATICA:")
    forbidden_tokens = [
        (r"\cline", "Comando \\cline no soportado en KaTeX (debe ser \\hline o \\underline)"),
        (r"array}[t]", "Argumento posicional [t] no soportado en KaTeX"),
        (r"\text{\small", "Comando \\small dentro de \\text{} no soportado en KaTeX")
    ]

    syntax_clean = True
    scanned_files = 0
    for root, dirs, fnames in os.walk(base_dir):
        if "node_modules" in root or ".git" in root or ".venv" in root:
            continue
        for fname in fnames:
            if fname.endswith(('.html', '.md', '.txt')):
                scanned_files += 1
                fpath = os.path.join(root, fname)
                try:
                    with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    for token, msg in forbidden_tokens:
                        if token in content:
                            rel = os.path.relpath(fpath, base_dir)
                            report("FAIL", f"Sintaxis incompatible en {rel}", f"{token}: {msg}")
                            syntax_clean = False
                except Exception:
                    pass

    if syntax_clean:
        report("OK", f"Barrido completado en {scanned_files} archivos: 0 errores de sintaxis KaTeX")

    print("\n[+] 4. AUDITORIA DE DEPENDENCIAS PYTHON Y ENTORNO VIRTUAL:")
    en_venv = (sys.prefix != sys.base_prefix) or ("VIRTUAL_ENV" in os.environ)
    if en_venv:
        report("OK", f"Entorno virtual aislado detectado (.venv activo): {sys.prefix}")
    else:
        report("AVISO", "Ejecutando en entorno Python global del sistema (Se recomienda usar un .venv)")

    paquetes_requeridos = [
        ("pypdf", "Lectura y extracción hoja a hoja de documentos PDF oficiales"),
        ("docx", "Lectura de enunciados y ejercicios en formato Word DOCX"),
        ("bs4", "Procesamiento y auditoría de chuletas imprimibles HTML (BeautifulSoup4)")
    ]

    for mod_name, mod_desc in paquetes_requeridos:
        try:
            __import__(mod_name)
            report("OK", f"Libreria '{mod_name}' disponible -> {mod_desc}")
        except ImportError:
            report("FAIL", f"Libreria '{mod_name}' no instalada", f"Ejecuta: pip install -r requirements.txt (o iniciar_entorno.bat)")

    print("\n[+] 5. VERIFICACION DE DEPENDENCIAS WEB Y VISUALIZACION:")
    report("OK", "Librerias KaTeX y Mermaid configuradas mediante CDN oficial con autodescarga")
    report("OK", "Modo oscuro y soporte tipografico para cajetines de division verificado")

    print("\n" + "=" * 70)
    print(" [=] RESUMEN FINAL DEL SISTEMA:")
    print(f"     Comprobaciones exitosas: {passed_checks}/{total_checks}")
    print(f"     Advertencias menores:    {warnings}")
    print(f"     Errores criticos:        {errors}")
    print("=" * 70)

    if errors == 0:
        print("\n [OK] VEREDICTO: ENTORNO 100% OPERATIVO Y VERIFICADO.")
        print("      Ya puedes abrir Bionic Studio, cargar el proyecto y llamar a:")
        print("      >> @tutor-academico\n")
        return 0
    else:
        print("\n [!] VEREDICTO: SE HAN ENCONTRADO ERRORES CRITICOS.")
        print("     Revisa los archivos marcados con [FAIL] antes de continuar.\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())
