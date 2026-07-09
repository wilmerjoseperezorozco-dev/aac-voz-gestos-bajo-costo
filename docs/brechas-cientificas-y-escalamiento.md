# Brechas científicas y hoja de ruta hacia escalamiento

Análisis de qué le falta al proyecto para sostenerse frente a revisión
científica seria y para funcionar fuera del entorno casero controlado
actual — con solución profesional propuesta para cada brecha. Todo lo
calculado en este documento usa datos **ya existentes** (sin grabar nada
nuevo con YP).

---

## 0. Rigor estadístico — resuelto hoy

Los reportes anteriores citaban porcentajes puntuales (80.6%, 92.3%, etc.)
sin intervalo de confianza — una debilidad real frente a un jurado o
revisor que sabe que n pequeño hace que un punto porcentual solo no
signifique nada. Se calcularon intervalos de confianza de Wilson (el
método correcto para proporciones con muestras pequeñas, a diferencia del
intervalo normal que falla cerca de 0% o 100%):

| Métrica | Punto | IC 95% (Wilson) | n |
|---|---|---|---|
| Voz — LOOCV global | 80.6% | 71.9%–87.1% | 103 |
| Gestos — LOOCV global | 80.0% | 62.7%–90.5% | 30 |
| En vivo, consenso unánime | 92.3% | 66.7%–98.6% | 13 |
| En vivo, mayoría (2/3) | 50.0% | 34.1%–65.9% | 34 |
| En vivo, mínimo (1/3) | 13.0% | 4.5%–32.1% | 23 |
| Voz — tarea única | 80.6% | 71.9%–87.1% | 103 |
| Voz — doble tarea | 36.7% | 21.9%–54.5% | 30 |
| Gestos — tarea única | 80.0% | 62.7%–90.5% | 30 |
| Gestos — doble tarea | 30.0% | 16.7%–47.9% | 30 |

**Hallazgo estadísticamente sólido:** los intervalos de tarea única y
doble tarea **no se traslapan** en ningún canal (voz: 71.9-87.1% vs.
21.9-54.5%; gestos: 62.7-90.5% vs. 16.7-47.9%). Esto significa que la
interferencia cognitivo-motora **no es ruido de muestra pequeña** — es un
efecto real y grande. Acción: incorporar esta tabla al artículo científico
(`articulo-cientifico.md` §3.3) en lugar de los porcentajes sueltos.

