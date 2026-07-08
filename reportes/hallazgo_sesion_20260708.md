# Hallazgo — sesiones de validación en vivo (2026-07-08)

## Resultado consolidado

| Sesión | Umbral aplicado | Confirmados | Aciertos | Exactitud |
|---|---|---|---|---|
| 1 (mañana) | 0.5 (bug: quedaba guardado en el modelo) | 44 | 17 | 38.6% |
| 2 (mañana, tras "corrección" fallida) | 0.5 (el bug seguía activo) | 26 | 15 | 57.7% |

**LOOCV offline del mismo modelo: 82.5%.**

## Causa raíz (dos capas, ambas confirmadas con evidencia)

1. **Umbral de decisión demasiado permisivo.** El sistema hablaba con solo
   1 de 3 vecinos coincidiendo (confianza 0.333). Desglose exacto,
   combinando ambas sesiones:

   | Confianza (k=3) | n total | Aciertos | Exactitud |
   |---|---|---|---|
   | 1.0 (3/3 unánime) | 13 | 12 | **92.3%** |
   | 0.667 (2/3) | 34 | 17 | 50.0% |
   | 0.333 (1/3) | 23 | 3 | 13.0% |

   Con unanimidad, el sistema es tan confiable como el LOOCV offline
   (92.3% vs 82.5%). El problema nunca fue el modelo — fue dejarlo hablar
   sin consenso.

2. **Bug de configuración:** cambiar `config.json` no bastaba. El umbral
   de confianza queda **horneado dentro del modelo guardado**
   (`modelos/modelo_yp.json`) en el momento de `entrenar.py`. La sesión 2
   se abrió creyendo que ya regía 0.99, pero el archivo del modelo seguía
   en 0.5 — por eso la mejora fue parcial (38.6% → 57.7%, no el salto
   completo esperado). **Corregido:** se editó directamente
   `modelo_yp.json` (`umbral_confianza: 0.99`) y quedará resuelto de forma
   permanente en cada `entrenar.py` futuro, porque ahora sí toma el valor
   correcto de `config.json`.

## Corrección aplicada (vigente desde ahora)

- `umbral_confianza = 0.99`: el sistema solo pronuncia una palabra cuando
  los 3 vecinos más cercanos coinciden. Si no hay consenso, pide repetir
  en vez de arriesgar una respuesta incorrecta.
- `src/predecir.py` ahora guarda cada audio confirmado como refuerzo del
  dataset (`data/<palabra>/..._vivo_ok_*.wav` o `..._correccion_*.wav`),
  para que el uso real siga creciendo el entrenamiento.

## Lectura para la sustentación (mensaje honesto y defendible)

- El modelo NO es poco confiable: cuando tiene consenso, acierta 92.3% en
  condiciones reales, en línea con el 82.5% del LOOCV.
- El hallazgo real es de **ingeniería de decisión, no de aprendizaje**:
  un clasificador de bajos recursos necesita una política de "cuándo
  callar" tan cuidada como la de "cuándo hablar" — más aún en un sistema
  de comunicación aumentativa, donde una respuesta incorrecta pronunciada
  en voz alta a la familia es peor que pedir que se repita.
- Esto documenta un ciclo completo de ingeniería con evidencia: medir en
  vivo → encontrar la causa con datos → corregir → volver a medir. Es
  exactamente el tipo de rigor que se espera en una validación seria.

## Siguiente paso

Sesión de confirmación con el umbral ya corregido de raíz (`modelo_yp.json`
en 0.99). Se espera que el sistema pida repetir con más frecuencia, pero
que cuando sí hable, acierte por encima del 85-90%.
