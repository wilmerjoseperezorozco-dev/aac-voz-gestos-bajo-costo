# Entorno físico de captura — protocolo casero para un "estudio" reproducible

Objetivo: que cada sesión con YP se vea y se comporte como una estación de
captura controlada — sin comprar nada caro — y que eso se refleje en menos
ruido en los datos (ya vimos en las sesiones reales que el volumen
inconsistente y el encuadre variable fueron causa directa de errores).

## 1. Micrófono — resolver el problema que ya tuvimos

En la primera sesión, 20 de 80 grabaciones se descartaron por volumen muy
bajo (`rms < 0.003`) — casi siempre por distancia inconsistente al
micrófono. Esto se arregla con **posición fija**, no con mejor hardware.

### Soporte de micrófono casero (elige uno)

| Opción | Materiales | Costo | Cómo |
|---|---|---|---|
| **Manos libres con mic (recomendado)** | Audífonos de celular con micrófono en el cable | $0 (ya lo tienen) | El mic queda a la misma distancia de la boca SIEMPRE, sin importar cómo se mueva la cabeza. Es la solución más simple y más robusta. |
| Brazo de "boom" casero | Palo de escoba o regla larga + cinta + pinza de ropa para sujetar el mic/celular | $0-5.000 | Fijar el palo a la silla con cinta, ajustar altura a la boca de YP, marcar el ángulo con cinta en el piso. |
| Soporte de manos libres | Clip de celular de los de "selfie stick" barato + servilletero o base de CD como peso | $10.000-15.000 | Si usan el micrófono del celular en vez de audífonos. |

### Tratamiento acústico (reduce eco y ruido de fondo)

- Graben en un cuarto con **clóset con ropa** — la ropa absorbe el eco
  mejor que casi cualquier otra cosa casera. Abran las puertas del clóset
  hacia el área de grabación.
- Si no hay clóset: cobijas o cojines colgados en la pared detrás de YP
  (no tienen que ser bonitos, solo estar ahí durante la grabación).
- **Filtro anti-pop casero:** un par de medias veladas estiradas sobre un
  aro de bordado o un gancho de ropa doblado en círculo, puesto entre la
  boca y el micrófono (~10 cm). Reduce los golpes de aire en palabras como
  "baño" o "ayuda" que ensucian la grabación.
- Apaguen ventilador/aire acondicionado/TV durante la sesión — es la
  mejora de "cero costo, mayor impacto" de toda esta lista.

### Consistencia entre sesiones

- Mismo cuarto, mismo horario si es posible (el ruido ambiente cambia
  entre el día y la noche).
- Anota en `registros/sesiones.csv` (columna observaciones) quién más
  estaba presente y cualquier ruido inusual — ya la columna existe, solo
  falta usarla.

## 2. Fondo de cámara — importante para que MediaPipe detecte bien

Un fondo desordenado o con movimiento (gente pasando, ventilador girando)
puede confundir la detección de postura. Un fondo limpio también hace que
las fotos/videos se vean profesionales en la sustentación.

### Fondo casero

- **Sábana o tela lisa** de un solo color (gris, azul oscuro, verde no
  fluorescente) colgada con cinta o chinches detrás de YP. Costo: $0 si ya
  tienen una sábana de repuesto.
- Evitar blanco puro (se "quema" con la luz) y evitar patrones (rayas,
  cuadros) — confunden tanto al ojo humano como al algoritmo de pose.
- Retirar espejos y superficies reflectivas del cuadro.
- Que nadie más camine detrás de YP mientras se captura — la detección de
  MediaPipe asume una sola persona.

### Luz (más importante que la cámara en sí)

- **Luz de frente, nunca a contraluz.** Si hay ventana, YP debe mirar
  HACIA la ventana, no darle la espalda (si le da la espalda, la cámara
  solo ve una silueta oscura).
- Softbox casero: cuelguen una sábana blanca o papel de mantequilla sobre
  la ventana para difuminar la luz del sol — luz pareja sin sombras duras.
- Relleno de sombras: una lámpara de escritorio apuntando a una pared
  blanca o a una hoja de papel aluminio arrugado y estirado sobre un
  cartón — rebota luz suave hacia la cara sin encandilar. Costo: $0,
  reusan lo que ya tienen en casa.

### Encuadre reproducible

- Marquen con cinta en el piso dónde va la silla de YP y dónde va el
  trípode/laptop — así todas las sesiones futuras usan el mismo encuadre,
  lo cual importa para comparar resultados entre sesiones.
- Altura de cámara: a la altura de los ojos de YP sentada, no desde abajo
  ni desde arriba (esas distorsionan la pose detectada).

## 3. Captura multi-ángulo — con lo que ya tienen (celulares)

El sistema solo necesita **un** ángulo frontal para que MediaPipe funcione
(esa es la cámara "oficial" que alimenta al modelo). Pero para la
sustentación y para documentar mejor el gesto real de YP, un segundo
ángulo agrega mucho valor científico y visual, sin tocar el código:

### Rig de dos cámaras casero

| Cámara | Propósito | Cómo montarla |
|---|---|---|
| **Cámara frontal (la que usa el sistema)** | Alimenta MediaPipe, la official | Laptop fija en el trípode/soporte marcado con cinta |
| **Cámara lateral (documentación, ~45°)** | Video de respaldo para mostrar el gesto desde otro ángulo en la sustentación; también sirve para verificar visualmente qué hizo YP cuando el sistema falla | Celular en modo grabación de video, apoyado en una pila de libros o una caja a 45° de YP |

**Trípode casero para el celular lateral:**
- Un vaso o taza boca abajo + cinta para fijar el celular en un ángulo, o
- Una caja de cartón con una ranura cortada del ancho del celular.
- Costo: $0.

**Sincronización sin hardware especial:** usen la misma cuenta regresiva
"3-2-1" que ya dicen los scripts (`grabar.py`, `gestos_grabar.py`) en voz
alta — ambas cámaras capturan el mismo instante porque las dos empiezan a
grabar cuando alguien dice "3, 2, 1, ¡ahora!". Es el método de
sincronización que usa cualquier set de filmación casero.

### Para más adelante (cuando haya presupuesto, ver `propuesta-expansion.md`)

Dos ángulos 2D sincronizados son, de hecho, el principio de la
**estereovisión** — con calibración se puede aproximar profundidad sin
comprar un Kinect. Es un paso intermedio razonable antes de invertir en
hardware 3D dedicado.

## 4. Checklist de la "ficha de sesión" (antes de grabar)

- [ ] Micrófono en posición fija (audífonos puestos o boom ajustado)
- [ ] Ventilador/TV apagados
- [ ] Fondo liso detrás de YP, sin gente ni movimiento
- [ ] Luz de frente, no a contraluz
- [ ] Silla y cámara en las marcas de cinta del piso
- [ ] (Opcional) celular lateral grabando, listo para el "3-2-1"
- [ ] Anotar en `registros/sesiones.csv`: hora, quién está presente, cómo
      se ve el ánimo de YP ese día

## 5. Por qué esto importa para la sustentación

Un jurado no solo evalúa el modelo — evalúa el **rigor del método**.
Mostrar fotos del "montaje" (fondo liso, mic fijo, marcas en el piso,
ficha de sesión) comunica que esto no fue una grabación improvisada, sino
un protocolo repetible — exactamente lo que se espera de una validación
científica, aunque el presupuesto haya sido cero.
