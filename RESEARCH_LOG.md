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

- **Pregunta de investigación:** ¿mejora la exactitud del sistema si se
  combinan voz y gesto capturados simultáneamente (la participante habla
  y gesticula al mismo tiempo)?
- **Metodología:** modelos entrenados exclusivamente con muestras de un
  solo canal (sin doble tarea); 30 pares sincronizados voz+gesto
  evaluados como conjunto de prueba independiente, sin contaminar el
  entrenamiento.
- **Resultado (intervalos de confianza exactos, Clopper-Pearson):**

  | Canal | Tarea única (IC95%) | Doble tarea (IC95%) | Caída |
  |---|---|---|---|
  | Voz | 80.6% (71.6-87.7%) | 36.7% (19.9-56.1%) | −43.9 pp |
  | Gestos | 80.0% (61.4-92.3%) | 30.0% (14.7-49.4%) | −50.0 pp |

  Los intervalos de tarea única y doble tarea no se traslapan en ningún
  canal — la caída no es atribuible al azar de una muestra pequeña, es
  un efecto real y de magnitud considerable.
- **Patrón de error en gestos:** bajo doble tarea, los gestos finos
  (levantar una mano, girar la cabeza) colapsan hacia el gesto de mayor
  amplitud y menor especificidad (levantar ambas manos), con una tasa de
  confusión del 100% (10 de 10 casos en cada gesto fino).
- **Interpretación:** consistente con la literatura de interferencia
  cognitivo-motora (dual-task interference) — cuando la atención se
  divide entre dos tareas motoras/cognitivas concurrentes, el sistema
  nervioso prioriza el patrón de movimiento más simple o dominante,
  perdiendo precisión en los matices finos. No es una deficiencia
  técnica del sistema: es un hallazgo científico que subraya que, para
  población con compromiso motor, la simplicidad operativa es superior
  a la complejidad tecnológica.
- **Consecuencia de diseño:** se rediseñó la arquitectura de fusión
  multimodal de captura simultánea a captura secuencial — el sistema
  solicita primero el canal de voz; únicamente si no se alcanza
  consenso, solicita el gesto por separado, con la atención completa de
  la participante en un solo canal a la vez, nunca dividida entre ambos.
- Detalle completo: `reportes/hallazgo_interferencia_20260708.md`.

## 2026-07-08 — Hallazgo: la política de decisión importa más que el modelo

- Dos sesiones iniciales de validación en vivo, con un umbral de
  decisión permisivo, arrojaron 38.6% y 57.7% de exactitud — muy por
  debajo del 80.6% de LOOCV. El análisis por nivel de confianza del
  modelo (k=3, fracción de vecinos que coinciden) reveló la causa real:

  | Confianza del modelo (k=3) | n | Exactitud | IC95% (Clopper-Pearson) |
  |---|---|---|---|
  | 1.0 — consenso unánime | 13 | 92.3% | 64.0-99.8% |
  | 0.67 — mayoría (2 de 3) | 34 | 50.0% | 32.4-67.6% |
  | 0.33 — mínima (1 de 3) | 23 | 13.0% | 2.8-33.6% |

- **Conclusión:** el modelo es confiable cuando alcanza consenso interno
  (92.3%, comparable al 80.6% del LOOCV) — la baja exactitud en vivo era
  producto de la política de decisión, no de la calidad del modelo.
- **Corrección aplicada:** el umbral de confianza se ajustó para exigir
  consenso unánime antes de comunicar una respuesta, siguiendo el
  principio de que, en un sistema de comunicación aumentativa, una
  respuesta incorrecta comunicada a la familia es más costosa que
  solicitar una repetición.

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

## 2026-09-08 — Fundamentación teórica: literatura de respaldo identificada

Se identificaron tres referencias bibliográficas para reforzar la
fundamentación teórica del proyecto (relevante tanto para la memoria
MAPFRE como para una futura aspiración de maestría en ingeniería
biomédica). Se listan aquí como base teórica a citar, no como fuente
de cambios de código:

