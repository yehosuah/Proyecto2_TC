# Proyecto 2: simplificación de CFG y algoritmo CYK

[Ver video de presentación](https://youtu.be/o0sZ9axf5T0?si=T53W78BlWkgml0Ma)

Programa en Python 3.9 o posterior, sin paquetes externos. Lee una gramática,
la simplifica, la convierte a Chomsky y reconoce una frase con programación
dinámica. Muestra SÍ/NO, tiempo y un árbol si la acepta.

| Parte | Responsable | Estado |
| --- | --- | --- |
| Modelo, lector, simplificación y Chomsky | Yehosua | Implementado con asistencia de Codex |
| CYK, árbol y tiempo | Miguel Rosas | Implementado con asistencia de Codex |
| Integración y documentación | Ambos | Programa y reporte completos; revisión humana conjunta pendiente |

## Ejecutar

En Windows usar `py -3`; en Linux/macOS, `python3` en los mismos comandos.
Desde la raíz del repositorio:

```powershell
py -3 main.py data/ingles.txt --sentence "She eats a cake with a fork"
py -3 main.py data/ingles.txt --sentence "she eats cake"
py -3 main.py data/ingles.txt --sentence ""
"He cooks" | py -3 main.py data/ingles.txt --stdin
py -3 main.py data/1.txt --sentence "( id ) + id"
py -3 -m unittest discover -s tests -v
py -3 benchmark.py --repeat 100
```

Ejemplo de salida para `she eats`:

```text
SÍ
Tiempo de reconocimiento: 0.000017450 s
Árbol sintáctico (CNF):
S
  NP
    she
  VP
    eats
```

La duración varía. El cronómetro incluye índices, tabla CYK y decisión;
excluye lectura, conversión, normalización, validación de CNF, reconstrucción
e impresión del árbol.

Se normaliza a minúsculas y se separa por espacios en blanco, incluidos tabuladores
y saltos de línea. `--case-sensitive` conserva mayúsculas. La puntuación se
conserva: `she eats.` se rechaza. Para aritmética separar también paréntesis
y operadores. `--stdin` consume toda la entrada como una frase y no puede
combinarse con `--sentence`. La entrada vacía se acepta solo si la CNF tiene
una regla vacía del inicio. La validación es sintáctica: `the cake drinks a knife`
se acepta aunque su significado sea extraño.

SÍ y NO terminan con código 0; errores de archivo/gramática/opciones con código 2.
Un rechazo no imprime árbol.

## Conversión y exportación

Sin opciones de frase se conserva el comando original:

```powershell
py -3 main.py data/1.txt
py -3 main.py data/1.txt --output output/aritmetica-cnf.txt --trace-dir output/etapas-aritmetica
py -3 main.py data/ingles.txt --sentence "he cooks" --output output/ingles-cnf.txt
```

`--trace-dir` guarda siete instantáneas: original y seis transformaciones.
`--start E` permite elegir el inicio. Los destinos no pueden coincidir con la
entrada ni entre salida y etapas. `output/` es regenerable y no se versiona.

## API y estructura

```python
from cfg import read_grammar, convert_to_cnf, cyk

conversion = convert_to_cnf(read_grammar("data/ingles.txt"))
result = cyk(conversion.grammar, "she eats".split())
print(result.accepted, result.elapsed_seconds)
if result.tree is not None:
    print(result.tree.to_text())
    assert result.tree.leaves() == result.tokens
```

La API recibe tokens exactos, sin normalizarlos, y exige CNF estricta.
El árbol pertenece a la gramática convertida; en inglés coincide con la original.

| Archivo | Función |
| --- | --- |
| `cfg/grammar.py` | Modelo, lectura y serialización |
| `cfg/cnf.py` | Simplificación y conversión a Chomsky |
| `cfg/cyk.py` | Tabla dinámica, resultado, árbol y cronómetro |
| `main.py` | Consola de conversión y reconocimiento |
| `benchmark.py` | Medianas reproducibles para nueve ejemplos |
| `tests/test_conversion.py` | 20 pruebas originales y oráculo independiente |
| `tests/test_cyk.py` | 9 pruebas de reconocimiento y árboles |
| `tests/test_cli_cyk.py` | 5 pruebas de integración de consola |
| `docs/reporte-final.md` | Diseño integrado, discusión, pruebas y tiempos |
| `docs/primera-mitad.md` | Detalle de transformaciones |
| `docs/entrega-miguel.md` | Contrato actualizado |
| `docs/colaboracion.md` | Contribuciones y revisiones pendientes |

## Formato de gramática

```text
S -> NP VP
NP -> she | he
VP -> eats
```

Separar símbolos con espacios y alternativas con `|`. `NP` e `id` son tokens
completos. `e` o `ε`, solos, representan vacío y están reservados. Los lados
izquierdos, el inicio y `%nonterminals` definen no terminales; los demás símbolos
son terminales, independientemente de sus mayúsculas. El primer lado izquierdo
es el inicio, salvo `%start S` o `--start`. Se admiten líneas vacías y comentarios
completos con `#`. Los símbolos no admiten espacios ni delimitadores reservados.
`%nonterminals A B` conserva símbolos sin reglas.

Una gramática `%start S` sin reglas genera ∅; `S -> e` genera {ε}.
El enunciado asigna 7 puntos a simplificación, 7 a CYK y 1 a documentación;
la documentación es obligatoria. Las pruebas locales y sus límites están en
el [reporte final](docs/reporte-final.md).
