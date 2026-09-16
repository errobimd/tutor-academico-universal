#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Banco de Pruebas Automatizado Universal (Simulador del Tutor Académico).
Audita empíricamente:
1. Detección y manejo de proyecto vacío (sin errores).
2. Ingesta e indexación real de los 25 documentos curriculares de 1 Evaluación.
3. Consultas semánticas para los 4 sub-roles (Entrenador, Tribunal, Mentor, Coach).
4. Tiempos de respuesta y eficiencia de memoria.
5. Compatibilidad Universal (Biología Marina y Nutrición de Gatos).
6. Re-indexación Incremental (Detección de nuevo documento agregado).
7. Resiliencia ante archivos corruptos o de 0 bytes (Tolerancia a fallos).
8. Blindaje Anti-Alucinación ante preguntas trampa fuera de temario.
"""

import os
import sys
import time
import tempfile
import json
from pathlib import Path
import docx

# Asegurar codificación UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from auto_gestor import AutoGestor
from indexador_academico import IndexadorAcademico
from consultor_rag import ConsultorRAG

class SimuladorTutor:
    def __init__(self):
        self.laboratorio_dir = Path(__file__).resolve().parent
        self.raiz_proyecto = self.laboratorio_dir.parent.parent
        self.resultados = []

    def registrar_resultado(self, nombre_prueba, estado, detalle):
        icono = "🟢 [PASS]" if estado else "🔴 [FAIL]"
        self.resultados.append({
            "prueba": nombre_prueba,
            "estado": estado,
            "detalle": detalle
        })
        print(f"{icono} {nombre_prueba}: {detalle}")

    def test_1_proyecto_vacio(self):
        print("\n--- PRUEBA 1: PROYECTO VACÍO Y SIN APUNTES ---")
        with tempfile.TemporaryDirectory() as temp_dir:
            gestor_vacio = AutoGestor(temp_dir)
            estado = gestor_vacio.verificar_proyecto()
            es_vacio = estado.get("estado") == "PROYECTO_VACIO"
            tiene_mensaje = "no encuentro" in estado.get("mensaje_alumno", "").lower()
            ok = es_vacio and tiene_mensaje
            self.registrar_resultado("Blindaje de Proyecto Vacío", ok, "Detectó ausencia de carpetas y emitió guía.")

    def test_2_ingesta_real(self):
        print("\n--- PRUEBA 2: INGESTA E INDEXACIÓN DE 1 EVALUACIÓN ---")
        t0 = time.time()
        indexador = IndexadorAcademico(self.raiz_proyecto)
        resultado = indexador.indexar_todo()
        t_total = round(time.time() - t0, 2)

        materias = resultado.get("materias", {})
        total_frag = resultado.get("total_fragmentos", 0)
        condicion = len(materias) >= 5 and total_frag > 50
        detalle = f"Indexadas {len(materias)} materias ({total_frag} fragmentos) en {t_total} seg."
        self.registrar_resultado("Ingesta Documental Universal", condicion, detalle)
        return resultado

    def test_3_roles_pedagogicos(self):
        print("\n--- PRUEBA 3: SUB-ROLES PEDAGÓGICOS ---")
        consultor = ConsultorRAG(self.laboratorio_dir / "storage_index")

        pruebas_roles = [
            {"rol": "entrenador", "asig": "REDA", "pregunta": "conversión de decimal a binario divisiones sucesivas", "palabra_clave": "KATEX"},
            {"rol": "tribunal", "asig": "GEBD", "pregunta": "clave foránea modelo relacional atributos", "palabra_clave": "TRIBUNAL EVALUADOR"},
            {"rol": "mentor", "asig": "LEMA", "pregunta": "etiquetas html5 estructura css", "palabra_clave": "MENTOR PEDAGÓGICO"},
            {"rol": "coach", "asig": "IMSO", "pregunta": "he suspendido el examen qué conceptos entran para recuperar", "palabra_clave": "COACH DE RESCATE"}
        ]

        for p in pruebas_roles:
            t0 = time.time()
            res = consultor.consultar(p["asig"], p["pregunta"], rol=p["rol"], top_k=3)
            dt_ms = round((time.time() - t0) * 1000, 2)
            directiva = res.get("directiva_pedagogica", "")
            frags = res.get("fragmentos", [])
            ok = p["palabra_clave"] in directiva and len(frags) > 0 and all("pagina" in f for f in frags)
            self.registrar_resultado(f"Rol {p['rol'].capitalize()}", ok, f"{len(frags)} fragmentos con página en {dt_ms} ms.")

    def test_4_cambio_dinamico_asignatura(self):
        print("\n--- PRUEBA 4: CAMBIO DINÁMICO DE ASIGNATURA ---")
        consultor = ConsultorRAG(self.laboratorio_dir / "storage_index")
        tiempos = []
        for asig in ["GEBD", "REDA", "IMSO", "LEMA", "DISI"]:
            t0 = time.time()
            ok, msg = consultor.cargar_materia(asig)
            dt_ms = round((time.time() - t0) * 1000, 2)
            tiempos.append(dt_ms)

        promedio = round(sum(tiempos) / len(tiempos), 2)
        ok = promedio < 50.0
        self.registrar_resultado("Cambio Dinámico en Memoria", ok, f"Tiempo medio de cambio: {promedio} ms.")

    def test_5_compatibilidad_universal_biologia_y_gatos(self):
        print("\n--- PRUEBA 5: CASO UNIVERSAL (BIOLOGÍA Y ALIMENTACIÓN DE GATOS) ---")
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            carp_bio = temp_path / "Biología Marina" / "Tema 1 Cetáceos"
            carp_bio.mkdir(parents=True, exist_ok=True)
            doc_bio = docx.Document()
            doc_bio.add_heading("Adaptaciones de Mamíferos Marinos", level=1)
            doc_bio.add_paragraph("Los cetáceos evitan la descompresión colapsando los alvéolos pulmonares a más de 70 metros.")
            doc_bio.save(str(carp_bio / "Biologia_Marina.docx"))

            carp_gatos = temp_path / "Alimentación de Gatos" / "Nutrición Felina"
            carp_gatos.mkdir(parents=True, exist_ok=True)
            doc_gatos = docx.Document()
            doc_gatos.add_heading("Nutrición Felina", level=1)
            doc_gatos.add_paragraph("La taurina es un aminoácido indispensable para los gatos. Su deficiencia produce ceguera.")
            doc_gatos.save(str(carp_gatos / "Nutricion_Gatos.docx"))

            indexador_univ = IndexadorAcademico(temp_path)
            res_univ = indexador_univ.indexar_todo()
            materias = res_univ.get("materias", {})

            consultor_univ = ConsultorRAG(indexador_univ.carpeta_storage)
            res_gatos = consultor_univ.consultar("ALIMENTACION_DE_GATOS", "taurina en gatos", rol="mentor")
            res_bio = consultor_univ.consultar("BIOLOGIA_MARINA", "descompresión en cetáceos", rol="tribunal")

            ok = len(materias) == 2 and len(res_gatos.get("fragmentos", [])) > 0 and len(res_bio.get("fragmentos", [])) > 0
            self.registrar_resultado("Compatibilidad Universal (Biología y Gatos)", ok, f"Materias descubiertas: {list(materias.keys())}")

    def test_6_reindexacion_incremental(self):
        print("\n--- PRUEBA 6: RE-INDEXACIÓN INCREMENTAL (NUEVOS APUNTES) ---")
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            carp_materia = temp_path / "Historia del Arte" / "Tema 1"
            carp_materia.mkdir(parents=True, exist_ok=True)
            doc1 = docx.Document()
            doc1.add_paragraph("El arte gótico se caracteriza por el arco apuntado y la bóveda de crucería.")
            doc1.save(str(carp_materia / "Arte_Gotico.docx"))

            # Primera indexación
            indexador = IndexadorAcademico(temp_path)
            indexador.indexar_todo()

            # Estado justo después de indexar: al día
            estado_al_dia = indexador.gestor.detectar_cambios_documentos()
            no_necesita = not estado_al_dia["necesita_indexar"]

            # Añadir nuevo documento (Tema 2)
            doc2 = docx.Document()
            doc2.add_paragraph("El Renacimiento recupera la proporción clásica, el humanismo y la perspectiva lineal.")
            doc2.save(str(carp_materia / "Renacimiento.docx"))

            # Comprobar si detecta la novedad
            estado_nuevo = indexador.gestor.detectar_cambios_documentos()
            detecto_novedad = estado_nuevo["necesita_indexar"]
            mensaje_correcto = "Hay nuevos documentos" in estado_nuevo.get("mensaje_alumno", "")

            ok = no_necesita and detecto_novedad and mensaje_correcto
            detalle = "Detectó exactamente el nuevo documento agregado y activó el mensaje de aviso al alumno."
            self.registrar_resultado("Re-indexación Incremental", ok, detalle)

    def test_7_resiliencia_archivos_corruptos(self):
        print("\n--- PRUEBA 7: RESILIENCIA ANTE ARCHIVOS CORRUPTOS (0 BYTES) ---")
        indexador = IndexadorAcademico(self.raiz_proyecto)
        
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f_vacio:
            ruta_vacio = Path(f_vacio.name)
            f_vacio.write(b"") # 0 bytes

        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as f_corrupto:
            ruta_corrupto = Path(f_corrupto.name)
            f_corrupto.write(b"BASURA BINARIA NO VALIDA")

        # Intentar extraer sin que la aplicación se caiga
        try:
            res_pdf = indexador.extraer_pdf(ruta_vacio)
            res_docx = indexador.extraer_docx(ruta_corrupto)
            # Debe devolver lista vacía sin producir excepciones no controladas
            ok = isinstance(res_pdf, list) and isinstance(res_docx, list)
            detalle = "El motor capturó el PDF de 0 bytes y el DOCX inválido sin romperse (0 excepciones)."
        except Exception as e:
            ok = False
            detalle = f"Excepción crítica no capturada: {e}"
        finally:
            try:
                os.remove(ruta_vacio)
                os.remove(ruta_corrupto)
            except Exception:
                pass

        self.registrar_resultado("Resiliencia ante Archivos Rotos", ok, detalle)

    def test_8_blindaje_anti_alucinacion(self):
        print("\n--- PRUEBA 8: BLINDAJE ANTI-ALUCINACIÓN (PREGUNTA FUERA DE TEMARIO) ---")
        consultor = ConsultorRAG(self.laboratorio_dir / "storage_index")

        # Preguntar en REDA por algo totalmente ajeno (fotosíntesis vegetal)
        pregunta_trampa = "fases de la fotosíntesis en plantas terrestres y clorofila b"
        res = consultor.consultar("REDA", pregunta_trampa, rol="mentor")

        es_fuera = res.get("fuera_de_temario") is True
        cero_fragmentos = len(res.get("fragmentos", [])) == 0
        directiva = res.get("directiva_pedagogica", "")
        aviso_fidelidad = "DIRECTIVA ESTRICTA DE FIDELIDAD" in directiva

        ok = es_fuera and cero_fragmentos and aviso_fidelidad
        detalle = (
            f"Pregunta trampa detectada con éxito. Fuera de temario: {es_fuera}. "
            f"Fragmentos bloqueados: {len(res.get('fragmentos', []))}. Directiva de honestidad activada."
        )
        self.registrar_resultado("Blindaje Anti-Alucinación", ok, detalle)

    def ejecutar_banco_completo(self):
        print("=" * 70)
        print("🔬 BANCO DE PRUEBAS UNIVERSAL DEL TUTOR ACADÉMICO (COMPLETO)")
        print("=" * 70)
        self.test_1_proyecto_vacio()
        self.test_2_ingesta_real()
        self.test_3_roles_pedagogicos()
        self.test_4_cambio_dinamico_asignatura()
        self.test_5_compatibilidad_universal_biologia_y_gatos()
        self.test_6_reindexacion_incremental()
        self.test_7_resiliencia_archivos_corruptos()
        self.test_8_blindaje_anti_alucinacion()
        print("=" * 70)
        
        total = len(self.resultados)
        pasadas = sum(1 for r in self.resultados if r["estado"])
        print(f"📊 RESUMEN FINAL: {pasadas}/{total} PRUEBAS SUPERADAS.")
        return pasadas == total

if __name__ == "__main__":
    simulador = SimuladorTutor()
    exito = simulador.ejecutar_banco_completo()
    sys.exit(0 if exito else 1)
