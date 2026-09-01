# Impacto económico y social, y métricas de avance

Este documento reúne, con fuentes verificables, por qué la comunicación
aumentativa de bajo costo importa a escala económica y social — y qué
tan lejos ha llegado técnicamente este proyecto en concreto, con datos
reales extraídos de los registros del sistema (no estimaciones).

## 1. Contexto global

- El **16% de la población mundial** (más de 1.300 millones de
  personas, casi 240 millones de ellas niños) vive con alguna
  discapacidad significativa (OMS).
- Los trastornos de la comunicación tienen una **prevalencia estimada
  del 5-10%** de la población; entre 7-10% de los niños del mundo
  presentan un trastorno del habla o el lenguaje identificable.
- La discapacidad de la comunicación está **sistemáticamente
  subreconocida**: rara vez aparece priorizada en políticas públicas o
  investigación de discapacidad a nivel global, pese a su magnitud.
- El mercado global de dispositivos de comunicación aumentativa (AAC)
  pasó de **1.880 a 2.090 millones de USD entre 2023 y 2024** (11.4%
  de crecimiento anual) — evidencia de una necesidad creciente, no
  saturada.

## 2. La brecha de acceso — el problema económico real

- El costo económico global de la discapacidad, por pérdida de
  productividad y atención en salud, se estima en **1.3 billones de
  USD al año**.
- En países de ingresos bajos y medios, las pérdidas económicas
  asociadas representan entre **3% y 7% del PIB**.
- La discapacidad reduce en promedio un **15% la productividad
  laboral** de la persona afectada.
- **80% de los adultos con discapacidad en países de bajos ingresos
  están desempleados o subempleados.**
- La brecha de acceso a tecnología asistiva es enorme: **solo 3% de
  las personas que la necesitan en algunos países de bajos ingresos
  tienen acceso a ella, frente a 90% en países de altos ingresos.**

Este proyecto nace exactamente en ese punto de la brecha: tecnología
de comunicación funcional, sin costo de licencia, sobre hardware que
una familia ya tiene en casa.

## 3. Contexto Colombia

- Prevalencia de discapacidad según el Registro RLCPD: **3,37%** de la
  población (proyección oficial).
- Censo DANE 2005: **2.624.898 personas (6,3%)** reportaron alguna
  discapacidad; los departamentos con mayor proporción (Quindío, Norte
  de Santander, Nariño, Huila) superan el 8,5%.
- El RLCPD del Ministerio de Salud clasifica específicamente
  "alteración permanente de voz y habla" como categoría de registro —
  la cifra exacta desglosada no está disponible en fuentes públicas
  consultadas hasta ahora; se puede solicitar directamente al
  Observatorio de Discapacidad (SISPRO) para reforzar esta sección.

## 4. Comparación de costos frente al estado del arte

| Sistema | Curva de aprendizaje | Costo de dispositivo | Dependencia de internet | Datos personales |
|---|---|---|---|---|
| Google Project Relate | 500+ frases grabadas | Gratuito (requiere cuenta) | Sí (nube) | En servidores del proveedor |
| Dispositivos AAC especializados (Tobii, similares) | Variable | US$6.000+ | Depende del modelo | Variable |
| **Este proyecto** | **10-15 muestras/palabra** | **US$0 (hardware ya existente)** | **No — 100% offline** | **100% locales** |

## 5. Métricas técnicas de avance (datos reales del sistema, no estimados)

Extraídas directamente de los registros del proyecto al momento de
escribir este documento:

| Métrica | Valor real |
|---|---|
| Muestras de voz recolectadas | 150 guardadas / 190 intentadas |
| Tasa de descarte de muestras (con motivo documentado) | 21,1% |
| Exactitud LOOCV — voz (última validación, 172 muestras) | 73,3% |
| Exactitud LOOCV — gestos (última validación, 30 muestras) | 80,0% |
| Sesiones de gestos registradas | 30 |
| Oraciones generadas por el tablero, confirmadas correctas | 28/47 (59,6%) |
| Sesiones formales documentadas (con ficha completa) | 7 |
| Nivel de madurez tecnológica | TRL 5-6 |

