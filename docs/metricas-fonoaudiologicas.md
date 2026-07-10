# Métricas fonoaudiológicas para el artículo científico

Cuatro métricas de esfuerzo comunicativo, respaldadas con literatura real
de investigación en AAC/HCI, aplicadas específicamente a la arquitectura
de dos capas (`arquitectura-vocabulario-nucleo-generativo.md`). No
modifican el flujo de prueba de la sesión del 10 de julio — son
documentación y preparación de análisis para el artículo científico.

---

## 1. KSPC-equivalente — reducción de esfuerzo motor

**Origen:** *Keystrokes Per Character* (MacKenzie, 2002) — métrica
fundacional en investigación de entrada de texto y AAC, mide cuántas
acciones motoras hace falta para producir cada carácter de salida.
Valores de referencia: ~10 para escaneo letra por letra con tecla única;
~0.5 para predicción de palabra avanzada.

**Adaptación a este sistema — "Selecciones por Palabra Comunicada" (SPC):**

```
SPC = (selecciones de escaneo realizadas) / (palabras en la oración final)
```

**Por qué es la métrica correcta aquí:** nuestro sistema no genera
caracteres, genera **oraciones completas** a partir de símbolos — el
paralelo correcto a KSPC no es por letra, es por palabra de salida. Ya
tenemos todos los datos para calcularla sin instrumentación nueva: cada
fila de `registros/predicciones_tablero.csv` tiene los símbolos
seleccionados (numerador) y la oración generada (cuyas palabras son el
denominador).

**Comparación de referencia (para el artículo):** un teclado de escaneo
letra por letra clásico necesitaría aproximadamente 1 selección por
carácter (KSPC≈1, sin corrección) para escribir, por ejemplo, "Me duele
la cabeza, quiero que venga mamá" (36 caracteres) — es decir, **~36
selecciones motoras**. Nuestro sistema logra la misma oración con **3
selecciones** (dolor + cabeza + mamá). Esa razón (36:3 ≈ 12x) es el
argumento cuantitativo central de reducción de esfuerzo motor para el
artículo — pendiente de confirmar con datos reales de uso, no solo el
ejemplo ilustrativo.

**Script ya preparado:** `src/metricas_fonoaudiologicas.py` calcula esto
automáticamente en cuanto haya datos reales de `predicciones_tablero.csv`
(aún no hay — se generan al usar el tablero, empezando con la sesión del
10 de julio en adelante).

## 2. Tasa de comunicación — palabras efectivas por minuto

**Estándar en investigación AAC:** palabras comunicadas exitosamente
(confirmadas por el usuario) dividido entre el tiempo total empleado.

```
Tasa (PPM) = palabras en oraciones CONFIRMADAS como correctas / minutos transcurridos
```

**Estado actual de instrumentación:** el registro ya guarda la hora de
cada oración generada (`fecha_hora`), pero **no guarda el momento en que
YP empezó a seleccionar el primer símbolo** — sin ese dato no se puede
calcular el tiempo real de composición por oración, solo el tiempo entre
oraciones consecutivas (una aproximación más ruidosa).

**Pendiente (NO se implementa hoy, no toca el plan de mañana):** agregar
un campo `hora_inicio_seleccion` a `tablero_escaneo.py` — una línea de
código, cero cambio de flujo para YP, decisión de cuándo agregarla queda
para después de validar que el tablero funciona en la práctica.

## 3. Precisión semántica de la expansión — evaluación con fonoaudiólogo

**Por qué debe ser evaluación humana, no solo automática:** una métrica
automática (como similitud de embeddings) no puede juzgar si "Me duele la
cabeza, quiero que venga mamá" captura correctamente lo que YP quiso decir
al seleccionar dolor+cabeza+mamá — eso requiere criterio clínico.

**Protocolo propuesto** (extensión natural de la prueba de línea base
humana ya pendiente en `protocolo-validacion.md` §4):

1. Un fonoaudiólogo (ciego a la selección de símbolos original) recibe
   pares (símbolos seleccionados, oración generada).
2. Clasifica cada oración en una escala: **Correcta** (captura la
   intención completa) / **Parcialmente correcta** (capta parte, pierde
   matices) / **Incorrecta** (tergiversa la intención, como el caso ya
   documentado de "mamá tiene dolor" en vez de "a mí me duele").
3. Se reporta el porcentaje en cada categoría, con intervalo de confianza
   de Clopper-Pearson (mismo estándar estadístico ya usado en el
   artículo).

**Ya tenemos evidencia preliminar propia** (no reemplaza la evaluación
con fonoaudiólogo, pero la anticipa): las 3 iteraciones documentadas en
`reportes/hallazgo_generador_llm_20260709.md` — 4/5 correctas en la
versión final del prompt, con el propio investigador haciendo el juicio.
Repetir ese juicio con un profesional clínico es lo que le da validez
científica real al número.

**Requiere:** reclutar un fonoaudiólogo — natural que sea parte del
mismo proceso de reclutamiento de voluntarios/expertos ya planeado
(`ruta-financiera-posicionamiento.md`, o directamente a través de la
Universidad de la Costa si tiene programa de Fonoaudiología).

## 4. Naturalidad / fluidez percibida — escala Likert con jueces expertos

**Diferencia clave con la métrica 3:** la precisión semántica pregunta
"¿significa lo correcto?"; la naturalidad pregunta "¿suena como algo que
diría una persona?" — son evaluaciones independientes, una oración puede
ser semánticamente correcta pero sonar robótica, o viceversa.

**Protocolo propuesto:**
1. 3-5 jueces (pueden ser los mismos oyentes de la prueba de línea base
   humana, o hablantes nativos de español sin relación con el proyecto)
   escuchan/leen cada oración generada.
2. Califican en escala Likert 1-5: "¿Qué tan natural suena esta oración
   en español, como si la hubiera dicho una persona?" (1=muy artificial,
   5=completamente natural).
3. Se reporta media, desviación estándar, y acuerdo entre jueces
   (coeficiente de correlación intraclase o similar).

**No requiere entrenamiento clínico** — a diferencia de la métrica 3,
cualquier hablante nativo puede ser juez de naturalidad, lo que la hace
más fácil de programar en paralelo con la prueba de línea base humana ya
pendiente.

---

## Resumen — qué se puede hacer ya y qué requiere más pasos

| Métrica | Estado | Bloqueador |
|---|---|---|
| KSPC-equivalente (SPC) | ✅ Script listo, calcula solo en cuanto haya datos reales | Ninguno — se activa con el primer uso real del tablero |
| Tasa de comunicación (PPM) | ⏳ Requiere 1 campo de logging adicional | Decisión de cuándo agregarlo (no antes del 10 de julio) |
| Precisión semántica (fonoaudiólogo) | ⏳ Protocolo diseñado | Reclutar fonoaudiólogo evaluador |
| Naturalidad (Likert, jueces) | ⏳ Protocolo diseñado | Reclutar 3-5 jueces (más fácil, sin requisito clínico) |

**Ninguna de estas cuatro cambia el plan del 10 de julio.** Su valor es
para el artículo científico y para las siguientes fases de validación,
una vez la Capa 1 (tablero) esté probada con YP y generando datos reales.
