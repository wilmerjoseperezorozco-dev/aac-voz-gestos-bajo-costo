# Research Log — decisiones y hallazgos

Bitácora técnica de decisiones y hallazgos de investigación, en orden
cronológico. Complementa a [`BITACORA.md`](BITACORA.md) (narrativa general
del proyecto) con el detalle técnico de cada hallazgo. Cada entrada enlaza
al reporte completo en `reportes/` cuando existe.

## 2026-07-06 — Pipeline de voz validado

- Validación LOOCV con datos sintéticos: 91.7% de exactitud (48 muestras,
  8 palabras).
- Persistencia del modelo verificada (guardar → cargar → predecir: 4/4).
- Estado: listo para sesiones reales con YP.

## 2026-07-07/08 — Primeras sesiones reales de voz y gestos

- Primeras grabaciones reales de voz y gestos con YP.
- Reportes de validación y matrices de confusión en `reportes/`.

## 2026-07-08 — Hallazgo: interferencia cognitivo-motora en doble tarea

- **Hallazgo:** al pedir a YP hacer dos tareas simultáneas (ej. hablar y
  gesticular a la vez), la exactitud cae de forma medible frente a tarea
  única, en ambos canales.
- Detalle completo: `reportes/hallazgo_interferencia_20260708.md`.

## 2026-07-09 — Evaluador ciego, optimización DTW, generador LLM

- **Evaluador ciego:** se incorporó un segundo evaluador que anota su
  propio juicio antes de ver la predicción del sistema, para evitar sesgo
  de confirmación en la validación en vivo.
  `reportes/hallazgo_evaluador_ciego_20260709.md`.
- **Optimización DTW:** el cuello de botella real no era el número de
  referencias comparadas sino una llamada `numpy` sin vectorizar dentro
  del bucle de `distancia_dtw()`. Vectorizado con broadcasting/`einsum`:
  **4.2x más rápido**, LOOCV de 150 muestras bajó de ~9-10 min a ~4 min,
  con la misma exactitud exacta (76.7%), verificado matemáticamente
  idéntico al resultado anterior (diferencia 8.88×10⁻¹⁶).
  `reportes/hallazgo_optimizacion_dtw_20260709.md`.
- **Generador de frases (LLM local):** primera versión del módulo de
  expansión de frases con salvaguarda anti-alucinación léxica.
  `reportes/hallazgo_generador_llm_20260709.md`.

## 2026-07-10 — Primera sesión real del tablero de escaneo

- Primer uso real del tablero de selección visual con YP.
- Hallazgos de usabilidad iniciales documentados en
  `reportes/hallazgo_primera_sesion_tablero_20260710.md`.

## 2026-07-14 — Vocabulario ampliado, layout horizontal, hallazgos conductuales

- Cuarta sesión del tablero, primera con vocabulario ampliado (35
  símbolos en ese momento) y layout horizontal sin scroll.
- **Resultado cuantitativo:** 11/17 (64.7%) de oraciones confirmadas como
  correctas. Mejor desempeño con 2 símbolos (70%) que con 3+ (67% y en
  descenso) — hallazgo consistente con carga cognitiva creciente al
  aumentar la longitud de la secuencia, no concluyente aún por tamaño de
  muestra pequeño.
- **Hallazgo técnico crítico:** `hablar()` descartaba silenciosamente
  fallos de reproducción de audio (`except Exception: pass`). Como YP no
  sabe leer, un fallo de audio silencioso deja el sistema inutilizable en
  ese momento. **Corregido**: reintento automático con un motor de voz
  recién creado, y advertencia visible si el fallo persiste.
- Detalle completo: `reportes/hallazgo_sesion_20260714.md`.

## 2026-07-20 — Vocabulario núcleo ampliado a 126 símbolos

- Expansión del vocabulario del tablero de 35 a 126 símbolos, en 10
  categorías, con base académica en Soto & Cooper (2021) — vocabulario
  núcleo temprano en español para usuarios de CAA.
- Implementado escaneo de dos niveles (categoría → símbolo dentro de la
  categoría) para mantener tiempos de ciclo manejables con un vocabulario
  tan ampliado.

## 2026-08-07 — Validación de gestos, iteración continua

- Nueva ronda de validación del canal de gestos
  (`reportes/validacion_gestos_20260807_233145.json`,
  `confusion_gestos_20260807_233145.png`).

## 2026-08-21 — Verificación visual de persona detectada (canal de gestos)

- **Problema identificado en sesión real:** el detector de postura
  (MediaPipe Pose) tomaba como referencia a la primera persona que
  reportaba, sin indicar en pantalla a quién había detectado. En la
  práctica, esto obligaba al cuidador/investigador a salir del encuadre
  de la cámara *antes* de empezar, sin forma de confirmarlo en vivo —
  riesgo real de grabar por error el movimiento del cuidador en lugar
  del de la persona usuaria.
- **Corrección implementada** (`src/gestos_features.py`):
  - El detector ahora reconoce hasta 2 personas simultáneas
    (`num_poses=2`) y dibuja el esqueleto de cada una en pantalla con
    colores distintos — verde para la persona cuyos datos se están
    grabando, otro color para cualquier persona adicional detectada
    pero ignorada, con una advertencia visible si hay más de una en
    cuadro.
  - Nueva vista previa (`verificar_encuadre()`), ejecutada al inicio de
    `gestos_grabar.py`: muestra la cámara en vivo con el esqueleto
    dibujado *antes* de empezar a grabar ninguna muestra real, para que
    el cuidador confirme el encuadre correcto sin gastar intentos.
  - Ventana de cámara ampliada de la resolución nativa por defecto a
    1280x720, con tamaño ajustable.
- **Por qué esto importa más allá de YP:** este patrón (identificación
  visual de a quién está siguiendo la cámara, antes y durante la
  captura) es relevante para cualquier cuidador que use este sistema con
  otra persona con discapacidad motora — no es una corrección puntual,
  es una salvaguarda de accesibilidad/seguridad de datos generalizable.
  Documentado también en `docs/plan-comunidad-open-source-2026.md`
  (sección de mejoras para personas con discapacidad motora).

## Próximos hallazgos a documentar

- Resultados de la ampliación de la serie de casos (más allá de YP).
- Resultados del piloto de instalación con un usuario externo (ver
  `docs/plan-comunidad-open-source-2026.md`, mes 9-10 de la ruta).