- **Tompkins, W. J. (ed.), *Biomedical Signal Processing and Signal
  Modeling*, Wiley, 1998.** Fundamento matemático (dominio de la
  frecuencia, filtros adaptativos, modelado de señales cuasi-periódicas
  ruidosas) directamente relacionado con el pipeline de extracción de
  características de voz (MFCC) y gestos ya implementado en
  `src/gestos_features.py` y `src/modelo.py`. Relevante en particular si
  se retoma la línea futura de sensores EMG (ver
  `docs/CONFIDENCIAL-especificacion-kit-captura-portatil.md`, sección 5).
- **Feher, J., *Quantitative Human Physiology: An Introduction*,
  Academic Press, 2012/2017.** Fundamento fisiológico del control motor
  del habla y la variabilidad de producción — sustento teórico de *por
  qué* el enfoque de clasificador personalizado (Mecanismo A, ver
  `docs/ruta-expansion-condiciones-neurologicas.md`) es apropiado para
  condiciones con compromiso motor del habla (disartria/apraxia), más
  allá de la validación empírica ya obtenida con YP.
- **Dey, N., Ashour, A. S. et al. (eds.), *Deep Learning Techniques for
  Biomedical and Health Informatics*, Springer, 2020.** Confirmado por
  el investigador principal como la obra referida. Relevante para
  justificar la migración futura del módulo
  de expansión de frases (actualmente Qwen2.5-1.5B-Instruct sobre CPU)
  hacia modelos locales de mayor capacidad, en línea con la
  justificación de GPU dedicada de la memoria MAPFRE v5.

**Nota metodológica:** estas referencias se incorporan como respaldo
teórico retrospectivo de decisiones ya tomadas empíricamente (no
determinaron el diseño original, que fue iterativo y validado con datos
reales de YP). Esta distinción debe mantenerse explícita en cualquier
documento formal que las cite, para no sugerir una fundamentación
teórica previa que no existió.

## 2026-09-18 — Canal de puntero: de la mirada a la cabeza

- **Pregunta:** ¿puede la webcam servir de canal de puntero (seguir un
  blanco en pantalla) para la participante, y con qué señal?
- **Observación de campo (informal, del investigador principal; no es
  una evaluación clínica):** a la participante le cuesta mover los ojos
  para seguir un estímulo y lo sigue moviendo la cabeza. Se había visto
  antes, con el dedo del investigador como estímulo, y ella lo confirmó.
- **Primera sesión, canal mirada (iris), una sola sesión:** el error
  medio fue 37% de la diagonal de pantalla, peor que apuntar siempre al
  centro (-42%). En las fijaciones (calibración) la relación entre la
  posición del iris y la del punto fue r = -0.09, y el giro de cabeza
  varió entre puntos unas 3 veces más que el iris (desviación 0.103 vs
  0.031). Coincide con la observación de campo, pero el instrumento aún
  no está validado: falta un control positivo con una persona sin
  dificultad ocular en las mismas condiciones.
- **Canal facial en los gestos (30 muestras, una sesión):** con solo
  rasgos de cara y ojos, 1-NN con LOOCV acertó 25/30 = 83.3% (IC 95%
  Clopper-Pearson 65.3–94.4%; azar 33.3%). Por grupo de rasgos: mirada
  66.7%, párpados 56.7%, cejas 73.3%. La señal viene sobre todo de cejas
  y postura de cabeza, no de la mirada. Limitación: los gestos se
  grabaron en bloques, así que la clase se confunde con el paso del
  tiempo (cansancio, luz, postura); una persona, una sesión.
- **Decisión:** el canal de puntero por defecto pasa a ser la **cabeza**
  (yaw/pitch de la matriz de orientación facial), con la mirada como
  canal opcional. Herramientas nuevas: monitor del operador con avisos
  de entorno, métricas de entorno por sesión y tendencia entre sesiones
  (`mirada_progreso.py`). Ver `CHANGELOG.md`.
- **Pendiente:** control positivo del instrumento (ver la entrada
  siguiente); primera sesión del canal cabeza con la participante;
  gestos en orden aleatorio para separar clase de deriva temporal.

## 2026-09-18 — Control positivo del canal cabeza (investigador, CTRL1)

- **Objetivo:** validar el instrumento con una persona sin dificultad
  motora antes de interpretar cualquier resultado de la participante.
- **Sesión:** una sola, del investigador principal (alias CTRL1), canal
  cabeza, ventana de 800x450, 30 fps, cara detectada 100% del tiempo y
  sin avisos de entorno.
