#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sensor Autónomo Universal y Gestor de Entorno del Tutor Académico.
100% Agnóstico: detecta dinámicamente cualquier temática, asignatura o materia
(Informática, Biología, Nutrición Felina, Historia, etc.) sin nombres fijos en código.
"""

import os
import sys
import re
import json
import hashlib
from pathlib import Path

# Asegurar codificación UTF-8 para consola Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def limpiar_nombre_materia(nombre_carpeta):
    """
    Limpia el nombre de la carpeta para mostrarlo de forma elegante al estudiante.
    Elimina nombres de profesores entre paréntesis si los hubiera:
    'GEBD - Gestión de bases de datos (JUANAN...)' -> 'GEBD - Gestión de bases de datos'
    'Nutrición y Alimentación de Gatos' -> 'Nutrición y Alimentación de Gatos'
    """
    limpio = re.sub(r'\s*\([^)]*\)', '', nombre_carpeta).strip()
    return limpio or nombre_carpeta

import unicodedata

def quitar_tildes(texto):
    """Elimina acentos y tildes para normalización limpia."""
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def generar_codigo_materia(nombre_carpeta):
    """
    Genera un identificador corto y limpio para la subcarpeta de almacenamiento.
    Ejemplos:
    'GEBD - Gestión de bases de datos' -> 'GEBD'
    'Nutrición Felina' -> 'NUTRICION_FELINA'
    'Biología Marina' -> 'BIOLOGIA_MARINA'
    'Alimentación de Gatos' -> 'ALIMENTACION_DE_GATOS'
    """
    nombre_limpio = limpiar_nombre_materia(nombre_carpeta)
    partes = nombre_limpio.split("-")
    primera_parte = partes[0].strip()
    
    # Si la primera parte es un código corto (ej. REDA, IMSO, MAT1)
    if len(primera_parte) <= 6 and primera_parte.isalnum():
        return primera_parte.upper()
    
    # Si es un nombre descriptivo
    sin_tildes = quitar_tildes(nombre_limpio)
    codigo = re.sub(r'[^a-zA-Z0-9]', '_', sin_tildes)
    codigo = re.sub(r'_+', '_', codigo).strip('_').upper()
    return codigo[:30]

def calcular_hash_archivo(ruta_archivo):
    """Calcula el hash MD5 y fecha de modificación de un archivo para control de cambios."""
    try:
        stat = os.stat(ruta_archivo)
        hasher = hashlib.md5()
        with open(ruta_archivo, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return {
            "mtime": stat.st_mtime,
            "size": stat.st_size,
            "md5": hasher.hexdigest()
        }
    except Exception:
        return None

class AutoGestor:
    def __init__(self, raiz_proyecto=None):
        if raiz_proyecto:
            self.raiz = Path(raiz_proyecto).resolve()
        else:
            cwd = Path.cwd().resolve()
            if (cwd / "1 Evaluación").exists():
                self.raiz = cwd
            elif Path("d:/Biblioteca_Temas/1 Evaluación").exists():
                self.raiz = Path("d:/Biblioteca_Temas").resolve()
            else:
                self.raiz = Path(__file__).resolve().parent.parent.parent
            
        self.carpeta_evaluacion = self.raiz / "1 Evaluación"
        self.carpeta_storage = Path(__file__).resolve().parent / "storage_index"
        self.ruta_manifest = self.carpeta_storage / "manifest.json"

    def verificar_proyecto(self):
        """
        Descubre dinámicamente cualquier carpeta que contenga documentos curriculares
        (PDFs, DOCXs), sin importar la temática o estructura.
        """
        carpetas_encontradas = []

        # 1. Si existe '1 Evaluación', explorar sus subcarpetas
        if self.carpeta_evaluacion.exists() and self.carpeta_evaluacion.is_dir():
            carpetas_encontradas.extend([d for d in self.carpeta_evaluacion.iterdir() if d.is_dir()])

        # 2. Explorar carpetas de primer nivel en la raíz (para proyectos temáticos como Biología, etc.)
        for item in self.raiz.iterdir():
            if item.is_dir() and item.name not in [
                ".git", ".venv", "Plantemiento con indexacion", "storage_index", 
                "skills", "html", "imagenes", "__pycache__", "1 Evaluación"
            ]:
                carpetas_encontradas.append(item)

        # 3. Clasificar materias y contar documentos
        materias_detectadas = {}
        total_docs = 0

        for carp in carpetas_encontradas:
            docs = list(carp.rglob("*.pdf")) + list(carp.rglob("*.docx"))
            if docs:
                codigo = generar_codigo_materia(carp.name)
                nombre_visible = limpiar_nombre_materia(carp.name)
                
                # Manejo de colisión de códigos
                if codigo in materias_detectadas and materias_detectadas[codigo]["ruta"] != str(carp):
                    codigo = f"{codigo}_{len(materias_detectadas)}"

                materias_detectadas[codigo] = {
                    "nombre": nombre_visible,
                    "ruta": str(carp),
                    "total_docs": len(docs)
                }
                total_docs += len(docs)

        if not materias_detectadas:
            return {
                "estado": "PROYECTO_VACIO",
                "mensaje_alumno": (
                    "¡Hola! Veo que has activado tu Tutor Académico, pero todavía no encuentro "
                    "carpetas con apuntes ni documentos en este proyecto.\n\n"
                    "Para poder enseñarte con tus propios materiales, añade tus carpetas de apuntes "
                    "(por ejemplo: Biología, Alimentación de Gatos, Redes, etc.) con sus PDFs o DOCXs.\n"
                    "En cuanto los pegues, los detectaré automáticamente y comenzaremos la sesión."
                ),
                "materias": {}
            }

        return {
            "estado": "ARCHIVOS_DETECTADOS",
            "total_archivos": total_docs,
            "materias": materias_detectadas
        }

    def detectar_cambios_documentos(self):
        """Compara con manifest.json para saber si hay que indexar."""
        revision = self.verificar_proyecto()
        if revision["estado"] == "PROYECTO_VACIO":
            return {
                "necesita_indexar": False,
                "es_primera_vez": False,
                "mensaje": revision["mensaje_alumno"]
            }

        manifest_previo = {}
        if self.ruta_manifest.exists():
            try:
                with open(self.ruta_manifest, "r", encoding="utf-8") as f:
                    manifest_previo = json.load(f)
            except Exception:
                manifest_previo = {}

        es_primera_vez = len(manifest_previo) == 0
        archivos_nuevos_o_modificados = []

        for codigo, info in revision["materias"].items():
            ruta_materia = Path(info["ruta"])
            for doc in list(ruta_materia.rglob("*.pdf")) + list(ruta_materia.rglob("*.docx")):
                info_hash = calcular_hash_archivo(doc)
                if not info_hash:
                    continue
                try:
                    rel_path = str(doc.relative_to(self.raiz))
                except Exception:
                    rel_path = str(doc)

                prev = manifest_previo.get(rel_path)
                if not prev or prev.get("md5") != info_hash["md5"]:
                    archivos_nuevos_o_modificados.append(doc)

        necesita_indexar = len(archivos_nuevos_o_modificados) > 0

        mensaje_alumno = None
        if es_primera_vez and necesita_indexar:
            mensaje_alumno = "Esta es la primera vez que usas el skill, tardará un poco más mientras preparo todo tu espacio de estudio..."
        elif necesita_indexar:
            mensaje_alumno = "Hay nuevos documentos en tus carpetas, tengo que indexarlos para poder darte nuevas lecciones sobre ellos... ¡Un segundo!"

        return {
            "necesita_indexar": necesita_indexar,
            "es_primera_vez": es_primera_vez,
            "archivos_nuevos": [str(p) for p in archivos_nuevos_o_modificados],
            "materias": revision["materias"],
            "mensaje_alumno": mensaje_alumno
        }

    def actualizar_manifest(self):
        self.carpeta_storage.mkdir(parents=True, exist_ok=True)
        manifest = {}
        revision = self.verificar_proyecto()
        if revision["estado"] == "ARCHIVOS_DETECTADOS":
            for codigo, info in revision["materias"].items():
                ruta_materia = Path(info["ruta"])
                for doc in list(ruta_materia.rglob("*.pdf")) + list(ruta_materia.rglob("*.docx")):
                    info_hash = calcular_hash_archivo(doc)
                    if info_hash:
                        try:
                            rel_path = str(doc.relative_to(self.raiz))
                        except Exception:
                            rel_path = str(doc)
                        manifest[rel_path] = info_hash

        with open(self.ruta_manifest, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        return manifest

if __name__ == "__main__":
    gestor = AutoGestor()
    estado = gestor.detectar_cambios_documentos()
    print(json.dumps(estado, indent=2, ensure_ascii=False))
