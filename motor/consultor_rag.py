#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Motor de Consulta RAG Universal y Modular.
Carga el índice de cualquier materia (Biología, Nutrición Animal, Redes, etc.)
y entrega directivas adaptadas a los 4 sub-roles pedagógicos.
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path

# Asegurar codificación UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from indexador_academico import VectorizadorLocal

def similitud_coseno(v1, v2):
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    return sum(a * b for a, b in zip(v1, v2))

class ConsultorRAG:
    def __init__(self, carpeta_storage=None):
        if carpeta_storage:
            self.carpeta_storage = Path(carpeta_storage).resolve()
        else:
            self.carpeta_storage = Path(__file__).resolve().parent / "storage_index"
        self.vectorizador = VectorizadorLocal(dim=768)
        self.indice_en_memoria = None
        self.materia_cargada = None

    def listar_materias_disponibles(self):
        """Devuelve la lista de materias indexadas en el almacenamiento."""
        materias = []
        if not self.carpeta_storage.exists():
            return materias
        for sub in self.carpeta_storage.iterdir():
            if sub.is_dir() and (sub / "index.json").exists():
                try:
                    with open(sub / "index.json", "r", encoding="utf-8") as f:
                        data = json.load(f)
                        materias.append({
                            "codigo": sub.name,
                            "nombre": data.get("nombre", sub.name),
                            "total_fragmentos": data.get("total_nodos", 0),
                            "temas": data.get("temas", [])
                        })
                except Exception:
                    materias.append({"codigo": sub.name, "nombre": sub.name})
        return materias

    def cargar_materia(self, codigo_materia):
        codigo = codigo_materia.strip()
        if self.materia_cargada == codigo and self.indice_en_memoria is not None:
            return True, f"Materia {codigo} ya en memoria."

        # 1. Búsqueda exacta
        ruta_indice = self.carpeta_storage / codigo / "index.json"
        
        # 2. Búsqueda insensible o normalizada
        if not ruta_indice.exists() and self.carpeta_storage.exists():
            cod_norm = re.sub(r'[^a-zA-Z0-9]', '', codigo.upper())
            for sub in self.carpeta_storage.iterdir():
                if sub.is_dir() and (sub / "index.json").exists():
                    sub_norm = re.sub(r'[^a-zA-Z0-9]', '', sub.name.upper())
                    if cod_norm == sub_norm or cod_norm in sub_norm or sub_norm in cod_norm:
                        ruta_indice = sub / "index.json"
                        codigo = sub.name
                        break

        if not ruta_indice.exists():
            return False, f"El índice de la materia '{codigo}' no existe en {self.carpeta_storage}."

        try:
            with open(ruta_indice, "r", encoding="utf-8") as f:
                self.indice_en_memoria = json.load(f)
            self.materia_cargada = codigo
            return True, f"Índice de {codigo} cargado ({self.indice_en_memoria.get('total_nodos', 0)} fragmentos)."
        except Exception as e:
            return False, f"Error al leer índice de {codigo}: {e}"

    def consultar(self, materia, pregunta, rol="mentor", tema=None, top_k=3):
        ok, msg = self.cargar_materia(materia)
        if not ok:
            return {"error": msg}

        vec_pregunta = self.vectorizador.vectorizar(pregunta)
        nodos = self.indice_en_memoria.get("nodos", [])
        puntuados = []

        rol_norm = rol.lower().strip()

        for nodo in nodos:
            if tema and tema.lower() not in nodo.get("tema", "").lower():
                continue

            sim = similitud_coseno(vec_pregunta, nodo.get("vector", []))

            # Ajuste de rol pedagógico
            if rol_norm == "entrenador":
                if nodo.get("tipo") in ["ejercicios", "practica", "soluciones"]:
                    sim += 0.15
            elif rol_norm == "tribunal":
                if nodo.get("tipo") == "teoria":
                    sim += 0.10
            elif rol_norm == "coach":
                if nodo.get("pagina", 1) <= 5:
                    sim += 0.08

            puntuados.append((sim, nodo))

        puntuados.sort(key=lambda x: x[0], reverse=True)
        mejores = puntuados[:top_k]

        # Stop words en español para filtro de coincidencia léxica
        STOP_WORDS = {"de", "la", "el", "en", "un", "una", "los", "las", "y", "o", "a", "por", "para", "con", "que", "es", "del", "al", "como", "sobre"}
        palabras_pregunta = set(re.findall(r'\b[a-zA-Záéíóúñ]{3,}\b', pregunta.lower())) - STOP_WORDS

        # Umbral de confianza anti-alucinación
        max_similitud = mejores[0][0] if mejores else 0.0
        
        # Comprobar si al menos una palabra clave de la pregunta está en los fragmentos
        texto_acumulado_mejores = " ".join(n["texto"].lower() for _, n in mejores)
        coincidencias_lexicas = sum(1 for p in palabras_pregunta if p in texto_acumulado_mejores)
        
        # Se considera fuera de temario si ninguna palabra clave de la pregunta existe en los fragmentos
        # o si la similitud matemática de fondo es prácticamente nula (< 0.05)
        if len(palabras_pregunta) > 0 and coincidencias_lexicas == 0:
            es_fuera_de_temario = True
        elif max_similitud < 0.05:
            es_fuera_de_temario = True
        else:
            es_fuera_de_temario = False

        fragmentos = []
        for sim, n in mejores:
            fragmentos.append({
                "similitud": round(sim, 4),
                "tema": n.get("tema"),
                "archivo": n.get("archivo"),
                "pagina": n.get("pagina"),
                "tipo": n.get("tipo"),
                "texto": n.get("texto")
            })

        if es_fuera_de_temario:
            directiva = (
                "🛡️ DIRECTIVA ESTRICTA DE FIDELIDAD (ANTI-ALUCINACIÓN):\n"
                f"- El concepto consultado ('{pregunta}') NO figura en los apuntes oficiales disponibles de {self.indice_en_memoria.get('nombre')}.\n"
                "- Responde con total honestidad al estudiante diciendo:\n"
                f"  'Este concepto no aparece en los temas oficiales de {self.indice_en_memoria.get('nombre')} analizados en tus apuntes.'\n"
                "- Queda TERMINANTEMENTE PROHIBIDO inventar definiciones o recurrir a conocimientos ajenos al temario del alumno."
            )
        else:
            directiva = self._generar_directiva_rol(rol_norm, fragmentos)

        return {
            "materia_codigo": self.materia_cargada,
            "materia_nombre": self.indice_en_memoria.get("nombre"),
            "rol_activado": rol_norm,
            "pregunta": pregunta,
            "fuera_de_temario": es_fuera_de_temario,
            "max_similitud": round(max_similitud, 4),
            "total_encontrados": len(fragmentos) if not es_fuera_de_temario else 0,
            "fragmentos": fragmentos if not es_fuera_de_temario else [],
            "directiva_pedagogica": directiva
        }

    def _generar_directiva_rol(self, rol, fragmentos):
        citas = [f"[Fuente: {f['archivo']}, Página {f['pagina']}]" for f in fragmentos]
        citas_txt = " | ".join(citas)

        if rol in ("glosario", "vocabulario"):
            return (
                "ETAPA 1 ACTIVADA: GLOSARIO INTUITIVO DE PALABRAS TÉCNICAS\n"
                "- Identifica los términos técnicos clave de la consulta en los apuntes.\n"
                "- Para cada término presenta: 1) Definición intuitiva con analogía cotidiana, 2) Definición formal del apunte, 3) Ejemplo real.\n"
                f"- Cita oficial: {citas_txt}"
            )
        elif rol in ("guia", "esquema"):
            return (
                "ETAPA 2 ACTIVADA: GUÍA VISUAL Y ESENCIAL\n"
                "- Genera un diagrama visual Mermaid (flowchart TD, graph LR o erDiagram).\n"
                "- Resume los 3 a 5 pilares conceptuales indispensables sin paja teórica.\n"
                f"- Cita oficial: {citas_txt}"
            )
        elif rol in ("entrenador", "taller", "ejercicios"):
            return (
                "ETAPA 3 ACTIVADA: TALLER PRÁCTICO Y EJERCICIOS\n"
                "- Plantea el ejercicio o problema guiando al alumno paso a paso.\n"
                "- Si la materia incluye cálculos matemáticos, RENDERIZA EN KATEX con \\hline (cajetines o escaleras).\n"
                "- No reveles el resultado final de golpe; pide al alumno que resuelva el siguiente paso.\n"
                f"- Cita oficial: {citas_txt}"
            )
        elif rol in ("tribunal", "test", "evaluacion"):
            return (
                "ETAPA 4 ACTIVADA: EVALUACIÓN DUAL (TEST / PREGUNTAS ABIERTAS)\n"
                "- Genera preguntas cerradas con 4 opciones (A, B, C, D) con 3 distractores basados en confusiones del temario, o preguntas de razonamiento abierto.\n"
                "- NO reveles la solución hasta que el alumno responda.\n"
                f"- Cita oficial: {citas_txt}"
            )
        elif rol in ("chuleta", "cheatsheet", "resumen"):
            return (
                "ETAPA 5 ACTIVADA: LA CHULETA DE 1 VISTAZO (CHEAT SHEET)\n"
                "- Máxima densidad informativa: tablas de equivalencias, fórmulas KaTeX, glosario flash de 1 línea y semáforo de errores fatales.\n"
                f"- Cita oficial: {citas_txt}"
            )
        elif rol == "coach":
            return (
                "MODO ACTIVADO: COACH DE RESCATE\n"
                "- Muestra empatía ante el suspenso y motiva al estudiante.\n"
                "- Identifica los conceptos indispensables que garantizan el aprobado.\n"
                f"- Cita oficial: {citas_txt}"
            )
        else:
            return (
                "MODO ACTIVADO: MENTOR PEDAGÓGICO\n"
                "- Aplica la tríada: 1) Analogía intuitiva cotidiana, 2) Definición formal del apunte, 3) Diagrama Mermaid si procede.\n"
                f"- Cita oficial obligatoria al final: {citas_txt}"
            )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Consultor RAG Universal")
    parser.add_argument("--materia", required=True, help="Código o nombre de la materia")
    parser.add_argument("--pregunta", required=True, help="Pregunta del alumno")
    parser.add_argument("--rol", default="mentor", choices=["mentor", "glosario", "guia", "entrenador", "tribunal", "chuleta", "coach"])
    parser.add_argument("--tema", default=None)
    args = parser.parse_args()

    consultor = ConsultorRAG()
    res = consultor.consultar(args.materia, args.pregunta, rol=args.rol, tema=args.tema)
    print(json.dumps(res, indent=2, ensure_ascii=False))
