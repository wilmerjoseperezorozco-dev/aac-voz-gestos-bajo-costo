# Artículo científico — versión estructurada (formato clínico I-IV)

Estructura ajustada según orientación editorial recibida, con los datos
reales del proyecto y **dos correcciones necesarias antes de someter a
cualquier revista** — ver recuadro de advertencias al inicio. Los campos
**[PENDIENTE]** requieren una decisión o dato que solo tú puedes dar.

---

## ⚠️ Correcciones aplicadas a la orientación recibida

1. **Diagnóstico de apraxia — no confirmado.** La orientación asume
   "apraxia motora del habla" como diagnóstico establecido. En este
   proyecto YP tiene una **caracterización funcional** ("desconexión
   motora del habla; apraxia/disartria a caracterizar"), sin evaluación
   clínica formal documentada. Usar "apraxia" como hecho en el título o la
   introducción sería una afirmación clínica no respaldada — riesgo real
   frente a un comité de ética o un revisor. Se mantiene lenguaje
   funcional/descriptivo en todo el documento, con apraxia/disartria como
   hipótesis diferencial a confirmar, no como diagnóstico.
2. **Comparación contra línea base humana — no ejecutada todavía.** La
   orientación pide una prueba de McNemar o Wilcoxon comparando aciertos
   del sistema vs. comprensión humana. **Esa prueba de línea base nunca se
   hizo** (estaba planeada en `protocolo-validacion.md` §4, pendiente de
   ejecución). No se puede reportar una comparación estadística sobre
   datos que no existen. Se deja como tarea obligatoria antes de someter
   el artículo — ver §3.3 y Anexo de tareas pendientes al final.

---

## Título (ajustado, sin sobre-reclamar diagnóstico)

*"Sistema personalizado de bajo costo para predicción de voz y gestos en
desconexión motora del habla: estudio de caso único (N=1) con hallazgo de
interferencia cognitivo-motora en fusión multimodal"*

## Autores

Wilmer José Pérez Orozco (Corporación Universidad de la Costa, CUC) —
autor principal. **[PENDIENTE]** asesor/docente institucional como
coautor (fortalece la credibilidad, no la resta).

## Resumen estructurado (máx. 250 palabras)

> **Objetivo:** desarrollar y validar un sistema personalizado de bajo
> costo para la predicción de voz y gestos como apoyo a la comunicación en
> una persona con desconexión motora del habla (estudio de caso, N=1).
> **Métodos:** se entrenó un clasificador k-vecinos-más-cercanos con
> distancia de alineamiento temporal dinámico (DTW) sobre características
> MFCC (voz) y landmarks de postura corporal (MediaPipe Pose), a partir de
> 103 muestras de voz y 30 de gestos de una participante (alias YP, 35
> años). La validación siguió dos vías: validación cruzada
> dejando-uno-fuera (LOOCV) offline, y confirmación humana en sesiones de
> uso en vivo. Se evaluó adicionalmente el efecto de la captura simultánea
> de voz y gesto mediante un diseño de entrenamiento en canal único y
> prueba en condición de doble tarea. **Resultados:** el sistema alcanzó
> 80.6% [IC95% Clopper-Pearson: 71.6–87.7%] de exactitud en voz y 80.0%
> [61.4–92.3%] en gestos (LOOCV). En validación en vivo, la exactitud fue
> 92.3% [64.0–99.8%] cuando el modelo alcanzó consenso interno unánime,
> frente a 13.0% [2.8–33.6%] con consenso mínimo. La captura simultánea de
> voz y gesto redujo la exactitud a 36.7% [19.9–56.1%] y 30.0%
> [14.7–49.4%] respectivamente — una caída cuyos intervalos de confianza
> no se traslapan con los de tarea única, consistente con interferencia
> cognitivo-motora de doble tarea. **Conclusiones:** un sistema de bajo
> costo (hardware $0 adicional) y bajo volumen de datos (10-15 muestras
> por categoría) puede alcanzar exactitud clínicamente útil cuando se
> exige consenso del modelo antes de comunicar una respuesta; la fusión
> multimodal debe ser secuencial, no simultánea, en usuarios con
> compromiso motor. Se requiere una comparación formal contra línea base
> de comprensión humana antes de establecer superioridad clínica.

## I. Introducción

### Contexto clínico
Las alteraciones neuromotoras del habla (que incluyen, según el caso,
apraxia, disartria u otras formas de desconexión entre la intención
comunicativa y su ejecución motora) reducen la inteligibilidad del habla
y, con ello, la autonomía comunicativa de quien las presenta. La
caracterización clínica precisa de cada caso individual (apraxia vs.
disartria vs. otro origen) requiere evaluación fonoaudiológica formal, que
para este estudio de caso está **pendiente de realizar** — se documenta
aquí el perfil funcional observado, no un diagnóstico.

### Justificación
Los sistemas comerciales de reconocimiento de voz (Google, Siri, Alexa)
están entrenados sobre corpus de habla típica a gran escala; su exactitud
cae drásticamente ante patrones de habla atípicos, porque el patrón
acústico de la persona se aleja de la distribución con la que el modelo
fue entrenado. Iniciativas como Google Project Relate abordan esto
mediante personalización, pero exigen un volumen de datos de entrada
elevado (≥500 frases), inviable para personas con fatiga motora
significativa.

### Brecha de conocimiento
Existe una brecha entre la personalización de alta exactitud (que exige
mucho dato) y la accesibilidad económica (hardware casero, sin nube). Este
trabajo explora si un enfoque de bajos recursos — vocabulario funcional
cerrado, 10-15 muestras por categoría, hardware ya disponible en el
hogar — puede cerrar parte de esa brecha, y documenta además un hallazgo
no cubierto en la literatura revisada: el efecto de la interferencia
cognitivo-motora al fusionar canales de voz y movimiento de forma
simultánea.

## II. Materiales y métodos

### Diseño experimental
Estudio de caso único (N=1) con enfoque de validación cruzada (LOOCV)
sobre el conjunto de referencia, complementado con validación en vivo
mediante confirmación humana sobre intentos reales, y un sub-estudio
experimental de interferencia cognitivo-motora con diseño de
entrenamiento-en-canal-único / prueba-en-doble-tarea.

### Participante
Alias **YP**, 38 años, sexo femenino. Perfil funcional: condición
neuromotora congénita con compromiso del habla y motor; conserva
capacidad de reconocimiento de estímulos visuales y sonoros (usada
deliberadamente en el protocolo para evitar el modelado verbal — ver más
abajo). Cuenta con **certificación oficial de discapacidad** (Ministerio
de Salud y Protección Social de Colombia) y caracterización clínica
formal (historia clínica e informe de valoración multidisciplinaria).
Por sensibilidad de datos de salud, el diagnóstico específico y los
puntajes de funcionamiento **no se publican** en este documento; se
mantienen en un anexo confidencial disponible para el comité de ética
institucional. Esta caracterización resuelve, para efectos del comité de
ética, la limitación de "ausencia de caracterización clínica formal"
señalada en versiones anteriores de este protocolo.

### Protocolo de adquisición
Micrófono a distancia fija de aproximadamente 15 cm de la boca (resuelto
mediante audífonos con micrófono integrado o soporte casero tipo brazo,
ver `entorno-fisico-captura.md`). Para evitar el modelado verbal (que la
participante repita mecánicamente lo que se le dice, en vez de producir su
propia emisión espontánea), la palabra o gesto objetivo se presentó
mediante **tarjetas de estímulo visual** (imagen/emoji), nunca
pronunciada primero por el acompañante. Se controló la fatiga limitando
las sesiones a un máximo de 15 minutos, con descansos, y registrando
observaciones de ánimo/fatiga en cada sesión (`registros/sesiones.csv`).

### Pipeline tecnológico
Arquitectura de tres etapas, cada una como módulo independiente:
- `grabar.py` — captura guiada de muestras con verificación de energía
  mínima y registro de trazabilidad.
- `entrenar.py` — extracción de características (MFCC 13 coeficientes +
  deltas para voz; landmarks de MediaPipe Pose normalizados para gestos) y
  entrenamiento de un clasificador k-NN (k=3) con distancia DTW.
- `predecir.py` — inferencia en vivo con umbral de decisión y salida por
  voz sintetizada.

Se adoptó **validación cruzada dejando-uno-fuera (LOOCV)** como estándar
metodológico apropiado para conjuntos de datos pequeños (n<150 por canal),
donde una partición train/test convencional dejaría muy pocas muestras de
prueba para ser informativa. LOOCV maximiza el uso del dato disponible
sin optimismo de sobreajuste, al evaluar cada muestra contra un modelo
entrenado con todas las demás.

### Consideraciones éticas
El protocolo se alinea con los principios de la **Declaración de
Helsinki** de la Asociación Médica Mundial (consentimiento informado
previo a cualquier procedimiento, minimización de riesgo, protección de
la confidencialidad) y con el marco legal colombiano aplicable: **Ley
1581 de 2012** (protección de datos personales — los audios/videos son
datos biométricos sensibles, almacenados exclusivamente en equipo local,
nunca en la nube ni compartidos con terceros) y **Resolución 8430 de
1993** del Ministerio de Salud (normas para investigación en salud con
seres humanos en Colombia, incluida la clasificación del riesgo de la
investigación). El consentimiento informado se firmó **antes** de
cualquier grabación o interacción de captura de datos. **[PENDIENTE]**
aval formal de comité de ética institucional — obligatorio antes de
someter a una revista indexada (ver `Protocolo_Investigacion_MVP_Voz_Gestos.docx`).

## III. Resultados

### Métricas técnicas (offline)
| Canal | n | Exactitud LOOCV | IC95% Clopper-Pearson |
|---|---|---|---|
| Voz (8 palabras) | 103 | 80.6% | 71.6%–87.7% |
| Gestos (3 clases) | 30 | 80.0% | 61.4%–92.3% |

[Insertar tabla por palabra/gesto desde `reportes/validacion_*.json` más
reciente, y las figuras `confusion_*.png` como Figura 1 y 2 — ya
incluidas en `Protocolo_Investigacion_MVP_Voz_Gestos.docx`.]

### Métricas clínicas (en vivo)
Sobre 44 y 26 intentos confirmados en dos sesiones de validación en vivo
(total 70, superando el mínimo de 30 exigido por el protocolo), la
exactitud dependió críticamente del nivel de consenso del modelo:

| Consenso del modelo | n | Exactitud | IC95% Clopper-Pearson |
|---|---|---|---|
| Unánime (3/3 vecinos) | 13 | 92.3% | 64.0%–99.8% |
| Mayoría (2/3) | 34 | 50.0% | 32.4%–67.6% |
| Mínimo (1/3) | 23 | 13.0% | 2.8%–33.6% |

Latencia media de predicción: 3.28 s con el banco de referencias actual
(103 muestras) — en el límite del umbral de usabilidad técnica (<3 s)
definido en el protocolo; ver `brechas-cientificas-y-escalamiento.md` §7
para el análisis de escalabilidad y la solución propuesta (reducción a
prototipos por clase) antes de ampliar el vocabulario o el número de
participantes.

### Comparación de línea base — PENDIENTE DE EJECUCIÓN
**No se puede reportar esta sección todavía.** El protocolo original
(`protocolo-validacion.md` §4) contempla un test de comprensión con 3-5
oyentes externos que no conocen a YP, comparando su porcentaje de acierto
al escuchar los audios crudos contra la exactitud del sistema. Esta prueba
**no se ha ejecutado**. Es la tarea pendiente de mayor prioridad antes de
someter el artículo — sin ella no hay base de datos para aplicar la prueba
de McNemar (comparación pareada de proporciones correlacionadas) o
Wilcoxon con rangos con signo que exige el diseño estadístico correcto
para esta comparación. Ver Anexo de tareas pendientes.

## IV. Discusión y conclusiones

### Interpretación
Las palabras con intervalos de confianza más amplios (agua, baño, dolor,
no, sí) no mostraron relación clara con la duración de la emisión
(correlación de Pearson r=−0.386, débil e inversa — hipótesis probada y
rechazada con los datos reales, ver `brechas-cientificas-y-escalamiento.md`
§1). Los pares más confundidos en voz (sí↔no, no↔baño, mamá↔comer,
dolor↔no, baño↔mamá, agua↔dolor) sugieren proximidad en el espacio
acústico MFCC más que un factor único explicativo; se deja como trabajo
futuro un análisis de distancia DTW intra- vs. inter-clase. En gestos, el
patrón es más claro: bajo doble tarea, los gestos finos colapsan
completamente (10/10 casos) hacia el gesto de mayor amplitud, un efecto
consistente con la literatura de interferencia cognitivo-motora de doble
tarea.

### Análisis de costos
El sistema completo se desarrolló con **$0 COP de hardware adicional**
(computador y micrófono ya disponibles en el hogar), frente a
dispositivos generadores de habla comerciales que superan los US$6.000.
Este diferencial de costo es, en sí mismo, un argumento de justicia
social y accesibilidad económica en salud, particularmente relevante en
contextos con acceso limitado a servicios especializados como el
departamento del Atlántico.

### Limitaciones metodológicas
- **N=1**: estudio de caso único; los hallazgos de exactitud no son
  generalizables estadísticamente a otras personas con perfiles motores
  distintos (sí lo es, con mayor solidez estadística, el hallazgo de
  interferencia cognitivo-motora, por el diseño de comparación pareada
  dentro del mismo sujeto).
- **Vocabulario cerrado**: 8 palabras y 3 gestos; no se ha evaluado la
  curva de degradación al ampliar el vocabulario.
- **Diagnóstico específico no publicado**: existe caracterización clínica
  formal (certificación oficial de discapacidad), pero se mantiene
  confidencial por sensibilidad de datos de salud; esto limita la
  posibilidad de que revisores externos evalúen directamente la
  correspondencia entre el perfil motor y los resultados técnicos, salvo
  a través del comité de ética institucional.
- **Sensibilidad al ruido ambiental**: documentada y parcialmente resuelta
  mediante protocolo de entorno casero (`entorno-fisico-captura.md`), pero
  no cuantificada de forma experimental entre entornos distintos.
- **Ausencia de comparación contra línea base humana** (pendiente, ver
  §III).
- **Sin aval de comité de ética institucional** al momento de redactar
  este documento (en trámite).

## Conclusiones y trabajo futuro
Viabilidad técnica demostrada de un sistema de comunicación aumentativa
personalizado y de bajo costo, con exactitud útil condicionada a una
política de decisión que exige consenso del modelo. El hallazgo de
interferencia cognitivo-motora tiene una implicación de diseño directa:
los sistemas AAC multimodales para usuarios con compromiso motor deben
usar fusión secuencial, no simultánea. Trabajo futuro: ejecutar la
comparación de línea base humana (prioridad inmediata), ampliar a una
serie de casos con voluntarios adicionales, migrar a hardware dedicado, y
extender el vocabulario con curva de degradación controlada — ver
`propuesta-expansion.md` y `brechas-cientificas-y-escalamiento.md`.

## Disponibilidad de datos y ciencia abierta

Se publicará el código (`grabar.py`, `entrenar.py`, `predecir.py` y
módulos asociados) en un repositorio público (GitHub o Zenodo) tras la
aceptación o en paralelo al sometimiento, **excluyendo estrictamente**
todo archivo de audio o video real de YP (carpetas `data/`, `data_gestos/`,
`data_vivo_confirmada/`) para proteger su identidad biométrica. Se
incluirán únicamente: código fuente, `data_demo/` (audios sintéticos),
reportes agregados de métricas (`reportes/*.json`), y documentación. El
enlace del repositorio se añadirá a esta sección una vez creado.

## Ruta de publicación

Categorías editoriales apropiadas para un estudio N=1 con componente
técnico y social fuerte: revistas de fonoaudiología/logopedia, ingeniería
biomédica o tecnologías asistivas, e informática en salud, que acepten
reportes de caso o artículos metodológicos breves. Selección de revista
específica **pendiente** — verificar indexación (Publindex/Scimago) y
alcance (nacional vs. regional) según la estrategia de
`ruta-financiera-posicionamiento.md`, y una vez el manuscrito esté cerca
de versión final.

## Referencias

Reutilizar la bibliografía ya compilada en `propuesta-expansion.md`
(Project Relate, Voiceitt, Talker, MediaPipe, Kinect) y
`neurociencia-biomarcadores.md` (si se incluye la sección de trabajo
futuro sobre biomarcadores). Agregar formato de citación según la revista
destino (APA o Vancouver).

---

## Anexo — Tareas pendientes antes de someter el manuscrito

1. **[CRÍTICO]** Ejecutar la prueba de línea base humana (3-5 oyentes
   externos, protocolo ya definido en `protocolo-validacion.md` §4) y
   aplicar la prueba de McNemar o Wilcoxon correspondiente.
2. Obtener aval del Comité de Ética, Bioética e Integridad Científica
   Institucional de la CUC (Acuerdo 1231/2018). Radicar
   `Protocolo_Investigacion_MVP_Voz_Gestos.docx` por correo institucional
   antes del **4 de agosto de 2026** para entrar a la sesión ordinaria del
   **25 de agosto de 2026** (último martes del mes; verificar festivos con
   la Secretaría Jurídica). Falta adjuntar: hoja de vida del investigador
   principal (ver checklist §9.4 del protocolo).
3. ~~Definir si se busca caracterización clínica formal~~ — **RESUELTO
   2026-07-08**: existe certificación oficial de discapacidad y registro
   clínico; se mantiene en anexo confidencial (`docs/CONFIDENCIAL-caracterizacion-clinica.md`,
   excluido de git), no en el manuscrito público.
4. Completar validación en vivo del flujo secuencial rediseñado
   (`multimodal_predecir.py`).
5. Crear el repositorio de código abierto y enlazarlo en "Disponibilidad
   de datos".
6. Seleccionar la revista/evento destino definitivo.
