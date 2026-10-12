# Reporte final: simplificación, Chomsky y CYK

## Objetivo y diseño integrado

El programa reconoce si una frase pertenece al lenguaje de una CFG y devuelve
SÍ/NO, duración y un árbol para una aceptación. Python 3.9+ y su biblioteca
estándar permiten ejecutar el proyecto sin instalar dependencias.

Flujo: archivo → `read_grammar` → `Grammar` → `convert_to_cnf` →
tokens de la frase → `cyk` → `CYKResult` → salida de consola.
La conexión usa el objeto directamente, sin archivos intermedios.

La primera mitad conserva el lenguaje al proteger el inicio, eliminar epsilon
y unitarias, retirar símbolos inútiles, separar terminales y binarizar cuerpos.
El modelo mantiene no terminales declarados para evitar que un símbolo sin
reglas se reclasifique como terminal. Se exportan siete instantáneas.
El [informe de primera mitad](primera-mitad.md) desarrolla cada transformación,
sus invariantes y pruebas. La CNF tiene reglas A → B C, A → terminal y,
opcionalmente, inicio → ε; el inicio no aparece a la derecha.

## Programación dinámica

Para n tokens, la celda T[i,j] representa el intervalo semiabierto [i,j).
Sus claves son los no terminales que derivan esos tokens; sus valores guardan
una producción y, para reglas binarias, el punto de división.
Se construyen índices terminal → reglas y (B,C) → reglas binarias.

1. Para cada token i, agregar A a T[i,i+1] cuando existe A → token.
2. Recorrer longitudes de 2 a n y todos sus intervalos.
3. Para cada separación k, combinar B de T[i,k] y C de T[k,j].
   Si existe A → B C, agregar A con esa regla y separación.
4. Aceptar si el inicio pertenece a T[0,n]. Para n=0, aceptar exclusivamente
   si existe la producción vacía del inicio.

El caso base corresponde exactamente a reglas terminales. Por inducción sobre
la longitud, cada combinación agrega una derivación válida del intervalo.
Toda derivación CNF no vacía tiene una raíz terminal o binaria con alguna
separación k; examinar todas asegura que la tabla encuentre cada derivación
posible. Esto fundamenta la decisión de pertenencia.

Se guarda una derivación por símbolo y celda. Reglas y símbolos se ordenan y
las separaciones se prueban en orden ascendente, por lo que la elección es
determinista en gramáticas ambiguas. No se enumeran todos los árboles.

## Resultado y árbol

`CYKResult` es inmutable: `accepted`, `tokens`, `elapsed_seconds` y `tree`
(`None` para rechazos). Cada `ParseTree` registra una `Production` y sus hijos:
dos nodos para reglas binarias, un terminal para reglas léxicas o ningún hijo
para epsilon. `leaves()` devuelve los tokens en orden; `to_text()` genera el
árbol indentado y muestra ε para el árbol vacío.

La reconstrucción usa postorden con una pila explícita; las hojas y la impresión
también usan pilas. No dependen del límite de recursión de Python. El árbol
pertenece a la CNF: en inglés esta coincide con la original; otras gramáticas
pueden introducir auxiliares o inicio nuevo. Recuperar el árbol original exige
correspondencias entre transformaciones y queda fuera del alcance acordado.

## Complejidad y cronómetro

Para gramática fija, CYK toma O(n³) tiempo y O(n²) espacio. Con N no terminales
y P producciones, la tabla ocupa O(n²N), más O(P) para índices. Cada separación
considera hasta N² pares y P reglas. La ordenación repetida de celdas permite
una cota conservadora O(n³(N² log(N+1) + P)), además de preparar y ordenar
producciones. El árbol no vacío tiene O(n) nodos. Su texto indentado puede ocupar
O(n²) caracteres en árboles profundos. La conversión previa puede generar hasta
2^k variantes para k ocurrencias anulables; esta limitación sigue vigente.

