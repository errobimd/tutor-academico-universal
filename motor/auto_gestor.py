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

# Importar clasificador pedagógico con fallback y bandera pendiente
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from clasificador_pedagogico import auditar_perfil_documento, comprobar_llm_disponible
except ImportError:
    try:
        from motor.clasificador_pedagogico import auditar_perfil_documento, comprobar_llm_disponible
    except ImportError:
        def auditar_perfil_documento(p):
            return {
                "perfil": "ACADEMICO_GENERAL",
                "admite_katex": False,
                "admite_mermaid_teoria": True,
                "admite_mermaid_ejercicios": False,
                "herramienta_ejercicios": "TEXTO_Y_ESQUEMAS",
                "prohibicion_especifica": "Priorizar claridad pedagógica.",
                "estado_clasificacion": "PROVISIONAL_HEURISTICO",
                "auditoria_llm_pendiente": True
            }
        def comprobar_llm_disponible():
            return False

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
    Lee las primeras líneas de la página 1 y 2 de un PDF o DOCX para inferir
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
                if len(texto_inicio.strip()) < 150 and len(reader.pages) > 1:
                    p1 = reader.pages[1].extract_text() or ""
                    texto_inicio += "\n" + p1
        elif ruta.suffix.lower() == ".docx":
            import docx
            doc = docx.Document(str(ruta))
            parrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            texto_inicio = "\n".join(parrafos[:8])
        elif ruta.suffix.lower() in (".md", ".txt", ".html"):
            with open(ruta, "r", encoding="utf-8", errors="ignore") as f:
                texto_inicio = f.read(2000)
    except Exception:
        pass

    if not texto_inicio:
        return re.sub(r'[-_.]+', ' ', ruta.stem).strip()

    lineas = [l.strip() for l in texto_inicio.split("\n") if len(l.strip()) > 3]
    patron_ruido = r'^(página|page|\d+guía|\d+|http|www|versión|octubre|noviembre|diciembre|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|copyright|todos los derechos|isbn|depósito|deposito|autor|autores|profesor|docente)'
    lineas_validas = [l for l in lineas if not re.match(patron_ruido, l, re.I)]

    if lineas_validas:
        frase = []
        caracteres = 0
        for l in lineas_validas[:4]:
            frase.append(l)
            caracteres += len(l)
            if caracteres > 45:
                break
        titulo = " ".join(frase)
        titulo = re.sub(r'\s+', ' ', titulo).strip()
        return titulo[:90]

    return re.sub(r'[-_.]+', ' ', ruta.stem).strip()

def limpiar_para_nombre_carpeta(texto, max_len=30):
    """Convierte un texto o temática en un nombre de directorio limpio, representativo y amigable para Windows."""
    if not texto:
        return "Materia_Nueva"
    # Eliminar caracteres prohibidos en rutas de Windows / Unix y puntuación extraña
    limpio = re.sub(r'[\\/:*?"<>|#%&{}<>$!\'":@+`|=_~^.,;()\[\]]', ' ', texto)
    limpio = re.sub(r'\s+', ' ', limpio).strip()
    
    palabras_vacias = {
        'de', 'la', 'el', 'en', 'y', 'del', 'los', 'las', 'un', 'una', 'para', 'con', 'por', 
        'sobre', 'al', 'se', 'su', 'sus', 'como', 'manual', 'guia', 'apuntes', 'introduccion'
    }
    
    palabras = [p for p in limpio.split(' ') if len(p) > 1]
    significativas = [p for p in palabras if quitar_tildes(p).lower() not in palabras_vacias]
    
    if significativas:
        candidato = " ".join([p.capitalize() for p in significativas[:4]])
    elif palabras:
        candidato = " ".join([p.capitalize() for p in palabras[:3]])
    else:
        candidato = "Materia_Nueva"
        
    if len(candidato) > max_len:
        candidato = candidato[:max_len].rsplit(' ', 1)[0]
        
    return candidato.strip() or "Materia_Nueva"

