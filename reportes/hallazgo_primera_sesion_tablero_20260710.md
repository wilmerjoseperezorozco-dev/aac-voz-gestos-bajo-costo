# Primera sesión real con YP — tablero de escaneo (Capa 1+2) — 2026-07-10

## Contexto de la sesión

Primera prueba del tablero de escaneo (`tablero_escaneo.py`, modo teclado)
directamente con YP, tras la validación técnica preliminar del generador
de oraciones (`hallazgo_generador_llm_20260709.md`). El investigador
principal asistió a YP en una fase inicial de familiarización con los
íconos antes de la selección independiente — esta sesión combina
aprendizaje asistido y uso funcional, no es una prueba de uso
independiente ciego; esa distinción se mantiene en el registro para
interpretar los resultados con precisión metodológica.

## Observaciones cualitativas

- **Familiarización con los íconos:** tras una breve explicación asistida
  de cada símbolo, YP identificó la mayoría de las imágenes con facilidad
  y aprendió a reconocer los primeros 11 símbolos del tablero.
- **Confusión específica:** los símbolos "yo" (🙋‍♀️) y "tu" (👉) generaron
  confusión recurrente. Es un patrón conocido en la literatura AAC — los
  pronombres son consistentemente una de las categorías más difíciles de
  representar icónicamente, al ser conceptos abstractos sin referente
  visual concreto.
- **Velocidad de escaneo:** el intervalo actual (1.8 s por símbolo,
  `INTERVALO_TECLADO_MS`) resultó rápido para el tiempo de procesamiento
  visual y de reacción motora de YP. Ella logró seleccionar exitosamente
  con la barra espaciadora, pero con esfuerzo — candidata directa a
  ajuste para la siguiente sesión.
- **Confirmación motora:** YP puede presionar una tecla física
  (espaciadora) de forma efectiva. Persiste la necesidad, ya anticipada
  en el diseño de expansión (`propuesta-expansion.md`), de un botón o
  interruptor físico dedicado — un blanco más grande y accesible que una
  tecla de teclado estándar, consistente con equipo de conmutación
  adaptada usado en sistemas AAC de referencia (Hawking/ACAT).
- **Capacidad comunicativa general:** con apoyo, YP demostró capacidad
  funcional para expresar una necesidad a través del tablero — el
  objetivo central de la Capa 1 queda validado como alcanzable, con
  necesidad de entrenamiento y acompañamiento profesional adicional
  (fonoaudiología) para consolidarlo.

## Datos cuantitativos de la sesión

10 intentos registrados en `registros/predicciones_tablero.csv`:

| Símbolos seleccionados | Oración generada | Confirmada |
|---|---|---|
| querer + mama + tu + television + comer | "Quiero que mamá me prepare la television para comer." | sí |
| bano + ayuda + dolor + ayuda + mama | "Me duele el bano, necesito ayuda, quiero que venga mamá." | no |
| bano + comer + salir + tu + television | "Vamos a la tele, comeremos algo y luego saliremos al bano." | no |
| bano + salir + tu | "Tengo hambre, quiero salir a bajar a comprar." | sí |
| mama + comer + mama + cansada + salir | "Mamá, quiero que coma y venga a salir." | no |
| yo + querer + dolor | "Me duele mi cabeza, quiero que me ayude mamá." | no |
| yo + querer + mas | "Quiero más." | sí |
| tu + dolor + bano | "Tú tienes dolor en el bano." | no |
| bano + yo + dolor | "Me duele el bano, me siento dolorida." | (sin confirmar) |
| yo + yo | "Estoy muy cansada, quiero descansar." | (sin confirmar) |

**Precisión semántica confirmada: 3/8 (37.5%)** de los intentos con
respuesta sí/no explícita — sensiblemente por debajo del 4/5 (80%)
observado en la evaluación preliminar controlada del 2026-07-09. La
diferencia es esperable y metodológicamente relevante: el conjunto de
prueba preliminar era pequeño y curado (5 combinaciones), mientras que
las selecciones reales de YP incluyen combinaciones más variadas y menos
predecibles (símbolos repetidos, combinaciones no anticipadas), que
exponen debilidades no capturadas en la prueba controlada.

**Métrica de esfuerzo motor (SPC, ver `metricas-fonoaudiologicas.md`):**
0.81 selecciones de escaneo por palabra generada, en promedio, sobre los
3 intentos confirmados como correctos — favorable frente a la referencia
de ~1 selección por carácter de un teclado de escaneo letra por letra.

## Hallazgo nuevo: alucinación de contenido no seleccionado

Dos intentos muestran al generador introduciendo información que YP no
seleccionó, un patrón distinto y más serio que el ya documentado descarte
del símbolo "no":

- "yo + querer + dolor" → "Me duele **mi cabeza**, quiero que **me ayude
  mamá**." — "cabeza" y "mamá" no forman parte de la selección.
- "yo + yo" → "Estoy **muy cansada, quiero descansar**." — ningún
  concepto de cansancio o descanso fue seleccionado.

Adicionalmente, "bano + yo + dolor" → "Me duele el bano, me siento
dolorida" reproduce el patrón de atribución incorrecta de sujeto
documentado en la iteración 1 del generador (`hallazgo_generador_llm_20260709.md`),
sugiriendo que la corrección aplicada no generaliza completamente a
combinaciones fuera del conjunto de prueba original.

## Implicaciones de diseño

1. **Intervalo de escaneo:** aumentar `INTERVALO_TECLADO_MS` de 1800 ms a
   un valor mayor (proponer 2500-3000 ms como punto de partida) para la
   siguiente sesión, y ajustar empíricamente según la respuesta de YP.
2. **Íconos de pronombres:** revisar los símbolos de "yo" y "tu" — evaluar
   alternativas más distintivas (por ejemplo, contraste de color o forma
   más marcado) o posponer su uso hasta consolidar el resto del
   vocabulario núcleo.
3. **Confirmación táctil:** explorar un interruptor o botón físico
   dedicado como entrada alternativa a la barra espaciadora, más
   accesible para el perfil motor de YP.
4. **Generador de oraciones:** la tasa de alucinación observada en uso
   real (selecciones repetidas o combinaciones no anticipadas) es un
   hallazgo relevante para el artículo y debe documentarse como
   limitación activa del sistema — la confirmación obligatoria de YP
   antes de comunicar cualquier oración sigue siendo, con esta evidencia,
   una salvaguarda no negociable del diseño.

## Próximo paso

Incorporar los ajustes de intervalo de escaneo y evaluar iconografía
alternativa para pronombres en la siguiente sesión de práctica con YP.