**Alerta honesta:** varias palabras (agua, baño, dolor, no, sí) tienen
intervalos de confianza anchos (>30 puntos porcentuales) — el dato real es
"no sabemos con precisión si es 73% o 90%", no que el sistema sea débil
ahí. Esto se resuelve con más muestras por palabra (brecha #2).

## 1. Explicación de los errores: se probó una hipótesis y se rechazó

Se probó si la **duración de la emisión** explica por qué ciertas palabras
fallan más (hipótesis razonable: emisiones más cortas dan menos tramas
para que DTW discrimine). Resultado con datos reales de las grabaciones:

| Palabra | Duración media (s) | Exactitud |
|---|---|---|
| ayuda | 0.65 | 91.7% |
| agua | 0.73 | 76.9% |
| dolor | 0.79 | 83.3% |
| comer | 0.92 | 80.0% |
| sí | 0.92 | 72.7% |
| baño | 0.99 | 72.7% |
| mamá | 1.09 | 88.2% |
| no | 1.31 | 75.0% |

Correlación de Pearson: **r = −0.386** (débil e inversa — contradice la
hipótesis; con n=8 palabras no es concluyente en ningún sentido).
**Conclusión honesta: la duración NO explica los errores.** La causa más
probable es similitud acústica intrínseca en el espacio MFCC entre pares
específicos (sí/no, no/baño, mamá/comer — ver matriz de confusión), no un
factor único y simple. Esto se deja como brecha #8 para análisis futuro
con la métrica correcta (distancia DTW promedio intra-clase vs
inter-clase), no con duración como proxy.

---

## Brechas para validar en otros entornos, con otras personas y en demostraciones

### Brecha 2 — Generalización entre entornos (validez externa)

**El problema:** todo el entrenamiento ocurrió en el mismo cuarto de la
casa de YP. No sabemos si el modelo funciona igual en la universidad
(auditorio, ruido distinto, acústica distinta) o en el nuevo entorno del
baño con mic de solapa.

**Solución profesional — protocolo de robustez ambiental:**
1. Etiquetar cada sesión con metadato de entorno (ya existe la columna
   "observaciones" en `registros/sesiones.csv` — usarla sistemáticamente:
   nombre del entorno, tipo de mic, nivel de ruido subjetivo).
2. Diseño experimental A/B: evaluar el modelo actual (entrenado en el
   entorno original) **sin reentrenar** contra grabaciones nuevas del
   entorno del baño — mide la caída de exactitud por cambio de entorno,
   exactamente como se hizo con la interferencia de doble tarea.
3. Si la caída es significativa, la solución no es "más modelo" sino
   **normalización de canal**: restar el espectro promedio de ruido de
   fondo de cada entorno antes de extraer MFCC (técnica estándar,
   ya viable con las herramientas actuales, `scipy`).

### Brecha 3 — Generalización entre personas (n=1 → serie de casos)

**El problema:** el modelo es 100% personalizado a YP. No hay evidencia de
que el método (no el modelo específico) funcione igual de bien con otra
persona con un perfil motor distinto.

**Solución profesional — protocolo de validación por participante:**
1. Cada voluntario nuevo recibe su propio modelo, entrenado y validado
   con el mismo protocolo LOOCV — nunca un modelo compartido.
2. Se construye una **tabla comparativa entre participantes** (exactitud
   LOOCV, exactitud en vivo, palabras problemáticas) — eso es lo que
   convierte un estudio de caso en una serie de casos con valor
   estadístico real.
3. Se documenta la **variabilidad entre personas** como resultado en sí
   mismo: ¿el método funciona igual de bien para todos, o hay perfiles
   motores donde falla más? Esa pregunta es más publicable que "funcionó
   con una persona".

### Brecha 4 — Estabilidad temporal (¿el modelo envejece?)

**El problema:** no hay evidencia de que la exactitud de YP se mantenga
en 4 semanas. La voz y el gesto de una persona pueden cambiar por fatiga
acumulada, aprendizaje motor, o progresión/mejora de su condición.

**Solución profesional — validación test-retest:**
1. Sesión de validación en vivo corta (10-15 intentos) cada 2 semanas,
   SIN reentrenar el modelo — mide si la exactitud se mantiene, sube
   (aprendizaje) o baja (necesidad de reentrenar).
2. Si baja de forma consistente, define la **cadencia de reentrenamiento**
   necesaria en producción (cada mes, cada trimestre) — dato clave para
   cualquier despliegue real, y para el artículo.

### Brecha 5 — Protocolo de contingencia para demostraciones públicas

**El problema:** una sustentación universitaria es la peor condición
posible para un sistema afinado en casa — ruido de auditorio, nerviosismo
de YP (el estrés también es una forma de doble tarea cognitiva, por la
misma lógica del hallazgo de interferencia), fallas de hardware.

**Solución profesional — protocolo de demo con degradación elegante:**
1. **Ensayo general** en un espacio similar al de la sustentación (mismo
   tipo de acústica) al menos una vez antes del día real.
2. **Plan B ya construido:** `demo_sintetico.py` funciona sin micrófono
   ni cámara —úsalo si el hardware falla en vivo.
3. **Plan C:** video pregrabado de una sesión exitosa en casa, listo para
   reproducir si el entorno en vivo es demasiado ruidoso.
4. **Modo "solo palabras fuertes"**: para la demo, limitar el vocabulario
   mostrado a las palabras con mejor IC (ayuda, mamá, dolor) en vez de
   arriesgar las de intervalo ancho — es honesto (son las palabras mejor
   validadas) y maximiza la probabilidad de una demo exitosa.

### Brecha 6 — Confiabilidad entre evaluadores en validación en vivo

**El problema:** hoy, la misma persona que ve la predicción del sistema en
pantalla confirma si fue correcta — riesgo real de sesgo de confirmación
("ya vi que dijo agua, seguro que dijo agua").

**Solución profesional — evaluación ciega:**
1. Un segundo evaluador (que no ve la pantalla) anota independientemente
   qué palabra/gesto cree que hizo YP, **antes** de ver la predicción del
   sistema.
2. Se compara la predicción del sistema contra el juicio del evaluador
   ciego, no contra la opinión de quien ya vio la respuesta — esto es lo
   que un revisor científico esperaría ver, y es gratis (no requiere
   hardware, solo una segunda persona en la sesión).

### Brecha 7 — Escalabilidad computacional

**El problema:** DTW compara contra cada muestra de referencia; con 103
muestras de voz una predicción tardó ~1.5s. Al sumar más palabras y más
participantes (cada uno con su propio banco de referencias), el tiempo de
predicción crece.

**Benchmark real (medido hoy, sin YP, variando el tamaño del banco de
referencias del dataset ya existente):**

| n de referencias | Latencia medida/proyectada | Escenario |
|---|---|---|
| 20 | 0.85 s | — |
| 60 | 1.63 s | — |
| 103 (actual) | 3.28 s | Dataset de YP hoy |
| 200 | ~5.9 s (proyectado) | Vocabulario ampliado (~16 palabras) |
| 500 | ~14.6 s (proyectado) | 3-4 participantes con el vocabulario actual |
| 1000 | ~29.2 s (proyectado) | Serie de casos completa (5+ participantes) |

Ajuste lineal: latencia(n) ≈ 0.029×n + 0.12 segundos.

**Esta es una brecha real y urgente, no hipotética.** El propio protocolo
exige latencia <3s (`protocolo-validacion.md`); ya con el dataset actual de
YP (103 muestras) estamos en el límite (3.28s), y agregar más
participantes o vocabulario sin cambiar de estrategia rompe el criterio.

**Actualización 2026-07-09 — RESUELTO parcialmente, con evidencia real
(ver `reportes/hallazgo_optimizacion_dtw_20260709.md`):**

Se probaron las dos soluciones propuestas y se compararon con datos reales
(150 muestras, 11 palabras):

1. **Prototipos por clase (k-medoids)**: funciona, pero **siempre cuesta
   exactitud** — el mejor equilibrio (k=6/clase) da 66 referencias, corta
   el tiempo a la mitad, pero pierde 2 puntos porcentuales (74.7% vs
   76.7%). Queda implementado en `src/prototipos.py` y validado en
   `src/comparar_prototipos.py`, listo para usar si hace falta más
   adelante.
2. **Optimizar la función DTW (implementado, preferido):** el cuello de
   botella real no era *cuántas* referencias se comparan, sino que
   `distancia_dtw()` llamaba `np.linalg.norm()` celda por celda dentro del
   bucle. Se vectorizó el cálculo de distancias con `numpy` (broadcasting
   + `einsum`), verificado matemáticamente idéntico (diferencia 8.88×10⁻¹⁶)
   contra la versión anterior. Resultado real: **4.2x más rápido por
   comparación DTW**, LOOCV completa de 150 muestras bajó de ~9-10 min a
   **4 min**, con la **misma exactitud exacta** (76.7%) — a diferencia de
   los prototipos, esta ruta no sacrifica nada.

**Nuevo tope de escalabilidad** (con el DTW optimizado): sube de
~150-170 muestras a **~350-400 muestras** antes de volver a necesitar
intervención. Si el dataset sigue creciendo más allá de eso, combinar con
prototipos por clase (ya implementados y validados) es el siguiente paso.

**Poda por participante** (sigue vigente, sin cambios): cada modelo
personal se ejecuta de forma aislada — el sistema de YP nunca compara
contra las referencias de otro participante, así que el crecimiento real
es solo por vocabulario de una persona, no por número de personas en el
proyecto.

---

## Síntesis — hoja de ruta hacia "lo grande"

```
Ahora (sin YP, ya ejecutable):
  - Brecha 0-1: rigor estadístico + análisis de errores        [HECHO HOY]
  - Brecha 7: benchmark de latencia y proyección                [siguiente sesión de análisis]

Próxima sesión con YP:
  - Brecha 5: ensayo de demo en el nuevo entorno (baño + mic solapa)
  - Brecha 6: incorporar evaluador ciego en la próxima validación en vivo

Próximas 2-4 semanas:
  - Brecha 4: primera medición test-retest (sesión corta sin reentrenar)
  - Brecha 2: comparar exactitud entorno original vs. entorno nuevo

Próximos 1-3 meses (requiere aval de comité de ética + voluntarios):
  - Brecha 3: primer voluntario adicional, tabla comparativa entre casos
  - Consolidar todo en el artículo científico con evidencia multi-entorno
    y multi-persona, no solo el caso único de YP
```

Este es el argumento que convierte el proyecto de "funcionó con una
persona en su casa" a "es un método validado con rigor, que generaliza
entre entornos y entre personas, con límites conocidos y cuantificados" —
la diferencia entre un buen trabajo estudiantil y un paper defendible.
