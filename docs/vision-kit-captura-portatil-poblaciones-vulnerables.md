# Visión: kit de captura portátil mejorado para poblaciones vulnerables con patologías motoras y fonoaudiológicas

Este documento describe hacia dónde puede escalar la **calidad de
captura de datos** del proyecto sin abandonar su principio central:
el software funciona en cualquier computador portátil, no requiere
hardware especial, y por lo tanto es accesible para personas y
comunidades de bajos recursos. Un espacio dedicado con obra física
(paneles fijos, aislamiento acústico estructural, aire acondicionado
instalado) se descartó deliberadamente — no porque no aportara valor
técnico, sino porque introduce requisitos legales y de infraestructura
(permisos de uso de suelo, adecuaciones de accesibilidad) que
contradicen el propósito del proyecto y no son razonables para una
fundación comunitaria. La mejora de la captura de datos se resuelve
con **equipo portátil, no con obra**.

**Estado de esta sección: visión y hoja de ruta, no implementado.**
Todo lo descrito aquí es un objetivo a mediano plazo, no una
característica actual del software (que sigue siendo TRL 5-6, ver
`fase-madurez-software.md`).

## Principio rector

El software sigue funcionando igual en cualquier portátil sin ningún
accesorio adicional — eso no cambia y sigue siendo el punto de entrada
principal para cualquier persona o familia. El equipo descrito aquí es
un **kit opcional de mejora de captura**, transportable, que se instala
y se retira de cualquier habitación sin modificarla — no requiere obra,
no requiere permiso de uso de suelo, y no altera el espacio de la
fundación aliada.

## Componentes del kit portátil (visión, por desarrollar)

1. **Nodo de cómputo dedicado (opcional)** — una unidad Raspberry Pi ya
   contemplada en el roadmap del proyecto, para correr el sistema sin
   depender del portátil personal del investigador. Sigue siendo
   equipo de mesa, no instalación.
2. **Cámara de profundidad portátil sobre trípode** — mejora sobre la
   webcam actual para registrar postura y movimiento con más
   precisión, sin ninguna fijación a pared o techo.
3. **Cámara RGB adicional sobre trípode** — registro visual de calidad
   consistente sesión a sesión, mismo criterio: portátil, se guarda al
   terminar.
4. **Micrófono articulado de mesa** — mejora directa sobre el
   micrófono casero actual, con montaje de escritorio (no de pared),
   fácil de transportar entre sesiones.
5. **Panel acústico portátil (biombo o mampara autoportante)** — reduce
   reverberación sin necesitar tratar las paredes del espacio; se
   despliega para la sesión y se guarda después.
6. **Sensores musculares (EMG) — canal nuevo a futuro**: no
   implementado todavía en el software; requeriría desarrollo de
   pipeline de captura y validación desde cero, igual que se hizo para
   voz y gestos. Se evalúa como línea de investigación aparte, no como
   parte inmediata del kit.

## Lo que se descartó, y por qué

- ❌ Cuarto dedicado con paneles acústicos fijos, aire acondicionado
  instalado y cableado estructurado — implica adecuación física
  permanente del espacio de la fundación aliada, con los riesgos
  normativos ya identificados (uso de suelo, accesibilidad NTC
  4595/4960/5017) para un inmueble que no fue construido con ese fin.
- ❌ Mobiliario clínico fijo — se mantiene el mobiliario y el espacio de
  la fundación tal como están; cualquier ajuste ergonómico se resuelve
  con accesorios portátiles (cojines de posicionamiento, soportes
  ajustables de mesa), no con reforma.
- ❌ Sistema de proyección de pantallas dedicado — el tablero sigue
  funcionando sobre el portátil o una pantalla táctil portátil ya
  contemplada en el roadmap de hardware, sin instalación fija.

## Relación con el software actual

El kit no reemplaza el enfoque de bajo costo del proyecto — lo
complementa opcionalmente. El sistema personalizado que corre en
cualquier portátil sigue siendo la vía de acceso principal, económica
y replicable; el kit portátil es una mejora de calidad de datos para
la serie de casos ampliada, sin crear una barrera de infraestructura
para ninguna comunidad o fundación aliada (ver
`ruta-expansion-condiciones-neurologicas.md`).
