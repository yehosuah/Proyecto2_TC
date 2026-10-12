# Etapas y evidencia de colaboración

Yehosua desarrolla simplificación y Chomsky; Miguel Rosas desarrolla CYK, tiempo
y árbol. Ambas mitades se implementaron con asistencia de Codex. La división
corresponde a las dos partes de 7 puntos del enunciado.

| Hito | Responsable | Estado |
| --- | --- | --- |
| Modelo, lector, simplificación y Chomsky | Yehosua | Implementado; 20 pruebas originales pasan |
| Revisión personal de primera mitad | Yehosua | Pendiente |
| CYK, árbol, tiempo y pruebas propias | Miguel Rosas | Implementado; 14 pruebas nuevas pasan |
| Integración y reporte | Ambos | Implementación y documentación completas con asistencia; revisión humana conjunta pendiente |

## Historial verificable

Primera mitad: commit `b4d24cd938249389cbc3300594f1bd2215f23acd`.
Segunda mitad: rama local `miguel/cyk-integracion`, identidad Git configurada
`MiguelRosas11 <roguemijose@gmail.com>`.

| Commit | Contribución |
| --- | --- |
| `cc3539d` | Reconocimiento CYK mediante tabla dinámica y referencias |
| `2dca3b0` | Árbol y medición con perf_counter |
| `c73350c` | Consola, frases y entrada estándar |
| `cab3514` | Pruebas de árboles, ambigüedad y oráculo independiente |
| Commit de documentación (consultar `git log`) | Reporte, guía, benchmark y estados de entrega |

Los commits registran cambios reales a petición de Miguel con asistencia de
Codex; no acreditan revisión humana de ninguno de los integrantes. No se publicó
esta rama ni se abrió PR durante esta continuación.

## Revisión antes de entregar

1. Yehosua ejecuta ejemplos y explica puntos fijos, ciclos, diferencia entre
   ∅ y {ε} e introducción de inicio nuevo.
2. Miguel explica recurrencia CYK, separaciones, referencias del árbol y cronómetro.
3. Ambos ejecutan la suite y ejemplos del reporte y revisan documentación.
4. Registrar revisiones reales y enlaces de publicación cuando ocurran.

La suite local aprobó 34 pruebas con Python 3.12.2 el 11 de octubre de 2026.
El reporte incluye tiempos medidos, sin atribuir revisiones ni ejecución de CI
que no se han verificado.
