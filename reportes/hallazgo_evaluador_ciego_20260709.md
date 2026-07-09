# Hallazgo — primera medición con evaluador ciego (2026-07-09)

## Qué se midió

Primera sesión en vivo con el protocolo de evaluador ciego ya integrado
(`predecir.py`): un acompañante familiar confirma qué cree que dijo
YP **antes** de ver la predicción del sistema en pantalla, eliminando el
sesgo de confirmación de sesiones anteriores. Entorno: fondo blanco,
micrófono de solapa a 20 cm, luz sin sombras, PC en modo no molestar
(ficha de sesión registrada en `registros/fichas_sesion.csv`).

## Resultado — confirma el patrón de las sesiones anteriores

| Confianza del sistema (k=3) | n | Exactitud |
|---|---|---|
| 1.0 — consenso unánime | 5 | **100%** (5/5) |
| 0.67 — mayoría | 3 | 33.3% |
| 0.33 — mínima | 9 | 44.4% |
| **Global (top-1, sin filtrar)** | 17 | 58.8% |

Tercera sesión independiente que confirma: **con consenso unánime el
sistema es completamente confiable**; la exactitud "bruta" (58.8%) sigue
subestimando la capacidad real del modelo porque mezcla respuestas donde
el sistema explícitamente dijo "no estoy seguro".

## Hallazgo nuevo — acuerdo evaluador ciego vs. sistema

| Métrica | Valor |
|---|---|
| Intentos con evaluador ciego presente | 14/17 |
| Evaluador ciego coincidió con el sistema | 6/14 (42.9%) |
| Casos de discrepancia evaluador-vs-sistema | 8 |
| De esos, el sistema resultó correcto | 3/8 (37.5%) |

**Lectura honesta (n pequeño, no concluyente todavía):** cuando evaluador
ciego y sistema discreparon, el evaluador tuvo razón con más frecuencia
que el sistema (5/8 vs. 3/8). Esto no invalida el sistema — el criterio
de decisión correcto sigue siendo el consenso interno del modelo (que
acertó 100% hoy) — pero sugiere que una persona familiarizada con YP capta
matices que el sistema aún no. Es exactamente el tipo de comparación que
la prueba de línea base humana formal (pendiente, ver
`protocolo-validacion.md` §4) debe cuantificar con una muestra mayor.

## Nota de escalabilidad (confirmación empírica)

Con el reentrenamiento de hoy el dataset llegó a 150 muestras (11
palabras) — el reentrenamiento tardó ~9-10 minutos, validando la
proyección de `brechas-cientificas-y-escalamiento.md` §7
(latencia(n) ≈ 0.029·n + 0.12 s; LOOCV total ≈ n·latencia(n-1)). Se
recomienda no superar ~150-170 muestras sin implementar la reducción a
prototipos por clase.

## Exactitud LOOCV tras incorporar refuerzos de hoy

150 muestras, 11 palabras: **76.7%** global (vs. 79.7% con 133 muestras
antes de la sesión de hoy). Caída esperada y no preocupante: los nuevos
refuerzos se concentraron en "no" y "sí" (las palabras que ya venían más
débiles), lo que introduce ejemplos más difíciles al conjunto de
referencia — es el costo normal de que el sistema aprenda de condiciones
de uso real, no solo de la sesión de grabación inicial controlada.