- **La cabeza sigue el blanco:** en las fijaciones de la calibración, el
  yaw se relaciona con la posición-x del punto (r = -0.76) y el pitch con
  la posición-y (r = +0.95); en la persecución, yaw contra blanco-x da
  r = -0.87 y pitch contra blanco-y r = +0.86. El instrumento capta el
  canal.
- **Hallazgo de calibración:** 7 de los 9 puntos salieron estables y
  consistentes. El primero (no se estabilizó durante la captura) y el
  último (quedó quieto cerca del centro, sin llegar al punto) no fueron
  alcanzados. Con los seis rasgos y todos los puntos, la persecución quedó
  53% peor que apuntar siempre al centro; con solo yaw + pitch, +10% mejor;
  descartando esos dos puntos atípicos (criterio que usa solo datos de
  calibración), error de 21% de la diagonal, +20% frente al centro y
  correlaciones de 0.85 (x) y 0.87 (y).
- **Cambios derivados (parcialmente retirados en la entrada siguiente):**
  el canal cabeza regresa solo con yaw + pitch (se mantiene); la ventana
  estable y el descarte de puntos atípicos NO resistieron las sesiones
  nuevas y se retiraron.
- **Limitaciones:** el criterio de descarte y la elección de rasgos se
  afinaron con esta misma sesión, así que falta confirmarlos con sesiones
  nuevas antes de darlos por buenos. Un solo control no es una referencia
  normativa. Incluso con un control sano el mapeo lineal supera por poco
  la línea base: es el techo de este montaje (9 puntos, ventana pequeña,
  webcam), útil para leer los resultados de la participante en relación
  con él.
- **Siguiente:** segunda sesión de control con el script actualizado
  (confirmación con datos nuevos), control del canal mirada, y luego la
  primera sesión del canal cabeza con la participante.

## 2026-09-18 — Dos sesiones más de control: calibrar con el seguimiento

- **Sesiones:** dos sesiones más del investigador (CTRL1), canal cabeza,
  mismo montaje. Estas sesiones ya funcionaron como la prueba fuera de
  muestra que faltaba.
- **Resultado negativo:** la regla de descarte de puntos de calibración,
  afinada con la primera sesión, ayudó en esa (+10% a +20% frente a
  apuntar al centro) pero empeoró las otras dos (+24% a -1%, y -97% a
  -273%). No generaliza y se retiró.
- **La señal cruda es estable:** en las tres sesiones el yaw se relaciona
  con la posición-x del blanco (r = -0.87, -0.96, -0.91). La relación
  vertical es más débil y variable (pitch con blanco-y: 0.86, 0.66, 0.46),
  porque la cabeza se inclina un rango mucho menor que el que gira (desv.
  de ~3-5° en pitch contra ~9-10° en yaw).
- **Lo frágil era la calibración con 9 puntos quietos:** en una sesión el
  yaw de la calibración quedó entre -3° y +4° y el de la persecución entre
  -10° y +19°; la estrategia de la persona cambia entre mantener un punto y
  seguir uno que se mueve. Calibrar con la primera mitad de la propia
  persecución y evaluar en la segunda (que el modelo no vio) mejoró en las
  tres sesiones: -9% → +25%, -148% → +62% y +21% → +28% frente a apuntar al
  centro.
- **Limitaciones:** una persona, tres sesiones, un mismo día. La segunda
  mitad repite posiciones de la primera (la trayectoria es periódica), así
  que es una prueba menos exigente que una trayectoria nueva; falta probar
  con otra trayectoria o con el mouse como blanco. El 12% a 28% de error
  restante y el eje vertical débil siguen sin resolverse.
- **Cambios:** el protocolo pasa a calibrar con el seguimiento (los 9 puntos
  quietos quedan como opción `--puntos`, para comparar), con alias visible al
  iniciar y un lanzador propio para sesiones de control.
- **Siguiente:** control del canal mirada, y luego la primera sesión de
  cabeza con la participante.

## 2026-09-23 — Revisión de literatura reciente en disartria (Scopus)

Revisión dirigida por palabras clave en Scopus de artículos sobre
disartria publicados en 2026, con dos hallazgos aplicables al proyecto
y dos de contexto clínico más amplio.

