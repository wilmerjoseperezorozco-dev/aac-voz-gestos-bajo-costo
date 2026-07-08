# Extensión a otras condiciones del cerebro — biomarcadores digitales de voz y movimiento

Cómo el mismo sistema (voz + movimiento como series temporales) se extiende a
la **detección temprana y el monitoreo** de otras condiciones neurológicas y
psiquiátricas — con el encuadre ético y científico que hace la propuesta
defendible y publicable.

> ⚠️ **Principio rector — leer antes que nada.** Esto NO es un diagnosticador.
> Ningún software de este tipo diagnostica Alzheimer, esquizofrenia ni nada.
> Lo que la ciencia respalda es **triaje y monitoreo**: señales objetivas que
> ayudan a un profesional de salud a decidir a quién derivar y a seguir la
> evolución de un paciente ya diagnosticado. El sistema NUNCA da un veredicto
> clínico; produce indicadores que un neurólogo/psiquiatra interpreta. Sin
> esta línea, la propuesta es irresponsable; con ella, es innovación seria.

## 1. Por qué nuestro sistema ya sirve de base

Lo que construimos para YP captura exactamente las dos señales que la
neurociencia usa como biomarcadores digitales:

| Señal que ya capturamos | Biomarcador clínico que representa |
|---|---|
| MFCC + duración + pausas (audio) | Ritmo del habla, pausas, prosodia |
| Series de pose/movimiento (cámara) | Motricidad, temblor, lentitud, expresividad facial |
| Texto de lo que se dice (a añadir) | Coherencia semántica, densidad de contenido, sintaxis |

El cambio de enfoque clave respecto al MVP de YP:

- **YP (n=1):** aprender el patrón de UNA persona para reconocer SUS
  palabras. Clasificación personalizada.
- **Cribado neurológico (cohortes):** comparar el habla/movimiento de una
  persona contra un patrón poblacional, o contra ELLA MISMA en el tiempo,
  para detectar desviaciones. Requiere datos de muchas personas con
  etiquetas clínicas — no se puede hacer con una sola.

## 2. Alzheimer y deterioro cognitivo leve — lo que la ciencia valida

Es el caso mejor respaldado. La investigación 2025-2026 muestra que en el
Alzheimer el habla presenta, de forma medible:

- **Habla más lenta, más pausas, desorganización temporal** — validado en
  inglés Y español (relevante para Colombia).
- Los *embeddings* de audio de modelos de reconocimiento superan a otros
  métodos; añadir las **pausas** como rasgo mejora consistentemente la
  clasificación.
- Se combina lo acústico (ritmo, tono) con lo lingüístico (léxico, sintaxis,
  semántica) en un solo protocolo.

**Prueba estándar reproducible (la "Cookie Theft" o descripción de imagen):**
se pide describir una lámina; se miden pausas, velocidad, riqueza de
vocabulario y coherencia. Esto encaja perfecto con nuestro pipeline: es
grabar audio + extraer rasgos temporales, algo que ya hacemos.

## 3. Psicosis / espectro esquizofrenia — encuadre correcto

Aquí hay que ser especialmente cuidadoso. **No existe un "detector de amigos
imaginarios" y construirlo sería estigmatizante y clínicamente falso.** Lo
que la ciencia realmente mide:

- **Densidad semántica baja** (decir mucho con poco contenido) y **pérdida de
  coherencia** entre frases predicen conversión a psicosis en jóvenes de alto
  riesgo. Un estudio clásico alcanzó alta precisión con análisis semántico
  latente + etiquetado gramatical.
- **Dinámica de pausas + coherencia semántica** evalúan el trastorno del
  pensamiento de forma automatizada.
- Modelos multimodales recientes reportan F1 ~83% distinguiendo psicosis
  temprana, y —crucial— **modelan la incertidumbre** (dicen "no estoy seguro"
  en vez de forzar una etiqueta).

El reencuadre responsable de tu idea de "patrones extraños": el sistema no
juzga el *contenido* (si habla de voces) sino la **estructura longitudinal**
del habla de una persona ya en seguimiento clínico — ¿su coherencia bajó esta
semana respecto a su línea base? Eso es una alerta para que el clínico
revise, no un diagnóstico. Es monitoreo, con consentimiento, dentro de un
tratamiento existente.

## 4. Otras condiciones donde el mismo motor aplica

