# Hallazgo — optimización de DTW vs. reducción a prototipos (2026-07-09)

## Pregunta

Ante la brecha de escalabilidad (LOOCV con 150 muestras tardando ~9-10
min), ¿conviene reducir el banco de referencias a prototipos por clase, u
optimizar la función DTW en sí?

## Experimento 1 — reducción a prototipos (k-medoids por punto-más-lejano)

Validado con LOOCV metodológicamente correcta (prototipos de la clase
excluida recalculados sin la muestra de prueba en cada pliegue, sin fuga
de datos). Ver `src/comparar_prototipos.py` y
`reportes/comparacion_prototipos.json`.

| Prototipos/clase | Referencias | Exactitud LOOCV | ms/predicción |
|---|---|---|---|
| 3 | 33 | 65.3% | 1516 |
| 4 | 44 | 66.7% | 2193 |
| 5 | 55 | 70.0% | 2900 |
| 6 | 66 | 74.7% | 3481 |
| 8 | 88 | 75.3% | 7003 |
| Completo | 150 | 76.7% | 7068 |

**Conclusión:** la reducción SÍ ahorra tiempo, pero **siempre a costa de
exactitud** — no hay forma de reducir el banco de referencias sin perder
información real sobre la variabilidad de cada palabra. El mejor punto de
equilibrio encontrado (k=6) todavía cuesta 2 puntos porcentuales.

## Experimento 2 — optimización de la función DTW (implementada)

Se identificó que `distancia_dtw()` llamaba `np.linalg.norm()` celda por
celda dentro del bucle de programación dinámica — el costo dominante real.
Se reemplazó por un cálculo vectorizado de las n×m distancias
punto-a-punto de una sola vez (broadcasting + `np.einsum`), sin tocar la
recurrencia de DTW (que sí tiene una dependencia secuencial real entre
celdas y no se puede vectorizar sin cambiar el algoritmo).

**Verificación de correctitud** (`verificar_dtw_optimizado.py`, 28
comparaciones de pares reales): diferencia máxima entre la implementación
vieja y la nueva = **8.88×10⁻¹⁶** (ruido de punto flotante, resultado
matemáticamente idéntico).

**Resultado medido:**

| Métrica | Antes | Después |
|---|---|---|
| ms/comparación DTW (benchmark aislado) | 5.10 | 1.22 (**4.2x**) |
| LOOCV completa, 150 muestras (tiempo real) | ~9-10 min | **4 min** |
| Exactitud LOOCV | 76.7% | 76.7% (idéntica) |

## Conclusión — por qué se prefirió esta ruta

La optimización de DTW da una mejora de velocidad **sin ningún costo de
exactitud**, mientras que la reducción a prototipos siempre implica una
concesión. Se implementó la optimización de DTW primero
(`src/modelo.py::distancia_dtw`); la reducción a prototipos queda
documentada y lista para aplicarse más adelante si el dataset sigue
creciendo y el margen de la optimización DTW no alcanza — son técnicas
complementarias, no excluyentes.

## Nuevo tope de escalabilidad (recalculado con DTW optimizado)

Con el speedup de 4.2x, el tope práctico de ~150-170 muestras (antes de
necesitar reducción a prototipos) sube proporcionalmente a
**~350-400 muestras** antes de que el reentrenamiento vuelva a superar
los ~15 minutos por sesión.