def analizar_tematica_y_sugerir_carpeta(ruta_doc, materias_existentes=None):
    """
    Lee la portada y contenido inicial de un documento suelto para:
    1. Identificar su temática real y título representativo.
    2. Evaluar si pertenece a alguna materia/directorio ya existente.
    3. Si es una temática nueva, sugerir un nombre de directorio limpio.
    4. Formular el consejo organizativo directo para el estudiante.
    """
    ruta = Path(ruta_doc)
    texto_inicio = ""
    try:
        if ruta.suffix.lower() == ".pdf":
            import pypdf
            reader = pypdf.PdfReader(str(ruta))
            num_paginas = len(reader.pages)
            if num_paginas > 0:
                p0 = reader.pages[0].extract_text() or ""
                texto_inicio = p0
                if len(p0.strip()) < 150 and num_paginas > 1:
                    p1 = reader.pages[1].extract_text() or ""
                    texto_inicio += "\n" + p1
        elif ruta.suffix.lower() == ".docx":
            import docx
            doc = docx.Document(str(ruta))
            parrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            texto_inicio = "\n".join(parrafos[:10])
    except Exception:
        pass

    nombre_limpio_archivo = re.sub(r'[-_.]+', ' ', ruta.stem).strip()
    if not texto_inicio or len(texto_inicio.strip()) < 10:
        tematica = nombre_limpio_archivo
        sug_carpeta = limpiar_para_nombre_carpeta(nombre_limpio_archivo)
        pregunta = (
            f"He encontrado el archivo suelto '{ruta.name}'. Para mantener ordenada tu biblioteca, "
            f"te aconsejo guardarlo en un directorio propio. ¿Quieres que creemos la carpeta "
            f"`{sug_carpeta}` (o dime cómo prefieres que se llame) y lo traslademos allí?"
        )
        return {
            "tematica": tematica,
            "sugerencia_carpeta": sug_carpeta,
            "sugerencia_carpeta_nombre": sug_carpeta,
            "ambito": "GENERAL",
            "afinidad_encontrada": False,
            "carpeta_existente": None,
            "pregunta_estudiante": pregunta
        }

    lineas = [l.strip() for l in texto_inicio.split("\n") if len(l.strip()) > 3]
    patron_ruido = r'^(página|page|\d+guía|\d+|http|www|versión|octubre|noviembre|diciembre|enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|copyright|todos los derechos|isbn|depósito|deposito|autor|autores|profesor|docente)'
    lineas_filtradas = [l for l in lineas if not re.match(patron_ruido, l, re.I)]

    if lineas_filtradas:
        frase = []
        caracteres = 0
        for l in lineas_filtradas[:4]:
            if len(re.findall(r'[a-zA-ZáéíóúÁÉÍÓÚñÑ]', l)) < len(l) * 0.4:
                continue
            frase.append(l)
            caracteres += len(l)
            if caracteres > 45:
                break
        tematica = " ".join(frase)
        tematica = re.sub(r'\s+', ' ', tematica).strip()[:90]
    else:
        tematica = nombre_limpio_archivo

    # Evaluar ámbito: ¿Curricular Académico o Interés Personal?
    ambito = evaluar_ambito_documento(tematica, texto_inicio, materias_existentes)

    # Evaluar afinidad con alguna materia existente
    afinidad_materia = None
    if materias_existentes:
        tokens_doc = set(re.findall(r'\b[a-záéíóúñ]{4,}\b', (tematica + " " + texto_inicio[:600]).lower()))
        mejor_coincidencia = 0
        
        for cod, mat in materias_existentes.items():
            if mat.get("es_archivo_suelto"):
                continue
            nombre_mat = mat.get("nombre", "")
            tokens_mat = set(re.findall(r'\b[a-záéíóúñ]{4,}\b', nombre_mat.lower()))
            comunes = tokens_doc.intersection(tokens_mat)
            comunes = {c for c in comunes if c not in {'tema', 'general', 'curso', 'evaluacion', 'apuntes'}}
            if len(comunes) > mejor_coincidencia and len(comunes) >= 2:
                mejor_coincidencia = len(comunes)
                afinidad_materia = mat

    if afinidad_materia:
        nombre_carpeta_existente = Path(afinidad_materia["ruta"]).name
        pregunta = (
            f"He encontrado el archivo suelto '{ruta.name}'. Tras analizar su contenido, "
            f"he identificado que trata sobre '{tematica}', lo cual se relaciona directamente con tu asignatura "
            f"'{afinidad_materia['nombre']}'. A modo de organización de tu biblioteca, "
            f"¿quieres que lo guardemos en la carpeta existente `{nombre_carpeta_existente}` para tener todos tus apuntes agrupados?"
        )
        return {
            "tematica": tematica,
            "sugerencia_carpeta": nombre_carpeta_existente,
            "sugerencia_carpeta_nombre": nombre_carpeta_existente,
            "ambito": "ACADEMICO",
            "afinidad_encontrada": True,
            "carpeta_existente": nombre_carpeta_existente,
            "pregunta_estudiante": pregunta
        }
    elif ambito == "INTERES_PERSONAL":
        sug_nombre = limpiar_para_nombre_carpeta(tematica)
        sug_relativa = f"Intereses Personales/{sug_nombre}"
        pregunta = (
            f"He encontrado el archivo suelto '{ruta.name}'. Tras analizar su portada y contenido, "
            f"he identificado que trata sobre '{tematica}'. Veo que es un tema de interés personal que "
            f"no entra en tus asignaturas oficiales de clase (Redes, Sistemas, Bases de Datos...). "
            f"Ya que disfrutas aprendiendo sobre todo tipo de temas con tu tutor, para mantener limpio tu temario académico "
            f"y no mezclarlo con tus materias de examen, te aconsejo archivarlo en su propia sección. "
            f"¿Deseas que creemos la carpeta `{sug_relativa}` (o dime cómo prefieres llamarla) para guardarlo y ordenar tus temas?"
        )
        return {
            "tematica": tematica,
            "sugerencia_carpeta": sug_relativa,
            "sugerencia_carpeta_nombre": sug_nombre,
            "ambito": "INTERES_PERSONAL",
            "afinidad_encontrada": False,
            "carpeta_existente": None,
            "pregunta_estudiante": pregunta
        }
    else:
        sug_nombre = limpiar_para_nombre_carpeta(tematica)
        sug_relativa = f"1 Evaluación/{sug_nombre}"
        pregunta = (
            f"He encontrado el archivo suelto '{ruta.name}'. Tras analizar su portada y contenido, "
            f"he identificado que trata sobre '{tematica}', perteneciente a tu ámbito de estudio. "
            f"Para mantener ordenada tu biblioteca, te aconsejo archivarlo en su propio directorio. "
            f"¿Deseas que creemos la carpeta `{sug_relativa}` (o dime cómo prefieres llamarla) para guardarlo y ordenar tus temas?"
        )
        return {
            "tematica": tematica,
            "sugerencia_carpeta": sug_relativa,
            "sugerencia_carpeta_nombre": sug_nombre,
            "ambito": "ACADEMICO",
            "afinidad_encontrada": False,
            "carpeta_existente": None,
            "pregunta_estudiante": pregunta
        }