- **Instrumento de autopercepción validado para la memoria (LwD):**
  Peres et al. (2026) validaron una versión reducida de 12 ítems del
  cuestionario *Living with Dysarthria* (LwD) en 47 personas con
  esclerosis múltiple, con correlación significativa entre el puntaje
  total y la severidad clínica de disartria (r=0.31, p=0.027) y
  consistencia interna alta (α=0.914). El **tiempo de fonación**
  (duración real de habla sin pausas, extraído de habla espontánea)
  fue el único predictor independiente del puntaje de autopercepción,
  explicando el 20.6% de la varianza (R²=0.206, p=0.006). Protocolo de
  grabación usado: vocal sostenida /a/, diptongo /iu/ repetido,
  diadococinesia /pataka/, oraciones con distinta entonación, y 60 s de
  habla espontánea — grabado con Praat (De Jong & Wempe, 2009) para
  detección automática de núcleos silábicos.
  Peres, M.L.M.K., Schuh, N., dos Santos, V.B., & Olchik, M.R. (2026).
  Self-perception of speech impairment in MS: Associations with
  dysarthria severity and speech measures. *Multiple Sclerosis and
  Related Disorders, 112*, 107342.
  https://doi.org/10.1016/j.msard.2026.107342
- **Datasets públicos de habla disártrica para validación externa
  (TORGO, UA-Speech):** dos artículos técnicos de 2026 usan estos
  corpus públicos en inglés para entrenar y evaluar clasificadores de
  disartria con embeddings de wav2vec2. Hallazgo técnico relevante para
  una futura migración de arquitectura: las **capas intermedias** del
  modelo (no la última) capturan mejor los rasgos articulatorios de la
  disartria — la última capa está optimizada para tareas lingüísticas,
  no motoras.
  Salim, S., Shahnawazuddin, S., & Ahmad, W. (2026). Towards inclusive
  voice biometrics: Dysarthria-discriminative embeddings for ASV
  system. *Computers and Electrical Engineering, 140*, 111531.
  https://doi.org/10.1016/j.compeleceng.2026.111531
  Sanjay, B., Vijayalakshmi, P., Actlin Jeeva, M.P., Priyadharshini,
  M.K., & Nagarajan, T. (2026). Multilingual dysarthria detection and
  severity classification using layer-wise embeddings from
  self-supervised speech models. *Speech Communication, 183*, 103464.
  https://doi.org/10.1016/j.specom.2026.103464
- **Contexto clínico (no aplicable directamente al software):**
  disartria inducida o agravada por estimulación cerebral profunda en
  Parkinson, con mejora reportada usando frecuencia de estimulación
  variable en un caso.
  Jia, F., Guo, Y., Wan, S., & Li, L. (2017). Severe subthalamic
  stimulation-induced dysarthria alleviated by a novel paradigm: A case
  report. *Journal of the Neurological Sciences, 372*, 270–271.
  https://doi.org/10.1016/j.jns.2016.11.048
- **Contexto clínico, fuera de alcance de las condiciones priorizadas:**
  ataxia cerebelosa autoinmune (anticuerpos anti-Ca/ARHGAP26) con
  disartria como uno de varios síntomas — mecanismo autoinmune raro,
  no motor puro; no se suma a `ruta-expansion-condiciones-neurologicas.md`.
  Wallwitz, U., Brock, S., Schunck, A., Wildemann, B., Jarius, S., &
  Hoffmann, F. (2017). From dizziness to severe ataxia and dysarthria:
  New cases of anti-Ca/ARHGAP26 autoantibody-associated cerebellar
  ataxia suggest a broad clinical spectrum. *Journal of
  Neuroimmunology, 309*, 77–81.
  https://doi.org/10.1016/j.jneuroim.2017.05.011
- **Próximo paso real:** evaluar agregar el protocolo de grabación del
  LwD (vocal sostenida, diadococinesia, habla espontánea de 60 s) como
  tarea adicional en las sesiones con la participante, y considerar
  TORGO/UA-Speech como referencia de validación externa del clasificador
  actual.

## Próximos hallazgos a documentar

- Resultados de la ampliación de la serie de casos (más allá de YP).
- Resultados del piloto de instalación con un usuario externo (ver
  `docs/plan-comunidad-open-source-2026.md`, mes 9-10 de la ruta).
