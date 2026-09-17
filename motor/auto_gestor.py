#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Sensor Autónomo Universal y Gestor de Entorno del Tutor Académico.
100% Agnóstico e Inteligente:
- Detecta dinámicamente carpetas y ARCHIVOS SUELTOS (sin carpeta).
- Lee la primera página (portada) de cada documento para deducir automáticamente
  su temática real (evitando nombres vacíos o genéricos como 'tema general').
- Genera en tiempo real el archivo TEMARIO_ACTIVO.md en el espacio de trabajo.
- Detecta novedades y emite alertas proactivas al alumno.
"""

import os
import sys
import re
import json
import hashlib
import unicodedata
from pathlib import Path

# Asegurar codificación UTF-8 para consola Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def quitar_tildes(texto):
    """Elimina acentos y tildes para normalización limpia."""
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

def limpiar_nombre_materia(nombre_carpeta):
    """
    Limpia el nombre de la carpeta para mostrarlo de forma elegante al estudiante.
    Elimina nombres de profesores entre paréntesis si los hubiera.
    """
    limpio = re.sub(r'\s*\([^)]*\)', '', nombre_carpeta).strip()
    return limpio or nombre_carpeta

def extraer_titulo_portada(ruta_doc):
    """
    Lee las primeras líneas de la página 1 de un PDF o DOCX para inferir
    el título o temática real del documento de forma autónoma.
    """
    ruta = Path(ruta_doc)
    texto_inicio = ""
    try:
        if ruta.suffix.lower() == ".pdf":
            import pypdf
            reader = pypdf.PdfReader(str(ruta))
            if reader.pages:
                texto_inicio = reader.pages[0].extract_text() or ""
        elif ruta.suffix.lower() == ".docx":
            import docx
            doc = docx.Document(str(ruta))
            parrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            texto_inicio = "\n".join(parrafos[:6])
    except Exception:
        pass

    if not texto_inicio:
        return ruta.stem

    lineas = [l.strip() for l in texto_inicio.split("\n") if len(l.strip()) > 3]
    lineas_validas = []
    for l in lineas:
        if not re.match(r'^(página|page|\d+guía|\d+|http|www|versión|octubre|noviembre|diciembre|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre)', l, re.I):
            lineas_validas.append(l)

    if lineas_validas:
        frase = []
        caracteres = 0
        for l in lineas_validas[:4]:
            frase.append(l)
            caracteres += len(l)
            if caracteres > 35:
                break
        titulo = " ".join(frase)
        titulo = re.sub(r'\s+', ' ', titulo).strip()
        return titulo[:90]

    return ruta.stem

def generar_codigo_materia(nombre_carpeta):
    """Genera un identificador corto y limpio para la subcarpeta de almacenamiento."""
    nombre_limpio = limpiar_nombre_materia(nombre_carpeta)
    partes = nombre_limpio.split("-")
    primera_parte = partes[0].strip()
    
    if len(primera_parte) <= 6 and primera_parte.isalnum():
        return primera_parte.upper()
    
    sin_tildes = quitar_tildes(nombre_limpio)
    codigo = re.sub(r'[^a-zA-Z0-9]', '_', sin_tildes)
    codigo = re.sub(r'_+', '_', codigo).strip('_').upper()
    return codigo[:30] or "MATERIA"

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
        self.ruta_catalogo_md = self.raiz / "TEMARIO_ACTIVO.md"

    def verificar_proyecto(self):
        """
        Descubre dinámicamente:
        1. Subcarpetas organizadas en '1 Evaluación/'
        2. Subcarpetas temáticas en la raíz del proyecto
        3. Documentos sueltos (PDFs/DOCXs sin carpeta) en '1 Evaluación/' y en la raíz
        Infiere semánticamente el tema leyendo la portada de los documentos.
        """
        materias_detectadas = {}
        total_docs = 0

        # Carpetas a ignorar
        carpetas_ignoradas = {
            ".git", ".venv", "Plantemiento con indexacion", "storage_index", 
            "skills", "html", "imagenes", "__pycache__", ".gemini", ".agents"
        }

        # 1. Explorar subcarpetas en '1 Evaluación'
        carpetas_a_escanear = []
        if self.carpeta_evaluacion.exists() and self.carpeta_evaluacion.is_dir():
            carpetas_a_escanear.extend([d for d in self.carpeta_evaluacion.iterdir() if d.is_dir()])

        # 2. Explorar subcarpetas en la raíz del proyecto
        for item in self.raiz.iterdir():
            if item.is_dir() and item.name not in carpetas_ignoradas and item.name != "1 Evaluación":
                carpetas_a_escanear.append(item)

        # 3. Procesar cada carpeta
        for carp in carpetas_a_escanear:
            docs = list(carp.rglob("*.pdf")) + list(carp.rglob("*.docx"))
            if docs:
                codigo = generar_codigo_materia(carp.name)
                nombre_base = limpiar_nombre_materia(carp.name)

                # Si el nombre de la carpeta es genérico (ej. 'tema general', 'varios', 'apuntes')
                # inferir el tema del contenido de su primer documento
                nombre_descriptivo = nombre_base
                if any(k in nombre_base.lower() for k in ["tema general", "varios", "apuntes", "documentos", "general", "otros"]):
                    tema_portada = extraer_titulo_portada(docs[0])
                    nombre_descriptivo = f"{nombre_base.upper()}: {tema_portada}"

                if codigo in materias_detectadas and materias_detectadas[codigo]["ruta"] != str(carp):
                    codigo = f"{codigo}_{len(materias_detectadas)}"

                materias_detectadas[codigo] = {
                    "nombre": nombre_descriptivo,
                    "ruta": str(carp),
                    "total_docs": len(docs),
                    "es_archivo_suelto": False,
                    "documentos": [str(d) for d in docs]
                }
                total_docs += len(docs)

        # 4. Procesar ARCHIVOS SUELTOS (PDFs o DOCXs sin carpeta)
        rutas_sueltas = []
        if self.carpeta_evaluacion.exists():
            rutas_sueltas.extend([f for f in self.carpeta_evaluacion.glob("*.pdf")] + [f for f in self.carpeta_evaluacion.glob("*.docx")])
        rutas_sueltas.extend([f for f in self.raiz.glob("*.pdf")] + [f for f in self.raiz.glob("*.docx")])

        for doc_suelto in rutas_sueltas:
            # Ignorar archivos en carpetas de sistema
            if doc_suelto.name.startswith("~$") or "temp" in doc_suelto.name.lower():
                continue
            tema_suelto = extraer_titulo_portada(doc_suelto)
            cod_suelto = f"DOC_{generar_codigo_materia(doc_suelto.stem)}"
            if cod_suelto in materias_detectadas:
                cod_suelto = f"{cod_suelto}_{len(materias_detectadas)}"

            # Sugerencia de carpeta inteligente
            sug_carpeta = "Cuidado de Gatos" if any(k in doc_suelto.name.lower() or k in tema_suelto.lower() for k in ["gatito", "gato", "felino"]) else f"Tema - {tema_suelto[:25]}"

            materias_detectadas[cod_suelto] = {
                "nombre": f"[Documento Suelto] {tema_suelto} ({doc_suelto.name})",
                "titulo_portada": tema_suelto,
                "nombre_archivo": doc_suelto.name,
                "ruta": str(doc_suelto),
                "total_docs": 1,
                "es_archivo_suelto": True,
                "sugerencia_carpeta": sug_carpeta,
                "documentos": [str(doc_suelto)]
            }
            total_docs += 1

        if not materias_detectadas:
            return {
                "estado": "PROYECTO_VACIO",
                "mensaje_alumno": (
                    "¡Hola! Veo que has activado tu Tutor Académico, pero todavía no encuentro "
                    "carpetas ni documentos en este proyecto.\n\n"
                    "Añade tus archivos (PDFs o DOCXs) dentro de carpetas o sueltos en el proyecto "
                    "y los detectaré automáticamente para comenzar."
                ),
                "materias": {}
            }

        return {
            "estado": "ARCHIVOS_DETECTADOS",
            "total_archivos": total_docs,
            "materias": materias_detectadas
        }

    def detectar_cambios_documentos(self):
        """Compara con manifest.json para saber si hay que indexar y detectar novedades."""
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
        novedades_titulos = []

        for codigo, info in revision["materias"].items():
            for ruta_doc_str in info["documentos"]:
                doc = Path(ruta_doc_str)
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
                    titulo = extraer_titulo_portada(doc)
                    novedades_titulos.append(f"{info['nombre']} -> {doc.name} ({titulo})")

        necesita_indexar = len(archivos_nuevos_o_modificados) > 0

        mensaje_alumno = None
        if es_primera_vez and necesita_indexar:
            mensaje_alumno = "Esta es la primera vez que usas el skill, tardará un poco más mientras preparo todo tu espacio de estudio..."
        elif necesita_indexar:
            lista_novedades = ", ".join([f"'{Path(p).name}'" for p in archivos_nuevos_o_modificados[:3]])
            mensaje_alumno = f"📢 ¡He detectado nuevos documentos en tus carpetas: {lista_novedades}! Los he incorporado a tu temario de estudio."

        return {
            "necesita_indexar": necesita_indexar,
            "es_primera_vez": es_primera_vez,
            "archivos_nuevos": [str(p) for p in archivos_nuevos_o_modificados],
            "novedades_titulos": novedades_titulos,
            "materias": revision["materias"],
            "mensaje_alumno": mensaje_alumno
        }

    def generar_catalogo_markdown(self, novedades=None):
        """
        Genera el archivo TEMARIO_ACTIVO.md en la raíz del proyecto para que
        cualquier agente o LLM en Bionic Studio sepa al instante qué materias
        existen, de qué trata cada una y si hay novedades.
        """
        revision = self.verificar_proyecto()
        if revision["estado"] == "PROYECTO_VACIO":
            contenido = "# 📚 TEMARIO ACTIVO\n\n*No se han detectado documentos en el espacio de trabajo.*"
        else:
            lineas = [
                "# 📚 TEMARIO ACTIVO DEL PROYECTO (ACTUALIZADO EN VIVO)",
                "> Este catálogo refleja los documentos reales descubiertos en el espacio de trabajo.",
                ""
            ]

            if novedades and len(novedades) > 0:
                lineas.append("### 📢 ¡NUEVOS DOCUMENTOS DETECTADOS RECIENTEMENTE!")
                for nov in novedades:
                    lineas.append(f"- 🔔 **{nov}**")
                lineas.append("")

            # Propuestas de organización para archivos sueltos
            sueltos = [info for info in revision["materias"].values() if info.get("es_archivo_suelto")]
            if sueltos:
                lineas.append("### 📁 ASISTENTE DE ORGANIZACIÓN (ARCHIVOS SUELTOS):")
                for s in sueltos:
                    lineas.append(f"- ⚠️ **Archivo suelto encontrado:** `{s['nombre_archivo']}`")
                    lineas.append(f"  * **Título real de la portada:** \"{s.get('titulo_portada', s['nombre_archivo'])}\"")
                    lineas.append(f"  * **Pregunta organizativa al estudiante:** \"He encontrado el archivo suelto '{s.get('titulo_portada', s['nombre_archivo'])}'. A modo de organización de tu biblioteca, ¿quieres que creemos una carpeta como `{s.get('sugerencia_carpeta', 'Nueva Carpeta')}` (o dime cómo prefieres que se llame la carpeta) para guardarlo y ordenar tus apuntes?\"")
                lineas.append("")

            lineas.append("## 🗂️ Materias y Asignaturas Disponibles:")
            
            emojis = ["🗄️", "🌐", "🖥️", "📄", "🏭", "🍅", "🌱", "🔬", "📚", "⚖️", "📊", "💡"]
            for idx, (codigo, info) in enumerate(revision["materias"].items(), start=1):
                emoji = emojis[(idx - 1) % len(emojis)]
                lineas.append(f"### [{idx}] {emoji} **{codigo}:** {info['nombre']}")
                lineas.append(f"- **Documentos ({info['total_docs']}):**")
                for doc_path in info["documentos"][:5]:
                    nombre_archivo = Path(doc_path).name
                    lineas.append(f"  * `{nombre_archivo}`")
                if info["total_docs"] > 5:
                    lineas.append(f"  * *(y {info['total_docs'] - 5} documentos adicionales)*")
                lineas.append("")

            contenido = "\n".join(lineas)

        try:
            with open(self.ruta_catalogo_md, "w", encoding="utf-8") as f:
                f.write(contenido)
            # También guardar en 1 Evaluación para visibilidad directa en Bionic Studio
            if self.carpeta_evaluacion.exists():
                with open(self.carpeta_evaluacion / "TEMARIO_ACTIVO.md", "w", encoding="utf-8") as f:
                    f.write(contenido)
        except Exception:
            pass

        return self.ruta_catalogo_md

    def organizar_archivo(self, archivo_nombre_o_ruta, nombre_carpeta):
        """
        Crea físicamente la carpeta dentro de 1 Evaluación/ y traslada el archivo suelto,
        reindexando y actualizando el catálogo automáticamente.
        """
        import shutil
        ruta_origen = Path(archivo_nombre_o_ruta)
        if not ruta_origen.is_absolute():
            # Buscar en 1 Evaluación o en la raíz
            posibles = [
                self.carpeta_evaluacion / ruta_origen.name,
                self.raiz / ruta_origen.name
            ]
            for p in posibles:
                if p.exists():
                    ruta_origen = p
                    break

        if not ruta_origen.exists():
            return {
                "exito": False,
                "error": f"No se encontró el archivo '{archivo_nombre_o_ruta}' para organizar."
            }

        carpeta_destino = self.carpeta_evaluacion / nombre_carpeta
        carpeta_destino.mkdir(parents=True, exist_ok=True)
        destino_final = carpeta_destino / ruta_origen.name

        shutil.move(str(ruta_origen), str(destino_final))

        # Reindexar el proyecto para reflejar la nueva estructura
        from indexador_academico import IndexadorAcademico
        indexador = IndexadorAcademico(raiz_proyecto=self.raiz)
        indexador.indexar_todo()

        # Actualizar manifest y catálogo
        self.actualizar_manifest()

        return {
            "exito": True,
            "archivo_original": ruta_origen.name,
            "carpeta_creada": str(carpeta_destino),
            "ruta_final": str(destino_final),
            "mensaje": f"Archivo '{ruta_origen.name}' movido exitosamente a la carpeta '{nombre_carpeta}'."
        }

    def actualizar_manifest(self):
        self.carpeta_storage.mkdir(parents=True, exist_ok=True)
        manifest = {}
        revision = self.verificar_proyecto()
        if revision["estado"] == "ARCHIVOS_DETECTADOS":
            for codigo, info in revision["materias"].items():
                for doc_str in info["documentos"]:
                    doc = Path(doc_str)
                    info_hash = calcular_hash_archivo(doc)
                    if info_hash:
                        try:
                            rel_path = str(doc.relative_to(self.raiz))
                        except Exception:
                            rel_path = str(doc)
                        manifest[rel_path] = info_hash

        with open(self.ruta_manifest, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        # Generar catálogo Markdown (en raíz y en 1 Evaluación)
        self.generar_catalogo_markdown()
        return manifest

if __name__ == "__main__":
    import sys
    gestor = AutoGestor()
    if len(sys.argv) > 2 and sys.argv[1] == "--organizar":
        archivo_arg = sys.argv[2]
        carpeta_arg = sys.argv[3] if len(sys.argv) > 3 else "Nueva Carpeta"
        resultado = gestor.organizar_archivo(archivo_arg, carpeta_arg)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    elif len(sys.argv) > 1 and sys.argv[1] == "--actualizar":
        manifest = gestor.actualizar_manifest()
        print("Manifest y catálogo actualizados exitosamente.")
    else:
        cambios = gestor.detectar_cambios_documentos()
        gestor.generar_catalogo_markdown(novedades=cambios.get("novedades_titulos", []))
        print(json.dumps(cambios, indent=2, ensure_ascii=False))
