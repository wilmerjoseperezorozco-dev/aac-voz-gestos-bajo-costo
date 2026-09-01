# Ruta de expansión — condiciones neurológicas, edad y proyectos hermanos

Este documento responde tres preguntas necesarias para ampliar la serie
de casos con rigor científico: ¿el sistema está especializado o es
generalizable?, ¿qué condiciones se pueden sumar de forma segura?, y
¿cómo se relaciona con otros proyectos de comunicación/neurodesarrollo
del mismo autor?

## El punto que ordena todo: dos mecanismos, dos diseños de investigación

Este proyecto combina dos mecanismos distintos, y es importante
nombrarlos por separado — mezclarlos en la misma narrativa de
validación sería un error metodológico real, no solo de redacción:

- **Mecanismo A — clasificador personalizado de caso único** (voz y
  gestos, k-NN + DTW, un modelo por persona). Es un diseño **n-of-1 /
  de sujeto único**: demuestra que el método se puede entrenar y
  validar por individuo con muestras pequeñas, no que "detecta la
  condición X en una población". Sumar participantes aquí significa
  sumar réplicas independientes del mismo protocolo de caso único.
- **Mecanismo B — tablero de escaneo + expansión de frases por LLM**.
  Es infraestructura asistiva genérica, agnóstica a la causa del
  problema de comunicación.

## 1. ¿Especializado o generalizable?

El clasificador es generalizable *como método* (cualquier señal motora
repetible y propia de la persona: voz, gesto, movimiento grueso), pero
su validación actual es específica de **disartria/apraxia** — daño en
la producción motora del habla. El tablero + LLM generaliza a
cualquier persona con necesidad de comunicación aumentativa simbólica,
sin importar la causa.

## 2. Condiciones candidatas para ampliar la serie de casos

**Nivel 1 — análogas directas al caso ya validado:**
- ELA (esclerosis lateral amiotrófica) con habla disártrica residual
- Parálisis cerebral con disartria/anartria
- Afasia motora o apraxia del habla post-ictus
- Traumatismo craneoencefálico con disartria adquirida

**Nivel 2 — mismo mecanismo, mayor heterogeneidad:**
- Enfermedad de Parkinson (disartria hipocinética)
- Esclerosis múltiple
- Atrofia muscular espinal / distrofia muscular con compromiso bulbar

**Fuera de este mecanismo** (déficit distinto — de lenguaje, cognición
o pragmática social, no de producción motora; el tablero puede
ayudarles pero no bajo el mismo diseño de clasificador personalizado):
trastorno del espectro autista sin compromiso motor del habla,
trastorno del desarrollo del lenguaje, mutismo selectivo, TDAH,
deterioro cognitivo/demencia.

## 3. Edad

No existe una edad mínima clínica para el uso de comunicación
aumentativa en general. Sin embargo, el vocabulario núcleo usado en el
tablero (Soto & Cooper, 2021, *Augmentative and Alternative
Communication*) está diseñado para niños que inician comunicación —
aplicarlo a una persona adulta es una adaptación documentada, no una
validación de que sea el vocabulario óptimo para adultos. Las
condiciones de Nivel 1-2 anteriores sesgan hacia población
adulta/adulta mayor (ELA, ictus, Parkinson, esclerosis múltiple); la
parálisis cerebral pediátrica quedaría como estrato aparte, con el
vocabulario originalmente pensado para niños.

## 4. Relación con otros proyectos del mismo autor

Existe un proyecto hermano de comunicación/neurodesarrollo que cubre
espectro autista, trastorno del desarrollo del lenguaje, mutismo
selectivo, TDAH y deterioro cognitivo, mediante tamizaje basado en
reglas (sin aprendizaje automático). **Se mantienen como proyectos
separados a propósito**: mezclar un tamizaje poblacional con un
clasificador de caso único produciría una narrativa de validación
confusa. Lo único potencialmente compartible entre ambos es el
concepto de tablero/vocabulario AAC — una posible extracción a módulo
común, evaluada a futuro, no una fusión de los dos sistemas.

## Qué tipo de alianzas buscamos por condición

- **Fundaciones/asociaciones de ELA, Parkinson, esclerosis múltiple,
  daño cerebral por ACV**: acceso a participantes voluntarios para
  ampliar la serie de casos, orientación clínica sobre criterios de
  inclusión razonables.
- **Servicios de fonoaudiología/terapia del lenguaje**: validación de
  los indicadores de autonomía comunicativa y carga del cuidador.
- **Especialistas en desarrollo de vocabulario AAC para adultos**: el
  vocabulario núcleo actual necesita una versión validada para
  población adulta, no solo adaptada.

Ver el Issue de alianzas fijado en este repositorio para contactar.

## Referencias

- ASHA, [AAC Practice Portal](https://www.asha.org/practice-portal/professional-issues/augmentative-and-alternative-communication/)
- ISAAC, [About AAC](https://isaac-online.org/english/about-aac/)
- AssistiveWare, [What difference does diagnosis make?](https://www.assistiveware.com/learn-aac/what-difference-diagnosis-make)
- Personalized ASR in ALS: [PMC12379579](https://pmc.ncbi.nlm.nih.gov/articles/PMC12379579/)
- AAC interventions for minimally verbal autism: [PMC13084014](https://pmc.ncbi.nlm.nih.gov/articles/PMC13084014/)
- Soto, G. & Cooper, B. (2021). An early Spanish vocabulary for children
  who use AAC. *Augmentative and Alternative Communication*,
  doi:10.1080/07434618.2021.1881822
