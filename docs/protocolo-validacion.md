# Protocolo de validación documentada — MVP predicción de voz

**Participante:** YP (mujer, 35 años, desconexión motora del habla; reconoce
sonidos e imágenes). **Objetivo:** demostrar de forma medible y reproducible
que un sistema personalizado de bajo costo puede traducir sus emisiones
vocales a palabras funcionales.

## 1. Consentimiento informado (obligatorio antes de grabar)

Documento físico firmado por YP (o su representante legal si aplica) que
incluya, como mínimo:

- Propósito del estudio y de las grabaciones.
- Que los audios son datos biométricos que se almacenan solo en esta PC.
- Que en publicaciones solo aparecerán alias (YP) y métricas agregadas.
- Derecho a retirarse en cualquier momento y a que se borren sus datos.
- Autorización específica (sí/no) para reproducir fragmentos de audio en la
  presentación universitaria.

## 2. Diseño del estudio

| Elemento | Definición |
|---|---|
| Vocabulario | 8 palabras funcionales (config.json): agua, sí, no, dolor, baño, ayuda, comer, mamá |
| Muestras | 10 por palabra (80 total), en ≥3 sesiones de días distintos |
| Sesión | ≤15 min, ambiente silencioso, mic a ~15 cm, misma hora del día si es posible |
| Estímulo | Tarjeta con imagen (sin modelar la palabra verbalmente) |
| Métrica offline | Exactitud LOOCV global y por palabra + matriz de confusión (automático en `entrenar.py`) |
| Métrica en vivo | % de aciertos confirmados en `registros/predicciones.csv` (el sistema pregunta tras cada intento) |
| Criterio de éxito MVP | ≥70% exactitud en vivo sobre ≥30 intentos, y latencia <3 s |
| Línea base | % de comprensión por oyentes no familiarizados escuchando los mismos audios SIN el sistema (esto cuantifica la mejora que aporta el MVP) |

## 3. Procedimiento por sesión

1. Verificar consentimiento vigente y disposición de YP ese día.
2. `python src/grabar.py` — grabar en bloques de 2-3 palabras con descansos.
3. Anotar observaciones (fatiga, ánimo, ruido) en `registros/sesiones.csv`.
4. Al completar el dataset: `python src/entrenar.py` → archivar el reporte
   JSON y la matriz de confusión PNG de `reportes/` (evidencia con fecha).
5. Sesiones de validación en vivo: `python src/predecir.py`, mínimo 30
   intentos repartidos en 2+ días, confirmando s/n cada predicción.

## 4. Análisis de la línea base (mejora demostrable)

Para afirmar "el sistema ayuda a entenderla mejor" se necesita comparación:

1. Seleccionar 2 audios por palabra (16 audios) al azar.
2. Pedir a 3-5 personas que NO conozcan a YP que escriban qué palabra oyen.
3. Comparar: % de comprensión humana directa vs. % de acierto del sistema.
4. Reportar ambas cifras con intervalo de confianza (n pequeño: reportar
   conteos crudos, sin exagerar significancia).

## 5. Qué mostrar en la universidad

1. **El problema** (30 s de contexto sobre habla disártrica y por qué los
   reconocedores comerciales fallan).
2. **Demo en vivo** con YP presente o con audios grabados + `predecir.py`.
   Plan B sin micrófono: `python src/demo_sintetico.py`.
3. **Evidencia**: matriz de confusión, curva de aciertos por sesión,
   comparación contra línea base humana.
4. **Costo total del MVP**: PC existente + audífonos de celular ≈ $0 COP
   adicionales (argumento de accesibilidad).

## 6. Registro de limitaciones (honestidad metodológica)

Documentar explícitamente: n=1 participante, vocabulario cerrado de 8
palabras, sensibilidad al ruido ambiente, y que la exactitud sintética
(91.7%) no es evidencia clínica — solo verificación técnica del pipeline.
