#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Clasificador Pedagógico Inteligente con Auditoría LlamaIndex + LLM y Fallback Heurístico con Banderas.
Determina para cada documento o materia:
- Si admite KaTeX (cajetines, divisiones, matemáticas).
- Si admite Mermaid en Teoría.
- Si admite Mermaid en Ejercicios (o si queda prohibido y se sustituye por Tablas Posicionales).
- Mantiene el flag 'auditoria_llm_pendiente' para consistencia eventual si el LLM estuvo apagado.
"""

import os
import sys
import json
import re
import urllib.request
import urllib.error
from pathlib import Path

# Asegurar codificación utf-8 en Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Configuración del endpoint local de LM Studio
LM_STUDIO_MODELS_URL = "http://127.0.0.1:1234/v1/models"
LM_STUDIO_CHAT_URL = "http://127.0.0.1:1234/v1/chat/completions"

# Disyuntor (Circuit Breaker): Si LM Studio falla una vez, no reintentar en el mismo ciclo
_LLM_ACTIVO_CIRCUITO = None

def comprobar_llm_disponible(timeout_seg=0.8):
    """Verifica si el servidor de LM Studio está activo y respondiendo."""
    global _LLM_ACTIVO_CIRCUITO
    if _LLM_ACTIVO_CIRCUITO is False:
        return False
    try:
        req = urllib.request.Request(LM_STUDIO_MODELS_URL, headers={"User-Agent": "TutorAcademico/1.0"})
        with urllib.request.urlopen(req, timeout=timeout_seg) as resp:
            return resp.status == 200
    except Exception:
        _LLM_ACTIVO_CIRCUITO = False
        return False

def extraer_muestra_documento(ruta_doc, max_caracteres=2500):
    """Extrae una muestra significativa del documento para su auditoría pedagógica."""
    ruta = Path(ruta_doc)
    texto = ""
    try:
        sufijo = ruta.suffix.lower()
        if sufijo == ".pdf":
            import pypdf
            reader = pypdf.PdfReader(str(ruta))
            paginas = len(reader.pages)
            # Portada e índice
            if paginas > 0:
                texto += (reader.pages[0].extract_text() or "") + "\n"
            if paginas > 1:
                texto += (reader.pages[1].extract_text() or "") + "\n"
            # Muestra central (posibles ejercicios o desarrollo)
            if paginas > 3:
                texto += (reader.pages[paginas // 2].extract_text() or "") + "\n"
        elif sufijo == ".docx":
            import docx
            doc = docx.Document(str(ruta))
            parrafos = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
            texto = "\n".join(parrafos[:30])
        elif sufijo in (".html", ".htm"):
            from bs4 import BeautifulSoup
            with open(ruta, "r", encoding="utf-8", errors="replace") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
            texto = soup.get_text(separator="\n")[:max_caracteres]
        elif sufijo in (".txt", ".md"):
            with open(ruta, "r", encoding="utf-8", errors="replace") as f:
                texto = f.read(max_caracteres)
        elif sufijo == ".tex":
            with open(ruta, "r", encoding="utf-8", errors="replace") as f:
                raw_tex = f.read()
            # Eliminar comentarios LaTeX (% hasta fin de línea)
            sin_comentarios = re.sub(r'(?<!\\)%.*$', '', raw_tex, flags=re.MULTILINE)
            # Extraer títulos y secciones clave
            titulos = re.findall(r'\\(?:title|section|chapter|subsection)\{([^}]+)\}', sin_comentarios)
            texto = ("Títulos TeX: " + " | ".join(titulos) + "\n" if titulos else "") + sin_comentarios[:max_caracteres]
        elif sufijo in (".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".bmp"):
            # Metadatos del recurso visual y deducción semántica por nombre y cabecera
            partes_info = [f"[RECURSO_VISUAL] Formato: {sufijo.upper()} | Archivo: {ruta.name}"]
            try:
                from PIL import Image
                with Image.open(ruta) as im:
                    partes_info.append(f"Dimensiones: {im.width}x{im.height}px | Modo: {im.mode}")
            except Exception:
                try:
                    stat = ruta.stat()
                    partes_info.append(f"Tamaño: {stat.st_size} bytes")
                except Exception:
                    pass
            nombre_limpio = re.sub(r'[-_.]+', ' ', ruta.stem).strip()
            partes_info.append(f"Descripción/Nombre del recurso gráfico: {nombre_limpio}")
            texto = " | ".join(partes_info)
    except Exception:
        pass

    texto_limpio = re.sub(r'\s+', ' ', texto).strip()
    return texto_limpio[:max_caracteres]

def clasificar_por_heuristica(texto_muestra, nombre_archivo=""):
    """
    Escaneo heurístico de seguridad cuando el LLM y Jev están desconectados.
    Detecta de forma universal disciplinas: Exactas/Ingeniería, Salud, Derecho, Humanidades o Hobbies.
    """
    texto_eval = (nombre_archivo + " " + texto_muestra).lower()
    
    # Términos de intereses personales y hobbies
    if any(k in texto_eval for k in ["gato", "gatito", "felino", "mascota", "perro", "cultivo", "tomate", "jardin", "receta", "cocina", "videojuego"]):
        return {
            "area_academica": "INTERES_PERSONAL_Y_AFICIONES",
            "perfil": "SOLO_CONCEPTUAL",
            "ambito": "INTERES_PERSONAL",
            "admite_katex": False,
            "admite_mermaid_teoria": True,
            "admite_mermaid_ejercicios": False,
            "herramienta_ejercicios": "PREGUNTAS_REFLEXIVAS",
            "prohibicion_especifica": "Prohibido KaTeX y fórmulas matemáticas (temática de afición o interés personal).",
            "estado_clasificacion": "PROVISIONAL_HEURISTICO",
            "auditoria_llm_pendiente": True
        }

    # Términos de Ciencias de la Salud y Biomédicas
    if any(k in texto_eval for k in ["medicina", "anatomia", "fisiologia", "celular", "farmaco", "patologia", "clinica", "enfermeria", "tejido", "arteria", "neurona", "proteina", "adn", "arn"]):
        return {
            "area_academica": "CIENCIAS_SALUD_Y_BIOMEDICAS",
            "perfil": "BIOMEDICO_APLICADO",
            "ambito": "ACADEMICO_OFICIAL",
            "admite_katex": False,
            "admite_mermaid_teoria": True,
            "admite_mermaid_ejercicios": False,
            "herramienta_ejercicios": "METODO_SOCRATICO_Y_CASOS_PRACTICOS",
            "prohibicion_especifica": "Priorizar rigor terminológico médico y esquemas de procesos; evitar KaTeX innecesario.",
            "estado_clasificacion": "PROVISIONAL_HEURISTICO",
            "auditoria_llm_pendiente": True
        }

    # Términos de Ciencias Sociales y Jurídicas
    if any(k in texto_eval for k in ["derecho", "articulo", "codigo civil", "penal", "constitucion", "tribunal", "ley", "demanda", "jurisprudencia", "economia", "macroeconomia", "empresa", "tributario"]):
        return {
            "area_academica": "CIENCIAS_SOCIALES_Y_JURIDICAS",
            "perfil": "ANALISIS_DOCTRINAL_O_HUMANISTICO",
            "ambito": "ACADEMICO_OFICIAL",
            "admite_katex": False,
            "admite_mermaid_teoria": True,
            "admite_mermaid_ejercicios": False,
            "herramienta_ejercicios": "METODO_SOCRATICO_Y_CASOS_PRACTICOS",
            "prohibicion_especifica": "Prohibido KaTeX en teoría jurídica; usar análisis de casos y preguntas socráticas.",
            "estado_clasificacion": "PROVISIONAL_HEURISTICO",
            "auditoria_llm_pendiente": True
        }

    # Términos de Arte y Humanidades
    if any(k in texto_eval for k in ["filosofia", "etica", "moral", "kant", "platon", "aristoteles", "historia", "siglo", "revolucion", "literatura", "poesia", "novela", "linguistica"]):
        return {
            "area_academica": "ARTE_Y_HUMANIDADES",
            "perfil": "ANALISIS_DOCTRINAL_O_HUMANISTICO",
            "ambito": "ACADEMICO_OFICIAL",
            "admite_katex": False,
            "admite_mermaid_teoria": True,
            "admite_mermaid_ejercicios": False,
            "herramienta_ejercicios": "PREGUNTAS_REFLEXIVAS",
            "prohibicion_especifica": "Fomentar el debate socrático y la contextualización histórica/filosófica.",
            "estado_clasificacion": "PROVISIONAL_HEURISTICO",
            "auditoria_llm_pendiente": True
        }

    # Términos de Cálculo Puro, Matemáticas y Conversión Numérica
    es_numeracion = any(k in texto_eval for k in ["numeracion", "sistemas de numeración", "base 2", "base 16", "base 8", "hexadecimal", "octal", "polinómica", "descomposición polinómica", "complemento a dos", "derivada", "integral", "limite", "matriz", "algebra", "ecuacion"])
    tiene_operadores = bool(re.search(r'(\d+\s*[\+\-\*\/÷]\s*\d+|16\^\d|2\^\d|\bbase\s*10\b)', texto_eval))

    if es_numeracion or (tiene_operadores and "red" not in texto_eval[:200]):
        return {
            "area_academica": "CIENCIAS_EXACTAS_E_INGENIERIA",
            "perfil": "CALCULO_NUMERICO_Y_FORMAL",
            "ambito": "ACADEMICO_OFICIAL",
            "admite_katex": True,
            "admite_mermaid_teoria": True,
            "admite_mermaid_ejercicios": False,
            "herramienta_ejercicios": "TABLA_PONDERACION_Y_CAJETINES" if "base" in texto_eval or "numeracion" in texto_eval else "KATEX_Y_MATRICES_FORMALES",
            "prohibicion_especifica": "PROHIBIDO Mermaid en ejercicios de cálculo o conversión numérica (usar KaTeX riguroso).",
            "estado_clasificacion": "PROVISIONAL_HEURISTICO",
            "auditoria_llm_pendiente": True
        }

    # Términos de Redes, Telecomunicaciones y Topologías
    es_redes = any(k in texto_eval for k in ["redes", "topologia", "osi", "tcp/ip", "packet tracer", "router", "switch", "subred", "vlsm", "mascara", "direccion ip"])
    if es_redes:
        return {
            "area_academica": "CIENCIAS_EXACTAS_E_INGENIERIA",
            "perfil": "ESTRUCTURAL_SISTEMICO",
            "ambito": "ACADEMICO_OFICIAL",
            "admite_katex": True,  # Para cálculo de máscaras y hosts
            "admite_mermaid_teoria": True,
            "admite_mermaid_ejercicios": True, # Para topología de red resultante
            "herramienta_ejercicios": "HIBRIDO_KATEX_Y_MERMAID",
            "prohibicion_especifica": "Mermaid exclusivo para topologías de red y modelos OSI/TCP; KaTeX para cálculo de subredes.",
            "estado_clasificacion": "PROVISIONAL_HEURISTICO",
            "auditoria_llm_pendiente": True
        }

    # Términos de Bases de Datos o Programación
    es_datos_marcas = any(k in texto_eval for k in ["base de datos", "sql", "relacional", "entidad", "html", "css", "xml", "marcas", "javascript", "python", "java", "c++"])
    if es_datos_marcas:
        return {
            "area_academica": "CIENCIAS_EXACTAS_E_INGENIERIA",
            "perfil": "LOGICO_DESARROLLO",
            "ambito": "ACADEMICO_OFICIAL",
            "admite_katex": False,
            "admite_mermaid_teoria": True,
            "admite_mermaid_ejercicios": True, # Diagramas ER o árboles DOM
            "herramienta_ejercicios": "CODIGO_Y_DIAGRAMAS_ER",
            "prohibicion_especifica": "KaTeX matemático innecesario; usar código formateado y diagramas relacionales.",
            "estado_clasificacion": "PROVISIONAL_HEURISTICO",
            "auditoria_llm_pendiente": True
        }

    # Perfil Académico General por defecto
    return {
        "area_academica": "ACADEMICO_GENERAL",
        "perfil": "ACADEMICO_GENERAL",
        "ambito": "ACADEMICO_OFICIAL",
        "admite_katex": False,
        "admite_mermaid_teoria": True,
        "admite_mermaid_ejercicios": False,
        "herramienta_ejercicios": "PREGUNTAS_REFLEXIVAS",
        "prohibicion_especifica": "Evitar diagramas Mermaid superfluos; priorizar claridad pedagógica.",
        "estado_clasificacion": "PROVISIONAL_HEURISTICO",
        "auditoria_llm_pendiente": True
    }

def clasificar_con_llm(texto_muestra, nombre_archivo=""):
    """
    Consulta al LLM local de LM Studio para obtener una auditoría pedagógica formal
    en formato JSON estructurado.
    """
    prompt_sistema = (
        "Eres un Catedrático y Auditor Pedagógico de Sistemas Informáticos. "
        "Analiza el siguiente fragmento de documento educativo y determina sus capacidades didácticas exactas.\n"
        "Debes responder EXCLUSIVAMENTE un objeto JSON válido con estas claves exactas:\n"
        "{\n"
        '  "perfil": "CALCULO_NUMERICO" | "HIBRIDO_REDES" | "LOGICO_ESTRUCTURAL" | "SOLO_CONCEPTUAL" | "ACADEMICO_GENERAL",\n'
        '  "ambito": "ACADEMICO_OFICIAL" | "INTERES_PERSONAL",\n'
        '  "admite_katex": true | false,\n'
        '  "admite_mermaid_teoria": true | false,\n'
        '  "admite_mermaid_ejercicios": true | false,\n'
        '  "herramienta_ejercicios": "TABLA_PONDERACION_Y_CAJETINES" | "HIBRIDO_KATEX_Y_MERMAID_TOPOLOGIA" | "CODIGO_Y_DIAGRAMAS_ER" | "PREGUNTAS_REFLEXIVAS",\n'
        '  "prohibicion_especifica": "breve indicación de qué NO hacer en ejercicios"\n'
        "}\n"
        "Regla: Si trata de conversiones binarias o matemáticas, admite_mermaid_ejercicios DEBE ser false (usar TABLA_PONDERACION_Y_CAJETINES). "
        "Si trata de mascotas, admite_katex DEBE ser false."
    )

    payload = {
        "model": "google/gemma-4-12b-qat",
        "messages": [
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": f"Nombre archivo: {nombre_archivo}\nContenido:\n{texto_muestra[:1800]}"}
        ],
        "temperature": 0.0,
        "max_tokens": 400
    }

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            LM_STUDIO_CHAT_URL,
            data=data,
            headers={"Content-Type": "application/json", "User-Agent": "TutorAcademico/1.0"}
        )
        with urllib.request.urlopen(req, timeout=2.5) as resp:
            res_raw = resp.read().decode("utf-8")
            res_json = json.loads(res_raw)
            contenido = res_json["choices"][0]["message"]["content"].strip()
            
            # Extraer bloque JSON si el modelo incluyó texto extra
            match = re.search(r'\{.*\}', contenido, re.DOTALL)
            if match:
                clasificacion = json.loads(match.group(0))
                clasificacion["estado_clasificacion"] = "CONFIRMADO_LLM"
                clasificacion["auditoria_llm_pendiente"] = False
                return clasificacion
    except Exception as e:
        global _LLM_ACTIVO_CIRCUITO
        _LLM_ACTIVO_CIRCUITO = False

# Importar conector resiliente de Jev
try:
    from conector_jev import ClienteJevResiliente
except ImportError:
    try:
        from motor.conector_jev import ClienteJevResiliente
    except ImportError:
        ClienteJevResiliente = None

_CLIENTE_JEV = None
def obtener_cliente_jev():
    global _CLIENTE_JEV
    if _CLIENTE_JEV is None and ClienteJevResiliente is not None:
        try:
            _CLIENTE_JEV = ClienteJevResiliente()
        except Exception:
            _CLIENTE_JEV = False
    return _CLIENTE_JEV if _CLIENTE_JEV is not False else None

EXTENSIONES_IMAGEN = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".bmp"}

def clasificar_recurso_visual_con_jev(texto_muestra, nombre_archivo=""):
    """
    Nivel 1 (Visión y Gráficas): Triangulación semántica ultrarrápida con Jev
    para identificar tipo de gráfico y pauta de interpretación pedagógica para el tutor.
    """
    cliente = obtener_cliente_jev()
    if not cliente:
        return None

    state = f"Recurso gráfico / imagen: {nombre_archivo}\nMetadatos y contexto:\n{texto_muestra[:1200]}"
    questions = {
        "tipo_recurso_visual": {
            "type": "choice",
            "instructions": "¿Qué tipo de gráfica, esquema o recurso visual representa este archivo?",
            "criteria": {
                "GRAFICA_ANALITICA_O_DATOS": "Gráfica cartesiana X/Y, funciones matemáticas, curvas de datos, histogramas o barras",
                "DIAGRAMA_ARQUITECTURA_O_RED": "Topología de red, mapa de sistemas, diagrama de bloques, modelo OSI/TCP o infraestructura",
                "ESQUEMA_BIOMEDICO_O_ANATOMICO": "Esquema anatómico, ciclo celular, vía bioquímica o diagrama de proceso clínico",
                "FLUJOGRAMA_Y_PROCESOS": "Flujograma de decisiones, algoritmo, mapa conceptual o árbol de derivación",
                "FORMULA_O_TABLA_GRAFICA": "Fórmula matemática compleja manuscrita/escaneada o tabla gráfica posicional",
                "ILUSTRACION_O_FOTOGRAFIA": "Fotografía real, captura de pantalla de software o ilustración conceptual"
            }
        },
        "estrategia_interpretacion_pedagogica": {
            "type": "choice",
            "instructions": "¿Qué pauta didáctica debe seguir el tutor para interpretar y explicar este gráfico al estudiante?",
            "criteria": {
                "LECTURA_CUANTITATIVA_EJES_Y_TENDENCIAS": "Analizar variables en ejes X/Y, unidades, máximos/mínimos y conclusiones de tendencia",
                "ANALISIS_ESTRUCTURAL_Y_RUTAS": "Explicar nodos, interfaces, capas, protocolos y enlaces de transmisión",
                "PASO_A_PASO_DEL_PROCESO": "Guiar secuencialmente a través de las bifurcaciones y decisiones del diagrama de flujo",
                "TRANSCRIPCION_FORMAL": "Transcribir la fórmula o cálculo gráfico a sintaxis KaTeX rigurosa",
                "DESCRIPCION_CONCEPTUAL": "Explicar el concepto ilustrado de forma intuitiva vinculándolo a la teoría"
            }
        },
        "area_academica": {
            "type": "choice",
            "instructions": "¿A qué gran disciplina o área del conocimiento se adscribe este recurso visual?",
            "criteria": {
                "CIENCIAS_EXACTAS_E_INGENIERIA": "Matemáticas, física, computación, redes de datos, telecomunicaciones o electrónica",
                "CIENCIAS_SALUD_Y_BIOMEDICAS": "Medicina, enfermería, biología, anatomía, fisiología o farmacia",
                "CIENCIAS_SOCIALES_Y_JURIDICAS": "Derecho, legislación, economía, psicología, administración",
                "ARTE_Y_HUMANIDADES": "Filosofía, historia, literatura, arte o lingüística",
                "FORMACION_PROFESIONAL_Y_TECNICA": "Ciclos formativos, oficios técnicos, mantenimiento",
                "INTERES_PERSONAL_Y_AFICIONES": "Temas de ocio, mascotas, botánica, aficiones personales"
            }
        }
    }

    try:
        res = cliente.consultar_decision(state, questions)
        if not res.get("exito"):
            return None

        answers = res.get("datos", {}).get("answers", {})
        tipo_vis = answers.get("tipo_recurso_visual", {}).get("choice", "ILUSTRACION_O_FOTOGRAFIA")
        estrategia = answers.get("estrategia_interpretacion_pedagogica", {}).get("choice", "DESCRIPCION_CONCEPTUAL")
        area = answers.get("area_academica", {}).get("choice", "CIENCIAS_EXACTAS_E_INGENIERIA")

        es_personal = (area == "INTERES_PERSONAL_Y_AFICIONES")
        return {
            "es_recurso_visual": True,
            "tipo_recurso_visual": tipo_vis,
            "estrategia_interpretacion_pedagogica": estrategia,
            "area_academica": area,
            "perfil": "ESTRUCTURAL_SISTEMICO" if tipo_vis in ("DIAGRAMA_ARQUITECTURA_O_RED", "FLUJOGRAMA_Y_PROCESOS") else "SOLO_CONCEPTUAL",
            "ambito": "INTERES_PERSONAL" if es_personal else "ACADEMICO_OFICIAL",
            "admite_katex": (tipo_vis == "FORMULA_O_TABLA_GRAFICA"),
            "admite_mermaid_teoria": True,
            "admite_mermaid_ejercicios": False,
            "herramienta_ejercicios": "PREGUNTAS_REFLEXIVAS",
            "prohibicion_especifica": "Recurso gráfico indexado; usar la pauta de interpretación para guiar al alumno visualmente.",
            "estado_clasificacion": "CONFIRMADO_JEV_VISION",
            "auditoria_llm_pendiente": False,
            "latencia_ms": res.get("latencia_ms", 0)
        }
    except Exception:
        return None

def clasificar_con_jev(texto_muestra, nombre_archivo=""):
    """
    Nivel 1: Consulta ultrarrápida al motor de Sistema 1 (Jev vía OpenRouter).
    Universal multi-disciplinar (Exactas, Salud, Jurídicas, Humanidades, FP, Hobbies).
    """
    sufijo = Path(nombre_archivo).suffix.lower()
    if sufijo in EXTENSIONES_IMAGEN:
        res_vis = clasificar_recurso_visual_con_jev(texto_muestra, nombre_archivo)
        if res_vis:
            return res_vis

    cliente = obtener_cliente_jev()
    if not cliente:
        return None

    state = f"Nombre del archivo: {nombre_archivo}\nContenido de muestra:\n{texto_muestra[:1500]}"
    questions = {
        "area_academica": {
            "type": "choice",
            "instructions": "¿A qué gran disciplina o área del conocimiento se adscribe este documento?",
            "criteria": {
                "CIENCIAS_EXACTAS_E_INGENIERIA": "Matemáticas, física, computación, redes de datos, telecomunicaciones, electrónica o sistemas informáticos",
                "CIENCIAS_SALUD_Y_BIOMEDICAS": "Medicina, enfermería, biología, anatomía, fisiología o farmacología",
                "CIENCIAS_SOCIALES_Y_JURIDICAS": "Derecho, legislación, economía, psicología, sociología, administración y finanzas",
                "ARTE_Y_HUMANIDADES": "Filosofía, historia, literatura, arte, lingüística o idiomas",
                "FORMACION_PROFESIONAL_Y_TECNICA": "Ciclos formativos, oficios, prevención de riesgos, mantenimiento y competencias técnicas",
                "INTERES_PERSONAL_Y_AFICIONES": "Temas no lectivos, aficiones, mascotas, cultivo, cocina o vida personal"
            }
        },
        "perfil": {
            "type": "choice",
            "instructions": "¿Cuál es la naturaleza didáctica del documento?",
            "criteria": {
                "CALCULO_NUMERICO_Y_FORMAL": "Fórmulas matemáticas, cálculo, conversión de bases numéricas, operaciones binarias, subnetting o física",
                "ESTRUCTURAL_SISTEMICO": "Modelos de capas (OSI/TCP), topologías de red, arquitecturas de sistemas, flujogramas o esquemas organizativos",
                "LOGICO_DESARROLLO": "Bases de datos relacionales, SQL, lenguajes de marcas (HTML/CSS/XML) o código de programación",
                "ANALISIS_DOCTRINAL_O_HUMANISTICO": "Leyes, artículos legales, historia, doctrina jurídica, análisis conceptual o filosófico",
                "BIOMEDICO_APLICADO": "Procesos patológicos, anatomía, casos clínicos y protocolos sanitarios",
                "SOLO_CONCEPTUAL": "Lecturas divulgativas o teóricas sin cálculos, fórmulas ni código",
                "ACADEMICO_GENERAL": "Temario académico estándar"
            }
        },
        "herramienta_ejercicios": {
            "type": "choice",
            "instructions": "¿Qué formato pedagógico debe usar el tutor al plantear ejercicios?",
            "criteria": {
                "TABLA_PONDERACION_Y_CAJETINES": "Tablas de ponderación de potencias o cajetines de división (prohibido Mermaid)",
                "KATEX_Y_MATRICES_FORMALES": "Ecuaciones y deducciones formales con KaTeX",
                "HIBRIDO_KATEX_Y_MERMAID": "Diagramas Mermaid combinados con análisis de red o flujogramas",
                "METODO_SOCRATICO_Y_CASOS_PRACTICOS": "Casos prácticos de aplicación, preguntas socráticas y análisis crítico",
                "CODIGO_Y_DIAGRAMAS_ER": "Bloques de código estructurado y diagramas entidad-relación",
                "PREGUNTAS_REFLEXIVAS": "Preguntas abiertas y reflexivas"
            }
        }
    }

    try:
        res = cliente.consultar_decision(state, questions)
        if not res.get("exito"):
            return None

        answers = res.get("datos", {}).get("answers", {})
        area = answers.get("area_academica", {}).get("choice", "ACADEMICO_GENERAL")
        perfil = answers.get("perfil", {}).get("choice", "ACADEMICO_GENERAL")
        herramienta = answers.get("herramienta_ejercicios", {}).get("choice", "PREGUNTAS_REFLEXIVAS")

        es_personal = (area == "INTERES_PERSONAL_Y_AFICIONES")
        admite_katex = (perfil in ("CALCULO_NUMERICO_Y_FORMAL", "ESTRUCTURAL_SISTEMICO")) and not es_personal
        admite_mermaid_teoria = not es_personal
        admite_mermaid_ejercicios = (perfil in ("ESTRUCTURAL_SISTEMICO", "LOGICO_DESARROLLO")) and not es_personal

        prohibicion = "Evitar diagramas superfluos; priorizar claridad pedagógica."
        if perfil == "CALCULO_NUMERICO_Y_FORMAL":
            prohibicion = "PROHIBIDO Mermaid en ejercicios de conversión o cálculo numérico (usar Tabla Posicional, Cajetines o KaTeX formal)."
        elif perfil == "LOGICO_DESARROLLO":
            prohibicion = "KaTeX matemático innecesario; usar código formateado y diagramas relacionales."
        elif perfil in ("ANALISIS_DOCTRINAL_O_HUMANISTICO", "BIOMEDICO_APLICADO"):
            prohibicion = "Fórmulas matemáticas innecesarias; priorizar rigor conceptual, método socrático y análisis de casos."
        elif es_personal:
            prohibicion = "Documento de interés personal; prohibido evaluar como examen oficial."

        return {
            "area_academica": area,
            "perfil": perfil,
            "ambito": "INTERES_PERSONAL" if es_personal else "ACADEMICO_OFICIAL",
            "admite_katex": admite_katex,
            "admite_mermaid_teoria": admite_mermaid_teoria,
            "admite_mermaid_ejercicios": admite_mermaid_ejercicios,
            "herramienta_ejercicios": herramienta,
            "prohibicion_especifica": prohibicion,
            "estado_clasificacion": "CONFIRMADO_JEV",
            "auditoria_llm_pendiente": False,
            "latencia_ms": res.get("latencia_ms", 0)
        }
    except Exception:
        return None

def auditar_perfil_documento(ruta_doc, forzar_reintento_llm=False):
    """
    Función principal de auditoría pedagógica en 3 niveles:
    1. Nivel 1: Jev (System 1 - Inferencia ultrarrápida, tipada y con reintentos).
    2. Nivel 2: LM Studio local (si está activo y disponible).
    3. Nivel 3: Fallback Heurístico inmediato (0 ms, offline garantizado).
    """
    p = Path(ruta_doc)
    muestra = extraer_muestra_documento(p)
    sufijo = p.suffix.lower()
    
    # 1. Nivel 1: Jev
    res_jev = clasificar_con_jev(muestra, nombre_archivo=p.name)
    if res_jev:
        return res_jev
        
    # 2. Nivel 2: LM Studio local (solo si no es imagen)
    if sufijo not in EXTENSIONES_IMAGEN and comprobar_llm_disponible():
        res_llm = clasificar_con_llm(muestra, nombre_archivo=p.name)
        if res_llm:
            return res_llm
            
    # 3. Nivel 3: Fallback seguro heurístico
    if sufijo in EXTENSIONES_IMAGEN:
        es_red = any(k in p.name.lower() for k in ["red", "topolog", "osi", "tcp", "router", "switch"])
        return {
            "es_recurso_visual": True,
            "tipo_recurso_visual": "DIAGRAMA_ARQUITECTURA_O_RED" if es_red else "ILUSTRACION_O_FOTOGRAFIA",
            "estrategia_interpretacion_pedagogica": "ANALISIS_ESTRUCTURAL_Y_RUTAS" if es_red else "DESCRIPCION_CONCEPTUAL",
            "area_academica": "CIENCIAS_EXACTAS_E_INGENIERIA" if es_red else "ACADEMICO_GENERAL",
            "perfil": "ESTRUCTURAL_SISTEMICO" if es_red else "SOLO_CONCEPTUAL",
            "ambito": "ACADEMICO_OFICIAL",
            "admite_katex": False,
            "admite_mermaid_teoria": True,
            "admite_mermaid_ejercicios": False,
            "herramienta_ejercicios": "PREGUNTAS_REFLEXIVAS",
            "prohibicion_especifica": "Recurso gráfico; guiar al alumno en su observación e interpretación.",
            "estado_clasificacion": "PROVISIONAL_HEURISTICO",
            "auditoria_llm_pendiente": True
        }

    return clasificar_por_heuristica(muestra, nombre_archivo=p.name)

if __name__ == "__main__":
    print("[*] Comprobando disponibilidad de motores pedagógicos...")
    cliente_j = obtener_cliente_jev()
    print(f"    ├─ Jev Resiliente: {'ONLINE' if cliente_j else 'NO CONFIGURADO'}")
    online_lm = comprobar_llm_disponible()
    print(f"    └─ LM Studio Local: {'ONLINE' if online_lm else 'OFFLINE'}")
    
    if len(sys.argv) > 1:
        doc_test = sys.argv[1]
        print(f"[*] Auditando documento: {doc_test}")
        resultado = auditar_perfil_documento(doc_test)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
