# 📜 MEMORIA HISTÓRICA Y TÉCNICA DE LA SESIÓN DE TRABAJO
**Proyecto:** Tutor Académico Universal & Gestor Autónomo de Biblioteca con LlamaIndex RAG  
**Fecha:** 17 de Septiembre de 2026  
**Repositorio GitHub:** [`errobimd/tutor-academico-universal`](https://github.com/errobimd/tutor-academico-universal)  
**Entorno de Trabajo:** Antigravity IDE (Local, Soberano y Offline) / Compatible con Bionic  

---

## 🎯 1. Resumen de Objetivos Planteados
El usuario solicitó evolucionar el sistema desde un tutor conversacional básico hacia un **ecosistema de tutoría académica y organización bibliotecaria integral**, guiado por principios pedagógicos claros y adaptado a las necesidades de un estudiante de ciclo formativo o instituto que no tiene por qué poseer conocimientos avanzados de informática.

Los ejes estratégicos acordados han sido:
1. **Autonomía Pedagógica del Alumno (Menú en 5 Pasos):** Que el tutor no imponga un orden rígido, sino que ofrezca un panel de 5 opciones para que el estudiante elija libremente por dónde empezar.
2. **Generación de Chuletas A4 Imprimibles:** Crear un recurso físico de alta densidad informativa maquetado para caber exactamente en 1 folio A4 sin desbordamientos.
3. **Representación Natural de Fórmulas y Divisiones Sucesivas:** Superar la fragilidad de matrices TeX genéricas e implementar los cajetines tradicionales de examen de la escuela española con restos marcados en círculos y guía de lectura.
4. **Segregación Inteligente de Ámbitos (Curricular vs Aficiones):** Reconocer y separar automáticamente asignaturas escolares de intereses personales (como mascotas o huerto), manteniendo limpio el temario de examen.
5. **Clarificación Conceptual:** Definir con rigor la distinción entre RAG (la estrategia metodológica) y LlamaIndex (la librería que ejecuta el RAG en local).
6. **Enfoque Pragmático para Bionic:** Diseñar una habilidad (Skill) nativa y un prompt maestro de activación de 1 clic sin necesidad de desplegar servidores complejos en la nube como RunPod.

---

## 🧭 2. Crónica del Desarrollo y Decisiones de Diseño

### 2.1. El Itinerario Didáctico en 5 Etapas
Se estructuró la intervención docente de la IA en 5 fases progresivas:
- **Etapa 1 (Glosario Intuitivo):** Tríada didáctica (Analogía cotidiana para niños de 10 años + Definición formal de los apuntes + Ejemplo real).
- **Etapa 2 (Guía Visual Mermaid):** Diagramas de bloques (`flowchart`, `graph`) con los 3 a 5 conceptos clave sin paja.
- **Etapa 3 (Taller KaTeX y Cajetines):** Práctica guiada socrática con matemáticas claras.
- **Etapa 4 (Evaluación Dual):** Test cerrado de 4 opciones con distractores basados en errores reales del apunte + 2 preguntas de desarrollo abierto.
- **Etapa 5 (Chuleta de 1 Vistazo):** Ficha de máxima densidad para repasar en el autobús en 5 minutos.

### 2.2. La Evolución de la Chuleta A4 y el Desafío de las Divisiones Sucesivas
- **Problema Detectado:** Al generar inicialmente la chuleta HTML para la asignatura de Redes (`REDA`), el navegador mostraba código TeX crudo debido a colisiones en los delimitadores inline `$`.
- **Intervención Pedagógica del Usuario:** El usuario señaló con gran acierto que *"las divisiones sucesivas no se muestran como tal, escritas en un papel"*.
- **Solución Implementada:** Se diseñó el componente visual `.paper-math` con cajetines tradicionales de división hispanos ($\lfloor\underline{\;2\;}$):
  - El dividendo `53` entra en el cajetín con el divisor `2`.
  - El cociente `26` abre el siguiente cajetín a la derecha, mientras que debajo queda el resto `(1)` en un círculo rojo.
  - La escalera continúa hasta el último cociente `[1]` en círculo verde.
  - Una flecha de lectura de abajo hacia arriba guía el sentido: $\mathbf{1} \to \mathbf{1} \to \mathbf{0} \to \mathbf{1} \to \mathbf{0} \to \mathbf{1} \implies 53_{10} = \mathbf{110101}_2$.
- **Auditoría Empírica en Navegador:** Se verificó visualmente con el agente-navegador (`browser_subagent`), capturando la imagen real que confirmó un renderizado perfecto tanto en pantalla como al imprimir en 1 hoja A4 con `@media print`.

### 2.3. Detección Inteligente de Ámbitos: El Caso del Gato y los Tomates
- **Problema de la Contaminación:** Si el alumno sube una guía de alimentación de gatos o de cultivo de tomates a la carpeta de estudio, un RAG descuidado mezclaría gatos con protocolos de red.
- **Solución Algorítmica:** Se incorporó en `auto_gestor.py` la función `evaluar_ambito_documento`.
  - Lee la portada y el texto inicial.
  - Compara con los descriptores curriculares oficiales de Informática (`REDA`, `GEBD`, `IMSO`, `LEMA`, `DISI`).
  - Al detectar términos zoológicos o botánicos, diagnostica `0% coincidencia académica` y clasifica el archivo como `INTERES_PERSONAL`.
  - El tutor formula una sugerencia respetuosa al alumno: *"Veo que has añadido un documento sobre cuidado de gatos. Como no es de tus asignaturas escolares, ¿quieres que lo guardemos en tu sección 'Intereses Personales/Mascotas' para mantener limpias tus materias de examen?"*.
  - Solo si el alumno lo autoriza, traslada el archivo y actualiza el catálogo vivo en `TEMARIO_ACTIVO.md`.

### 2.4. Clarificación Fundamental: RAG vs LlamaIndex
Durante la conversación se abordó la diferencia esencial entre ambos términos:
- **RAG (Retrieval-Augmented Generation):** Es el **concepto o la receta**. Establece que el modelo no debe alucinar de memoria, sino consultar fragmentos relevantes en los apuntes y responder citando la fuente.
- **LlamaIndex:** Es el **robot de cocina / software en Python** que ejecuta esa receta: trocea los PDFs, genera los vectores semánticos en disco local (`storage_index/`), y recupera el fragmento con su número de página en milisegundos.

### 2.5. Apuesta por la Simplicidad y la Soberanía Local (Bionic)
El usuario evaluó la opción de desplegar servidores web o nubes como RunPod, concluyendo que la experiencia de usuario óptima para un alumno que ya tiene **Bionic** consiste en centrarse en el **Skill** (`SKILL.md`).
- Se descartaron complejidades en la nube.
- Se creó la guía [`PROMPT_ACTIVACION_BIONIC.md`](file:///d:/Biblioteca_Temas/PROMPT_ACTIVACION_BIONIC.md) con el prompt de 1 clic.
- Todo el conocimiento queda respaldado en el repositorio GitHub oficial.

---

## 📦 3. Archivos y Módulos Clave del Sistema

| Archivo | Ubicación | Función Principal |
| :--- | :--- | :--- |
| `SKILL.md` | `.agents/skills/tutor-academico/SKILL.md` | Habilidad maestra para Bionic/Antigravity con el itinerario de 5 etapas y reglas anti-alucinación. |
| `generador_chuletas_html.py` | `Plantemiento con indexacion/laboratorio_indexacion/` | Generador de chuletas A4 imprimibles con cajetines tradicionales de examen y KaTeX. |
| `auto_gestor.py` | `Plantemiento con indexacion/laboratorio_indexacion/` | Centinela de biblioteca, analizador de portadas y separador de materias vs aficiones. |
| `consultor_rag.py` | `Plantemiento con indexacion/laboratorio_indexacion/` | Motor de consulta RAG sobre LlamaIndex con citas por página oficial. |
| `indexador_academico.py` | `Plantemiento con indexacion/laboratorio_indexacion/` | Indexador vectorial que construye la memoria local en `storage_index/`. |
| `REVISION_GENERAL_Y_ESTADO_PROYECTO.md` | Raíz del proyecto y repositorio | Documento de balance integral y catálogo de materias. |
| `PROMPT_ACTIVACION_BIONIC.md` | Raíz del proyecto y repositorio | Prompt de 1 clic para arrancar el tutor en Bionic. |
| `CHULETA_REDA.html` | `html/` y carpeta de la materia | Hoja A4 auditada visualmente con la escalera tradicional de divisiones. |

---

## 🔬 4. Certificación y Veredicto Empírico
Todas las modificaciones fueron verificadas mediante ejecución en terminal, auditoría en navegador web headless en tiempo real y sincronización en GitHub.
- **Veredicto:** `"Corrección Segura"`
- **Rama:** `main`
