# Hallazgo — interferencia cognitivo-motora en captura simultánea (2026-07-08)

## Pregunta que se probó

¿Se puede pedirle a YP que hable y haga un gesto **al mismo tiempo** para
combinar los dos canales (voz + movimiento) en una sola señal más robusta?

## Metodología

Se grabaron 30 pares sincronizados (YP dice la palabra Y hace el gesto en
la misma ventana de 3 segundos) para los 3 significados compartidos: sí,
no, ayuda. Se entrenó cada modelo (voz, gestos) **solo con las muestras de
un solo canal** (sin doble tarea) y se evaluaron las 30 muestras
simultáneas como conjunto de prueba **separado** (no mezclado con el
entrenamiento) — metodología correcta para medir generalización real, no
solo ajuste al propio dataset.

## Resultado

| Canal | Exactitud con una sola tarea | Exactitud con doble tarea (voz+gesto a la vez) | Caída |
|---|---|---|---|
| Voz | 80.6% | **36.7%** | −43.9 pp |
| Gestos | 80.0% | **30.0%** | −50.0 pp |

Ambos canales caen a niveles cercanos al azar (para gestos, 3 clases →
33% es puro azar; el 30% medido está prácticamente en el piso).

## Patrón del error (gestos, el más claro)

```
no_cabeza_lado  (real) → predicho ayuda_dos_manos: 10/10 veces
si_mano_arriba  (real) → predicho ayuda_dos_manos: 10/10 veces
ayuda_dos_manos (real) → predicho ayuda_dos_manos:  9/10 veces (correcto)
```

Bajo doble tarea, los gestos finos (una mano, giro de cabeza) colapsan
hacia el movimiento más grande y menos específico (ambas manos arriba).
Es consistente con la literatura de interferencia cognitivo-motora: cuando
la atención se divide entre dos tareas motoras/cognitivas, el sistema
nervioso prioriza el movimiento más simple/dominante y pierde precisión en
los matices — un efecto documentado en investigación de doble tarea en
personas con compromiso motor.

## Decisión de diseño (consecuencia directa del hallazgo)

**No se debe pedir captura simultánea en el sistema real.** Se rediseñó
`src/multimodal_predecir.py` de captura *simultánea* a **secuencial**:

1. Captura solo voz (con toda la atención de YP en hablar).
2. Si la voz no da consenso total, **entonces** se pide el gesto por
   separado (con toda la atención en el movimiento) como desempate.
3. Nunca se piden ambos canales a la vez.

Los 60 pares "_multi_" (30 voz + 30 gesto) quedan **excluidos del
entrenamiento** de los modelos de un solo canal (ver cambios en
`src/entrenar.py` y `src/gestos_entrenar.py`) — mezclarlos degradaba el
modelo limpio de 80%/80.6% a 68-81%. Se conservan como evidencia archivada
del estudio de interferencia, no como material de entrenamiento.

## Por qué esto es un resultado valioso para la sustentación

- Es una pregunta de investigación real, con metodología correcta
  (train/test separados, no contaminados) y un resultado cuantificado.
- Conecta directamente el proyecto con neurociencia motora (interferencia
  de doble tarea), no solo con ingeniería de software.
- Cambió una decisión de diseño real, con evidencia — el sistema construido
  después de este hallazgo es mejor que el que había antes.
- Es honesto: probamos una hipótesis razonable (fusión simultánea) y los
  datos mostraron que estaba equivocada. Eso es ciencia, y es más
  convincente ante un jurado que solo mostrar números que salieron bien.