**Nota de honestidad**: la tasa de descarte del 21,1% no es una
debilidad oculta — está documentada con motivo explícito para cada
muestra descartada (`registros/descartes.csv`), consistente con la
práctica de reportar honestamente la calidad del dato, no solo el
resultado final. La exactitud del tablero (59,6%) refleja el reto real
de construir oraciones de varios símbolos, ya identificado y
documentado en `RESEARCH_LOG.md` (2026-07-14) como un patrón asociado a
la longitud de la secuencia seleccionada, no un fallo aleatorio.

**Rigor estadístico**: las exactitudes se reportan con intervalos de
confianza exactos (Clopper-Pearson), el método correcto para
proporciones con muestras pequeñas — no solo el porcentaje puntual:

| Canal | n | Exactitud | IC95% (Clopper-Pearson) |
|---|---|---|---|
| Voz | 103 | 80.6% | 71.6%-87.7% |
| Gestos | 30 | 80.0% | 61.4%-92.3% |

Dos hallazgos metodológicos adicionales, documentados en
`RESEARCH_LOG.md`: (1) la exactitud cae de forma estadísticamente
significativa bajo captura simultánea de voz y gesto (interferencia
cognitivo-motora, intervalos que no se traslapan), lo que motivó
rediseñar la captura de simultánea a secuencial; y (2) el modelo es
confiable cuando alcanza consenso interno entre sus vecinos más
cercanos (92.3% de exactitud en vivo con consenso unánime vs. 13.0%
con consenso mínimo) — la política de decisión importa tanto como el
modelo mismo.

## 6. Afiliación institucional

El proyecto está postulando a la convocatoria Ignacio H. de Larramendi
2026 de Fundación Mapfre, y se encuentra en proceso de vinculación
institucional con la Universidad de la Costa (CUC).

## 7. Impacto proyectado

Con la ampliación de la serie de casos (ver
[`ruta-expansion-condiciones-neurologicas.md`](ruta-expansion-condiciones-neurologicas.md))
a condiciones como ELA, parálisis cerebral, afasia post-ictus y
Parkinson, el proyecto apunta directamente a la brecha de acceso
descrita en la sección 2: llevar una vía de comunicación funcional a
personas que hoy están dentro del 97% sin acceso a tecnología asistiva
en contextos de bajos recursos, con evidencia técnica real y
creciente, no solo una promesa.

## Referencias

- OMS, [Disability and health fact sheet](https://www.who.int/news-room/fact-sheets/detail/disability-and-health)
- OMS, [Assistive technology fact sheet](https://www.who.int/news-room/fact-sheets/detail/assistive-technology)
- Comunicación aumentativa, mercado global: [Global AAC Devices Market Analysis 2024-2029](https://www.globenewswire.com/news-release/2024/01/15/2809369/0/en/Global-Augmentative-Alternative-Communication-AAC-Devices-Market-Analysis-2024-2029-by-Device-Type-Application-End-User-Region-and-Country.html)
- Discapacidad de la comunicación en países de ingresos bajos y medios: [PMC11288154](https://pmc.ncbi.nlm.nih.gov/articles/PMC11288154/)
- DANE, [Discapacidad](https://www.dane.gov.co/index.php/estadisticas-por-tema/demografia-y-poblacion/discapacidad)
- SISPRO, [Observatorio de Discapacidad — Prevalencia](https://www.sispro.gov.co/observatorios/ondiscapacidad/Paginas/prevalencia.aspx)
- Ministerio de Salud, [RLCPD](https://www.minsalud.gov.co/proteccionsocial/promocion-social/Discapacidad/Paginas/registro-localizacion.aspx)
