# Sesión 2026-07-14 — vocabulario ampliado, layout horizontal, hallazgos conductuales

## Contexto

Cuarta sesión real del tablero de escaneo con YP, la primera con el
vocabulario ampliado a 35 símbolos (animales, frutas, acciones) y con el
centro de comunicación como punto de entrada. Se corrigió en la misma
sesión un bug de lanzamiento de los modos de consola (ver
`reportes/hallazgo_primera_sesion_tablero_20260710.md` para el historial
de hallazgos previos).

## Observaciones conductuales

- **Mejora en identificación de pronombres:** la confusión "yo"/"tu"
  documentada en la primera sesión (2026-07-10) mostró mejora — YP
  distingue los símbolos con más consistencia tras la práctica
  acumulada.
- **Práctica voluntaria y ánimo:** YP practica el habla de forma
  voluntaria, con ánimo notablemente mejorado; muestra intención activa
  de nombrar palabras nuevas o describir lo que observa, no solo
  responder a instrucciones.
- **Comprensión emergente de secuencia:** comenzó a entender el orden en
  que debe seleccionar símbolos para construir una frase — funciona con
  consistencia en selecciones de 2 símbolos; con 3 símbolos aparece
  confusión de orden más seguido. Datos de hoy (n pequeño, no
  concluyente estadísticamente pero consistente con la observación):
  2 símbolos 7/10 (70%), 3 símbolos 4/6 (67%), 4 símbolos 0/1.
- **Comunicación contextual con significado compartido familiar:** en al
  menos un caso, YP formó una selección de solo 2 símbolos con intención
  de broma o referencia a una interacción hogareña específica — el
  significado no era literal en el texto generado, pero la familia,
  compartiendo el contexto doméstico, logró interpretar correctamente lo
  que quería decir. Esto sugiere que la efectividad comunicativa real
  del sistema es mayor de lo que la sola precisión semántica del LLM
  captura — la interpretación humana familiar complementa al sistema.
- **Resiliencia ante errores:** cuando la oración generada sale mal, YP
  no se desmotiva — vuelve a intentar la misma selección hasta obtener
  un resultado que refleje lo que quiere decir. Ejemplo registrado hoy:
  "perro + gallina" generó primero "La gallina quiere un perro para
  perro" (rechazado), reintentado con la misma selección generó "Perro
  gallina" (aceptado).
- **La interacción con el tablero es motivante en sí misma:** a YP le
  gusta la interacción con el computador portátil para seleccionar
  símbolos, independientemente del resultado — refuerza el valor del
  sistema como herramienta de aprendizaje, no solo de comunicación
  funcional.

## Datos cuantitativos

17 intentos registrados hoy, **11/17 (64.7%) confirmados como
correctos**. Desglose por número de símbolos seleccionados:

| Símbolos | Correctos | % |
|---|---|---|
| 2 | 7/10 | 70% |
| 3 | 4/6 | 67% |
| 4 | 0/1 | 0% |

## Hallazgo técnico: falla intermitente del audio generado

YP no sabe leer — el texto generado sin su correspondiente audio deja el
sistema inutilizable para ella en ese momento. Se identificó que la
función `hablar()` (`src/predecir.py`, compartida por los 4 modos)
descartaba silenciosamente cualquier fallo de reproducción (`except
Exception: pass`), sin ningún aviso ni reintento. Causa raíz probable:
inestabilidad conocida de `pyttsx3` sobre el motor SAPI5 de Windows al
reutilizar el mismo objeto de motor durante muchas llamadas seguidas
dentro del mismo proceso.

**Corregido:** `hablar()` ahora reintenta automáticamente con un motor de
voz recién creado si el motor reutilizado falla, y si de verdad no logra
reproducir el audio, imprime una advertencia visible en la consola en
vez de fallar en silencio. Probado con 5 llamadas seguidas simulando una
sesión real, sin fallos.

## Próximo paso

Confirmar en la próxima sesión que el audio suena de forma consistente
en cada oración generada. Seguir observando el punto de confusión en
selecciones de 3+ símbolos para determinar si es un límite real de carga
cognitiva o simplemente falta de práctica con selecciones más largas.
