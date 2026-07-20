# MVP — Predicción de voz para personas con desconexión motora del habla

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21314646.svg)](https://doi.org/10.5281/zenodo.21314646)

> **Aviso:** este es un prototipo de investigación de comunicación
> aumentativa y alternativa (AAC). **No es un dispositivo médico**, no ha
> sido evaluado ni registrado ante ninguna autoridad sanitaria (incluida
> INVIMA en Colombia), y no está diseñado para diagnóstico, tratamiento ni
> monitoreo clínico de ninguna condición. Uso bajo responsabilidad propia.
> Licencia: MIT (ver [LICENSE](LICENSE)). Repositorio:
> [github.com/wilmerjoseperezorozco-dev/aac-voz-gestos-bajo-costo](https://github.com/wilmerjoseperezorozco-dev/aac-voz-gestos-bajo-costo).

Sistema mínimo y económico que aprende a reconocer **palabras seleccionadas
pronunciadas por una persona específica** (participante YP, 38 años,
desconexión motora del habla) y las convierte en voz sintetizada clara.
No requiere internet, GPU ni hardware especial: solo esta PC y un micrófono
casero (audífonos de celular sirven).

## Por qué funciona este enfoque

Los reconocedores de voz comerciales fallan con habla disártrica/aprásica
porque están entrenados con habla típica. Este MVP invierte el problema:
**no intenta entender el habla estándar, aprende los patrones únicos de la
persona**. Con solo 10 grabaciones por palabra, el clasificador k-NN con
alineamiento temporal dinámico (DTW) compara cada nueva emisión contra las
muestras de referencia, tolerando sílabas alargadas o fragmentadas.

## Flujo de uso (3 comandos)

```bash
# 1. Grabar muestras de YP (10 por palabra, sesiones cortas)
python src/grabar.py

# 2. Entrenar y generar el reporte de validación (métricas + matriz de confusión)
python src/entrenar.py

# 3. Predicción en vivo: ella habla → el sistema muestra y pronuncia la palabra
python src/predecir.py
```

Prueba sin micrófono (verificación del pipeline / plan B para la demo):

```bash
python src/demo_sintetico.py   # genera voces sintéticas y valida el sistema
```

## Canal de gestos (cámara)

Mismo flujo, mismo clasificador k-NN+DTW, pero la señal es el movimiento
del cuerpo captado por la webcam (MediaPipe Pose, 15 fps verificados):

```bash
python src/gestos_grabar.py     # graba 10 muestras por gesto (con vista previa)
python src/gestos_entrenar.py   # entrena + reporte LOOCV en reportes/
python src/gestos_predecir.py   # gesto en vivo → palabra hablada
```

Gestos iniciales en `config.json` (ajustables a lo que YP pueda hacer):
levantar una mano = sí, girar la cabeza = no, ambas manos = ayuda.

## Estructura

| Carpeta / archivo | Contenido |
|---|---|
| `config.json` | Vocabulario (8 palabras funcionales), parámetros de audio y modelo |
| `src/audio_features.py` | Extracción MFCC + deltas con recorte de silencio (numpy/scipy puro) |
| `src/modelo.py` | Clasificador k-NN + DTW con validación LOOCV |
| `src/grabar.py` | Sesión de grabación guiada con registro CSV |
| `src/entrenar.py` | Entrenamiento + reporte de validación (JSON + PNG) |
| `src/predecir.py` | Predicción en vivo con voz sintetizada (Microsoft Sabina, es-MX) |
| `data/` | Grabaciones reales de YP (privadas — **no publicar**) |
| `data_demo/` | Audios sintéticos de prueba (publicables) |
| `modelos/` | Modelo entrenado (`modelo_yp.npz` + `.json`) |
| `reportes/` | Métricas de validación y matrices de confusión con fecha |
| `registros/` | Trazabilidad: sesiones de grabación y aciertos en vivo (CSV) |
| `docs/` | Protocolo de validación y plan ejecutable |

## Estado de verificación (2026-07-06)

- Pipeline completo verificado en esta PC con datos sintéticos:
  **91.7% de exactitud LOOCV** (48 muestras, 8 palabras).
- Persistencia del modelo verificada (guardar → cargar → predecir: 4/4).
- Voz en español disponible: Microsoft Sabina Desktop (es-MX).

## Consejos para las sesiones con YP

1. Sesiones de máximo 15 minutos, con pausas — la fatiga degrada las muestras.
2. Ambiente silencioso y el micrófono siempre a la misma distancia (~15 cm).
3. Lo que importa es la **consistencia**, no la claridad: si ella dice "agua"
   como "a-ua", perfecto — el sistema aprende SU forma de decirlo.
4. Usar las tarjetas con imágenes (ella reconoce imágenes) para pedirle cada
   palabra sin modelarla verbalmente primero.
5. Registrar observaciones en `registros/sesiones.csv` (columna observaciones).

## Ética y privacidad

- Consentimiento informado firmado ANTES de la primera grabación
  (ver `docs/protocolo-validacion.md`).
- Los audios de `data/` son datos biométricos sensibles: nunca subirlos a
  repositorios públicos. Al publicar, usar solo `data_demo/` y métricas agregadas.
- En documentos públicos usar el alias **YP**, nunca el nombre completo.

---

## 🌐 Overview · Resumen

<table>
<tr>
<td width="50%">

### 🇬🇧 English

**Low-cost AAC system for motor speech disconnection** — offline, no GPU, no internet required.

**What it solves:** Commercial speech recognizers fail people with dysarthria or apraxia because they are trained on typical voices. This system reverses the challenge: instead of forcing the person to approximate standard speech, it learns *their* unique patterns from as few as 10 recordings per word.

**At maturity:** The person speaks a word (or makes a gesture) → a k-NN + DTW classifier recognizes it in real time → the word appears on screen and is spoken aloud through the local TTS engine. Voice and gesture channels run independently and can be used simultaneously.

**Quick start:**
```bash
python src/grabar.py      # record 10 samples per word
python src/entrenar.py    # train + generate validation report
python src/predecir.py    # live: speak → text + audio output
```
No microphone? Run `python src/demo_sintetico.py` to validate the full pipeline with synthetic data.

**Status:** Phase 1 · Pipeline validated — 91.7 % LOOCV accuracy (8 words, synthetic data). Real sessions with YP pending.

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21314646.svg)](https://doi.org/10.5281/zenodo.21314646)

</td>
<td width="50%">

### 🇨🇴 Español

**Sistema AAC de bajo costo para desconexión motora del habla** — sin internet, sin GPU, sin hardware especial.

**Qué resuelve:** Los reconocedores comerciales fallan con habla disártrica o apráxica porque entrenan con voces típicas. Este sistema invierte el reto: en lugar de pedirle a la persona que se acerque al habla estándar, aprende *sus* patrones únicos con tan solo 10 grabaciones por palabra.

**En fase madura:** La persona dice una palabra (o hace un gesto) → un clasificador k-NN + DTW la reconoce en tiempo real → la palabra aparece en pantalla y se vocaliza a través del motor TTS local. Los canales de voz y gesto funcionan de forma independiente y pueden usarse en simultáneo.

**Inicio rápido:**
```bash
python src/grabar.py      # grabar 10 muestras por palabra
python src/entrenar.py    # entrenar + generar reporte de validación
python src/predecir.py    # en vivo: habla → texto + salida de audio
```
¿Sin micrófono? Ejecuta `python src/demo_sintetico.py` para validar el pipeline completo con datos sintéticos.

**Estado:** Fase 1 · Pipeline validado — 91,7 % de precisión LOOCV (8 palabras, datos sintéticos). Sesiones reales con YP pendientes.

</td>
</tr>
</table>
