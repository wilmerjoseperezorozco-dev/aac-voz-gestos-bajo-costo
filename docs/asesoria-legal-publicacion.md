# Marco legal y ético de divulgación

Este documento resume el marco legal colombiano y los criterios que rigen
qué material del proyecto es apto para divulgación pública en cada etapa,
y por qué. Complementa el consentimiento informado firmado por YP y el
protocolo de investigación (`Protocolo_Investigacion_MVP_Voz_Gestos.docx`).

---

## Material apto para divulgación pública

| Material | Justificación |
|---|---|
| Código fuente (`grabar.py`, `entrenar.py`, `predecir.py`, etc.) | No contiene datos personales de YP |
| Métricas agregadas (exactitud, matrices de confusión, intervalos de confianza) | Son estadísticas, no identifican a una persona |
| `data_demo/` (audios sintéticos) | Generados artificialmente, no son datos reales de YP |
| Documentos metodológicos (protocolo, hallazgos técnicos) usando el alias **YP** | El alias protege identidad; consistente con el consentimiento firmado |
| Presentación en RedCOLSI describiendo el método y resultados agregados | Nivel estudiantil, sin exposición de datos identificables |
| El protocolo de investigación, para uso interno con el comité de ética | Es exactamente su destinatario previsto |

## Material restringido y su fundamento legal

| Material | Fundamento legal | Condición de desbloqueo |
|---|---|---|
| Audios/videos crudos de YP (`data/`, `data_gestos/`, `data_vivo_confirmada/`) | Ley 1581 de 2012 y Decreto 1377 de 2013: constituyen datos biométricos y de salud, categoría de "dato sensible"; el consentimiento vigente autoriza uso académico interno, no publicación pública del dato crudo | Autorización explícita y específica de YP para esa finalidad exacta |
| Fotos o videos donde se identifique el rostro de YP (demo pública, sustentación, prensa) | El derecho a la propia imagen, reconocido en la jurisprudencia constitucional colombiana, es distinto y separado del derecho a la protección de datos; el consentimiento actual autoriza el procesamiento de datos para investigación, no la exhibición pública de imagen/rostro | Autorización específica y separada para uso de imagen, con finalidad exacta declarada |
| Nombre completo de YP en cualquier documento público | Compromiso de anonimización asumido en el consentimiento firmado | No aplica — se usa siempre el alias |
| Sometimiento a revista indexada | Requisito editorial estándar: aval de comité de ética institucional | Aval del comité de ética |
| Afirmación de superioridad estadística del sistema frente a comprensión humana | No existe el dato — la prueba de línea base con oyentes externos está pendiente de ejecución | Ejecutar el test de línea base ya definido en el protocolo |
| Uso del término "apraxia" como diagnóstico de YP | No existe evaluación clínica formal que lo confirme | Evaluación fonoaudiológica o neurológica formal, o mantener la caracterización funcional ya adoptada |

---

## Capacidad jurídica de la participante

La Ley 1996 de 2019 eliminó la figura de interdicción para personas con
discapacidad y estableció que toda persona mayor de 18 años con
discapacidad tiene plena capacidad jurídica por defecto, con derecho a
recibir apoyos para tomar sus propias decisiones, salvo que un proceso
judicial específico haya establecido lo contrario.

En consecuencia:

- Salvo que exista un proceso judicial de adjudicación de apoyos vigente
  para YP, su propia firma en el consentimiento informado es válida y
  suficiente, sin requerir per se la firma de un representante legal.
- La ley recomienda un proceso de consentimiento accesible, apoyado en
  herramientas de comunicación (como las tarjetas de imágenes usadas en
  el protocolo de grabación) que aseguren su comprensión y expresión de
  voluntad. El propio sistema desarrollado en este proyecto puede, con el
  tiempo, integrarse a ese proceso de apoyo a la comunicación.

## Revistas objetivo

| Revista | Área | Indexación conocida |
|---|---|---|
| Revista Colombiana de Rehabilitación | Fonoaudiología/rehabilitación (Colombia) | Publindex (histórico categoría B) |
| Revista Mexicana de Ingeniería Biomédica | Ingeniería biomédica (Latinoamérica) | SciELO, Latindex, open access |
| Revista Ingeniería Biomédica (Colombia) | Ingeniería biomédica (Colombia) | SciELO Colombia |

La indexación vigente debe verificarse en Publindex/Scimago Journal Rank
antes de someter, así como la aceptación editorial de reportes de caso.
RedCOLSI se mantiene como paso previo recomendado, no como sustituto.

## Criterios de verificación antes de cualquier envío externo

- El material usa exclusivamente el alias YP.
- El material excluye audios/videos crudos.
- Si incluye foto o video con rostro identificable: existe autorización
  específica de imagen, separada del consentimiento de datos.
- No se afirma un diagnóstico clínico no confirmado.
- Si es para revista indexada: existe aval del comité de ética.
- Si se afirma comparación contra desempeño humano: el test de línea base
  ya fue ejecutado.