| Condición | Señal principal | Marcador |
|---|---|---|
| Parkinson | Voz + movimiento | Voz monótona, temblor, lentitud (bradicinesia) — nuestro canal de cámara con MediaPipe ya mide esto |
| Depresión (MDD) | Voz | Prosodia plana, habla lenta, menos variación de tono |
| Deterioro cognitivo leve | Voz + lenguaje | Pausas, búsqueda de palabras, menor complejidad |
| Ictus / afasia | Voz + movimiento | Igual que el caso de YP: rehabilitación y comunicación |

## 5. Cómo se "soluciona algo" desde neurociencia + IA

El valor no es diagnosticar; es **cerrar la brecha de acceso**. En el
Atlántico y zonas rurales de Colombia no hay neurólogos suficientes ni
pruebas costosas. Un cribado por voz de 3 minutos, con un celular, permite:

1. **Detección temprana → derivación:** marcar a quién conviene que vea un
   especialista, meses antes de que la familia note síntomas graves.
2. **Monitoreo entre citas:** seguir la evolución de un paciente diagnosticado
   sin que viaje a la ciudad cada semana.
3. **Objetividad:** una medida repetible que complementa el juicio clínico.
4. **Tamizaje comunitario de bajo costo:** llevar el cribado a donde no llega
   la neurología.

## 6. Ruta ejecutable realista (y honesta sobre lo que falta)

```
Fase A (posible ya, educativa): prototipo de cribado de Alzheimer
  - Implementar la tarea de descripción de imagen + extracción de pausas,
    velocidad y riqueza léxica sobre nuestro pipeline actual.
  - Entrenar/validar con un DATASET PÚBLICO con etiquetas clínicas
    (p. ej. retos ADReSS/ADReSSo, DementiaBank — acceso académico).
  - Entregable universitario: demostrar el pipeline sobre datos validados,
    reportando métricas honestas. SIN pacientes reales todavía.

Fase B (requiere alianza clínica y comité de ética):
  - Convenio con un hospital/universidad con área de neurología o psiquiatría.
  - Aprobación de comité de ética (IRB) + consentimiento informado.
  - Recolección de cohorte local con etiquetas clínicas reales.
  - El software SIEMPRE como apoyo a la decisión, nunca autónomo.

Fase C (producto): dispositivo de tamizaje comunitario validado clínicamente,
  con marcado regulatorio (INVIMA en Colombia) si se usa asistencialmente.
```

## 7. Límites que DEBES declarar en la presentación

- No diagnostica; es apoyo a la decisión clínica.
- Un modelo entrenado en otro idioma/población puede no servir en Colombia
  (sesgo de datos) — por eso importa validar localmente.
- Riesgo de falsos positivos → ansiedad; y de estigma, sobre todo en salud
  mental. El diseño debe minimizar daño (modelar incertidumbre, no etiquetar).
- Datos de salud = altamente sensibles: consentimiento, anonimización,
  almacenamiento local, cumplimiento de habeas data (Ley 1581 de 2012, CO).
- Requiere validación clínica y aprobación ética antes de cualquier uso real.

## 8. Referencias (bibliografía para la propuesta)

Alzheimer / deterioro cognitivo:
- Futuro del ML en detección por voz (Acoustics 2025): https://doi.org/10.3390/acoustics7040072
- Screening de deterioro cognitivo multidominio (Frontiers Aging Neurosci): https://www.frontiersin.org/journals/aging-neuroscience/articles/10.3389/fnagi.2026.1816747/full
- Revisión sistemática de IA explicable en declive cognitivo (npj Digital Medicine): https://www.nature.com/articles/s41746-025-02105-z
- Benchmark de modelos fundacionales de voz para demencia (arXiv 2506.11119): https://arxiv.org/abs/2506.11119
- Reto multilingüe ADReSS-M (español incluido): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11218814/

Psicosis / esquizofrenia:
- Marcadores semánticos y acústicos, ML combinatorio (Schizophrenia Bulletin): https://academic.oup.com/schizophreniabulletin/article/49/Supplement_2/S163/6776140
- Modelado de incertidumbre multimodal en el espectro de psicosis (npj Digital Medicine): https://www.nature.com/articles/s41746-025-02309-3
- Pausas + coherencia semántica para trastorno del pensamiento (arXiv 2507.13551): https://arxiv.org/pdf/2507.13551
- Predicción de psicosis por densidad semántica y contenido latente (Schizophrenia, Nature): https://www.nature.com/articles/s41537-019-0077-9
- Marcadores longitudinales de cambio en psicosis (NPP Digital Psychiatry): https://www.nature.com/articles/s44277-025-00034-z
