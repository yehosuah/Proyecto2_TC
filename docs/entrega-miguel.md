# Entrega a Miguel Rosas

## Punto de partida

La primera mitad lee una CFG, la simplifica, la convierte a Chomsky y valida el
resultado. Tu segunda mitad consiste en implementar CYK, construir el árbol y
medir el tiempo de reconocimiento. Estos componentes no están implementados.

Primero ejecutar `python3 -m unittest discover -s tests -v`. Después revisar
`cfg/grammar.py`, el resultado de `python3 main.py data/ingles.txt` y este contrato.

## Contrato disponible

```python
from cfg import read_grammar, convert_to_cnf, validate_cnf

original = read_grammar("data/ingles.txt")
conversion = convert_to_cnf(original)
grammar = conversion.grammar
assert not validate_cnf(grammar)

print(grammar.start)          # "S" para la gramática inglesa
print(grammar.nonterminals)   # frozenset[str]
print(grammar.terminals)      # frozenset[str]
for production in sorted(grammar.productions):
    print(production.lhs, production.rhs)
```

Cada `rhs` es una tupla. Después de convertir, tendrá dos no terminales, un
terminal o estará vacía únicamente en una producción del inicio. No asumir que
el inicio siempre se llama S: consultar `grammar.start`.

El conversor también puede producir una gramática sin reglas: representa ∅.
Para una entrada de cero tokens, aceptar únicamente si existe la producción
`Production(grammar.start, ())`. La gramática inglesa no la tiene.

Puede usarse la API directamente; no hace falta escribir y volver a leer un
archivo entre conversión y reconocimiento.

## Tareas de la segunda mitad

1. Crear el módulo de CYK. Recibir una `Grammar` validada y una secuencia de
   tokens. Miguel define la estructura de su resultado y la documenta.
2. Llenar la tabla dinámica: palabras individuales, intervalos mayores y todos
   los puntos de separación. Decidir pertenencia usando `grammar.start`.
3. Guardar las reglas y separaciones utilizadas para recuperar al menos un árbol
   cuando la oración sea aceptada. El enunciado pide un árbol, no todos.
4. Medir con un reloj adecuado para duraciones, como `time.perf_counter`, y
   documentar qué se incluye en la medición. Separar la preparación de la
   gramática del tiempo de validación de la frase.
5. Integrar una entrada textual de frases y mostrar SÍ/NO, tiempo y árbol.
   Mantener disponible el comando de conversión, o documentar su nuevo comando.
6. Añadir pruebas propias en `tests/test_cyk.py` y escribir la sección de CYK
   del reporte. Revisar con Yehosua el recorrido completo.

La interfaz de frases debe decidir explícitamente el tratamiento de mayúsculas
y espacios. El enunciado da ejemplos con mayúscula inicial, mientras sus terminales
están en minúscula; se recomienda normalizar a minúsculas antes de separar palabras.
No eliminar puntuación silenciosamente: la gramática no contiene signos de puntuación.

## Casos previstos para verificar

Estos resultados se deducen de las reglas; aún no son resultados ejecutados de CYK.

| Entrada normalizada | Esperado | Razón |
| --- | --- | --- |
| `she eats a cake with a fork` | SÍ | NP seguido de VP; VP admite PP |
| `the cat drinks the beer` | SÍ | Ambas frases nominales usan Det N |
| `he cooks` | SÍ | VP puede ser un verbo terminal |
| `she eats` | SÍ | La gramática permite un verbo sin objeto |
| `the cake drinks a knife` | SÍ | Estructura válida aunque el significado sea extraño |
| `she eats cake` | NO | cake no es un NP sin determinante |
| `cat drinks the beer` | NO | cat no es un NP sin determinante |
| `she dances` | NO | dances no pertenece al vocabulario |
| cadena vacía | NO | La gramática inglesa no genera ε |

Añadir pruebas para ambigüedad, tokens desconocidos y reconstrucción del árbol:
sus hojas, de izquierda a derecha, deben coincidir con los tokens de la frase.

## Entrega de Miguel

La segunda mitad se considera lista cuando una frase entra al programa completo,
se convierte la gramática mediante la primera mitad, CYK determina pertenencia,
se muestra el tiempo y se obtiene un árbol para las frases aceptadas. Deben pasar
tanto las pruebas nuevas como las de conversión, y estar documentadas las decisiones.

Trabajar desde su propia cuenta GitHub, con commits de sus cambios y un pull request
que Yehosua pueda revisar. El usuario de GitHub de Miguel todavía no se ha indicado.
