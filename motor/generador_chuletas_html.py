#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador de Chuletas Imprimibles de Alta Densidad (1 Hoja A4)
Tutor Académico Inteligente.
Crea archivos HTML ultra optimizados con estilos @media print para que al imprimir
o exportar a PDF (Ctrl + P) ocupe exactamente 1 página A4 sin desbordamientos.
Incluye renderizado de fórmulas KaTeX, tablas de equivalencias, glosario flash
y semáforo de errores fatales de examen.
"""

import os
import sys
import re
import json
import argparse
from pathlib import Path
from datetime import datetime

# Asegurar codificación UTF-8
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent))
from auto_gestor import AutoGestor

def generar_html_chuleta(datos_materia, nodos, ruta_salida):
    """
    Genera el archivo HTML autocontenido maquetado para 1 hoja A4.
    """
    nombre_materia = datos_materia.get("nombre", "Materia")
    codigo_materia = datos_materia.get("codigo", "MATERIA")
    
    # 1. Analizar nodos para extraer términos, fórmulas y citas
    terminos_encontrados = []
    citas_encontradas = set()
    
    patron_termino = re.compile(r'^[•\-–]?\s*([A-ZÁÉÍÓÚ][a-zA-ZáéíóúñÁÉÍÓÚÑ0-9\s/_-]{2,25})\s*[:–-]\s*(.+)', re.M)
    
    for n in nodos:
        txt = n.get("texto", "")
        arch = n.get("archivo", "")
        pag = n.get("pagina", "")
        if arch and pag:
            citas_encontradas.add(f"{arch} (pág. {pag})")
            
        for m in patron_termino.finditer(txt):
            concepto = m.group(1).strip()
            definic = m.group(2).strip()
            if len(definic) > 15 and len(concepto) < 30 and not any(t[0].lower() == concepto.lower() for t in terminos_encontrados):
                def_corta = definic.split(".")[0].strip() + "."
                if len(def_corta) < 140:
                    terminos_encontrados.append((concepto, def_corta, f"{arch} p.{pag}"))

    # Bloques predeterminados de alta densidad según la materia
    es_redes = "red" in nombre_materia.lower() or "reda" in codigo_materia.lower()
    es_bd = "base" in nombre_materia.lower() or "gebd" in codigo_materia.lower() or "datos" in nombre_materia.lower()

    if es_redes:
        tabla_html = """
        <table class="data-table">
          <thead>
            <tr><th>Base</th><th>Símbolos</th><th>Ponderación</th><th>Ejemplo</th></tr>
          </thead>
          <tbody>
            <tr><td><b>Binario (2)</b></td><td>0, 1</td><td>2<sup>0</sup>, 2<sup>1</sup>, 2<sup>2</sup>, 2<sup>3</sup>...</td><td>1101<sub>2</sub> = 13<sub>10</sub></td></tr>
            <tr><td><b>Octal (8)</b></td><td>0 al 7</td><td>8<sup>0</sup>=1, 8<sup>1</sup>=8, 8<sup>2</sup>=64</td><td>17<sub>8</sub> = 15<sub>10</sub></td></tr>
            <tr><td><b>Decimal (10)</b></td><td>0 al 9</td><td>10<sup>0</sup>=1, 10<sup>1</sup>=10, 10<sup>2</sup>=100</td><td>53<sub>10</sub></td></tr>
            <tr><td><b>Hexadecimal (16)</b></td><td>0-9, A-F</td><td>16<sup>0</sup>=1, 16<sup>1</sup>=16 (A=10, F=15)</td><td>2A<sub>16</sub> = 42<sub>10</sub></td></tr>
          </tbody>
        </table>
        """
        formulas_html = r"""
        <div class="formula-box">
          <div class="formula-title">1. Conversión Polinómica a Decimal:</div>
          <p>$$N_{10} = d_n \cdot b^n + \dots + d_1 \cdot b^1 + d_0 \cdot b^0$$</p>
        </div>
        <div class="formula-box">
          <div class="formula-title">2. Divisiones Sucesivas (Decimal a Base $b$):</div>
          <p style="font-size: 9px; margin-bottom: 3px;">Dividir sucesivamente entre la base <b>$b$</b>. El resultado se lee desde el <b>último cociente</b> seguido de los <b>restos en orden inverso</b>:</p>
          <div style="text-align: center;">
          $$
          \begin{array}{r|l}
          53 & 2 \\
          \hline
          26 & 2 \quad \to \text{Resto: } \mathbf{1} \\
          \hline
          13 & 2 \quad \to \text{Resto: } \mathbf{0} \\
          \hline
          6 & 2 \quad \to \text{Resto: } \mathbf{1} \\
          \hline
          3 & 2 \quad \to \text{Resto: } \mathbf{0} \\
          \hline
          \mathbf{1} & 2 \quad \to \text{Resto: } \mathbf{1} \\
          \hline
          & \mathbf{1} \quad \leftarrow \text{Último cociente}
          \end{array}
          $$
          </div>
          <p style="text-align: center; font-size: 10px; font-weight: bold; margin-top: 3px;">
            $$\implies 53_{10} = \mathbf{110101}_2$$
          </p>
        </div>
        """
        errores_fatales = [
            ("Orden de lectura de restos:", "Leer de izquierda a derecha en lugar de abajo a arriba (último cociente hacia el primer resto)."),
            ("Letras en Hexadecimal:", "Olvidar que A=10, B=11, C=12, D=13, E=14, F=15 y sumar caracteres como texto."),
            ("Acarreos en suma binaria:", "Olvidar que 1 + 1 = 0 con acarreo de 1, y 1 + 1 + 1 = 1 con acarreo de 1.")
        ]
    elif es_bd:
        tabla_html = """
        <table class="data-table">
          <thead><tr><th>Concepto</th><th>Relacional</th><th>Definición Breve</th></tr></thead>
          <tbody>
            <tr><td><b>Entidad</b></td><td>Tabla</td><td>Objeto del mundo real con existencia independiente.</td></tr>
            <tr><td><b>Atributo</b></td><td>Columna / Campo</td><td>Propiedad o característica que describe a la entidad.</td></tr>
            <tr><td><b>Tupla</b></td><td>Fila / Registro</td><td>Instancia concreta con valores para cada atributo.</td></tr>
            <tr><td><b>Clave Primaria (PK)</b></td><td>PRIMARY KEY</td><td>Identificador único irremplazable y no nulo.</td></tr>
            <tr><td><b>Clave Ajena (FK)</b></td><td>FOREIGN KEY</td><td>Referencia a la clave primaria de otra tabla.</td></tr>
          </tbody>
        </table>
        """
        formulas_html = r"""
        <div class="formula-box">
          <div class="formula-title">Reglas de Integridad Básicas:</div>
          <p>1. <b>Integridad de Entidad:</b> Ningún componente de la Clave Primaria puede ser nulo ($PK \neq \text{NULL}$).</p>
          <p>2. <b>Integridad Referencial:</b> Toda clave ajena ($FK$) debe coincidir con un valor existente de la $PK$ referenciada o ser nula.</p>
        </div>
        """
        errores_fatales = [
            ("Claves primarias nulas:", "Permitir valores NULL o duplicados en columnas definidas como PRIMARY KEY."),
            ("Borrado en cascada descontrolado:", "Eliminar registros padre sin prever la pérdida de registros hijos dependientes."),
            ("Confundir Cardinalidad:", "Asignar relación 1:1 en lugar de 1:N por no analizar si un elemento puede tener múltiples hijos.")
        ]
    else:
        items_tabla = terminos_encontrados[:4] or [("Concepto 1", "Definición básica", ""), ("Concepto 2", "Definición secundaria", "")]
        filas = "".join([f"<tr><td><b>{c}</b></td><td>{d}</td></tr>" for c, d, _ in items_tabla])
        tabla_html = f"""
        <table class="data-table">
          <thead><tr><th>Término</th><th>Definición Esencial</th></tr></thead>
          <tbody>{filas}</tbody>
        </table>
        """
        formulas_html = """
        <div class="formula-box">
          <div class="formula-title">Regla de Oro de la Materia:</div>
          <p>Consistencia, observación metódica y aplicación estricta de las pautas técnicas oficiales descritas en el manual.</p>
        </div>
        """
        errores_fatales = [
            ("Ignorar pautas oficiales:", "Actuar por intuición en lugar de seguir las especificaciones del temario."),
            ("Mezclar unidades:", "No verificar las unidades de medida o dosificación prescritas."),
            ("Falta de comprobación:", "Dar por finalizado un procedimiento sin verificar los indicadores de control.")
        ]

    terminos_flash = terminos_encontrados[:6]
    if not terminos_flash:
        terminos_flash = [
            ("Término Clave", "Definición técnica directa extraída del temario oficial.", "")
        ]

    flash_html = "".join([
        f'<div class="flash-item"><b>• {c}:</b> {d}</div>'
        for c, d, _ in terminos_flash
    ])

    errores_html = "".join([
        f'<li class="error-item"><span class="badge-danger">¡OJO!</span> <b>{tit}</b> {desc}</li>'
        for tit, desc in errores_fatales
    ])

    citas_html = ", ".join(list(citas_encontradas)[:4]) if citas_encontradas else "Apuntes oficiales del espacio de trabajo"

    html_completo = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Chuleta de 1 Vistazo - {nombre_materia}</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/contrib/auto-render.min.js" 
          onload="renderMathInElement(document.body, {{delimiters: [{{left: '$$', right: '$$', display: true}}, {{left: '$', right: '$', display: false}}], throwOnError: false}});"></script>
  <style>
    :root {{
      --primary: #1e293b;
      --accent: #2563eb;
      --danger: #dc2626;
      --warning: #d97706;
      --border: #cbd5e1;
      --bg-card: #f8fafc;
    }}
    
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-size: 11px;
      line-height: 1.3;
      color: #0f172a;
      background: #f1f5f9;
      padding: 12px;
    }}

    .page-container {{
      max-width: 210mm;
      min-height: 297mm;
      margin: 0 auto;
      background: #ffffff;
      padding: 10mm;
      border-radius: 6px;
      box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    /* Barra de herramientas en pantalla */
    .toolbar {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 10px;
      padding-bottom: 6px;
      border-bottom: 2px solid var(--accent);
    }}

    .btn-print {{
      background: var(--accent);
      color: #ffffff;
      border: none;
      padding: 6px 14px;
      border-radius: 4px;
      font-weight: 600;
      cursor: pointer;
      font-size: 11px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    .btn-print:hover {{
      background: #1d4ed8;
    }}

    .header-sheet {{
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 8px;
      border-bottom: 1.5px solid var(--primary);
      padding-bottom: 4px;
    }}

    .title-area h1 {{
      font-size: 15px;
      color: var(--primary);
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: -0.2px;
    }}

    .title-area p {{
      font-size: 10px;
      color: #64748b;
    }}

    .badge-a4 {{
      background: #e0e7ff;
      color: #3730a3;
      padding: 2px 6px;
      border-radius: 3px;
      font-size: 9px;
      font-weight: 700;
    }}

    /* Cuadrícula de 2 columnas */
    .grid-layout {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      flex-grow: 1;
    }}

    .card {{
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: 4px;
      padding: 7px;
      page-break-inside: avoid;
      break-inside: avoid;
    }}

    .card-title {{
      font-size: 10.5px;
      font-weight: 700;
      color: var(--primary);
      margin-bottom: 5px;
      display: flex;
      align-items: center;
      gap: 4px;
      border-bottom: 1px solid #e2e8f0;
      padding-bottom: 2px;
    }}

    /* Tablas compactas */
    .data-table {{
      width: 100%;
      border-collapse: collapse;
      font-size: 10px;
    }}

    .data-table th, .data-table td {{
      padding: 3px 4px;
      border: 1px solid #cbd5e1;
      text-align: left;
    }}

    .data-table th {{
      background: #e2e8f0;
      font-weight: 700;
      color: #1e293b;
    }}

    /* Cajas de fórmulas */
    .formula-box {{
      background: #ffffff;
      border: 1px solid #e2e8f0;
      border-radius: 3px;
      padding: 4px;
      margin-bottom: 4px;
    }}

    .formula-title {{
      font-weight: 600;
      font-size: 9.5px;
      color: #475569;
      margin-bottom: 2px;
    }}

    /* Glosario Flash */
    .flash-item {{
      margin-bottom: 4px;
      font-size: 9.5px;
      line-height: 1.25;
    }}

    /* Errores de examen */
    .error-list {{
      list-style: none;
    }}

    .error-item {{
      font-size: 9.5px;
      margin-bottom: 4px;
      display: flex;
      align-items: flex-start;
      gap: 4px;
    }}

    .badge-danger {{
      background: #fee2e2;
      color: var(--danger);
      font-size: 8px;
      font-weight: 800;
      padding: 1px 3px;
      border-radius: 2px;
      flex-shrink: 0;
    }}

    /* Pie de página */
    .footer-sheet {{
      margin-top: 6px;
      padding-top: 4px;
      border-top: 1px solid #e2e8f0;
      display: flex;
      justify-content: space-between;
      font-size: 8.5px;
      color: #94a3b8;
    }}

    /* ESTILOS EXACTOS DE IMPRESIÓN (1 HOJA A4) */
    @media print {{
      @page {{
        size: A4 portrait;
        margin: 6mm 6mm 6mm 6mm;
      }}
      body {{
        background: #ffffff !important;
        padding: 0 !important;
        font-size: 10px !important;
      }}
      .no-print {{
        display: none !important;
      }}
      .page-container {{
        width: 100% !important;
        max-width: 100% !important;
        min-height: 0 !important;
        height: 100% !important;
        box-shadow: none !important;
        padding: 0 !important;
        border: none !important;
      }}
      .card {{
        border: 1px solid #94a3b8 !important;
        box-shadow: none !important;
        padding: 5px !important;
        margin-bottom: 4px !important;
      }}
    }}
  </style>
</head>
<body>

  <div class="page-container">
    
    <!-- Barra de control en pantalla -->
    <div class="toolbar no-print">
      <div><b>🎓 Tutor Académico Universal</b> — Vista previa de impresión</div>
      <button class="btn-print" onclick="window.print()">
        🖨️ Imprimir Chuleta en 1 Hoja A4 (o Guardar PDF)
      </button>
    </div>

    <!-- Encabezado de la Chuleta -->
    <div class="header-sheet">
      <div class="title-area">
        <h1>⚡ Chuleta de 1 Vistazo: {nombre_materia}</h1>
        <p>Resumen ultracondensado de conceptos clave, fórmulas y reglas de examen</p>
      </div>
      <span class="badge-a4">HOJA A4</span>
    </div>

    <!-- Cuadrícula 2 Columnas -->
    <div class="grid-layout">
      
      <!-- Columna 1 -->
      <div class="column">
        
        <!-- Bloque 1: Tabla de Parámetros y Equivalencias -->
        <div class="card">
          <div class="card-title">📊 1. Tabla de Parámetros y Equivalencias Críticas</div>
          {tabla_html}
        </div>

        <!-- Bloque 2: Fórmulas Matemáticas Directas -->
        <div class="card" style="margin-top: 6px;">
          <div class="card-title">🧮 2. Fórmulas de Cálculo Directo (KaTeX)</div>
          {formulas_html}
        </div>

      </div>

      <!-- Columna 2 -->
      <div class="column">
        
        <!-- Bloque 3: Diccionario Flash -->
        <div class="card">
          <div class="card-title">📖 3. Diccionario Flash (1 Línea por Término)</div>
          {flash_html}
        </div>

        <!-- Bloque 4: Semáforo de Errores Fatales de Examen -->
        <div class="card" style="margin-top: 6px;">
          <div class="card-title" style="color: var(--danger);">🚨 4. Las 3 Trampas Fatales de Examen</div>
          <ul class="error-list">
            {errores_html}
          </ul>
        </div>

        <!-- Bloque 5: Pautas de Resolución -->
        <div class="card" style="margin-top: 6px;">
          <div class="card-title">🧭 5. Método de Resolución Rápida</div>
          <p style="font-size: 9px; line-height: 1.3;">
            1. Anota datos y base original.<br>
            2. Aplica la fórmula directa de la columna izquierda sin saltarte pasos intermedios.<br>
            3. Comprueba el resultado en sentido inverso (ej. pasa el binario obtenido de nuevo a decimal).
          </p>
        </div>

      </div>

    </div>

    <!-- Pie de página con fuentes oficiales -->
    <div class="footer-sheet">
      <span>📖 <b>Fuentes Oficiales:</b> {citas_html}</span>
      <span>Generado el {datetime.now().strftime('%d/%m/%Y')} | Tutor Académico Oficial</span>
    </div>

  </div>

</body>
</html>
"""
    
    ruta_p = Path(ruta_salida)
    ruta_p.parent.mkdir(parents=True, exist_ok=True)
    with open(ruta_p, "w", encoding="utf-8") as f:
        f.write(html_completo)
        
    return ruta_p

