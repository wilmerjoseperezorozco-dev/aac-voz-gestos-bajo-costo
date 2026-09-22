# Protocolo de entorno físico de captura

> Versión general, sin datos de ninguna persona real. Generaliza el
> protocolo casero usado desde la Fase 1 del proyecto (referenciado
> como "Anexo B" en el expediente de la convocatoria MAPFRE), para que
> cualquier sesión nueva — con la participante actual o con futuros
> participantes de la serie de casos ampliada — mantenga condiciones de
> grabación comparables entre sí.

## Por qué importa estandarizar el entorno

El clasificador (voz y gestos) es sensible a la calidad y consistencia
de la señal de entrada. Grabar unas sesiones con buena luz y otras a
contraluz, o unas con ruido de fondo y otras en silencio, introduce
variabilidad que no viene de la persona sino del entorno — y puede
confundirse con una mejora o un empeoramiento real del sistema. Este
protocolo existe para que esa fuente de ruido quede controlada.

## Lista de verificación antes de cada sesión

- [ ] **Micrófono en posición fija** — auriculares con micrófono
      integrado, o un soporte casero tipo brazo. Evitar sostenerlo a
      mano o dejarlo sobre una superficie que se mueva.
- [ ] **Ruido ambiente reducido** — ventilador, televisor y otros
      aparatos ruidosos apagados durante la sesión.
- [ ] **Fondo de cámara liso y de color uniforme** — sin patrones ni
      movimiento de otras personas detrás de quien graba.
- [ ] **Iluminación frontal** — nunca a contraluz (ventana o luz
      detrás de la persona).
- [ ] **Encuadre de cámara y posición de la silla marcados**, de forma
      reproducible entre sesiones (por ejemplo, con cinta en el piso
      para la posición de la silla).
- [ ] **Verificación de encuadre antes de grabar** — usar la vista
      previa que ya ofrecen los scripts de captura (`verificar_encuadre()`
      en `gestos_features.py`) para confirmar que la cámara detecta a
      la persona correcta antes de empezar.

## Ficha de sesión (registrar en cada sesión, no solo al inicio del proyecto)

| Campo | Valor |
|---|---|
| Fecha y hora | |
| Personas presentes | |
| Estado de ánimo / fatiga observado | |
| Incidencias de ruido o interrupción | |
| Canal grabado (voz / gestos / cara / mirada) | |
| Observaciones adicionales | |

Esta ficha complementa, no reemplaza, los registros automáticos que ya
generan los scripts (`registros/sesiones.csv`, `sesiones_gestos.csv`,
etc.) — recoge el contexto humano que un CSV no captura por sí solo.

## Relación con otros documentos

- El consentimiento informado de cada sesión sigue un proceso aparte —
  ver [`plantilla-consentimiento-informado-serie-de-casos.md`](plantilla-consentimiento-informado-serie-de-casos.md).
- Los hallazgos sobre calidad de captura y su efecto en los resultados
  se documentan en [`RESEARCH_LOG.md`](../RESEARCH_LOG.md) a medida que
  se acumulan sesiones nuevas.
