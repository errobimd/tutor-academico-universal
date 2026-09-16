#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Motor de Indexación Modular Académico Universal.
Extrae PDFs hoja a hoja y DOCXs, particionando los índices por materia en
storage_index/{CODIGO_MATERIA}/, compatible con cualquier disciplina
(Informática, Biología, Nutrición Animal, etc.).
"""

import os
import sys
import re
import json
import math
from pathlib import Path
from collections import Counter
import pypdf
import docx

# Importar el auto_gestor local
sys.path.insert(0, str(Path(__file__).resolve().parent))
from auto_gestor import AutoGestor

# Asegurar codificación UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def limpiar_texto(texto):
    if not texto:
        return ""
    texto = re.sub(r'[ \t]+', ' ', texto)
    texto = re.sub(r'\n{3,}', '\n\n', texto)
    return texto.strip()

def clasificar_tipo_documento(nombre_archivo):
    nombre = nombre_archivo.lower()
    if any(k in nombre for k in ["ejercicio", "actividad", "taller", "tarea", "problema"]):
        return "ejercicios"
    if any(k in nombre for k in ["practica", "práctica", "laboratorio", "caso"]):
        return "practica"
    if any(k in nombre for k in ["solucion", "solución", "respuestas"]):
        return "soluciones"
    return "teoria"

class VectorizadorLocal:
    def __init__(self, dim=256):
        self.dim = dim

    def vectorizar(self, texto):
        tokens = re.findall(r'\b[a-zA-ZáéíóúÁÉÍÓÚñÑ0-9_]{2,}\b', texto.lower())
        if not tokens:
            return [0.0] * self.dim
            
        vec = [0.0] * self.dim
        counts = Counter(tokens)
        total = len(tokens)
        
        for token, count in counts.items():
            tf = (count / total) * (1.0 + math.log(1.0 + len(token)))
            h = hash(token) % self.dim
            vec[h] += tf
            if len(token) > 4:
                h_sub = hash(token[:4]) % self.dim
                vec[h_sub] += tf * 0.5
                
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [round(x / norm, 5) for x in vec]
        return vec

class IndexadorAcademico:
    def __init__(self, raiz_proyecto=None):
        self.gestor = AutoGestor(raiz_proyecto)
        self.raiz = self.gestor.raiz
        self.carpeta_storage = self.gestor.carpeta_storage
        self.vectorizador = VectorizadorLocal(dim=256)

    def extraer_pdf(self, ruta_pdf):
        paginas_extraidas = []
        try:
            reader = pypdf.PdfReader(str(ruta_pdf))
            total_paginas = len(reader.pages)
            for num_pag, page in enumerate(reader.pages, start=1):
                texto = page.extract_text() or ""
                texto = limpiar_texto(texto)
                if texto and len(texto) > 30:
                    paginas_extraidas.append({
                        "pagina": num_pag,
                        "total_paginas": total_paginas,
                        "texto": texto
                    })
        except Exception as e:
            print(f"⚠️ Error al leer PDF {ruta_pdf.name}: {e}", file=sys.stderr)
        return paginas_extraidas

    def extraer_docx(self, ruta_docx):
        fragmentos = []
        try:
            doc = docx.Document(str(ruta_docx))
            buffer_texto = []
            num_seccion = 1

            for p in doc.paragraphs:
                txt = limpiar_texto(p.text)
                if txt:
                    buffer_texto.append(txt)
                    if len(" ".join(buffer_texto)) > 600:
                        fragmentos.append({
                            "pagina": num_seccion,
                            "total_paginas": 1,
                            "texto": "\n".join(buffer_texto)
                        })
                        buffer_texto = []
                        num_seccion += 1

            for tabla in doc.tables:
                filas_tabla = []
                for row in tabla.rows:
                    celdas = [limpiar_texto(c.text) for c in row.cells]
                    filas_tabla.append(" | ".join(celdas))
                if filas_tabla:
                    fragmentos.append({
                        "pagina": num_seccion,
                        "total_paginas": 1,
                        "texto": "TABLA:\n" + "\n".join(filas_tabla)
                    })
                    num_seccion += 1

            if buffer_texto:
                fragmentos.append({
                    "pagina": num_seccion,
                    "total_paginas": max(1, num_seccion),
                    "texto": "\n".join(buffer_texto)
                })
        except Exception as e:
            print(f"⚠️ Error al leer DOCX {ruta_docx.name}: {e}", file=sys.stderr)
        return fragmentos

    def fragmentar_texto(self, texto, max_chars=800):
        oraciones = re.split(r'(?<=[.?!])\s+', texto)
        chunks = []
        actual = []
        longitud_actual = 0

        for oracion in oraciones:
            oracion = oracion.strip()
            if not oracion:
                continue
            if longitud_actual + len(oracion) > max_chars and actual:
                chunks.append(" ".join(actual))
                actual = [oracion]
                longitud_actual = len(oracion)
            else:
                actual.append(oracion)
                longitud_actual += len(oracion)

        if actual:
            chunks.append(" ".join(actual))
        return chunks or [texto]

    def indexar_todo(self):
        revision = self.gestor.verificar_proyecto()
        if revision["estado"] == "PROYECTO_VACIO":
            return {
                "exito": False,
                "mensaje": revision["mensaje_alumno"]
            }

        materias = revision.get("materias", {})
        resumen = {
            "materias": {},
            "total_fragmentos": 0,
            "total_documentos": revision.get("total_archivos", 0)
        }

        self.carpeta_storage.mkdir(parents=True, exist_ok=True)

        for codigo, info in materias.items():
            print(f"📚 Indexando Materia: {codigo} - {info['nombre']}...")
            ruta_materia = Path(info["ruta"])
            carpeta_indice = self.carpeta_storage / codigo
            carpeta_indice.mkdir(parents=True, exist_ok=True)

            documentos = list(ruta_materia.rglob("*.pdf")) + list(ruta_materia.rglob("*.docx"))
            nodos_materia = []
            temas_detectados = set()

            for doc in documentos:
                nombre_archivo = doc.name
                tipo_doc = clasificar_tipo_documento(nombre_archivo)
                try:
                    rel_padre = doc.parent.relative_to(ruta_materia)
                    tema_nombre = str(rel_padre).split(os.sep)[0] if str(rel_padre) != "." else "General"
                except Exception:
                    tema_nombre = "General"
                temas_detectados.add(tema_nombre)

                if doc.suffix.lower() == ".pdf":
                    paginas = self.extraer_pdf(doc)
                else:
                    paginas = self.extraer_docx(doc)

                for p in paginas:
                    num_pag = p["pagina"]
                    chunks = self.fragmentar_texto(p["texto"])
                    for idx_chunk, chunk in enumerate(chunks):
                        nodo_id = f"{codigo}_{re.sub(r'[^a-zA-Z0-9]', '_', tema_nombre)}_p{num_pag}_c{idx_chunk}"
                        vector = self.vectorizador.vectorizar(chunk)
                        
                        nodo = {
                            "id": nodo_id,
                            "materia_codigo": codigo,
                            "materia_nombre": info["nombre"],
                            "tema": tema_nombre,
                            "archivo": nombre_archivo,
                            "pagina": num_pag,
                            "tipo": tipo_doc,
                            "texto": chunk,
                            "vector": vector
                        }
                        nodos_materia.append(nodo)

            ruta_indice_json = carpeta_indice / "index.json"
            with open(ruta_indice_json, "w", encoding="utf-8") as f:
                json.dump({
                    "materia_codigo": codigo,
                    "nombre": info["nombre"],
                    "temas": sorted(list(temas_detectados)),
                    "total_nodos": len(nodos_materia),
                    "nodos": nodos_materia
                }, f, indent=2, ensure_ascii=False)

            resumen["materias"][codigo] = {
                "nombre": info["nombre"],
                "temas": sorted(list(temas_detectados)),
                "documentos": len(documentos),
                "fragmentos_indexados": len(nodos_materia)
            }
            resumen["total_fragmentos"] += len(nodos_materia)

        self.gestor.actualizar_manifest()
        return resumen

if __name__ == "__main__":
    indexador = IndexadorAcademico()
    resultado = indexador.indexar_todo()
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