`time.perf_counter` empieza antes de construir índices y tabla y termina tras
decidir pertenencia. Excluye lectura/conversión, preparación de tokens,
validación de CNF, reconstrucción y formato/impresión del árbol. La consola
publica segundos con nueve decimales.

## Entrada e integración

La consola aplica `lower().split()` por defecto, admitiendo mayúscula inicial,
espacios repetidos, tabuladores y saltos de línea. `--case-sensitive` conserva
mayúsculas. La puntuación se conserva: `she eats.` se rechaza. La API recibe
tokens exactos, admite iterables y rechaza una cadena sin separar o tokens
vacíos, con espacios o de otro tipo. Un token desconocido produce NO.

`--sentence ""` representa una frase vacía. `--stdin` lee toda la entrada como
una frase. Sin estas opciones se conserva la conversión original; exportación,
etapas y `--start` pueden combinarse con reconocimiento. SÍ y NO terminan con
código 0; entradas inválidas con código 2. La sintaxis no evalúa significado:
`the cake drinks a knife` pertenece al lenguaje. No se agregó interfaz gráfica
ni analizador léxico para aritmética sin espacios.

## Pruebas y resultados observados

Validación local del 11 de octubre de 2026: Python 3.12.2, Windows AMD64.
`py -3 -m unittest discover -s tests -v`: **34 pruebas aprobadas**,
20 originales y 14 nuevas. No se atribuye ejecución de CI a cambios locales;
el flujo existente sigue configurado para Python 3.9 y 3.12.

Las pruebas nuevas comprueban nueve ejemplos, inicio distinto de S, ∅ y {ε},
tokens completos, reglas inválidas, ambigüedad, separaciones extremas,
símbolos repetidos, generadores, mayúsculas exactas y consola con exportación.
Los árboles examinados se verifican por raíz, reglas, símbolos de hijos y hojas
en el orden original. Los rechazos no tienen árbol.

El oráculo independiente enumera lenguajes por punto fijo. Se generaron 40 CFG
con semilla 2026 y se compararon las 15 palabras sobre {a,b} hasta longitud 3
con CYK tras conversión: **600 decisiones coincidentes**. También se reconocieron
todas las palabras aritméticas del oráculo hasta cinco tokens y se verificó su
igualdad con la referencia del docente. Esta evidencia es acotada, no una prueba
formal para todas las gramáticas y longitudes.

Mediciones reales: `py -3 benchmark.py --repeat 100`, un calentamiento por frase
y mediana de 100 ejecuciones del intervalo descrito, en la misma máquina.

| Frase | Tokens | Aceptada | Mediana (ms) |
| --- | ---: | --- | ---: |
| she eats a cake with a fork | 7 | SÍ | 0.042500 |
| the cat drinks the beer | 5 | SÍ | 0.029750 |
| he cooks | 2 | SÍ | 0.017250 |
| she eats | 2 | SÍ | 0.017450 |
| the cake drinks a knife | 5 | SÍ | 0.028550 |
| she eats cake | 3 | NO | 0.020000 |
| cat drinks the beer | 4 | NO | 0.022300 |
| she dances | 2 | NO | 0.016300 |
| (vacía) | 0 | NO | 0.016400 |

Estos tamaños pequeños no demuestran empíricamente la complejidad cúbica.
Los tiempos dependen del sistema y su carga; el script permite repetirlos.

## Discusión y entrega

La integración resolvió la diferencia entre frase y tokens, las mayúsculas del
enunciado, la cadena vacía, el inicio variable y la conservación de conversión.
Se midió solo reconocimiento para separar el costo de convertir una gramática
del de validar la frase. Las referencias por celda recuperan un árbol válido
sin multiplicar memoria por todas las derivaciones ambiguas.

En este entorno `python` apuntaba al alias de Microsoft Store; se verificó con
`py -3`, sin instalar paquetes ni modificar el sistema. El programa, pruebas
y documentación están completos para revisión. La revisión personal de Yehosua
y la conjunta siguen pendientes y no se presumen por pruebas automatizadas.
La segunda mitad se implementó con asistencia de Codex e identidad Git de Miguel.
