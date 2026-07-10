# Arquitectura de dos capas — vocabulario núcleo + expansión generativa

Propuesta de arquitectura (2026-07-09), corregida en el diseño de la Capa 1
y respaldada con literatura real antes de construir nada.

## Por qué se corrige el diseño original

La propuesta original planteaba entrenar reconocimiento de voz/gesto para
las 200-400 palabras del vocabulario núcleo, igual que hicimos con las 11
palabras actuales (10 grabaciones reales por palabra). **Eso es
clínicamente inviable**: 400 palabras × 10 grabaciones = 4.000
grabaciones, y ya vimos hoy que 150 muestras generan fatiga y presión de
tiempo en las sesiones. Además, cuantas más palabras se intenten
reconocer por voz, más difícil es discriminarlas (ver
`brechas-cientificas-y-escalamiento.md`).

**La solución estándar en AAC (y la que se usa aquí) es distinta:** el
vocabulario núcleo no se *reconoce por voz*, se *selecciona de un
tablero* — YP no tiene que decir "dolor", solo tiene que señalar/mirar el
ícono de "dolor" entre 200-400 disponibles, usando el **escaneo** (el
tablero resalta opciones una por una o por categorías) y **una sola señal
ya validada** para confirmar — el mismo principio que usaba Stephen
Hawking con un solo músculo de la mejilla, ya discutido en
`comunicacion-explicativa.md`.

Esto significa que **la Capa 1 reutiliza el 100% de lo ya validado**: la
señal "sí" (92-100% de confianza con consenso unánime) o el gesto de
mayor amplitud se convierten en el botón de "confirmar selección" del
escaneo — cero entrenamiento nuevo de voz/gesto necesario para escalar de
11 a 400 símbolos.

## Capa 1 — Selección motora reducida (corregida)

- **Tablero de vocabulario núcleo**: 200-400 íconos, usando
  [ARASAAC](https://arasaac.org/) — el banco de pictogramas de AAC en
  español más usado y de licencia abierta (Creative Commons), gratuito,
  diseñado exactamente para este propósito.
- **Escaneo**: el sistema resalta íconos (o categorías → íconos, escaneo
  de dos niveles, más rápido para tableros grandes) en secuencia
  automática.
- **Confirmación**: la señal de voz/gesto de mayor confianza ya validada
  con YP (recomendado: la que dé consenso unánime más consistente — hoy
  "sí" con 100% en la última sesión) detiene el escaneo en el ítem
  deseado.
- **Salida de la Capa 1**: 2-5 símbolos seleccionados en orden — la
  "semilla semántica".

## Capa 2 — Expansión generativa (respaldo científico real)

Existe precedente académico directo: **KWickChat** (Shen et al., 2022) es
un sistema publicado que toma una "bolsa de palabras clave" y un modelo
de lenguaje genera una oración conversacional completa, contextualizada
con la conversación y con información del usuario — exactamente el
concepto propuesto. Trabajo más reciente (2025) adapta LLMs
específicamente para AAC basada en caracteres/abreviaciones, confirmando
que es un área de investigación activa, no una idea aislada.

### Requisito de diseño no negociable: el LLM debe correr LOCAL

Las selecciones de YP revelan intención comunicativa personal, a veces de
salud ("dolor", "cansada") — es dato sensible por la misma razón que
protegemos sus audios (Ley 1581/2012). **Nunca debe enviarse a una API en
la nube.** Se valida en la literatura 2026 que un Raspberry Pi 5 (8GB)
corre modelos locales de 1-3B parámetros a velocidad interactiva vía
`llama.cpp`, sin dependencia de nube — en esta PC (con más recursos que
una Pi) el rendimiento será aún mejor.

**Modelos candidatos** (multilingüe, capaces en español, livianos):
Qwen2.5 (1.5B), Phi-3 Mini, Gemma 2B — cualquiera corre vía `llama.cpp`
sin GPU.

### Flujo completo

1. YP selecciona 2-5 símbolos vía escaneo (Capa 1).
2. El LLM local recibe la semilla semántica + contexto (hora del día,
   quién está presente, historial reciente — reutiliza el esquema de
   contexto ya diseñado en `comunicacion-explicativa.md` §3).
3. Genera una oración fluida y gramaticalmente correcta.
4. Se pronuncia por TTS (ya implementado).
5. **YP confirma o corrige** (mismo patrón ya validado en `predecir.py`:
   "¿fue correcta?") — necesario porque un LLM puede alucinar una
   intención que no es la suya; nunca se envía la oración generada como
   definitiva sin confirmación.

## Plan de implementación por fases (no saltar directo a 400 símbolos)

Dada la lección de hoy sobre escalabilidad, se recomienda empezar
pequeño y validar antes de crecer:

| Fase | Alcance | Objetivo |
|---|---|---|
| 1 (MVP) | 20-30 símbolos núcleo, escaneo + confirmación con "sí" ya validado, LLM local (Qwen2.5-1.5B) | Validar que el escaneo funciona con YP y que las oraciones generadas tienen sentido |
| 2 | 100-200 símbolos, ajustar velocidad de escaneo según fatiga observada | Escalar el tablero manteniendo usabilidad |
| 3 | 200-400 símbolos (vocabulario núcleo completo) | Cobertura del ~80% del habla cotidiana |

## Decisiones pendientes (requieren definición antes de programar)

1. **Interfaz del tablero**: ¿pantalla de la PC (rápido de construir,
   funciona ya) o esperar al kit Raspberry Pi + pantalla táctil
   (`propuesta-expansion.md`)? Se puede prototipar en la PC y migrar
   después — el código no cambia (numpy/scipy puro sigue funcionando en
   la Pi).
2. **Modelo LLM específico**: Qwen2.5-1.5B es la recomendación inicial
   (buen soporte de español, liviano) — confirmar antes de descargar
   (~1-3 GB).
3. **Símbolos de la Fase 1**: ¿cuáles 20-30 conceptos priorizar? Sugerido:
   partir del vocabulario ya validado (11 palabras) + ampliar con las
   categorías de `comunicacion-explicativa.md` (motivo/causa/deseo:
   partes del cuerpo, personas, lugares, acciones básicas).

## Referencias

- Vocabulario núcleo cubre ~80% del habla cotidiana, 200-400 palabras
  (Beukelman et al.): [AssistiveWare — Teaching with core words](https://www.assistiveware.com/blog/teaching-core-words-building-blocks-communication-and-curriculum)
- KWickChat — generación de oraciones AAC por bolsa de palabras clave con
  contexto conversacional: [ResearchGate](https://www.researchgate.net/publication/359401189_KWickChat_A_Multi-Turn_Dialogue_System_for_AAC_Using_Context-Aware_Sentence_Generation_by_Bag-of-Keywords)
- Adaptación de LLMs para AAC basada en caracteres (2025): [arXiv 2501.10582](https://arxiv.org/pdf/2501.10582)
- ARASAAC — banco de pictogramas AAC en español, licencia abierta: [arasaac.org](https://arasaac.org/)
- Modelos locales pequeños en Raspberry Pi 5, benchmarks reales 2026: [TinyWeights.dev](https://tinyweights.dev/posts/run-llms-raspberry-pi-5/)
