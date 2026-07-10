# Cumplimiento normativo y estrategia de publicación

Este documento cubre el marco regulatorio aplicable al software (clasificación
de dispositivos médicos, licenciamiento, propiedad intelectual) y las
venues de publicación identificadas para el proyecto. Complementa
`asesoria-legal-publicacion.md`, centrado en la protección de datos de la
participante.

---

## 1. Clasificación regulatoria del software

Según la normativa de INVIMA (regulador colombiano de dispositivos
médicos), un software se clasifica como dispositivo médico en función del
propósito que el fabricante declare — diagnóstico, prevención,
monitoreo, tratamiento o alivio de enfermedad. Esa clasificación exige
registro sanitario (45-90 días hábiles según la clase de riesgo) y
responsabilidad regulatoria formal.

En consecuencia, el sistema se describe consistentemente como:

> Prototipo de investigación / herramienta de comunicación aumentativa y
> alternativa (AAC) de apoyo — no es un dispositivo médico, no ha sido
> evaluado ni registrado ante INVIMA, no está diseñado para diagnóstico ni
> tratamiento de ninguna condición.

Este lenguaje se mantiene de forma visible en el `README.md` del
repositorio, en cualquier artículo, póster o presentación, y en cualquier
demo pública — es el criterio que distingue un proyecto de investigación
estudiantil de un producto médico no registrado.

## 2. Licenciamiento del código

El repositorio se publica bajo licencia **MIT**, que incluye cláusula de
exención de responsabilidad ("AS IS", sin garantía): el software se
entrega tal cual, sin garantías, y el autor no es responsable por el uso
que terceros le den. Apache-2.0 es la alternativa considerada cuando se
requiere una cláusula explícita de concesión de patentes.

## 3. Higiene del repositorio antes de la publicación

Criterios aplicados antes de cada `git push` a un repositorio público:

- Revisión de todo el historial de commits (no solo el estado actual) en
  busca de archivos de `data/`, `data_gestos/`, `data_vivo_confirmada/`
  que se hayan subido por accidente.
- `.gitignore` con esas carpetas configurado antes del primer commit al
  repo público.
- Si algo sensible queda en el historial: se reescribe el historial
  (`git filter-repo` o equivalente) antes de hacer público el repositorio
  — borrar y volver a commitear no es suficiente, el contenido sigue
  siendo accesible en el historial.
- Ninguna credencial, API key o `.env` en el código.
- Etiquetado (`git tag`) de la versión exacta citada en cualquier
  artículo, de forma que un lector pueda ubicar la versión que generó los
  resultados reportados.

## 4. Propiedad intelectual al publicar en revista

Se prioriza revistas con licencia **CC-BY** (mantiene la autoría, permite
reutilización con atribución) sobre las que exigen cesión completa de
copyright; toda transferencia de derechos se revisa antes de firmar. Se
verifica que la revista esté indexada en **DOAJ** (Directory of Open
Access Journals) antes de someter, como salvaguarda frente a revistas
depredadoras. La titularidad del software es independiente de la
publicación de un artículo sobre él — el texto y el código tienen
regímenes de derechos separados.

## 5. Venues de publicación identificadas

### Ruta A — Software

**Journal of Open Source Software (JOSS)**: gratuita, revisión pública en
GitHub, ciclo de 2-4 semanas. Requiere un mínimo de 6 meses de historial
público del repositorio (commits, issues, releases) antes del envío. El
paper de JOSS versa sobre el software en sí, de forma complementaria —no
competitiva— al artículo científico sobre los resultados con YP.

### Ruta B — Hallazgo científico/técnico (interferencia cognitivo-motora)

**ACM ASSETS (SIGACCESS Conference on Computers and Accessibility)**:
conferencia de referencia mundial en tecnología y accesibilidad, con
Student Research Competition orientada a trabajo estudiantil. El ciclo
2026 cerró el 24 de junio; el objetivo realista es el ciclo 2027. No es
de revisión anónima y exige formato de PDF accesible.

**CLEI (Conferencia Latinoamericana de Informática)**: venue regional de
cómputo con indexación IEEE Xplore. El ciclo 2026 (México, septiembre)
cerró el registro de resúmenes el 19 de abril; objetivo realista: ciclo
2027. Incluye competencias de tesis de maestría/doctorado.

### Ruta C — Clínica/salud

Revista Colombiana de Rehabilitación, Revista Mexicana de Ingeniería
Biomédica, Revista Ingeniería Biomédica (Colombia) — ver
`asesoria-legal-publicacion.md` para el detalle. Estas venues son
apropiadas cuando el énfasis del artículo es clínico/salud; ASSETS/JOSS/
CLEI cuando el énfasis es técnico/ingeniería. No son excluyentes: el
hallazgo de interferencia cognitivo-motora, por ejemplo, es relevante
para ambas audiencias y puede dar lugar a artículos distintos sobre el
mismo proyecto.

### Secuencia planificada

```
1. RedCOLSI                                        — credibilidad inmediata
2. Repo público + 6 meses de historial              — en paralelo desde ahora
3. Artículo científico (salud/rehabilitación)        — tras aval de ética
4. JOSS (software)                                   — a los 6 meses del repo
5. ASSETS / CLEI 2027                                — con tiempo de preparación
```

## 6. Criterios de verificación antes de publicar

- El sistema se describe siempre como prototipo de investigación / AAC,
  nunca como diagnóstico o tratamiento.
- Licencia MIT aplicada antes de publicar el código.
- Historial de git libre de datos sensibles antes de hacer público el
  repositorio.
- Versión exacta (`git tag`) referenciada en cualquier artículo.
- Ninguna cesión total de copyright firmada sin revisión previa.
- Revista o venue verificada en DOAJ o de reputación conocida.
- Disclaimer de "no es dispositivo médico" visible en README y en
  cualquier demo pública.
