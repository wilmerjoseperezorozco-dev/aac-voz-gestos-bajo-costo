# MVP — Predicción de voz para personas con desconexión motora del habla

> **Aviso:** este es un prototipo de investigación de comunicación
> aumentativa y alternativa (AAC). **No es un dispositivo médico**, no ha
> sido evaluado ni registrado ante ninguna autoridad sanitaria (incluida
> INVIMA en Colombia), y no está diseñado para diagnóstico, tratamiento ni
> monitoreo clínico de ninguna condición. Uso bajo responsabilidad propia.
> Licencia: MIT (ver [LICENSE](LICENSE)). Repositorio:
> [github.com/wilmerjoseperezorozco-dev/aac-voz-gestos-bajo-costo](https://github.com/wilmerjoseperezorozco-dev/aac-voz-gestos-bajo-costo).

Sistema mínimo y económico que aprende a reconocer **palabras seleccionadas
pronunciadas por una persona específica** (participante YP, 35 años,
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
