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
    except Exception:
        pass

    texto_limpio = re.sub(r'\s+', ' ', texto).strip()
    return texto_limpio[:max_caracteres]

def clasificar_por_heuristica(texto_muestra, nombre_archivo=""):
    """
    Escaneo heurístico de seguridad cuando el LLM está desconectado.
    Busca operadores matemáticos, términos de red, bases de datos o aficiones.
    """
    texto_eval = (nombre_archivo + " " + texto_muestra).lower()
    
    # Términos de intereses personales
    if any(k in texto_eval for k in ["gato", "gatito", "felino", "mascota", "perro", "cultivo", "tomate", "jardin", "receta", "cocina"]):
        return {
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

    # Términos de Sistemas de Numeración / Cálculo Puro
    es_numeracion = any(k in texto_eval for k in ["numeracion", "sistemas de numeración", "base 2", "base 16", "base 8", "hexadecimal", "octal", "polinómica", "descomposición polinómica", "complemento a dos"])
    tiene_operadores = bool(re.search(r'(\d+\s*[\+\-\*\/÷]\s*\d+|16\^\d|2\^\d|\bbase\s*10\b)', texto_eval))

    if es_numeracion or (tiene_operadores and "red" not in texto_eval[:200]):
        return {
            "perfil": "CALCULO_NUMERICO",
            "ambito": "ACADEMICO_OFICIAL",
            "admite_katex": True,
            "admite_mermaid_teoria": True,
            "admite_mermaid_ejercicios": False,
            "herramienta_ejercicios": "TABLA_PONDERACION_Y_CAJETINES",
            "prohibicion_especifica": "PROHIBIDO Mermaid en ejercicios de conversión numérica (usar Tabla Posicional o Cajetines).",
            "estado_clasificacion": "PROVISIONAL_HEURISTICO",
            "auditoria_llm_pendiente": True
        }

    # Términos de Redes y Topologías
    es_redes = any(k in texto_eval for k in ["redes", "topologia", "osi", "tcp/ip", "packet tracer", "router", "switch", "subred", "vlsm", "mascara", "direccion ip"])
    if es_redes:
        return {
            "perfil": "HIBRIDO_REDES",
            "ambito": "ACADEMICO_OFICIAL",
            "admite_katex": True,  # Para cálculo de máscaras y hosts
            "admite_mermaid_teoria": True,
            "admite_mermaid_ejercicios": True, # Para topología de red resultante
            "herramienta_ejercicios": "HIBRIDO_KATEX_Y_MERMAID_TOPOLOGIA",
            "prohibicion_especifica": "Mermaid exclusivo para topologías de red y modelos OSI/TCP; KaTeX para cálculo de subredes.",
            "estado_clasificacion": "PROVISIONAL_HEURISTICO",
            "auditoria_llm_pendiente": True
        }

    # Términos de Bases de Datos o Lenguajes de Marcas
    es_datos_marcas = any(k in texto_eval for k in ["base de datos", "sql", "relacional", "entidad", "html", "css", "xml", "marcas"])
    if es_datos_marcas:
        return {
            "perfil": "LOGICO_ESTRUCTURAL",
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
        "perfil": "ACADEMICO_GENERAL",
        "ambito": "ACADEMICO_OFICIAL",
        "admite_katex": False,
        "admite_mermaid_teoria": True,
        "admite_mermaid_ejercicios": False,
        "herramienta_ejercicios": "TEXTO_Y_ESQUEMAS",
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
        print(f"    [!] LM Studio no disponible ({e}). Activando fallback heurístico seguro e inmediato.", flush=True)
        pass

    # Si falló la llamada o el parseo, recurrir a la heurística
    return None

def auditar_perfil_documento(ruta_doc, forzar_reintento_llm=False):
    """
    Función principal de auditoría:
    1. Extrae muestra del documento.
    2. Si LM Studio está disponible, clasifica con el LLM.
    3. Si no, o si falla, clasifica por heurística con la bandera 'auditoria_llm_pendiente = True'.
    """
    p = Path(ruta_doc)
    muestra = extraer_muestra_documento(p)
    
    if comprobar_llm_disponible():
        res_llm = clasificar_con_llm(muestra, nombre_archivo=p.name)
        if res_llm:
            return res_llm
            
    # Fallback seguro
    return clasificar_por_heuristica(muestra, nombre_archivo=p.name)

if __name__ == "__main__":
    print("[*] Comprobando disponibilidad de LM Studio...")
    online = comprobar_llm_disponible()
    print(f"    └─ LM Studio Online: {online}")
    
    if len(sys.argv) > 1:
        doc_test = sys.argv[1]
        print(f"[*] Auditando documento: {doc_test}")
        resultado = auditar_perfil_documento(doc_test)
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