def main():
    parser = argparse.ArgumentParser(description="Generador de Chuletas HTML de 1 Hoja A4")
    parser.add_argument("--materia", required=True, help="Código o nombre de la materia (ej. REDA, GEBD)")
    parser.add_argument("--tema", default=None, help="Nombre del tema específico si procede")
    parser.add_argument("--salida", default=None, help="Ruta de destino del archivo HTML generado")
    args = parser.parse_args()

    raiz = Path(__file__).resolve().parent.parent.parent
    gestor = AutoGestor(raiz_proyecto=raiz)
    revision = gestor.verificar_proyecto()

    codigo_objetivo = None
    info_materia = None

    for cod, info in revision["materias"].items():
        if cod.lower() == args.materia.lower() or args.materia.lower() in info["nombre"].lower():
            codigo_objetivo = cod
            info_materia = info
            break

    if not info_materia:
        codigo_objetivo = args.materia.upper()
        info_materia = {"nombre": args.materia, "ruta": str(raiz / "1 Evaluación" / args.materia)}

    ruta_indice = Path(__file__).resolve().parent / "storage_index" / codigo_objetivo / "index.json"
    nodos = []
    if ruta_indice.exists():
        try:
            with open(ruta_indice, "r", encoding="utf-8") as f:
                data = json.load(f)
                nodos = data.get("nodos", [])
        except Exception:
            pass

    if args.salida:
        salida = Path(args.salida).resolve()
    else:
        carpeta_materia = Path(info_materia.get("ruta", raiz / "1 Evaluación"))
        if not carpeta_materia.exists():
            carpeta_materia = raiz / "1 Evaluación"
        salida = carpeta_materia / f"CHULETA_{codigo_objetivo}.html"

    ruta_creada = generar_html_chuleta(
        {"nombre": info_materia.get("nombre", codigo_objetivo), "codigo": codigo_objetivo},
        nodos,
        salida
    )

    carpeta_html_publica = raiz / "html"
    carpeta_html_publica.mkdir(parents=True, exist_ok=True)
    copia_publica = carpeta_html_publica / f"CHULETA_{codigo_objetivo}.html"
    import shutil
    shutil.copyfile(str(ruta_creada), str(copia_publica))

    resultado = {
        "exito": True,
        "materia": codigo_objetivo,
        "nombre": info_materia.get("nombre", codigo_objetivo),
        "archivo_generado": str(ruta_creada),
        "archivo_publico": str(copia_publica),
        "mensaje": f"Chuleta imprimible de 1 página A4 generada exitosamente en '{ruta_creada}'."
    }
    print(json.dumps(resultado, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
