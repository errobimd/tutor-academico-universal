# 🎓 Tutor Académico Inteligente Universal (Offline & RAG Local)
> **Profesor particular autónomo para Bionic Studio (LM Studio Bionic) con LlamaIndex, KaTeX riguroso, menús por asignatura y 4 sub-roles pedagógicos.**

[![Bionic Studio](https://img.shields.io/badge/Bionic_Studio-Skill_Compatible-8A2BE2.svg)](#)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](#)
[![100% Offline](https://img.shields.io/badge/Privacidad-100%25_Local_%2F_Offline-green.svg)](#)
[![KaTeX](https://img.shields.io/badge/KaTeX-Math_Strict-critical.svg)](#)
[![Tests](https://img.shields.io/badge/Tests-11%2F11_PASS-success.svg)](#)
[![Licencia MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#)

---

## ⚡ INSTALACIÓN (ELIGE TU MÉTODO FAVORITO)

### 🥇 Método 1: En 1 Clic (Recomendado e Infalible)
Abre **PowerShell** en tu ordenador (pulsa la tecla Windows, escribe `powershell` y pulsa Enter) y pega esta línea:

```powershell
git clone https://github.com/errobimd/tutor-academico-universal.git "$HOME\.agents\skills\tutor-academico"
```

> **¡Listo!** Abre **Bionic Studio**, crea un nuevo chat y ya tendrás disponible **`@tutor-academico`** en tu menú de habilidades. Sin intermediarios ni fallos de herramientas.

---

### 🥈 Método 2: Descarga Manual Directa (Sin usar terminal)
1. Pulsa el botón verde superior **`Code`** $\to$ **`Download ZIP`** en este repositorio.
2. Descomprime la carpeta descargada.
3. Renombra la carpeta a `tutor-academico` y muévela a tu carpeta de habilidades:
   * En Windows: `C:\Users\<TuUsuario>\.agents\skills\tutor-academico`
   * En Linux/Mac: `~/.agents/skills/tutor-academico`
4. Abre **Bionic Studio** y escribe `@tutor-academico`.

---

### 🥉 Método 3: Desde el Asistente de Bionic Studio (Vía Chat)
Si tu modelo local soporta la invocación de herramientas de sistema:
1. Abre **Bionic Studio**.
2. Ve a la sección de **Habilidades** (o pulsa *Crear Skill*).
3. Pega este mensaje:

```text
Instala el skill @instalador-tutor desde el repositorio oficial:
https://github.com/errobimd/tutor-academico-universal.git

Configura el entorno para desplegar el Tutor Académico Inteligente con motor LlamaIndex local, menús numerados por asignatura, 4 sub-roles pedagógicos y KaTeX riguroso.
```

---

## 📂 ¿CÓMO ORGANIZAR TUS APUNTES? (COMPATIBILIDAD UNIVERSAL)

El tutor es **100% agnóstico**: sirve para cualquier materia o carrera (Informática, Biología, Medicina, Derecho, Nutrición Animal, etc.). 

Solo coloca tus carpetas de apuntes dentro de tu espacio de trabajo:

```text
Mi_Espacio_De_Estudio/
│
├── 1 Evaluación/                           <- Opcional: puedes agrupar por evaluación
│   ├── Planificación de Redes/
│   │   ├── Tema 1 - Numeración.pdf
│   │   └── Ejercicios_Binario.docx
│   │
│   └── Gestión de Bases de Datos/
│       └── Apuntes_Modelo_Relacional.pdf
│
└── Otras Materias (Cualquier disciplina)/
    ├── Biología Marina/
    │   └── Cetaceos_y_Buceo.pdf
    │
    └── Alimentación y Nutrición Felina/
        └── Manual_Dietas_Gatos.pdf
```

El motor detectará automáticamente los nombres de tus carpetas, creará los índices de cada materia por separado y te mostrará el menú numerado para elegir qué estudiar.

---

## 🎭 LOS 4 SUB-ROLES PEDAGÓGICOS DINÁMICOS

El tutor detecta automáticamente lo que necesitas y adopta uno de estos 4 roles:

| Sub-Rol | Cuándo se activa | Comportamiento Didáctico |
| :--- | :--- | :--- |
| 🔧 **El Entrenador Práctico** | *"Dame problemas"*, *"cálculos"* | Desglosa operaciones paso a paso en **KaTeX riguroso** (cajetines encadenados $\underline{\;2\;}$ y escaleras). No revela la solución de golpe. |
| ⚖️ **El Tribunal Evaluador** | *"Hazme un test"*, *"examen"* | Genera preguntas cerradas tipo test (A, B, C, D) con 3 distractores basados en las trampas reales del temario. |
| 🌱 **El Mentor Intuitivo** | *"Explícame qué es..."*, *"dudas"* | Aplica la tríada: *Analogía cotidiana $\to$ Definición formal $	o$ Diagrama Mermaid*. |
| 🧭 **El Coach de Rescate** | *"He suspendido"*, *"recuperar"* | Diagnostica en qué fallaste y te diseña un plan de mínimos con lo imprescindible para aprobar. |
| ⚡ **Hoja de Resumen (Cheat Sheet)** | *"Chuleta para el bus en 10 min"* | Comprime el tema en 1 sola pantalla: tabla oro, fórmulas, rangos y trucos de examen sin paja teórica. |

---

## 🏛️ ARQUITECTURA TÉCNICA: DESACOPLAMIENTO DE RECURSOS

```text
    TU MEMORIA RAM Y CPU                               TARJETA GRÁFICA (VRAM)
┌─────────────────────────────────┐               ┌───────────────────────────────┐
│     Motor Python (LlamaIndex)   │               │         Bionic Studio         │
│                                 │               │           (Qwen 2.5)          │
│ • Lee PDFs página a página      │    JSON       │                               │
│ • Índices aislados por materia  │ ────────────> │ • Recibe fragmentos + página  │
│ • Búsqueda en < 10 milisegundos │   Fragmento   │ • Redacta lecciones en KaTeX  │
│ • CERO consumo de VRAM          │   + Página    │ • Cita: [Archivo.pdf, Pág X]  │
└─────────────────────────────────┘               └───────────────────────────────┘
```

1. **Cero consumo de VRAM:** El motor RAG corre en la CPU y RAM. Tu tarjeta gráfica queda 100% libre para que el modelo local corra a máxima velocidad.
2. **Citas Verificables Obligatorias:** Ninguna afirmación se hace sin indicar `[Fuente: Archivo.pdf, Página: X]`.
3. **Blindaje Anti-Alucinación:** Si preguntas por algo ajeno al temario (ej. fotosíntesis en una clase de redes), el tutor te dice con total honestidad que no aparece en tus apuntes.

---

## 🧪 BANCO DE PRUEBAS AUTOMATIZADO

El motor incluye su propia suite de pruebas de estrés (`motor/simulador_tutor.py`) con 11 auditorías (100% PASS). Puedes comprobar su estado con:

```bash
python motor/simulador_tutor.py
```
