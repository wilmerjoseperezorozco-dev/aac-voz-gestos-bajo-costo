# Visión: laboratorio multimodal para poblaciones vulnerables con patologías motoras y fonoaudiológicas

Este documento describe hacia dónde puede escalar el proyecto más allá
del prototipo actual (un sistema personalizado en una PC casera):
un espacio físico dedicado de investigación en comunicación
aumentativa, pensado específicamente para comunidades con alta
vulnerabilidad socioeconómica y territorial en el Caribe colombiano,
donde el acceso a fonoaudiología y tecnología asistiva especializada
es más limitado que en el resto de la ciudad.

**Estado de esta sección: visión y hoja de ruta, no implementado.**
Todo lo descrito aquí es un objetivo a mediano plazo, no una
característica actual del software (que sigue siendo TRL 5-6, ver
`fase-madurez-software.md`).

## Por qué un espacio dedicado, y por qué en estas comunidades

Las barreras de acceso a comunicación aumentativa y a servicios de
fonoaudiología no se distribuyen igual dentro de una misma ciudad: la
vulnerabilidad territorial y socioeconómica se suma a la vulnerabilidad
por discapacidad, no la reemplaza. Un espacio de investigación
dedicado, ubicado donde esa necesidad es mayor —no donde es más
cómodo para el investigador— es en sí mismo parte del argumento de
impacto social del proyecto, no un detalle logístico.

## Componentes del laboratorio (visión, por desarrollar)

1. **Estación de trabajo central** — un único punto de cómputo que
   orquesta la captura de todos los canales y sirve de panel de
   control durante cada sesión.
2. **Nodos de borde** — unidades de cómputo dedicadas de bajo costo
   (línea Raspberry Pi ya usada en el proyecto) por canal de captura,
   evitando que un solo equipo cargue con todo.
3. **Captura visual y de profundidad** — más allá de la webcam
   actual, cámaras de profundidad dedicadas para registrar postura y
   movimiento con mayor precisión.
4. **Captura RGB de alta resolución** — registro visual de calidad
   consistente sesión a sesión.
5. **Sistema de proyección de pantallas** — el tablero de selección
   sobre hardware dedicado, más una pantalla de apoyo para el
   acompañante o investigador.
6. **Audio profesional de fonoaudiología** — micrófono articulado de
   posición fija y reproducible, mejora directa sobre el micrófono
   casero usado hasta ahora.
7. **Sensores musculares (EMG)** — canal nuevo, no implementado
   todavía en el software, para capturar activación muscular
   orofacial/de miembros como complemento a la visión por computadora.
8. **Red y sincronización** — infraestructura para que todos los
   canales queden sincronizados con precisión de tiempo.
9. **Soportes y estructuras físicas** — ajustables por participante,
   relevante para una serie de casos con perfiles motores distintos.
10. **Mobiliario clínico y ergonomía** — posicionamiento adecuado para
    personas con compromiso motor, validado por un profesional de
    salud, no mobiliario genérico.
11. **Aislamiento acústico** — condición ambiental controlada,
    necesaria para la calidad de la captura de voz.

## Seguridad del espacio físico

En comunidades con alta vulnerabilidad territorial, la seguridad del
espacio de investigación es parte razonable de la planeación de
cualquier laboratorio físico dedicado — no distinta de la que
consideraría cualquier institución al abrir un espacio en una zona
así. Se contempla una alianza institucional con las autoridades de
seguridad locales (Policía Nacional, a través del CAI más cercano)
para contar con un canal directo ante emergencias o intrusiones —
una medida de protección del espacio y de quienes lo usan, no una
función del software ni un mecanismo de vigilancia sobre los
participantes.

## Relación con el software actual

El laboratorio no reemplaza el enfoque de bajo costo del proyecto —
lo complementa. El sistema personalizado que corre en una PC casera
sigue siendo la vía de acceso más económica y replicable; el
laboratorio dedicado es la infraestructura necesaria para ampliar la
serie de casos con el rigor y la reproducibilidad que exige la
siguiente etapa de investigación (ver
`ruta-expansion-condiciones-neurologicas.md`).

## Estado de las piezas nuevas

- Los puntos 1-6, 8-11 son extensiones de hardware/infraestructura
  sobre patrones ya usados en el proyecto (Raspberry Pi, cámaras,
  audio dedicado) — no requieren rediseñar el software base.
- El punto 7 (sensores EMG) sí requiere desarrollo de software nuevo
  desde cero: no existe todavía ningún pipeline de captura,
  extracción de características, ni validación para esta señal en el
  proyecto.