def evaluar_ambito_documento(tematica, texto_inicio, materias_existentes=None):
    """
    Determina si un documento pertenece al ámbito académico formal (currículo de clase)
    o a un ámbito extracurricular / interés personal (mascotas, aficiones, botánica, etc.).
    """
    tokens_academicos = {
        'redes', 'datos', 'base', 'bases', 'sistemas', 'operativos', 'software', 'hardware', 
        'programacion', 'marcas', 'html', 'css', 'digitalizacion', 'protocolo', 'ip', 'tcp', 
        'router', 'switch', 'sql', 'servidor', 'computador', 'ordenador', 'informatica', 
        'evaluacion', 'tarea', 'actividad', 'ejercicio', 'practica', 'examen', 'packet', 'tracer',
        'cuestionario', 'competencias', 'digitales', 'implantacion', 'administracion'
    }
    
    if materias_existentes:
        for mat in materias_existentes.values():
            if not mat.get("es_archivo_suelto") and not mat.get("es_interes_personal"):
                tokens_academicos.update(re.findall(r'\b[a-záéíóúñ]{4,}\b', mat.get("nombre", "").lower()))
                
    texto_eval = (tematica + " " + (texto_inicio or "")[:1200]).lower()
    tokens_doc = set(re.findall(r'\b[a-záéíóúñ]{4,}\b', texto_eval))
    
    terminos_personales = {
        'gato', 'gatito', 'gatitos', 'felino', 'felinos', 'perro', 'perros', 'cachorro', 'canino', 
        'mascota', 'mascotas', 'veterinaria', 'cultivo', 'tomate', 'huerto', 'jardin', 'plantas', 
        'botanica', 'cocina', 'receta', 'alimentacion', 'nutricion', 'guitarra', 'musica', 
        'deporte', 'entrenamiento', 'aficion', 'hobby', 'videojuego', 'horticultura', 'animales'
    }
    
    coincidencias_personales = tokens_doc.intersection(terminos_personales)
    coincidencias_academicas = tokens_doc.intersection(tokens_academicos)
    
    # Si detecta términos marcadamente personales y baja relación con el temario académico
    if coincidencias_personales and len(coincidencias_academicas) <= 1:
        return "INTERES_PERSONAL"
        
    # Si tiene relación clara con materias de clase
    if len(coincidencias_academicas) >= 2:
        return "ACADEMICO"
        
    # Si no tiene coincidencias con el curso oficial
    if len(coincidencias_academicas) == 0:
        return "INTERES_PERSONAL"
        
    return "ACADEMICO"



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
        elif len(sys.argv) > 1 and not sys.argv[1].startswith("--") and Path(sys.argv[1]).exists():
            self.raiz = Path(sys.argv[1]).resolve()
        else:
            # Detección inteligente ascendente de la raíz del proyecto
            aqui = Path(__file__).resolve()
            partes = aqui.parts
            if ".agents" in partes:
                idx = partes.index(".agents")
                self.raiz = Path(*partes[:idx])
            else:
                candidato = aqui.parent
                raiz_encontrada = None
                while candidato.parent != candidato:
                    if (candidato / ".agents").exists() and candidato.name != ".agents":
                        raiz_encontrada = candidato
                        break
                    if (candidato / "Obsidian").exists() and candidato.name != "Obsidian":
                        raiz_encontrada = candidato
                        break
                    if (candidato / "1 Evaluación").exists() and candidato.name != "1 Evaluación":
                        raiz_encontrada = candidato
                        break
                    candidato = candidato.parent
                
                if raiz_encontrada:
                    self.raiz = raiz_encontrada
                else:
                    cwd = Path.cwd().resolve()
                    if (cwd / ".agents").exists() or (cwd / "Obsidian").exists() or (cwd / "1 Evaluación").exists() or (cwd / "TEMARIO_ACTIVO.md").exists():
                        self.raiz = cwd
                    else:
                        self.raiz = aqui.parent.parent.parent.parent
            
        self.carpeta_evaluacion = self.raiz / "1 Evaluación"
        self.carpeta_storage = Path(__file__).resolve().parent / "storage_index"
        self.ruta_manifest = self.carpeta_storage / "manifest.json"
        self.ruta_catalogo_md = self.raiz / "TEMARIO_ACTIVO.md"

    def evaluar_ambito_documento(self, ruta_doc):
        """Evalúa si un documento es del ámbito académico o de interés personal."""
        info = analizar_tematica_y_sugerir_carpeta(ruta_doc)
        return info.get("ambito", "ACADEMICO"), info.get("tematica", ""), info.get("sugerencia_carpeta", "")

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
            carpetas_a_escanear.extend([
                d for d in self.carpeta_evaluacion.iterdir() 
                if d.is_dir() and not d.name.startswith('.') and d.name not in carpetas_ignoradas
            ])

        # 2. Explorar subcarpetas en 'Intereses Personales' (si existe)
        carpeta_intereses = self.raiz / "Intereses Personales"
        if carpeta_intereses.exists() and carpeta_intereses.is_dir():
            carpetas_a_escanear.extend([
                d for d in carpeta_intereses.iterdir() 
                if d.is_dir() and not d.name.startswith('.') and d.name not in carpetas_ignoradas
            ])

        # 3. Explorar subcarpetas en la raíz del proyecto
        for item in self.raiz.iterdir():
            if item.is_dir() and not item.name.startswith('.') and item.name not in carpetas_ignoradas and item.name not in ("1 Evaluación", "Intereses Personales"):
                if "obsidian" in item.name.lower():
                    # Si es bóveda o carpeta Obsidian, explorar sus subcarpetas organizadas
                    subcarpetas_obs = [s for s in item.iterdir() if s.is_dir() and not s.name.startswith('.')]
                    for sub_obs in subcarpetas_obs:
                        sub_niveles = [sn for sn in sub_obs.iterdir() if sn.is_dir() and not sn.name.startswith('.')]
                        if sub_niveles:
                            carpetas_a_escanear.extend(sub_niveles)
                        else:
                            carpetas_a_escanear.append(sub_obs)
                    if not subcarpetas_obs:
                        carpetas_a_escanear.append(item)
                else:
                    carpetas_a_escanear.append(item)

        ARCHIVOS_SISTEMA_IGNORADOS = {
            "requirements.txt", "system_prompt_tutor.txt", "temario_activo.md",
            "ejemplo_operaciones_latex.html", "ejemplo_operaciones_latex.md", "verificar_entorno.py",
            "readme.md", "skill.md", "instrucciones_tutor_bionic.md", "mapa_de_scripts_y_herramientas.md",
            "memoria_sesion_y_conversacion.md", "prompt_activacion_bionic.md", "revision_general_y_estado_proyecto.md"
        }

        # 4. Procesar cada carpeta
        for carp in carpetas_a_escanear:
            docs = (
                list(carp.rglob("*.pdf")) + 
                list(carp.rglob("*.docx")) + 
                list(carp.rglob("*.html")) + 
                list(carp.rglob("*.txt")) +
                list(carp.rglob("*.md"))
            )
            # Descartar cualquier archivo que esté dentro de carpetas ocultas (.agents, .venv, etc.) o de sistema
            docs = [
                f for f in docs 
                if not any(part.startswith('.') for part in f.parts) and
                f.name.lower() not in ARCHIVOS_SISTEMA_IGNORADOS
            ]
            if docs:
                codigo = generar_codigo_materia(carp.name)
                nombre_base = limpiar_nombre_materia(carp.name)

                es_personal = (
                    "interes" in str(carp).lower() or 
                    carp.parent.name == "Intereses Personales" or
                    any(k in carp.name.lower() for k in ["gato", "gatito", "felino", "mascota", "tomate", "cultivo", "horticultura", "cocina"])
                )

                nombre_descriptivo = nombre_base
                if any(k in nombre_base.lower() for k in ["tema general", "varios", "apuntes", "documentos", "general", "otros"]):
                    tema_portada = extraer_titulo_portada(docs[0])
                    nombre_descriptivo = f"{nombre_base.upper()}: {tema_portada}"
                    if any(k in tema_portada.lower() for k in ["tomate", "cultivo", "gato", "gatito"]):
                        es_personal = True

                if codigo in materias_detectadas and materias_detectadas[codigo]["ruta"] != str(carp):
                    codigo = f"{codigo}_{len(materias_detectadas)}"

                perfil_materia = auditar_perfil_documento(docs[0]) if docs else {}
                es_personal_final = es_personal or (perfil_materia.get("ambito") == "INTERES_PERSONAL")

                materias_detectadas[codigo] = {
                    "nombre": nombre_descriptivo,
                    "ruta": str(carp),
                    "total_docs": len(docs),
                    "es_archivo_suelto": False,
                    "es_interes_personal": es_personal_final,
                    "perfil_didactico": perfil_materia,
                    "documentos": [str(d) for d in docs]
                }
                total_docs += len(docs)

        # 5. Procesar ARCHIVOS SUELTOS (PDFs, DOCXs, HTMLs, TXTs o MDs sin carpeta)
        rutas_sueltas = []
        for ext in ("*.pdf", "*.docx", "*.html", "*.txt", "*.md"):
            if self.carpeta_evaluacion.exists():
                rutas_sueltas.extend(self.carpeta_evaluacion.glob(ext))
            if carpeta_intereses.exists():
                rutas_sueltas.extend(carpeta_intereses.glob(ext))
            rutas_sueltas.extend(self.raiz.glob(ext))

        rutas_sueltas_unicas = []
        vistas = set()
        for r in rutas_sueltas:
            res = str(r.resolve())
            if res not in vistas:
                vistas.add(res)
                rutas_sueltas_unicas.append(r)

        for doc_suelto in rutas_sueltas_unicas:
            # Ignorar archivos en carpetas de sistema, temporales u ocultos
            if (
                doc_suelto.name.startswith("~$") or 
                doc_suelto.name.startswith(".") or 
                "temp" in doc_suelto.name.lower() or 
                doc_suelto.name.lower() in ARCHIVOS_SISTEMA_IGNORADOS or
                any(part.startswith('.') for part in doc_suelto.parts)
            ):
                continue
            
            analisis = analizar_tematica_y_sugerir_carpeta(doc_suelto, materias_detectadas)
            cod_suelto = f"DOC_{generar_codigo_materia(doc_suelto.stem)}"
            if cod_suelto in materias_detectadas:
                cod_suelto = f"{cod_suelto}_{len(materias_detectadas)}"

            perfil_suelto = auditar_perfil_documento(doc_suelto)
            es_pers_suelto = (analisis.get("ambito") == "INTERES_PERSONAL") or (perfil_suelto.get("ambito") == "INTERES_PERSONAL")

            materias_detectadas[cod_suelto] = {
                "nombre": f"[Documento Suelto] {analisis['tematica']} ({doc_suelto.name})",
                "titulo_portada": analisis['tematica'],
                "nombre_archivo": doc_suelto.name,
                "ruta": str(doc_suelto),
                "total_docs": 1,
                "es_archivo_suelto": True,
                "es_interes_personal": es_pers_suelto,
                "ambito": analisis.get("ambito", "ACADEMICO"),
                "perfil_didactico": perfil_suelto,
                "sugerencia_carpeta": analisis['sugerencia_carpeta'],
                "sugerencia_carpeta_nombre": analisis.get('sugerencia_carpeta_nombre', analisis['sugerencia_carpeta']),
                "afinidad_encontrada": analisis['afinidad_encontrada'],
                "carpeta_existente": analisis['carpeta_existente'],
                "pregunta_estudiante": analisis['pregunta_estudiante'],
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
        modificados_oficiales = []
        nuevos_oficiales = []
        sueltos_detectados = []
        novedades_titulos = []

        for codigo, info in revision["materias"].items():
            es_suelto = info.get("es_archivo_suelto", False)
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
                    
                    if prev is not None:
                        # Archivo ya conocido pero con contenido modificado
                        if not es_suelto:
                            modificados_oficiales.append((doc.name, info['nombre']))
                            novedades_titulos.append(f"[Modificado] {info['nombre']} -> {doc.name}")
                        else:
                            sueltos_detectados.append(doc.name)
                    else:
                        # Archivo completamente nuevo
                        if not es_suelto:
                            nuevos_oficiales.append((doc.name, info['nombre']))
                            novedades_titulos.append(f"[Nuevo] {info['nombre']} -> {doc.name} ({titulo})")
                        else:
                            sueltos_detectados.append(doc.name)

        necesita_indexar = len(archivos_nuevos_o_modificados) > 0

        mensaje_alumno = None
        if es_primera_vez and necesita_indexar:
            total_docs = len(archivos_nuevos_o_modificados)
            segundos_est = max(10, int(total_docs * 0.6))
            mensaje_alumno = (
                f"¡Hola! Soy tu Tutor Académico 🎓.\n"
                f"He detectado tu biblioteca con {total_docs} documentos y esquemas de estudio.\n"
                f"Estoy analizando tus apuntes y estructurando las secciones clave. "
                f"Me tomará aproximadamente {segundos_est} segundos.\n"
                f"Tómate un café o un refresco ☕🥤 mientras preparo tu aula de estudio..."
            )
        elif necesita_indexar:
            mensajes_partes = []
            if modificados_oficiales:
                nombres_mods = ", ".join([f"'{m[0]}' ({m[1]})" for m in modificados_oficiales[:3]])
                mensajes_partes.append(f"📝 He detectado modificaciones en {nombres_mods}. Se han reindexado para actualizar el contexto de estudio.")
            if nuevos_oficiales:
                nombres_nuevos = ", ".join([f"'{n[0]}' ({n[1]})" for n in nuevos_oficiales[:3]])
                mensajes_partes.append(f"📢 ¡Nuevos documentos añadidos a tus asignaturas: {nombres_nuevos}! Incorporados al temario.")
            if sueltos_detectados:
                nombres_s = ", ".join([f"'{s}'" for s in sueltos_detectados[:2]])
                mensajes_partes.append(f"📁 Se han encontrado archivos sueltos ({nombres_s}) pendientes de organizar.")
            mensaje_alumno = " ".join(mensajes_partes)

        return {
            "necesita_indexar": necesita_indexar,
            "es_primera_vez": es_primera_vez,
            "archivos_nuevos": [str(p) for p in archivos_nuevos_o_modificados],
            "modificados_oficiales": modificados_oficiales,
            "nuevos_oficiales": nuevos_oficiales,
            "sueltos_detectados": sueltos_detectados,
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
                    lineas.append(f"  * **Temática identificada:** \"{s.get('titulo_portada', s['nombre_archivo'])}\"")
                    lineas.append(f"  * **Directorio sugerido:** `{s.get('sugerencia_carpeta', 'Nueva_Carpeta')}`")
                    lineas.append(f"  * **Pregunta organizativa al estudiante:** \"{s.get('pregunta_estudiante', '')}\"")
                lineas.append("")

            # 1. Separar materias en Académicas y de Interés Personal
            academicas = [(cod, inf) for cod, inf in revision["materias"].items() if not inf.get("es_interes_personal") and not inf.get("es_archivo_suelto")]
            personales = [(cod, inf) for cod, inf in revision["materias"].items() if inf.get("es_interes_personal") and not inf.get("es_archivo_suelto")]
            
            emojis_acad = ["🗄️", "🌐", "🖥️", "📄", "🏭", "📊", "💡", "🔬"]
            emojis_pers = ["🐱", "🍅", "🌱", "🐾", "🎸", "🍳", "📚", "✨"]

            contador_global = 1
            if academicas:
                lineas.append("## 🎓 ASIGNATURAS OFICIALES (EVALUACIÓN ACADÉMICA):")
                for cod, info in academicas:
                    emoji = emojis_acad[(contador_global - 1) % len(emojis_acad)]
                    lineas.append(f"### [{contador_global}] {emoji} **{cod}:** {info['nombre']}")
                    lineas.append(f"- **Documentos ({info['total_docs']}):**")
                    for doc_path in info["documentos"][:5]:
                        nombre_archivo = Path(doc_path).name
                        lineas.append(f"  * `{nombre_archivo}`")
                    if info["total_docs"] > 5:
                        lineas.append(f"  * *(y {info['total_docs'] - 5} documentos adicionales)*")
                    
                    p_did = info.get("perfil_didactico", {})
                    if p_did:
                        estado_aud = p_did.get('estado_clasificacion', 'CONFIRMADO')
                        lineas.append(f"- **🎯 Perfil Didáctico:** `{p_did.get('perfil', 'GENERAL')}` [{estado_aud}]")
                        lineas.append(f"  * **Herramienta en Ejercicios:** {p_did.get('herramienta_ejercicios', 'Estándar')}")
                        lineas.append(f"  * **Regla Estricta:** {p_did.get('prohibicion_especifica', 'Ninguna')}")
                        if p_did.get("auditoria_llm_pendiente"):
                            lineas.append("  * ⏳ *(Bandera activa: Clasificación heurística provisional. Pendiente de refinamiento con LLM).*")
                    
                    lineas.append("")
                    contador_global += 1

            if personales:
                lineas.append("## 🌟 TUS TEMAS DE INTERÉS PERSONAL Y HOBBIES:")
                for cod, info in personales:
                    emoji = emojis_pers[(contador_global - 1) % len(emojis_pers)]
                    lineas.append(f"### [{contador_global}] {emoji} **{cod}:** {info['nombre']}")
                    lineas.append(f"- **Documentos ({info['total_docs']}):**")
                    for doc_path in info["documentos"][:5]:
                        nombre_archivo = Path(doc_path).name
                        lineas.append(f"  * `{nombre_archivo}`")
                    if info["total_docs"] > 5:
                        lineas.append(f"  * *(y {info['total_docs'] - 5} documentos adicionales)*")
                    
                    p_did = info.get("perfil_didactico", {})
                    if p_did:
                        estado_aud = p_did.get('estado_clasificacion', 'CONFIRMADO')
                        lineas.append(f"- **🎯 Perfil Didáctico:** `{p_did.get('perfil', 'GENERAL')}` [{estado_aud}]")
                        lineas.append(f"  * **Herramienta en Ejercicios:** {p_did.get('herramienta_ejercicios', 'Estándar')}")
                        lineas.append(f"  * **Regla Estricta:** {p_did.get('prohibicion_especifica', 'Ninguna')}")
                        if p_did.get("auditoria_llm_pendiente"):
                            lineas.append("  * ⏳ *(Bandera activa: Clasificación heurística provisional. Pendiente de refinamiento con LLM).*")
                    
                    lineas.append("")
                    contador_global += 1

            contenido = "\n".join(lineas)

        try:
            with open(self.ruta_catalogo_md, "w", encoding="utf-8") as f:
                f.write(contenido)
            # También guardar en 1 Evaluación para visibilidad directa en Bionic Studio si existe y no es la raíz
            if self.carpeta_evaluacion.exists() and self.carpeta_evaluacion.resolve() != self.raiz.resolve():
                with open(self.carpeta_evaluacion / "TEMARIO_ACTIVO.md", "w", encoding="utf-8") as f:
                    f.write(contenido)
        except Exception:
            pass

        return self.ruta_catalogo_md

    def organizar_archivo(self, archivo_nombre_o_ruta, nombre_carpeta):
        """
        Crea físicamente la carpeta (en 'Intereses Personales/' o '1 Evaluación/')
        y traslada el archivo suelto, reindexando y actualizando el catálogo automáticamente.
        """
        import shutil
        ruta_origen = Path(archivo_nombre_o_ruta)
        if not ruta_origen.is_absolute():
            # Buscar en 1 Evaluación, en Intereses Personales o en la raíz
            posibles = [
                self.carpeta_evaluacion / ruta_origen.name,
                self.raiz / "Intereses Personales" / ruta_origen.name,
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

        p_carpeta = Path(nombre_carpeta)
        if p_carpeta.is_absolute():
            carpeta_destino = p_carpeta
        elif p_carpeta.parts and p_carpeta.parts[0] in ("1 Evaluación", "Intereses Personales"):
            carpeta_destino = self.raiz / p_carpeta
        elif "interes" in str(nombre_carpeta).lower():
            carpeta_destino = self.raiz / "Intereses Personales" / p_carpeta.name
        else:
            nombre_carpeta_lower = str(nombre_carpeta).lower()
            es_personal = (
                (self.raiz / "Intereses Personales" / p_carpeta.name).exists() or
                any(k in nombre_carpeta_lower for k in ["gato", "gatito", "felino", "mascota", "tomate", "cultivo", "horticultura", "cocina"])
            )
            if es_personal:
                carpeta_destino = self.raiz / "Intereses Personales" / p_carpeta.name
            else:
                carpeta_destino = self.carpeta_evaluacion / p_carpeta.name

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
            "mensaje": f"Archivo '{ruta_origen.name}' movido exitosamente a '{carpeta_destino.relative_to(self.raiz)}'."
        }

    def actualizar_manifest(self):
        self.carpeta_storage.mkdir(parents=True, exist_ok=True)
        manifest = {}
        revision = self.verificar_proyecto()
        if revision["estado"] == "ARCHIVOS_DETECTADOS":
            for codigo, info in revision["materias"].items():
                p_did = info.get("perfil_didactico", {})
                for doc_str in info["documentos"]:
                    doc = Path(doc_str)
                    info_hash = calcular_hash_archivo(doc)
                    if info_hash:
                        try:
                            rel_path = str(doc.relative_to(self.raiz))
                        except Exception:
                            rel_path = str(doc)
                        info_hash["perfil_didactico"] = p_did
                        info_hash["auditoria_llm_pendiente"] = p_did.get("auditoria_llm_pendiente", False)
                        info_hash["estado_clasificacion"] = p_did.get("estado_clasificacion", "CONFIRMADO")
                        manifest[rel_path] = info_hash

        with open(self.ruta_manifest, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)

        # Generar catálogo Markdown (en raíz y en 1 Evaluación)
        self.generar_catalogo_markdown()
        return manifest

    def sincronizar_con_github(self):
        """
        Verifica silenciosamente si hay una nueva versión del Skill en GitHub
        con timeout rápido (2s). Si no hay internet, activa el modo offline
        sin bloquear al estudiante y garantizando la operatividad 100% local.
        """
        import urllib.request
        url_raw = "https://raw.githubusercontent.com/errobimd/tutor-academico-universal/main/skills/tutor-academico/SKILL.md"
        rutas_locales = [
            self.raiz / ".agents" / "skills" / "tutor-academico" / "SKILL.md",
            self.raiz / "1 Evaluación" / ".agents" / "skills" / "tutor-academico" / "SKILL.md"
        ]
        try:
            req = urllib.request.Request(url_raw, headers={"User-Agent": "TutorAcademicoAutoSync"})
            with urllib.request.urlopen(req, timeout=2) as res:
                if res.status == 200:
                    contenido_remoto = res.read().decode("utf-8")
                    actualizado = False
                    for ruta in rutas_locales:
                        if ruta.exists():
                            with open(ruta, "r", encoding="utf-8") as f:
                                contenido_local = f.read()
                            if contenido_local.strip() != contenido_remoto.strip():
                                with open(ruta, "w", encoding="utf-8") as f:
                                    f.write(contenido_remoto)
                                actualizado = True
                    return {
                        "exito": True, 
                        "offline": False,
                        "actualizado": actualizado,
                        "mensaje_alumno": "✨ Conectado a GitHub: Tu tutor cuenta con las últimas directivas actualizadas." if actualizado else None
                    }
        except Exception:
            # Captura limpia de fallo de red (sin internet o timeout rápido)
            return {
                "exito": True,
                "offline": True,
                "actualizado": False,
                "mensaje_alumno": "🌐 Estás trabajando sin conexión a Internet, pero no te preocupes: todo tu temario, esquemas y lecciones están 100% operativos en tu ordenador local."
            }
        return {"exito": True, "offline": False, "actualizado": False, "mensaje_alumno": None}

if __name__ == "__main__":
    import sys
    # Extraer posible raíz pasada como argumento posicional (no flag)
    raiz_arg = None
    args_limpios = []
    for a in sys.argv[1:]:
        if not a.startswith("--") and Path(a).exists() and raiz_arg is None:
            raiz_arg = a
        else:
            args_limpios.append(a)

    gestor = AutoGestor(raiz_proyecto=raiz_arg)
    if len(args_limpios) > 1 and args_limpios[0] == "--organizar":
        archivo_arg = args_limpios[1]
        carpeta_arg = args_limpios[2] if len(args_limpios) > 2 else "Nueva Carpeta"
        resultado = gestor.organizar_archivo(archivo_arg, carpeta_arg)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    elif len(args_limpios) > 0 and args_limpios[0] == "--actualizar":
        manifest = gestor.actualizar_manifest()
        print("Manifest y catálogo actualizados exitosamente.")
    else:
        cambios = gestor.detectar_cambios_documentos()
        gestor.generar_catalogo_markdown(novedades=cambios.get("novedades_titulos", []))
        print(json.dumps(cambios, indent=2, ensure_ascii=False))
