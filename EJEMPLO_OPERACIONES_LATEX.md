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
