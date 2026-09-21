#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conector Resiliente de Alta Disponibilidad para TypeSafe Jev vía OpenRouter.
Integrado en el motor oficial del Tutor Académico.
- Control de timeouts adaptativos.
- Algoritmo de reintentos con Exponential Backoff y Jitter.
- Bitácora de auditoría detallada (jev_resiliencia.log).
- Tolerancia absoluta a saturación.
"""

import os
import sys
import time
import json
import random
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# Asegurar codificación utf-8 en Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

OPENROUTER_ENDPOINT = "https://openrouter.ai/api/alpha/decisions"

class ClienteJevResiliente:
    def __init__(self, api_key=None, ruta_log=None, timeout_base=2.5, max_reintentos=3):
        # 1. Leer de parámetro explícito
        # 2. Leer de variable de entorno OPENROUTER_API_KEY
        # 3. Leer de archivo local config_api.json (ignorado por Git)
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            candidatos_cfg = [
                Path(__file__).resolve().parent / "config_api.json",
                Path(__file__).resolve().parent.parent / "config_api.json",
                Path(__file__).resolve().parent.parent.parent / "config_api.json",
                Path(__file__).resolve().parent.parent.parent.parent / "config_api.json",
                Path.cwd() / "config_api.json",
                Path.cwd() / "1 Evaluación" / "config_api.json"
            ]
            for c in candidatos_cfg:
                if c.exists():
                    try:
                        with open(c, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            self.api_key = data.get("OPENROUTER_API_KEY")
                            if self.api_key:
                                break
                    except Exception:
                        pass

        self.timeout_base = timeout_base
        self.max_reintentos = max_reintentos
        
        if ruta_log:
            self.ruta_log = Path(ruta_log)
        else:
            # Por defecto: junto a vigilante.log en .agents/skills/
            base_skills = Path(__file__).resolve().parent.parent.parent
            self.ruta_log = base_skills / "jev_resiliencia.log"
            
        self._inicializar_log()

    def _inicializar_log(self):
        """Prepara el archivo de log si no existe."""
        if not self.ruta_log.exists():
            try:
                with open(self.ruta_log, "w", encoding="utf-8") as f:
                    f.write(f"======================================================================\n")
                    f.write(f"📋 BITÁCORA DE RESILIENCIA Y AUDITORÍA EN TIEMPO REAL - TYPESAFE JEV\n")
                    f.write(f"   Iniciado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"   Endpoint: {OPENROUTER_ENDPOINT}\n")
                    f.write(f"======================================================================\n\n")
            except Exception:
                pass

    def registrar_log(self, nivel, evento, mensaje, metadata=None):
        """Registra un evento estructurado en el archivo log."""
        ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        linea = f"[{ahora}] [{nivel:^7}] [{evento:^18}] {mensaje}"
        if metadata:
            linea += f" | Metadata: {json.dumps(metadata, ensure_ascii=False)}"
        linea += "\n"
        
        try:
            with open(self.ruta_log, "a", encoding="utf-8") as f:
                f.write(linea)
                f.flush()
        except Exception:
            pass
            
        return linea.strip()

    def consultar_decision(self, state, questions, model="~typesafe/jev-latest", callback_alumno=None, timeout_forzado=None):
        """
        Ejecuta la consulta a Jev con tolerancia a fallos, reintentos con backoff y registro en log.
        """
        if not self.api_key or not self.api_key.startswith("sk-or-"):
            self.registrar_log("WARN", "SIN_API_KEY", "No se detectó API Key válida de OpenRouter.")
            return {"exito": False, "modo": "SIN_API_KEY"}

        timeout_actual = timeout_forzado if timeout_forzado is not None else self.timeout_base
        payload = {
            "model": model,
            "state": state,
            "questions": questions
        }
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/errobimd/tutor-academico-universal",
            "X-Title": "Tutor Academico Universal - Motor Jev"
        }

        notifico_pausa = False
        t_inicio_total = time.time()

        self.registrar_log("INFO", "PETICION_INICIADA", f"Consulta enviada a {model}", {
            "preguntas": list(questions.keys()),
            "longitud_estado": len(state)
        })

        for intento in range(1, self.max_reintentos + 1):
            t_intento = time.time()
            req = urllib.request.Request(OPENROUTER_ENDPOINT, data=data, headers=headers, method="POST")
            
            try:
                with urllib.request.urlopen(req, timeout=timeout_actual) as resp:
                    latencia_ms = int((time.time() - t_intento) * 1000)
                    latencia_total_ms = int((time.time() - t_inicio_total) * 1000)
                    res_raw = resp.read().decode("utf-8")
                    datos = json.loads(res_raw)

                    if notifico_pausa:
                        msg_rec = "🟢 ¡Línea despejada y motor de decisiones reconectado con éxito! Continuamos..."
                        self.registrar_log("AVISO", "RECONEXION_EXITOSA", f"Servidor recuperado tras {intento} intentos.", {"latencia_total_ms": latencia_total_ms})
                        if callback_alumno:
                            callback_alumno("RECONEXION", msg_rec)

                    self.registrar_log("EXITO", "DECISION_RECIBIDA", f"Decisión en {latencia_ms} ms (Total: {latencia_total_ms} ms)", {
                        "id": datos.get("id"),
                        "coste": datos.get("usage", {}).get("cost", 0.0),
                        "intento": intento
                    })

                    return {
                        "exito": True,
                        "modo": "JEV_ONLINE",
                        "latencia_ms": latencia_ms,
                        "latencia_total_ms": latencia_total_ms,
                        "intentos": intento,
                        "datos": datos
                    }

            except Exception as error:
                latencia_fallo_ms = int((time.time() - t_intento) * 1000)
                codigo_http = getattr(error, "code", "TIMEOUT/ERROR_RED")

                self.registrar_log("WARN", "FALLO_INTENTO", f"Intento {intento}/{self.max_reintentos} falló ({codigo_http}): {error}", {
                    "latencia_fallo_ms": latencia_fallo_ms
                })

                if not notifico_pausa and intento < self.max_reintentos:
                    msg_esp = "⏳ Los servidores de inferencia rápida tienen alta demanda. Reconectando en segundo plano..."
                    self.registrar_log("AVISO", "MENSAJE_ALUMNO", "Emitido aviso de saturación al alumno.")
                    if callback_alumno:
                        callback_alumno("SATURACION", msg_esp)
                    notifico_pausa = True

                if intento < self.max_reintentos:
                    jitter = random.uniform(0.1, 0.4)
                    espera = round(1.2 * (2 ** (intento - 1)) + jitter, 2)
                    self.registrar_log("INFO", "RETROCESO_EXPONENCIAL", f"Esperando {espera}s antes del intento {intento+1}...", {"espera_s": espera})
                    time.sleep(espera)
                else:
                    self.registrar_log("ERROR", "REINTENTOS_AGOTADOS", f"Todos los reintentos fallaron. Activando contingencia.")
                    return {
                        "exito": False,
                        "modo": "FALLBACK_REQUERIDO",
                        "error": str(error),
                        "latencia_total_ms": int((time.time() - t_inicio_total) * 1000)
                    }
