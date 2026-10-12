# Proyecto 2: simplificación de CFG y algoritmo CYK

Proyecto de Teoría de la Computación, desarrollado por etapas en Python.
La primera mitad implementa la simplificación y conversión a forma normal de
Chomsky. La segunda mitad, a cargo de Miguel Rosas, está pendiente.

| Parte | Responsable | Estado |
| --- | --- | --- |
| Modelo, lector, simplificación y Chomsky | Yehosua | Implementación asistida por Codex; 20 pruebas pasan; revisión personal pendiente |
| CYK, árbol sintáctico y tiempo de reconocimiento | Miguel Rosas | Pendiente |
| Integración, ejemplos de frases y reporte final | Ambos | Pendiente |

El programa actual convierte gramáticas. Todavía no reconoce frases ni genera
árboles sintácticos. Esa es la entrega que desarrollará Miguel.

## Ejecutar la primera mitad

Requiere Python 3.9 o posterior, sin paquetes externos. Desde la raíz del repo:

```bash
python3 main.py data/1.txt
python3 main.py data/1.txt --output output/aritmetica-cnf.txt --trace-dir output/etapas-aritmetica
python3 main.py data/ingles.txt --output output/ingles-cnf.txt
python3 -m unittest discover -s tests -v
```

`--trace-dir` guarda el original y las seis transformaciones en archivos separados.
`--start E` permite elegir el símbolo inicial. Los errores de entrada terminan
con código 2 y un mensaje en stderr. `output/` es regenerable y no se versiona.

## Estructura

```text
cfg/grammar.py          Modelo, lectura y escritura de gramáticas
cfg/cnf.py              Simplificación, conversión y validación de CNF
main.py                 Interfaz de conversión por consola
data/1.txt              Gramática aritmética proporcionada
data/1-cnf.txt          Resultado de referencia proporcionado
data/ingles.txt         Gramática inglesa del enunciado
tests/test_conversion.py
docs/primera-mitad.md   Diseño, explicación, discusión y validación
docs/entrega-miguel.md  Contrato de integración y trabajo pendiente
docs/colaboracion.md    Etapas y registro de contribuciones
```

## Formato de gramática

```text
S -> NP VP
NP -> she | he
VP -> eats
```

- Separar los símbolos con espacios; `NP` e `id` son símbolos completos.
- Separar alternativas con `|` y usar `->` para cada producción.
- `e` o `ε`, solos, representan la cadena vacía; están reservados.
- Los lados izquierdos definen no terminales. Los demás símbolos son terminales,
  independientemente de si están escritos en mayúsculas.
- El primer lado izquierdo es el inicio, salvo cabecera `%start S` o `--start`.
- `%nonterminals A B` permite declarar no terminales sin reglas. Las etapas
  intermedias pueden necesitar esa cabecera para conservar su clasificación.
- Se admiten líneas vacías y comentarios de línea completa con `#`.
- No se admiten terminales con espacios ni los delimitadores reservados como símbolos.

La salida usa `%start` para conservar el inicio incluso si no quedan reglas.
Una gramática sin reglas genera el lenguaje vacío; una regla `S -> e` genera
la cadena vacía. Son casos distintos.

## Criterios del proyecto

El enunciado asigna 7 puntos a simplificación, 7 a CYK y 1 a documentación.
Exige respuesta SÍ/NO, tiempo de validación, árbol sintáctico y documentación
de diseño, discusión y pruebas. La documentación es obligatoria para tener nota.

La gramática inglesa ya satisface la forma de Chomsky, pero eso no reemplaza
la implementación del conversor. Los archivos aritméticos permiten ejercitarla.
El conversor usa la variante estricta que impide el inicio a la derecha; por eso
puede introducir un nuevo inicio y nombres auxiliares diferentes del ejemplo.

La documentación actual corresponde a la primera mitad. El reporte completo
se cerrará cuando Miguel termine su módulo y ambos revisen la integración.

Para continuar, leer [la entrega a Miguel](docs/entrega-miguel.md).
