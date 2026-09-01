# MVP — Comunicación aumentativa de bajo costo para desconexión motora del habla

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

## Estado actual (2026-08)

- **Voz**: pipeline validado con datos reales de YP, exactitud LOOCV
  ~77-80% según la sesión (ver `reportes/`); vocabulario configurable en
  `config.json` (15 palabras funcionales activas).
- **Gestos**: canal validado con MediaPipe Pose, exactitud LOOCV ~80% en
  gestos configurados.
- **Tablero de selección + expansión de frases**: en uso real desde
  julio de 2026, con múltiples sesiones documentadas. En la sesión más
  reciente con datos cuantitativos (2026-07-14): 64.7% de oraciones
  confirmadas como correctas sobre 17 intentos, con mejor desempeño en
  selecciones de 2 símbolos (70%) que de 3+ (67% y en descenso) —
  hallazgo consistente con carga cognitiva creciente, documentado en
  `reportes/hallazgo_sesion_20260714.md`.
- **Nivel de madurez**: TRL 5-6 (demostración con usuaria real en entorno
  relevante) — ver `docs/fase-madurez-software.md` para el detalle y la
  ruta hacia TRL 7.
- **Limitaciones conocidas**: estudio de caso único (N=1), vocabulario de
  voz cerrado, requiere Python 3.12 con dependencias instaladas (ver
  sección de limitaciones abajo para el detalle completo).

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

**Quick start:**
```bash
py -3.12 src/grabar.py      # record samples per word
py -3.12 src/entrenar.py    # train + generate validation report
py -3.12 src/predecir.py    # live: speak → text + audio output
py -3.12 src/tablero_escaneo.py  # visual selection board
```

**Status:** TRL 5-6 — real-world demonstration with a single participant
(YP), multiple documented sessions since July 2026. Single-case study;
expansion to a multi-case series is the current priority.

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

**Inicio rápido:**
```bash
py -3.12 src/grabar.py      # grabar muestras por palabra
py -3.12 src/entrenar.py    # entrenar + generar reporte de validación
py -3.12 src/predecir.py    # en vivo: habla → texto + audio
py -3.12 src/tablero_escaneo.py  # tablero de selección visual
```

**Estado:** TRL 5-6 — demostración real con una participante (YP),
múltiples sesiones documentadas desde julio de 2026. Estudio de caso
único; ampliar a una serie de casos es la prioridad actual.

**Contribuciones:** código abierto para uso (licencia MIT), mantenimiento
único — no se aceptan Pull Requests externos, ver
[`CONTRIBUTING.md`](CONTRIBUTING.md).

</td>
</tr>
</table>
