# Hallazgo — primera validación del generador de oraciones local (2026-07-09)

## Qué se probó

Capa 2 de `docs/arquitectura-vocabulario-nucleo-generativo.md`: expandir
2-3 símbolos seleccionados en una oración fluida, usando un modelo de
lenguaje **100% local** (Qwen2.5-1.5B-Instruct, cuantizado GGUF, vía
`llama-cpp-python`, sin nube — la intención comunicativa de YP es dato
sensible). Modelo descargado de
[Qwen/Qwen2.5-1.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF)
(oficial), ~1.1 GB.

## Iteración 1 — prompt básico

| Entrada | Salida | Evaluación |
|---|---|---|
| dolor + cabeza + mamá | "Mamá tiene dolor en la cabeza." | ❌ Sujeto equivocado — le atribuyó el síntoma a mamá, no a YP |
| agua + querer | "Quiero beber agua." | ✅ |
| cansada + salir + no | "Cansada de no salir, decide salir de noche." | ❌ Incoherente |
| yo + querer + television | "Quiero ver la televisión." | ✅ |
| baño + ayuda | "Ayuda en el baño." | ⚠️ Vago, no captura la petición |

**2/5 correctas.** Hallazgo: el modelo por defecto asigna síntomas/estados
a la última persona mencionada, no a quien se comunica — riesgo real de
seguridad semántica en un sistema AAC (podría comunicar que otra persona
está enferma, no YP).

## Iteración 2 — regla explícita + ejemplo embebido en el prompt de sistema

Se agregó la regla "los síntomas/estados son siempre de ELLA" con un
ejemplo narrado dentro del texto del prompt de sistema.

| Entrada | Salida | Evaluación |
|---|---|---|
| dolor + cabeza + mamá | "Me duele la cabeza, quiero que venga mamá." | ✅ |
| agua + querer | "Me duele la cabeza, quiero que me ayude con la deshidratación." | ❌❌ El ejemplo se "filtró" a una entrada no relacionada |
| baño + ayuda | "Me duele el baño, necesito ayuda." | ❌ Sin sentido — misma contaminación |

**Empeoró.** Hallazgo metodológico importante: en modelos pequeños
(1.5B), un ejemplo **narrado dentro del prompt de sistema** contamina
generaciones no relacionadas — el modelo lo trata como patrón a repetir,
no como ilustración de una regla.

## Iteración 3 — ejemplo como turno real de conversación (corrección)

Se movió el ejemplo a un par de turnos `user`/`assistant` reales antes de
la consulta, en vez de texto narrado en el prompt de sistema — técnica
estándar de *few-shot prompting* que ancla el patrón sin contaminar
entradas distintas.

| Entrada | Salida | Evaluación |
|---|---|---|
| dolor + cabeza + mamá | "Mi cabeza duele, necesito que venga mamá." | ✅ |
| agua + querer | "Quiero beber agua." | ✅ |
| cansada + salir + no (de noche) | "Estoy cansada, quiero salir de noche." | ⚠️ Correcta pero **descarta "no"** |
| yo + querer + television | "Quiero ver la televisión." | ✅ |
| baño + ayuda | "Necesito ayuda para ir al baño." | ✅ |

**4/5 correctas**, con concordancia de género femenino ajustada
adicionalmente ("dolorida", no "dolorido").

## Hallazgo persistente — el símbolo "no" se descarta de forma repetible

En las 3 iteraciones, cualquier combinación que incluyera "no" como
símbolo de contenido (no de confirmación) produjo una oración que lo
ignoraba silenciosamente. No es ruido — se repite de forma consistente.
**Interpretación:** "no" es semánticamente ambiguo fuera de una pregunta
directa (¿no qué?) y el modelo, sin ese contexto, lo omite en vez de
arriesgar una interpretación incorrecta — en cierto sentido, un
comportamiento "conservador" pero indeseable porque pierde información
que la usuaria sí seleccionó.

## Decisión de diseño resultante

1. **"sí"/"no" se reservan para su rol ya validado**: señales de
   confirmación en el escaneo (Capa 1) y en `predecir.py`/`gestos_predecir.py`
   — no como símbolos de contenido para la Capa 2 generativa. Si se
   necesita negación explícita en una oración, debe modelarse como un
   símbolo de contenido distinto (ej. "no quiero" como concepto propio),
   no reutilizando "no".
2. **Los ejemplos de few-shot para LLMs pequeños siempre van como turnos
   de conversación reales, nunca narrados dentro del prompt de sistema**
   — regla general para cualquier trabajo futuro con este modelo.
3. **La confirmación de YP sigue siendo obligatoria** (ya estaba en el
   diseño): con 4/5 de aciertos, ningún resultado generado se comunica
   sin que ella lo confirme primero — el margen de error real (~20%)
   confirma que este paso no es opcional.

## Próximo paso

Construir la interfaz de escaneo (Capa 1: tablero + selección por señal
ya validada) — la Capa 2 (generación) ya está validada como técnicamente
viable y local, lista para integrarse.
