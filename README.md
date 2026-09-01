# MVP — Comunicación aumentativa de bajo costo para desconexión motora del habla

[![Tests](https://github.com/wilmerjoseperezorozco-dev/aac-voz-gestos-bajo-costo/actions/workflows/tests.yml/badge.svg)](../../actions/workflows/tests.yml)
[![Coverage — clasificador core](https://img.shields.io/badge/coverage_(modelo.py)-82%25-brightgreen)](tests/test_modelo.py)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21314646.svg)](https://doi.org/10.5281/zenodo.21314646)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![TRL 5-6](https://img.shields.io/badge/TRL-5--6-orange)](docs/fase-madurez-software.md)
[![Buscamos alianzas](https://img.shields.io/badge/🤝_Buscamos_alianzas-Fundaciones_en_Barranquilla-brightgreen)](../../issues/2)

> ### 🤝 ¿Tu fundación o institución quiere sumarse?
> Este proyecto busca aliados en Barranquilla y el Caribe colombiano para
> ampliar su impacto: más participantes, hardware de bajo costo, y
> llegar a más familias que necesitan una vía de comunicación accesible.
> **[Conoce la propuesta y escríbeme →](../../issues/2)**
>
> ¿Trabajas con ELA, Parkinson, esclerosis múltiple, secuelas de ACV u
> otras condiciones con compromiso motor del habla? Hay una búsqueda de
> alianzas específica por condición, con la ruta de expansión completa:
> **[Ver condiciones y ruta de expansión →](../../issues/3)** ·
> [`docs/ruta-expansion-condiciones-neurologicas.md`](docs/ruta-expansion-condiciones-neurologicas.md)
>
> 📊 ¿Por qué importa esto a escala? Impacto económico y social con
> fuentes verificables (OMS, Banco Mundial, DANE) + métricas reales de
> avance del proyecto:
> **[`docs/impacto-economico-social-y-metricas.md`](docs/impacto-economico-social-y-metricas.md)**

El proyecto está postulando a la convocatoria Ignacio H. de Larramendi
2026 de Fundación Mapfre, y se encuentra en proceso de vinculación
institucional con la Universidad de la Costa (CUC).

> **Aviso:** este es un prototipo de investigación de comunicación
> aumentativa y alternativa (AAC). **No es un dispositivo médico**, no ha
> sido evaluado ni registrado ante ninguna autoridad sanitaria (incluida
> INVIMA en Colombia), y no está diseñado para diagnóstico, tratamiento ni
> monitoreo clínico de ninguna condición. Uso bajo responsabilidad propia.
> Licencia: MIT (ver [LICENSE](LICENSE)). Repositorio:
> [github.com/wilmerjoseperezorozco-dev/aac-voz-gestos-bajo-costo](https://github.com/wilmerjoseperezorozco-dev/aac-voz-gestos-bajo-costo).

Sistema de comunicación aumentativa de tres capas para una persona con
desconexión motora del habla (participante YP), construido enteramente
sobre hardware ya disponible en el hogar — sin internet, sin GPU, sin
licencias comerciales:

1. **Reconocimiento personalizado de voz y gestos** — aprende los
   patrones únicos de la persona (voz con k-NN+DTW sobre MFCC, gestos con
   MediaPipe Pose), no un modelo genérico de habla típica.
2. **Tablero de selección visual** — 126 símbolos organizados en 10
   categorías, con escaneo de dos niveles (categoría → símbolo), pensado
   para cuando la vía directa de voz o gesto no basta.
3. **Expansión automática de frases** — un modelo de lenguaje local arma
   oraciones completas a partir de los conceptos seleccionados, con
   salvaguardas léxicas para no introducir ideas que la persona no eligió.

## 🏆 Posición en el estado del arte

| Aspecto | Sistemas comerciales | Este MVP |
|---|---|---|
| Curva de aprendizaje | 500+ frases grabadas (ej. Google Project Relate) | **10 muestras/palabra** |
| Costo de dispositivo | ~US$6.000+ (dispositivos AAC especializados) | **$0 (tu PC)** |
| Dependencia de internet | Sí (requiere nube) | **No (100% offline)** |
| Soporte de idiomas | Limitado (mayormente inglés) | **Español (extensible)** |
| Datos personales | En servidores del proveedor | **100% locales** |

## Por qué funciona este enfoque

Los reconocedores de voz comerciales fallan con habla disártrica/aprásica
porque están entrenados con habla típica. Este MVP invierte el problema:
**no intenta entender el habla estándar, aprende los patrones únicos de la
persona**. Con solo 10 grabaciones por palabra, el clasificador k-NN con
alineamiento temporal dinámico (DTW) compara cada nueva emisión contra las
muestras de referencia, tolerando sílabas alargadas o fragmentadas.

## Cómo empezar (sin terminal, doble clic)

```bash
INICIAR.bat   # abre el menú central con las 4 secciones (con consola visible, útil para depurar)
```

Para uso diario sin ninguna ventana de consola, crea un acceso directo a
`src/lanzar_silencioso.py` con `pythonw.exe` (ver comentarios en ese
archivo) — recomendado para presentaciones o demos.

## Flujo de uso (línea de comandos)

```bash
# Voz
py -3.12 src/grabar.py       # grabar muestras de voz
py -3.12 src/entrenar.py     # entrenar + reporte de validación (LOOCV)
py -3.12 src/predecir.py     # predicción en vivo: ella habla → texto + audio

# Gestos (webcam)
py -3.12 src/gestos_grabar.py
py -3.12 src/gestos_entrenar.py
py -3.12 src/gestos_predecir.py

# Tablero de selección + expansión de frases
py -3.12 src/tablero_escaneo.py
```

Prueba sin micrófono (verificación del pipeline / plan B para demo):

```bash
py -3.12 src/demo_sintetico.py
```

Ver la carpeta [`lanzadores/`](lanzadores/) para un `.bat` dedicado a cada
script, con Python 3.12 fijado explícitamente.

## Estructura

| Carpeta / archivo | Contenido |
|---|---|
| `config.json` | Vocabulario de voz, parámetros de audio y modelo |
| `src/vocabulario_nucleo.py` | Vocabulario núcleo del tablero (126 símbolos, 10 categorías, base académica Soto & Cooper 2021) |
| `src/audio_features.py` | Extracción MFCC + deltas con recorte de silencio |
| `src/modelo.py` | Clasificador k-NN + DTW con validación LOOCV |
| `src/gestos_features.py` | Extracción de landmarks de postura corporal (MediaPipe) |
| `src/tablero_escaneo.py` | Tablero de selección visual con escaneo de dos niveles |
| `src/generador_llm.py` | Expansión de frases con salvaguarda anti-alucinación léxica |
| `src/centro_comunicacion.py` | Menú central que lanza las 4 secciones (voz, gestos, tablero, multimodal) |
| `src/grabar.py` / `gestos_grabar.py` / `multimodal_grabar.py` | Sesiones de grabación guiadas |
| `src/entrenar.py` / `gestos_entrenar.py` | Entrenamiento + reporte de validación (JSON + PNG) |
| `src/predecir.py` / `gestos_predecir.py` / `multimodal_predecir.py` | Predicción en vivo con voz sintetizada |
| `data/`, `data_gestos/`, `registros/`, `modelos/` | Datos y modelos reales de YP (privados — **no publicar**, protegidos por `.gitignore`) |
| `data_demo/` | Audios sintéticos de prueba (publicables) |
| `reportes/` | Métricas de validación, matrices de confusión y hallazgos de sesión, con fecha |
| `docs/` | Metodología, plan de madurez del software y documentación de investigación |
| `lanzadores/` | Un `.bat` por script, con Python 3.12 fijado |

## Estado actual (2026-09)

- **Voz**: pipeline validado con datos reales de YP. Validación de
  referencia (n=103 muestras, 8 palabras): **80.6% de exactitud LOOCV,
  IC95% 71.6%-87.7%** (Clopper-Pearson). El vocabulario y el tamaño de
  la muestra siguen creciendo — ver `RESEARCH_LOG.md` para la
  cronología completa de validaciones.
- **Gestos**: canal validado con MediaPipe Pose. 80.0% de exactitud
  LOOCV, IC95% 61.4%-92.3% (n=30, 3 gestos).
- **Tablero de selección + expansión de frases**: en uso real desde
  julio de 2026, con múltiples sesiones documentadas y una tasa de
  oraciones confirmadas correctas cercana al 60% sobre el total de
  intentos registrados — el detalle sesión por sesión, incluyendo el
  patrón de mejor desempeño en selecciones cortas, está en
  `RESEARCH_LOG.md`.
- **Nivel de madurez**: TRL 5-6 (demostración con usuaria real en entorno
  relevante) — ver `docs/fase-madurez-software.md` para el detalle y la
  ruta hacia TRL 7.
- **Limitaciones conocidas**: estudio de caso único (N=1), vocabulario de
  voz cerrado, requiere Python 3.12 con dependencias instaladas (ver
  sección de limitaciones abajo para el detalle completo).

## 🔬 Hallazgos científicos

Dos hallazgos metodológicos, con estadística formal, documentados en
detalle en [`RESEARCH_LOG.md`](RESEARCH_LOG.md):

1. **Interferencia cognitivo-motora en captura simultánea.** Al capturar
   voz y gesto al mismo tiempo, la exactitud cae de forma
   estadísticamente significativa (voz: 80.6% → 36.7%, gestos: 80.0% →
   30.0%; los intervalos de confianza no se traslapan en ningún canal —
   efecto real, no ruido de muestra pequeña). Este hallazgo motivó
   rediseñar la arquitectura de captura, de simultánea a secuencial.
2. **La política de decisión importa tanto como el modelo.** El sistema
   es confiable cuando alcanza consenso interno entre sus vecinos más
   cercanos (92.3% de exactitud en vivo con consenso unánime) pero no
   con consenso parcial (13.0% con consenso mínimo) — la baja exactitud
   inicial en vivo no era un problema del modelo, sino del umbral de
   decisión, que se corrigió en consecuencia.

Ver también [`docs/impacto-economico-social-y-metricas.md`](docs/impacto-economico-social-y-metricas.md)
para el contexto de impacto (OMS, Banco Mundial, DANE) y las métricas
completas.

## Consejos para sesiones de grabación

1. Sesiones de máximo 15 minutos, con pausas — la fatiga degrada las muestras.
2. Ambiente silencioso y el micrófono siempre a la misma distancia (~15 cm).
3. Lo que importa es la **consistencia**, no la claridad: si ella dice "agua"
   como "a-ua", perfecto — el sistema aprende SU forma de decirlo.
4. Usar tarjetas con imágenes para pedir cada palabra sin modelarla
   verbalmente primero.
5. Registrar observaciones en `registros/sesiones.csv`.

## Ética y privacidad

- Consentimiento informado firmado antes de cada tipo de grabación,
  revisado y renovable, con derecho explícito a retirarse y a la
  eliminación de los datos.
- Los datos biométricos (`data/`, `data_gestos/`, `modelos/`,
  `registros/`) son sensibles: nunca se publican, están excluidos del
  repositorio por `.gitignore`. Al publicar, se usa solo `data_demo/` y
  métricas agregadas.
- En documentos públicos se usa siempre el alias **YP**, nunca el nombre
  real ni datos identificables.
- **Marco normativo aplicable:** Declaración de Helsinki (Asociación
  Médica Mundial) como referencia ética internacional para
  investigación con seres humanos; Ley 1581 de 2012 (Colombia,
  protección de datos personales/habeas data); Resolución 8430 de 1993
  (Ministerio de Salud, normas científicas y técnicas para
  investigación en salud) — la investigación se clasifica como de
  **riesgo mínimo** bajo esta resolución, dado el esquema de
  procesamiento local (offline) por diseño, sin alteración de la
  condición de salud de la participante ni exposición de información
  sensible a terceros.

## Comunidad y contribuciones

Este es un proyecto de **código abierto para uso libre, con mantenimiento
único** — ver [`CONTRIBUTING.md`](CONTRIBUTING.md) para la política
completa. En resumen: puedes usar y adaptar el código libremente (MIT),
pero el repositorio oficial no acepta Pull Requests externos; las
sugerencias van por [Issues](../../issues).

## Limitaciones conocidas y próximos pasos

- Estudio de caso único (N=1) — validación con más participantes en
  curso, necesaria para generalizar el método.
- Vocabulario de voz cerrado (15 palabras activas) — el tablero ya cubre
  126 conceptos, la vía de voz sigue siendo más limitada.
- Requiere Python 3.12 con dependencias instaladas manualmente; un
  instalador empaquetado sin terminal está en el roadmap
  (`docs/plan-comunidad-open-source-2026.md`).
- Fusión voz+gesto simultánea aún no implementada como modo único
  (existe captura multimodal, pero la fusión de señales es trabajo
  futuro).
- Sin soporte todavía para acceso por switch/pulsador único, relevante
  para personas con compromiso motor más severo que YP.

Ver `docs/plan-comunidad-open-source-2026.md` para la ruta completa a
12 meses.

## Citación

Ver [`CITATION.cff`](CITATION.cff). DOI de la versión publicada:
[10.5281/zenodo.21314646](https://doi.org/10.5281/zenodo.21314646).

---

## 🌐 Overview · Resumen

<table>
<tr>
<td width="50%">

### 🇬🇧 English

**Low-cost, three-layer AAC system for motor speech disconnection** —
offline, no GPU, no internet required. Combines personalized speech and
gesture recognition, a visual selection board (126 concepts), and
automatic sentence expansion with lexical safeguards.

**What it solves:** Commercial speech recognizers fail people with
dysarthria or apraxia because they are trained on typical voices. This
system reverses the challenge: instead of forcing the person to
approximate standard speech, it learns *their* unique patterns from as
few as 10 recordings per word.

**State of the art**

| Aspect | Commercial systems | This project |
|---|---|---|
| Learning curve | 500+ recorded phrases (e.g. Google Project Relate) | **10 samples/word** |
| Device cost | ~US$6,000+ (specialized AAC devices) | **$0 (your PC)** |
| Internet dependency | Yes (cloud-based) | **No — 100% offline** |
| Personal data | On provider's servers | **100% local** |

**Quick start:**
```bash
py -3.12 src/grabar.py      # record samples per word
py -3.12 src/entrenar.py    # train + generate validation report
py -3.12 src/predecir.py    # live: speak → text + audio output
py -3.12 src/tablero_escaneo.py  # visual selection board
```

**Status:** TRL 5-6 — real-world demonstration with a single participant
(YP), multiple documented sessions since July 2026. Reference validation
(n=103 samples, 8 words): **80.6% LOOCV accuracy, 95% CI 71.6%-87.7%**
(exact Clopper-Pearson interval); gesture channel: 80.0%, 95% CI
61.4%-92.3% (n=30). Single-case study; expansion to a multi-case series
is the current priority.

**Scientific findings** (full statistical detail in
[`RESEARCH_LOG.md`](RESEARCH_LOG.md)):
1. **Cognitive-motor interference under simultaneous capture.** Capturing
   voice and gesture at the same time causes a statistically significant
   accuracy drop (voice: 80.6% → 36.7%; gestures: 80.0% → 30.0%;
   non-overlapping confidence intervals — a real effect, not small-sample
   noise). This finding drove a redesign from simultaneous to sequential
   capture.
2. **Decision policy matters as much as the model.** The system is
   reliable when its nearest-neighbor classifier reaches internal
   consensus (92.3% live accuracy at unanimous consensus) but not under
   partial consensus (13.0% at minimum consensus) — the initial low
   live-session accuracy was a decision-threshold issue, not a model
   quality issue, and was corrected accordingly.

**Ethics and regulatory framework:** informed consent (signed, renewable,
right to withdraw), Declaration of Helsinki, Colombian data-protection
law (Ley 1581/2012), and Resolución 8430/1993 (Colombian Ministry of
Health) — classified as **minimal risk** given the fully local/offline
processing design. Sensitive biometric data never leaves local storage;
public materials use only the alias "YP," never identifying information.

**Economic and social context:** communication disability affects an
estimated 5-10% of the global population, yet only ~3% of people who
need assistive technology in low-income countries have access to it,
versus ~90% in high-income countries (WHO). Full sourced analysis in
[`docs/impacto-economico-social-y-metricas.md`](docs/impacto-economico-social-y-metricas.md).

**Partnerships:** actively seeking alliances with foundations and
clinical organizations working with ALS, Parkinson's, multiple
sclerosis, stroke-related aphasia, and related motor speech disorders,
to expand the case series — see [Issue #2](../../issues/2) and
[Issue #3](../../issues/3). The project is applying to Fundación
Mapfre's Ignacio H. de Larramendi 2026 grant and is in the process of
institutional affiliation with Universidad de la Costa (CUC).

**Contributing:** open source for use (MIT license), single-maintainer
repository — no external Pull Requests accepted, see
[`CONTRIBUTING.md`](CONTRIBUTING.md).

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21314646.svg)](https://doi.org/10.5281/zenodo.21314646)

</td>
<td width="50%">

### 🇨🇴 Español

**Sistema AAC de tres capas y bajo costo para desconexión motora del
habla** — sin internet, sin GPU, sin hardware especial. Combina
reconocimiento personalizado de voz y gestos, un tablero de selección
visual (126 conceptos) y expansión automática de frases con salvaguardas
léxicas.

**Qué resuelve:** Los reconocedores comerciales fallan con habla
disártrica o apráxica porque entrenan con voces típicas. Este sistema
invierte el reto: en lugar de pedirle a la persona que se acerque al
habla estándar, aprende *sus* patrones únicos con tan solo 10 grabaciones
por palabra.

**Estado del arte**

| Aspecto | Sistemas comerciales | Este proyecto |
|---|---|---|
| Curva de aprendizaje | 500+ frases grabadas (ej. Google Project Relate) | **10 muestras/palabra** |
| Costo de dispositivo | ~US$6.000+ (dispositivos AAC especializados) | **$0 (tu PC)** |
| Dependencia de internet | Sí (requiere nube) | **No — 100% offline** |
| Datos personales | En servidores del proveedor | **100% locales** |

**Inicio rápido:**
```bash
py -3.12 src/grabar.py      # grabar muestras por palabra
py -3.12 src/entrenar.py    # entrenar + generar reporte de validación
py -3.12 src/predecir.py    # en vivo: habla → texto + audio
py -3.12 src/tablero_escaneo.py  # tablero de selección visual
```

**Estado:** TRL 5-6 — demostración real con una participante (YP),
múltiples sesiones documentadas desde julio de 2026. Validación de
referencia (n=103, 8 palabras): **80.6% de exactitud LOOCV, IC95%
71.6%-87.7%** (Clopper-Pearson); gestos: 80.0%, IC95% 61.4%-92.3%
(n=30). Estudio de caso único; ampliar a una serie de casos es la
prioridad actual.

**Hallazgos científicos** (detalle estadístico completo en
[`RESEARCH_LOG.md`](RESEARCH_LOG.md)):
1. **Interferencia cognitivo-motora en captura simultánea.** Capturar
   voz y gesto al mismo tiempo causa una caída de exactitud
   estadísticamente significativa (voz: 80.6% → 36.7%; gestos: 80.0% →
   30.0%; intervalos de confianza que no se traslapan — efecto real, no
   ruido de muestra pequeña). Motivó el rediseño hacia captura
   secuencial.
2. **La política de decisión importa tanto como el modelo.** El sistema
   es confiable con consenso interno unánime (92.3% en vivo) pero no
   con consenso parcial (13.0% con consenso mínimo) — la baja exactitud
   inicial en vivo era un problema del umbral de decisión, no del
   modelo, y se corrigió en consecuencia.

**Ética y marco normativo:** consentimiento informado (firmado,
renovable, con derecho a retirarse), Declaración de Helsinki, Ley 1581
de 2012 (protección de datos), y Resolución 8430 de 1993 (Ministerio de
Salud) — clasificada como **riesgo mínimo** dado el procesamiento
100% local. Los datos biométricos nunca salen del almacenamiento local;
los materiales públicos usan solo el alias "YP".

**Contexto económico y social:** la discapacidad de la comunicación
afecta a un 5-10% estimado de la población mundial, pero solo ~3% de
quienes necesitan tecnología asistiva en países de bajos ingresos tiene
acceso a ella, frente a ~90% en países de altos ingresos (OMS). Análisis
completo con fuentes en
[`docs/impacto-economico-social-y-metricas.md`](docs/impacto-economico-social-y-metricas.md).

**Alianzas:** en búsqueda activa de fundaciones y organizaciones
clínicas que trabajen con ELA, Parkinson, esclerosis múltiple, afasia
post-ictus y condiciones afines, para ampliar la serie de casos — ver
[Issue #2](../../issues/2) y [Issue #3](../../issues/3). El proyecto
está postulando a la convocatoria Ignacio H. de Larramendi 2026 de
Fundación Mapfre, y en proceso de vinculación institucional con la
Universidad de la Costa (CUC).

**Contribuciones:** código abierto para uso (licencia MIT), mantenimiento
único — no se aceptan Pull Requests externos, ver
[`CONTRIBUTING.md`](CONTRIBUTING.md).

</td>
</tr>
</table>
