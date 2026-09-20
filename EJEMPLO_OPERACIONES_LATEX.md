# EJEMPLOS VISUALES: OPERACIONES ESCRITAS (LATEX vs TEXTO)

Este archivo muestra cómo deben escribirse las operaciones matemáticas en el chat de Bionic Studio para que cualquier persona las entienda como si estuvieran escritas en una pizarra o en una libreta de clase.

> 💡 **Para ver cómo se dibuja en pantalla:** Puedes hacer doble clic en el archivo adjunto `EJEMPLO_OPERACIONES_LATEX.html` en tu navegador para ver la renderización gráfica exacta.

---

## 1. DIVISIONES SUCESIVAS (CONVERSIÓN DECIMAL A BINARIO)

### ❌ CÓMO NO SE DEBE HACER (Texto plano confuso que nadie entiende):
```text
53 / 2 = Cociente 26, Resto: 1
26 / 2 = Cociente 13, Resto: 0
13 / 2 = Cociente 6, Resto: 1
```

### ✅ CÓMO SE DEBE HACER (En KaTeX con cajetines de división encadenados o escalera):
El tutor escribirá cualquiera de estos formatos estándar 100% compatibles:

**Opción A: Cajetines Tradicionales Encadenados con Divisor Subrayado:**
```latex
$$
\begin{array}{r|l} 53 & \underline{\;2\;} \\ \mathbf{1} & 26 \end{array}
\;\xrightarrow{/2}\;
\begin{array}{r|l} 26 & \underline{\;2\;} \\ \mathbf{0} & 13 \end{array}
\;\xrightarrow{/2}\;
\begin{array}{r|l} 13 & \underline{\;2\;} \\ \mathbf{1} & 6 \end{array}
\;\xrightarrow{/2}\;
\begin{array}{r|l} 6 & \underline{\;2\;} \\ \mathbf{0} & 3 \end{array}
\;\xrightarrow{/2}\;
\begin{array}{r|l} 3 & \underline{\;2\;} \\ \mathbf{1} & \mathbf{1} \end{array}
$$
```

**Opción B: Escalera Vertical Tradicional en Columna:**
```latex
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
```

**Resultado visual que ve el alumno en pantalla:**
- Cada número tiene su cajetín de dividir (`|` y `\underline`) o su fila de resto claramente delimitada.
- Los restos aparecen destacados en negrita ($\mathbf{1, 0, 1, 0, 1}$).
- El último cociente ($\mathbf{1}$) cierra la cadena.
- Leyendo los restos de derecha a izquierda (o de abajo hacia arriba):
  $$\mathbf{53_{10} = 110101_2}$$

---

## 2. DIVISIÓN TRADICIONAL CON RESTAS DESGLOSADAS

Cuando se explica una división con resta paso a paso:

```latex
$$
\begin{array}{r@{\quad}l}
53 & \begin{array}{|l} 2 \\ \hline \end{array} \\
\underline{-4}\phantom{0} & 26 \\
13 & \\
\underline{-12} & \\
\mathbf{1} & \leftarrow \text{Resto final}
\end{array}
$$
```

---

## 3. SUMA BINARIA CON ACARREOS ALINEADOS

```latex
$$
\begin{array}{cccccc}
\text{Acarreos:} & \scriptstyle{1} & \scriptstyle{1} & \scriptstyle{1} & & \\
& & 1 & 1 & 0 & 1_2 \\
+ & & 0 & 1 & 1 & 1_2 \\
\hline
& 1 & 0 & 1 & 0 & 0_2
\end{array}
$$
```

---

## 4. TABLAS DE PONDERACIÓN POSICIONAL (CONVERSIÓN A DECIMAL)

Para conversiones numéricas de Binario, Octal o Hexadecimal a Decimal, se debe utilizar SIEMPRE una matriz encasillada `\begin{array}{|l|c|...}` con filas de Pesos, Dígitos y Aportes, aislada con saltos de línea propios.

### A. Binario a Decimal (Ejemplo: $101010_2 \to 42_{10}$):
```latex
$$
\begin{array}{|l|c|c|c|c|c|c|}
\hline
\text{\textbf{Posición}} & 5 & 4 & 3 & 2 & 1 & 0 \\
\hline
\text{\textbf{Potencia}} & 2^5 & 2^4 & 2^3 & 2^2 & 2^1 & 2^0 \\
\hline
\text{\textbf{Peso}} & 32 & 16 & 8 & 4 & 2 & 1 \\
\hline
\text{\textbf{Bit Binario}} & \mathbf{1} & 0 & \mathbf{1} & 0 & \mathbf{1} & 0 \\
\hline
\text{\textbf{Aporte Activo}} & \mathbf{32} & 0 & \mathbf{8} & 0 & \mathbf{2} & 0 \\
\hline
\end{array}
$$

$$
\text{\textbf{Suma activa: }} 32 + 8 + 2 = \mathbf{42_{10}}
$$
```

### B. Hexadecimal a Decimal (Ejemplo: $2F_{16} \to 47_{10}$):
```latex
$$
\begin{array}{|l|c|c|}
\hline
\text{\textbf{Posición}} & 1 & 0 \\
\hline
\text{\textbf{Potencia}} & 16^1 & 16^0 \\
\hline
\text{\textbf{Peso}} & 16 & 1 \\
\hline
\text{\textbf{Dígito Hex}} & \mathbf{2} & \mathbf{F}\;(15) \\
\hline
\text{\textbf{Cálculo Parcial}} & 2 \times 16 = 32 & 15 \times 1 = 15 \\
\hline
\end{array}
$$

$$
\text{\textbf{Total Decimal: }} 32 + 15 = \mathbf{47_{10}}
$$
```

---

## 5. REGLAS CRÍTICAS DE SINTAXIS KATEX (ANTI-ROTURA)

1. ⛔ **PROHIBIDO concatenar bloques en la misma línea:**  
   NUNCA escribas `$$ bloque 1 $$ $$ bloque 2 $$`. Cada bloque matemático `$$` debe comenzar y terminar en su propia línea independiente con saltos de línea.
2. ⛔ **PROHIBIDO falsear tablas con `\quad |\quad`:**  
   NUNCA intentes alinear datos en una sola línea usando barras verticales de texto. Usa siempre matrices estructuradas `\begin{array}` con delimitadores `&` y saltos de fila `\\ \hline`.
3. ⛔ **PROHIBIDO bloques de código para fórmulas:**  
   NUNCA uses triples comillas graves (\`\`\`latex, \`\`\`math o \`\`\`katex). Las fórmulas deben escribirse directamente en texto con `$$` para que Bionic las renderice de forma nativa.

