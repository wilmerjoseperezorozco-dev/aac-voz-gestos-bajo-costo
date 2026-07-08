# Asesoría legal y editorial — qué se puede publicar ya y qué no

Checklist proactivo, con el marco legal colombiano exacto detrás de cada
punto. Úsalo antes de subir, mostrar o enviar cualquier material del
proyecto a un tercero.

---

## ✅ Se puede publicar / mostrar YA

| Material | Por qué es seguro |
|---|---|
| Código fuente (`grabar.py`, `entrenar.py`, `predecir.py`, etc.) | No contiene datos personales de YP |
| Métricas agregadas (exactitud, matrices de confusión, intervalos de confianza) | Son estadísticas, no identifican a una persona |
| `data_demo/` (audios sintéticos) | Generados artificialmente, no son datos reales de YP |
| Documentos metodológicos (protocolo, hallazgos técnicos) usando el alias **YP** | El alias protege identidad; consistente con el consentimiento firmado |
| Presentación en RedCOLSI describiendo el método y resultados agregados | Nivel estudiantil, sin exposición de datos identificables |
| El Word/protocolo de investigación, para uso interno con el comité de ética | Es exactamente su destinatario previsto |

## ❌ NO se puede publicar todavía — con la razón legal exacta

| Material | Bloqueo legal | Qué falta para desbloquearlo |
|---|---|---|
| Audios/videos crudos de YP (`data/`, `data_gestos/`, `data_vivo_confirmada/`) | **Ley 1581 de 2012 + Decreto 1377 de 2013**: son datos biométricos y de salud, categoría de "dato sensible" — requieren autorización explícita para cada finalidad específica, y el consentimiento actual autoriza uso académico interno, no publicación pública del dato crudo | Autorización explícita adicional y específica de YP para ESA finalidad exacta, si algún día se decide publicarlos (no recomendado) |
| **Fotos o videos donde se vea la cara de YP** (demo pública, video para la sustentación, nota de prensa) | **Derecho a la propia imagen** (reconocido en jurisprudencia constitucional colombiana): es un derecho **distinto y separado** del derecho a la protección de datos. El consentimiento que ya tienes autoriza el *procesamiento de datos* para investigación — **no** autoriza automáticamente mostrar su imagen/rostro en un video público, prensa o redes | Una autorización específica y separada para uso de imagen, con la finalidad exacta descrita (ej. "video de la sustentación universitaria", "nota de prensa de la universidad") |
| Nombre completo de YP en cualquier documento público | Viola el compromiso de anonimización ya asumido en el consentimiento firmado | Nunca — usar siempre el alias |
| Sometimiento a una revista indexada | Sin aval de comité de ética institucional, la mayoría de revistas serias lo rechazan de entrada (requisito editorial estándar, no solo preferencia) | Aval del comité de ética (`Protocolo_Investigacion_MVP_Voz_Gestos.docx` ya está armado para solicitarlo) |
| Afirmar superioridad estadística del sistema vs. comprensión humana | No existe el dato — la prueba de línea base nunca se ejecutó | Ejecutar el test de línea base (protocolo ya definido) |
| Afirmar "apraxia" como diagnóstico de YP | No hay evaluación clínica formal que lo confirme | Evaluación fonoaudiológica/neurológica formal, o mantener el lenguaje funcional ya usado |

---

## Punto legal que probablemente no tenías en el radar: capacidad jurídica

Verifiqué la **Ley 1996 de 2019**, que es importante y buena noticia para
el proyecto: eliminó la figura de "interdicción" para personas con
discapacidad y estableció que **toda persona mayor de 18 años con
discapacidad tiene plena capacidad jurídica por defecto**, con derecho a
recibir *apoyos* para tomar sus propias decisiones — no a que alguien
decida por ella, salvo que un proceso judicial específico haya
establecido lo contrario.

**Qué significa para el consentimiento de YP:**
- Salvo que exista un proceso judicial de "adjudicación de apoyos" formal
  que diga lo contrario, **su propia firma en el consentimiento
  informado es válida y suficiente** — no se necesita per se la firma de
  un representante legal.
- La ley recomienda un **proceso de consentimiento accesible**: usar
  apoyos de comunicación (como las tarjetas de imágenes que ya usas en el
  protocolo de grabación) para asegurar que ella entiende y expresa su
  voluntad, no solo que alguien firme por ella. El propio sistema que
  estás construyendo puede, con el tiempo, ser parte de ese proceso de
  apoyo a su comunicación — un argumento bonito y honesto para el
  artículo.
- **Verificar (solo tú lo sabes):** ¿existe algún proceso judicial de
  adjudicación de apoyos para YP? Si no existe, el consentimiento actual
  firmado por ella es jurídicamente correcto. Si existe, se necesitaría
  también la participación de la persona designada como apoyo.

## Revistas objetivo reales (verificadas, no genéricas)

| Revista | Área | Indexación conocida |
|---|---|---|
| Revista Colombiana de Rehabilitación | Fonoaudiología/rehabilitación (Colombia) | Publindex (histórico categoría B) |
| Revista Mexicana de Ingeniería Biomédica | Ingeniería biomédica (Latinoamérica) | SciELO, Latindex, open access |
| Revista Ingeniería Biomédica (Colombia) | Ingeniería biomédica (Colombia) | SciELO Colombia |

Antes de elegir, verifica en Publindex/Scimago Journal Rank la indexación
vigente (cambia con el tiempo) y confirma que aceptan reportes de caso —
no todas lo hacen. RedCOLSI sigue siendo el paso previo recomendado, no
sustituto de estas revistas.

## Checklist final antes de cualquier envío externo

- [ ] ¿El material usa solo el alias YP? (nunca el nombre real)
- [ ] ¿El material excluye audios/videos crudos?
- [ ] Si hay foto/video de su cara: ¿existe autorización específica de
      imagen, separada del consentimiento de datos?
- [ ] ¿Se evita afirmar un diagnóstico clínico no confirmado?
- [ ] Si es para revista indexada: ¿ya hay aval del comité de ética?
- [ ] Si se afirma comparación contra humanos: ¿el test de línea base ya
      se ejecutó?
