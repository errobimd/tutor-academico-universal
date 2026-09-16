# 🎓 Guía Rápida de Instalación y Uso: Tutor Académico Inteligente
> **Tutor particular 100% offline y privado para Bionic Studio (LM Studio Bionic), con motor LlamaIndex, KaTeX riguroso, menús por asignatura, 4 sub-roles pedagógicos y modo Cheat Sheet.**

---

## ⚡ 1. ¿Qué es este Tutor Académico?

Este tutor es un profesor particular de alto rendimiento diseñado para ayudarte a estudiar y aprobar tus asignaturas usando **exclusivamente tus propios apuntes** (PDFs y DOCXs). 

* 🔒 **100% Offline y Privado:** Tus documentos nunca salen de tu ordenador.
* 🚀 **Cero consumo de VRAM en búsqueda:** El motor RAG corre en tu CPU y RAM; toda la potencia de tu tarjeta gráfica se reserva para que el modelo responda a máxima velocidad.
* 📐 **Fórmulas y Esquemas:** Renderiza operaciones matemáticas paso a paso y diagramas visuales (Mermaid).
* 🎭 **4 Sub-Roles Pedagógicos Dinámicos:**
  * 🔧 **El Entrenador Práctico:** Desglosa problemas numéricos y conversiones paso a paso.
  * ⚖️ **El Tribunal Evaluador:** Te pone a prueba con exámenes tipo test con preguntas trampa.
  * 🌱 **El Mentor Intuitivo:** Te explica conceptos complejos con analogías cotidianas y diagramas.
  * 🧭 **El Coach de Rescate:** Te rescata si has suspendido, diseñándote un plan de mínimos.
  * ⚡ **Modo Cheat Sheet (Autobús):** Comprime cualquier tema en 1 sola pantalla para repasar 10 minutos antes del examen.

---

## 🧠 2. Modelos de Lenguaje (LLMs) Recomendados

Para que el tutor responda con la máxima inteligencia pedagógica, estructura impecable y sin errores de formato:

### 🏆 Recomendación Estrella (Para PCs Potentes con 16 GB a 24 GB de VRAM):
👉 **`Qwen 2.5 32B Instruct` (Cuantización Q4_K_M o Q5_K_M)**
* **¿Por qué es el mejor?** Es el modelo abierto número 1 del mundo en su tamaño para educación técnica. Tiene un dominio nativo del castellano, razona problemas complejos paso a paso, dibuja diagramas perfectos y jamás sufre bucles de repetición.
* **Requisitos:** Tarjeta gráfica como RTX 3090, RTX 4080, RTX 4090 o equipos con memoria unificada (Apple Silicon M2/M3/M4 de 32GB+).

### 🥈 Opción Probada y Muy Eficiente (8 GB a 12 GB de VRAM):
👉 **`Gemma 4 / 2 12B QAT`** o **`Qwen 2.5 14B Instruct`**
* **¿Por qué?** Funciona con una agilidad fantástica, consume muy poca memoria y mantiene una gran precisión en explicaciones teóricas y diagramas.

### 🥉 Opción Extrema (Para estaciones de trabajo con 24 GB+ o doble GPU):
👉 **`Qwen 2.5 72B Instruct`** o **`Llama 3.3 70B Instruct`**
* Máxima fidelidad y profundidad universitaria.

> 💡 **Ajuste de Oro en Bionic Studio / LM Studio:**  
> En los ajustes de inferencia del modelo (barra lateral derecha), configura el parámetro **`Repetition Penalty` en `1.1`** (en lugar de 1.0). Esto evita que el modelo "tartamudee" o repita bloques en respuestas muy largas.

---

## 🚀 3. Instalación Rápida (Elige tu método)

### 🥇 Método 1: En 1 Clic desde PowerShell (Recomendado)
1. Abre **PowerShell** en tu ordenador (pulsa la tecla Windows, escribe `powershell` y pulsa Enter).
2. Copia y pega esta única línea de comando:

```powershell
git clone https://github.com/errobimd/tutor-academico-universal.git "$HOME\.agents\skills\tutor-academico"
```

3. Abre **Bionic Studio**, crea un nuevo chat y ya tendrás disponible **`@tutor-academico`**.

---

