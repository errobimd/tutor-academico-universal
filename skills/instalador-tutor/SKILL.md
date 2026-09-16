---
name: instalador-tutor
description: Habilidad de instalación automática en 1 paso para Bionic Studio. Descarga el motor universal del Tutor Académico desde GitHub (errobimd) y registra la habilidad definitiva @tutor-academico.
---

# HABILIDAD DE INSTALACIÓN AUTOMÁTICA: @instalador-tutor

## 🎯 PROPÓSITO
Esta habilidad es un **instalador autónomo**. Su única función es preparar el espacio de trabajo del estudiante, descargar los componentes del motor RAG universal desde el repositorio oficial de GitHub de errobimd y registrar la habilidad definitiva: `@tutor-academico`.

---

## 🚀 PROTOCOLO DE INSTALACIÓN EN 3 PASOS

Cuando el usuario invoque esta habilidad (escribiendo `@instalador-tutor` o ejecutando el prompt oficial de bienvenida), ejecutarás silenciosamente estos 3 pasos:

### PASO 1: Verificación del Espacio de Trabajo
1. Comprueba si existe la carpeta `skills/tutor-academico/`.
2. Si no existe, créala.
3. Comprueba si el alumno ya tiene alguna carpeta de apuntes (como `1 Evaluación/`, `Apuntes/`, `Biología/`, `Redes/`, etc.). Si no la tiene, prepárate para orientarle de forma amable tras la instalación.

### PASO 2: Despliegue del Motor y Registro de la Habilidad
1. Registra la habilidad `@tutor-academico` copiando la especificación oficial con:
   - Menú dinámico de asignaturas.
   - Los 4 sub-roles pedagógicos (Entrenador con KaTeX, Tribunal con exámenes A/B/C/D, Mentor con diagramas Mermaid y Coach de rescate tras suspensos).
   - Modo Hoja de Resumen (Cheat Sheet de 1 página).
   - Blindaje anti-alucinaciones y citas de página obligatorias.
2. Asegura la disponibilidad de los scripts del motor universal (`auto_gestor.py`, `indexador_academico.py`, `consultor_rag.py`).

### PASO 3: Mensaje Final de Bienvenida al Alumno
Presenta al alumno este mensaje de éxito:

> 🎉 **¡Instalación completada con éxito!**  
> Tu Tutor Académico Inteligente ya está listo en Bionic Studio.  
> 
> 👉 **¿Cómo empezar?**  
> Escribe simplemente: **`@tutor-academico`** en el chat.  
> 
> 💡 *Recuerda: Si aún no has pegado tus apuntes, coloca tus carpetas de asignaturas con sus PDFs dentro de este proyecto y el tutor los indexará automáticamente al comenzar.*
