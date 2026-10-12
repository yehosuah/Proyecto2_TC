# Contrato de integración y entrega de la segunda mitad

La segunda mitad está implementada con asistencia de Codex. Se conserva el
contrato original de `Grammar`, `Production` y `ConversionResult`.

```python
from cfg import read_grammar, convert_to_cnf, validate_cnf, cyk

conversion = convert_to_cnf(read_grammar("data/ingles.txt"))
grammar = conversion.grammar
assert not validate_cnf(grammar)
result = cyk(grammar, "she eats a cake with a fork".split())
assert result.accepted
assert result.tree.leaves() == result.tokens
print(result.elapsed_seconds)
print(result.tree.to_text())
```

`Grammar.start` determina el inicio sin asumir S. Producciones y cuerpos son
inmutables; los cuerpos contienen tokens completos. Una CNF sin reglas genera
∅; la cadena vacía se acepta solo con `Production(grammar.start, ())`.
`validate_cnf` devuelve una tupla vacía cuando no hay errores.

`cyk` exige CNF, recibe un iterable de tokens exactos y devuelve
`CYKResult(accepted, tokens, elapsed_seconds, tree)`. Un rechazo tiene `tree=None`.
La consola convierte primero y normaliza a minúsculas por defecto; conserva
puntuación y ofrece `--case-sensitive`. El cronómetro incluye índices, tabla
y decisión; excluye conversión y reconstrucción del árbol.

Comprobación de entrega:

```powershell
py -3 -m unittest discover -s tests -v
py -3 main.py data/ingles.txt --sentence "She eats a cake with a fork"
py -3 main.py data/ingles.txt --sentence "she eats cake"
py -3 main.py data/ingles.txt --sentence ""
py -3 main.py data/1.txt --sentence "( id ) + id"
py -3 main.py data/1.txt --output output/aritmetica-cnf.txt --trace-dir output/etapas-aritmetica
py -3 benchmark.py
```

Se verificaron 34 pruebas localmente en Python 3.12.2. Diseño, mediciones y
límites están en el [reporte final](reporte-final.md). Falta revisión humana
conjunta y eventual publicación según instrucciones del usuario.
