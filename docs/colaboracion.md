# Etapas y evidencia de colaboración

## Acuerdo

Python como lenguaje. Yehosua desarrolla la primera mitad de simplificación y
Chomsky; Miguel Rosas desarrolla CYK, tiempo y árbol. Ambos revisan integración
y documentación. La división sigue las dos partes de 7 puntos del enunciado.

| Hito | Responsable | Condición de entrega | Estado |
| --- | --- | --- | --- |
| Modelo y contrato de conexión | Yehosua; Miguel revisa al recibir | API y formatos documentados | Preparado; revisión de Miguel pendiente |
| Simplificación y Chomsky | Yehosua | Conversor y pruebas aprobadas | Implementado con asistencia de Codex |
| Revisión personal de primera mitad | Yehosua | Ejecutar ejemplos y explicar transformaciones | Pendiente |
| CYK y árbol | Miguel Rosas | Reconocimiento, tiempo, árbol y pruebas propias | Pendiente |
| Integración y reporte final | Ambos | Demostración completa y documentación de ambas partes | Pendiente |

## Evidencia que debe quedar

- Un commit inicial contiene la implementación asistida de la primera mitad.
  No implica que Miguel ya haya contribuido ni que Yehosua ya la haya revisado.
- Cada persona realiza sus cambios con su propia identidad Git y conserva
  commits que describen el trabajo realizado.
- Miguel trabaja en una rama propia o un fork y abre un pull request para su
  segunda mitad. Yehosua revisa código, pruebas y documentación.
- La revisión y las correcciones de integración quedan en el historial real.
- Al cerrar el proyecto, registrar los enlaces de commits y PR junto a la
  contribución concreta. Completar esta sección a medida que ocurra el trabajo.

No se han simulado commits de Miguel ni revisiones de ninguno de los integrantes.
Todavía falta su usuario de GitHub para invitarlo como colaborador; también puede
usar un fork del repositorio público y proponer los cambios mediante pull request.

## Revisión que debe hacer Yehosua antes de entregar

1. Ejecutar los tests y el ejemplo aritmético con `--trace-dir`.
2. Explicar por qué se calcula un punto fijo para anulables y productivos.
3. Mostrar cómo se eliminan ciclos unitarios y por qué no se pierden palabras.
4. Explicar la diferencia entre ∅ y {ε}, y el motivo de un inicio nuevo.
5. Revisar el contrato con Miguel y registrar cualquier ajuste acordado.

## Cierre conjunto

Completar ejemplos aceptados/rechazados, incluir tiempos realmente medidos,
capturar un árbol y discutir obstáculos reales de integración. El documento
`primera-mitad.md` es la base del reporte, no el reporte final completo.
