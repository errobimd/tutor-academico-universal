# 🎓 Tutor Académico Inteligente Universal (Offline & RAG Local)
> **Profesor particular autónomo para Bionic Studio (LM Studio Bionic) con LlamaIndex, KaTeX riguroso, menús por asignatura y 4 sub-roles pedagógicos.**

[![Bionic Studio](https://img.shields.io/badge/Bionic_Studio-Skill_Compatible-8A2BE2.svg)](#)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](#)
[![100% Offline](https://img.shields.io/badge/Privacidad-100%25_Local_%2F_Offline-green.svg)](#)
[![KaTeX](https://img.shields.io/badge/KaTeX-Math_Strict-critical.svg)](#)
[![Licencia MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#)

---

## ⚡ INSTALACIÓN EN 1 PASO (PARA EL ALUMNO)

No necesitas ejecutar terminales, ni archivos `.bat`, ni compilar código. Para instalar el tutor en tu ordenador:

1. Abre **Bionic Studio**.
2. Pulsa en **"Crear Skill desde Chat"** (o en la sección de Habilidades).
3. **Copia y pega este prompt oficial:**

```text
Instala el skill @instalador-tutor desde el repositorio oficial:
https://github.com/errobimd/tutor-academico-universal.git

Configura el entorno para desplegar el Tutor Académico Inteligente con motor LlamaIndex local, menús numerados por asignatura, 4 sub-roles pedagógicos y KaTeX riguroso.
```

4. ¡Y listo! Al finalizar, escribe simplemente **`@tutor-academico`** y tu profesor te dará la bienvenida.

---

## 📂 ¿CÓMO ORGANIZAR TUS APUNTES? (COMPATIBILIDAD UNIVERSAL)

El tutor es **100% agnóstico**: sirve para cualquier materia o carrera (Informática, Biología, Medicina, Derecho, Nutrición Animal, etc.). 

Solo coloca tus carpetas de apuntes dentro de tu espacio de trabajo:

```
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
└── Otras Materias (Ejemplo)/
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
| 🌱 **El Mentor Intuitivo** | *"Explícame qué es..."*, *"dudas"* | Aplica la tríada: *Analogía cotidiana $\to$ Definición formal $\to$ Diagrama Mermaid*. |
| 🧭 **El Coach de Rescate** | *"He suspendido"*, *"recuperar"* | Diagnostica en qué fallaste y te diseña un plan de mínimos con lo imprescindible para aprobar. |
| ⚡ **Hoja de Resumen (Cheat Sheet)** | *"Chuleta para el bus en 10 min"* | Comprime el tema en 1 sola pantalla: tabla oro, fórmulas, rangos y trucos de examen sin paja teórica. |

---

## 🏛️ ARQUITECTURA TÉCNICA: DESACOPLAMIENTO DE RECURSOS

```
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

El motor incluye su propia suite de pruebas de estrés (`motor/simulador_tutor.py`). Puedes comprobar su estado con:

```bash
python motor/simulador_tutor.py
```
> **Resultado del Pase de Pruebas Oficial:** **11/11 pruebas superadas con éxito (100% PASS)**.

---

## 👤 Autor y Licencia
Desarrollado y mantenido por **[@errobimd](https://github.com/errobimd)**.  
Distribuido bajo licencia MIT. ¡Siéntete libre de adaptarlo para tus propios estudios!