### 🥈 Método 2: Descarga Manual Directa (Sin comandos)
1. Entra al repositorio oficial:  
   🔗 **[https://github.com/errobimd/tutor-academico-universal](https://github.com/errobimd/tutor-academico-universal)**
2. Haz clic en el botón verde superior **`Code`** y selecciona **`Download ZIP`**.
3. Descomprime el archivo descargado.
4. Cambia el nombre de la carpeta a `tutor-academico` y cópiala en tu ruta de habilidades:
   * **En Windows:** `C:\Users\<TuUsuario>\.agents\skills\tutor-academico`
   * *(O también en:* `C:\Users\<TuUsuario>\.cache\lm-studio\skills\tutor-academico`*)*
   * **En Mac / Linux:** `~/.agents/skills/tutor-academico`
5. Abre o reinicia **Bionic Studio**.

---

## 📂 4. Cómo Organizar tus Apuntes de Estudio

El tutor es **100% universal**: sirve para cualquier curso o carrera (Informática, Redes, Biología, Medicina, Derecho, etc.).

Solo debes colocar tus carpetas de asignaturas en tu espacio de trabajo de la siguiente forma:

```text
Mi_Espacio_De_Estudio/
│
├── 1 Evaluación/                       <- Carpetas de tus asignaturas
│   ├── Planificación de Redes/
│   │   ├── Tema 1 - Numeración.pdf
│   │   └── Ejercicios_Binario.docx
│   │
│   └── Gestión de Bases de Datos/
│       └── Apuntes_Modelo_Relacional.pdf
│
└── Otras Materias (Opcional)/
    └── Biología Marina/
        └── Tema_Cetaceos.pdf
```

El motor del tutor detectará automáticamente los nombres de las carpetas y creará un menú numerado para que elijas qué estudiar.

---

## 💬 5. Primeros Pasos en el Chat de Bionic Studio

### Paso 1: Saludo e Inicio
Abre un nuevo chat en Bionic Studio y escribe:
```text
@tutor-academico Hola, ¿qué asignaturas tenemos disponibles hoy?
```
El tutor te responderá dándote la bienvenida y mostrándote el menú numerado de tus materias descubiertas.

---

### Paso 2: Ejemplos de Mensajes para Estudiar

Copia y pega cualquiera de estos ejemplos para activar los diferentes modos:

* 🔧 **Para resolver problemas paso a paso (Entrenador):**
  > *"Quiero estudiar Redes. Ponme un ejercicio de conversión de decimal a binario paso a paso y desglosa los cálculos."*

* ⚖️ **Para ponerte a prueba antes de un examen (Tribunal):**
  > *"Elige Bases de Datos y hazme una pregunta de examen tipo test con 4 opciones (A, B, C, D) sobre claves primarias y foráneas."*

* 🌱 **Para entender conceptos difíciles con diagramas (Mentor):**
  > *"Quiero estudiar Lenguajes de Marcas. Explícame qué es el árbol DOM en HTML con una analogía de la vida real y un diagrama visual."*

* 🧭 **Si has suspendido o vas mal de tiempo (Coach de Rescate):**
  > *"He suspendido el primer parcial de Sistemas Operativos en la parte de permisos y procesos. Necesito un plan quirúrgico de mínimos para aprobar la recuperación."*

* ⚡ **Para repasar justo antes del examen (Modo Autobús):**
  > *"Hazme una hoja de resumen de 1 página (Cheat Sheet) de Redes para repasar en el autobús 10 minutos antes del examen."*

---

## 🛠️ 6. Solución Rápida a Dudas Frecuentes

1. **¿Qué hago si no me sale `@tutor-academico` al escribir `@`?**  
   Cierra completamente la ventana de Bionic Studio y vuelve a abrirla. Al arrancar, escaneará la carpeta `.agents\skills` y lo detectará automáticamente.
2. **¿Cómo hacer que cite las páginas exactas de mis PDFs?**  
   Arrastra el archivo PDF dentro del chat de Bionic Studio o usa el icono de adjuntar archivo. De este modo, el modelo leerá la página física real y te la citará al pie de su respuesta: `[Fuente: Apuntes.pdf, Página X]`.
3. **¿Puedo cambiar de asignatura a mitad de sesión?**  
   Sí, en cualquier momento puedes escribirle: *"Quiero cambiar de materia"* y te volverá a mostrar el menú de opciones.

---
*Manual oficial generado para el Tutor Académico Inteligente Universal.*
