# Primera mitad: simplificación y Chomsky

## Alcance y diseño

La entrada de esta etapa es una gramática libre de contexto. La salida es una
gramática equivalente en forma normal de Chomsky y una secuencia de instantáneas
para inspeccionar cómo se obtuvo. La entrada de frases corresponde a la segunda etapa.

El flujo es: archivo → lector → `Grammar` → transformaciones → validación de
Chomsky → archivo o consumo directo desde Python.

`Production` contiene `lhs` (un símbolo) y `rhs` (una tupla de símbolos).
`Grammar` contiene el inicio, un conjunto inmutable de producciones y los no
terminales declarados. La cadena vacía se representa con `()`. Los conjuntos
eliminan producciones duplicadas; la ordenación al escribir hace determinista la salida.

`convert_to_cnf(grammar)` devuelve `ConversionResult` con:

- `grammar`: resultado final.
- `stages`: tupla de pares `(nombre, gramática)` con el original y seis etapas.

La gramática de entrada no se modifica. `validate_cnf` devuelve una tupla de
errores; una tupla vacía indica que todas las producciones cumplen el formato.

## Algoritmo, paso a paso

1. **Proteger el inicio.** Si aparece a la derecha, introducir un símbolo nuevo
   con una producción hacia el inicio anterior. Así, la eventual regla vacía
   del inicio no se propaga a posiciones internas.
2. **Eliminar epsilon.** Calcular por punto fijo los símbolos anulables. Para
   cada producción, construir las alternativas que conservan u omiten cada
   ocurrencia anulable. Conservar una producción vacía únicamente para el inicio.
3. **Eliminar unitarias.** Las reglas `A -> B`, con B no terminal, forman un grafo.
   Para cada A, recorrer todos sus destinos alcanzables y copiar sus producciones
   no unitarias. El conjunto de visitados evita ciclos infinitos.
4. **Eliminar símbolos inútiles.** Calcular primero cuáles producen alguna cadena
   terminal, y descartar reglas que dependan de símbolos improductivos. Luego
   recorrer desde el inicio y descartar lo inalcanzable.
5. **Separar terminales.** En cuerpos de longitud dos o más, sustituir cada
   terminal por una variable auxiliar con una regla como `T0 -> palabra`.
6. **Binarizar.** Sustituir cuerpos largos por cadenas de reglas binarias:
   `A -> B C D` se transforma en `A -> B B0` y `B0 -> C D`.

Las variables auxiliares se eligen evitando colisiones con todos los símbolos
existentes, incluidos terminales. Al finalizar, el validador exige `A -> B C`,
`A -> terminal` o, exclusivamente para el inicio, `S -> ε`; el inicio no puede
aparecer en un cuerpo.

## Ejemplo para explicar en clase

Con `S -> A A` y `A -> a | e`, A es anulable y las dos ocurrencias se consideran
por separado. Aparecen `S -> A A`, `S -> A` y `S -> e`. Al quitar la unitaria,
el resultado es `S -> A A | a | e`, `A -> a`. Las palabras posibles siguen
siendo ε, `a` y `a a`.

Para el material aritmético, ejecutar:

```bash
python3 main.py data/1.txt --output output/aritmetica-cnf.txt --trace-dir output/etapas-aritmetica
```

Abrir las etapas en orden y localizar primero la desaparición de epsilon, luego
la de reglas unitarias, y finalmente las variables que sustituyen terminales
y dividen cuerpos largos. El archivo del docente usa otros nombres auxiliares;
la igualdad textual no es el criterio de corrección.

## Pruebas realizadas

Comando: `python3 -m unittest discover -s tests -v`.

Validación local inicial: 20 pruebas aprobadas con Python 3.9.6.
Una de ellas recorre 40 gramáticas pequeñas generadas con semilla fija 2024.

| Caso | Comprobación |
| --- | --- |
| Archivos proporcionados | Lectura de `id` como símbolo y `e` como vacío |
| Epsilon y símbolos repetidos | Se conservan todas las combinaciones anulables |
| Inicio recursivo y anulable | Se conserva ε sin dejar el inicio a la derecha |
| Ciclos unitarios | Terminan y conservan las palabras generadas |
| Símbolos sin producciones después de simplificar | Siguen siendo no terminales hasta ser eliminados |
| Símbolos improductivos o inalcanzables | Se eliminan sin introducir palabras |
| Lenguaje vacío y lenguaje {ε} | Se distinguen correctamente |
| Cuerpos largos, mixtos y colisiones de nombres | Resultado válido en Chomsky |
| Gramática inglesa | Sus 30 producciones permanecen iguales |
| Gramática aritmética | Lenguaje coincide con original y referencia hasta 5 tokens |
| 40 gramáticas pequeñas | Todas las etapas conservan las palabras de hasta 3 tokens |
| Serialización y segunda conversión | Escritura/lectura conserva la gramática y la conversión es idempotente |
| Consola | Exporta siete instantáneas, informa errores y protege la entrada |

El oráculo de pruebas enumera palabras mediante un punto fijo; no implementa CYK.
La comparación acotada comprueba exhaustivamente las palabras hasta la longitud
indicada para esas gramáticas, pero no constituye una prueba formal para todas
las longitudes. Los invariantes de las transformaciones y el validador complementan
esa evidencia.

## Discusión y límites

- **Clasificación de símbolos:** si A pierde todas sus reglas al quitar epsilon,
  no debe convertirse accidentalmente en un terminal. El modelo conserva su
  declaración durante las etapas intermedias. Hay pruebas específicas para esto.
- **Repetir la conversión:** las pruebas detectaron un cambio innecesario de inicio
  al volver a convertir una gramática que aceptaba ε. Se corrigió protegiendo el
  inicio solo cuando aparece a la derecha.
- **Referencia aritmética:** la variante estricta de Chomsky introduce un inicio
  nuevo porque E aparece a la derecha; esto explica una diferencia con `1-cnf.txt`.
- **Costo de epsilon:** con k ocurrencias anulables en un cuerpo pueden aparecer
  hasta 2^k alternativas. Esta implementación didáctica no impone un límite de
  recursos para gramáticas muy grandes.
- **Formato de entrada:** los símbolos se separan por espacios; `e` y `ε` están
  reservados. No se implementa un analizador léxico para expresiones sin espacios.
- **Árbol de CYK:** CYK construye el árbol de la gramática convertida. Reconstruir
  el árbol de la gramática original requeriría registrar correspondencias adicionales;
  no es necesario para la gramática inglesa entregada, que permanece igual.

## Integración con el reporte final

El [reporte final](reporte-final.md) incorpora diseño y complejidad de CYK,
estructura del árbol, intervalo del cronómetro y tiempos realmente medidos.
La suite integrada tiene 34 pruebas aprobadas localmente con Python 3.12.2.
La revisión humana de ambas partes sigue pendiente.
