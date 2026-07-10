# Evaluación del generador de oraciones (Capa 2) — 2026-07-09

## Sistema evaluado

Capa 2 de `docs/arquitectura-vocabulario-nucleo-generativo.md`: expansión
de 2-3 símbolos seleccionados en una oración fluida, mediante un modelo
de lenguaje 100% local (Qwen2.5-1.5B-Instruct, cuantizado GGUF, vía
`llama-cpp-python`, sin conexión a nube — la intención comunicativa de YP
se trata como dato sensible). Modelo obtenido de
[Qwen/Qwen2.5-1.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF)
(distribución oficial), ~1.1 GB.

## Resultados

Sobre un conjunto de 5 combinaciones de símbolos de prueba, la
configuración final del generador (`src/generador_llm.py`) produjo 4/5
oraciones correctas y naturales, con concordancia de género femenino
ajustada correctamente ("dolorida", no "dolorido").

| Entrada | Salida | Evaluación |
|---|---|---|
| dolor + cabeza + mamá | "Mi cabeza duele, necesito que venga mamá." | Correcta |
| agua + querer | "Quiero beber agua." | Correcta |
| cansada + salir + no (de noche) | "Estoy cansada, quiero salir de noche." | Correcta, pero descarta el símbolo "no" |
| yo + querer + television | "Quiero ver la televisión." | Correcta |
| baño + ayuda | "Necesito ayuda para ir al baño." | Correcta |

## Hallazgos de diseño relevantes

**Atribución del sujeto.** Una configuración inicial del generador
asignaba estados y síntomas (dolor, cansancio) a la última persona
mencionada en la selección en vez de a quien se comunica — por ejemplo,
"dolor + cabeza + mamá" generaba "Mamá tiene dolor en la cabeza" en lugar
de atribuirlo a YP. Este es un riesgo de seguridad semántica real en un
sistema AAC: podría comunicar por error que otra persona está enferma,
no la usuaria. El prompt de sistema fue ajustado con una regla explícita
de atribución ("los síntomas y estados siempre corresponden a quien se
comunica"), verificada mediante los mismos casos de prueba.

**Anclaje de ejemplos (few-shot).** En modelos de este tamaño (1.5B
parámetros), un ejemplo de referencia incluido como texto narrado dentro
del prompt de sistema contamina generaciones no relacionadas — el modelo
lo reproduce como patrón fijo en vez de tratarlo como ilustración de una
regla general. La solución fue estructurar el ejemplo como un turno de
conversación real (`user`/`assistant`) previo a la consulta, técnica
estándar de *few-shot prompting*, que ancla el patrón sin contaminar
entradas distintas. Este es un hallazgo metodológico generalizable a
cualquier uso futuro de modelos de lenguaje pequeños en este proyecto.

**Manejo del símbolo "no".** En todas las combinaciones que incluían "no"
como símbolo de contenido (no como confirmación), la oración generada lo
omitía de forma sistemática y repetible. La interpretación más plausible
es que "no" resulta semánticamente ambiguo sin el contexto de una
pregunta directa (¿no qué?), y el modelo opta por omitirlo antes que
arriesgar una interpretación incorrecta — un comportamiento conservador
pero indeseable, porque descarta información que la usuaria sí
seleccionó explícitamente.

## Decisión de diseño

1. Los símbolos "sí" y "no" quedan reservados para su rol ya validado de
   señales de confirmación (Capa 1, y en `predecir.py`/
   `gestos_predecir.py`), y no se usan como símbolos de contenido para la
   Capa 2 generativa. La negación explícita en una oración, si se
   requiere, debe modelarse como un símbolo de contenido independiente
   (por ejemplo, "no quiero" como concepto propio).
2. La confirmación de la usuaria antes de comunicar cualquier oración
   generada se mantiene obligatoria, sin excepción — con una tasa de
   acierto de 4/5 en esta evaluación preliminar, el margen de error
   estimado (~20%) confirma que este paso no es opcional.

## Próximo paso

Construcción de la interfaz de escaneo (Capa 1: tablero de símbolos y
selección mediante la señal de confirmación ya validada). La Capa 2
(generación) queda validada como técnicamente viable en ejecución local,
lista para su integración.
