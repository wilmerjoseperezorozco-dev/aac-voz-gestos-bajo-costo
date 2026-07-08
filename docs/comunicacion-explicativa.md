# De palabras a explicaciones — comunicación de motivo, causa y razón

Cómo pasar del vocabulario de 8 palabras a que YP pueda **explicar qué le
pasó, por qué, y qué quiere** — inspirado en la arquitectura real del
sistema de Stephen Hawking.

## 1. La lección de Hawking (ACAT)

| Componente de su silla | Equivalente en nuestro sistema |
|---|---|
| Sensor infrarrojo de mejilla (1 señal binaria) | Las 7 palabras fuertes de YP = 7 señales confiables (+ futuro gesto por cámara/Arduino) |
| Teclado por barrido (scanning) | Tablero de imágenes que se iluminan por turnos; YP dice «sí» cuando pasa la opción que quiere |
| Predictor SwiftKey entrenado con SUS libros | Dataset personal de diálogos confirmados (§3) |
| Sintetizador DECtalk (su voz característica) | Voz Sabina es-MX (ya funcionando) |
| Software Intel ACAT, open source | [github.com/intel/acat](https://github.com/intel/acat) — referencia citable y adaptable |

Hawking comunicaba ideas complejas a 1-2 palabras/minuto porque el sistema
**predecía a partir de su corpus personal**. La velocidad no venía de la
señal, venía de la predicción.

## 2. Tres niveles de comunicación explicativa

### Nivel 1 — Árbol de diálogo guiado (implementable ya, sin hardware nuevo)

El sistema (o el acompañante) recorre un árbol de preguntas sí/no + tableros:

```
"¿Te sientes mal?" ──sí──> "¿Es dolor?" ──sí──> [tablero: cabeza|estómago|pecho|otro]
        │                        │
        no                       no──> [tablero: triste|miedo|cansada|hambre]
        │
        └──> "¿Necesitas algo?" ──> [tablero: agua|comer|baño|mamá|salir]
                                          │
                              "¿Por qué?" (causa) ──> [tablero contextual]
```

Estructura fija de cada ciclo: **MOTIVO** (¿qué pasa?) → **CAUSA** (¿por
qué?) → **DESEO** (¿qué hacemos?). Al final el sintetizador pronuncia la
frase completa reconstruida: *"Me duele la cabeza porque no dormí, quiero
agua"* — YP escucha su idea dicha en voz alta y confirma con sí/no.

### Nivel 2 — Frases telegráficas por plantilla

Tablero con ranuras: `[YO SIENTO] [___] [PORQUE] [___] [QUIERO] [___]`.
Cada ranura se llena por barrido o por palabra hablada. Es la función
central de los dispositivos comerciales de >US$6.000, reproducible en
nuestra Raspberry Pi con pantalla táctil.

### Nivel 3 — Predicción personalizada (el "SwiftKey de YP")

Con el dataset del §3, el sistema aprende las asociaciones de YP:
- dolor + noche → sugiere "cabeza" primero (si ese es su patrón)
- agua + después de comer → sugiere "pastilla"
Modelo inicial: conteo de n-gramas sobre tripletas (simple, explicable,
sin nube). Evolución: modelo de lenguaje pequeño afinado localmente.

## 3. Esquema del dataset de respuestas personales

Cada diálogo confirmado se registra en `registros/dialogos.csv`:

| Campo | Ejemplo |
|---|---|
| fecha_hora | 2026-07-10T20:15:00 |
| contexto | noche, despues_de_comer, en_cama |
| pregunta | ¿por qué lloras? |
| senales | dolor, si(cabeza), no(pastilla) |
| significado_confirmado | le duele la cabeza, no quiere pastilla, quiere compañía |
| confirmado_por | mamá |

Reglas de recolección:
1. Solo se registra lo que YP **confirmó** (sí final al escuchar la frase).
2. El contexto se anota con etiquetas fijas (momento del día, lugar,
   actividad previa) — son los rasgos que alimentan la predicción.
3. Meta inicial: 50 diálogos confirmados en 4 semanas de uso doméstico.
4. Este corpus es tan sensible como los audios: alias YP, nunca publicarlo
   crudo; en el paper solo estadísticas agregadas.

## 4. Por qué esto fortalece la propuesta universitaria

- Muestra un **camino de escalamiento claro**: palabra → frase → explicación,
  cada nivel validable con el mismo protocolo (¿la familia entendió lo que
  YP quiso decir? sí/no medible).
- Conecta con un precedente universalmente conocido (Hawking) y con
  software libre vigente (ACAT) — credibilidad inmediata ante el jurado.
- El dataset de diálogos es en sí mismo una **contribución publicable**:
  corpus de comunicación aumentativa en español de un caso real, algo
  escaso en la literatura.

## 5. Orden de implementación sugerido

1. [ ] Tablero sí/no + árbol de 3 preguntas en la PC (motivo→causa→deseo),
       usando el clasificador de voz actual para capturar sí/no/palabras.
2. [ ] Registro automático en `registros/dialogos.csv` al confirmar.
3. [ ] Frase sintetizada completa al final de cada ciclo.
4. [ ] Tras 50 diálogos: primer predictor n-gramas (sugerir la causa más
       probable dado contexto+motivo).
5. [ ] Migrar el tablero a la Raspberry Pi con pantalla táctil (Fase RPi).
