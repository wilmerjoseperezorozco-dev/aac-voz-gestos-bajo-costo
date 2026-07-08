# Protección del ingeniero de software + dónde publicar

Este documento te protege a **ti**, como autor y desarrollador — distinto
de `asesoria-legal-publicacion.md`, que protege a YP. Úsalos juntos.

---

## 1. La protección más importante: cómo describes el software

Verifiqué la normativa de INVIMA (regulador colombiano de dispositivos
médicos). Hallazgo clave: **un software se clasifica como dispositivo
médico según el propósito que el "fabricante" (tú) declare que tiene** —
diagnóstico, prevención, monitoreo, tratamiento o alivio de enfermedad. Si
cae en esa clasificación, exige registro sanitario (45-90 días hábiles
según la clase de riesgo) y responsabilidad regulatoria formal.

**Esto significa que la redacción que uses es, literalmente, tu escudo
legal.** Nunca describas el sistema como "diagnóstico", "tratamiento",
"monitoreo clínico" ni nada que suene a dispositivo médico. Descríbelo
siempre como:

> "Prototipo de investigación / herramienta de comunicación aumentativa y
> alternativa (AAC) de apoyo — no es un dispositivo médico, no ha sido
> evaluado ni registrado ante INVIMA, no está diseñado para diagnóstico ni
> tratamiento de ninguna condición."

**Acción concreta:** agrega esta frase (o una variante) en:
- El `README.md` del repositorio, de forma visible.
- Cualquier artículo, póster o presentación.
- Cualquier demo pública (dilo en voz alta antes de la sustentación).

Esto no es solo prudencia — es la diferencia entre "proyecto de
investigación estudiantil" y "producto médico no registrado", que sí
tiene consecuencias legales reales para quien lo distribuye.

## 2. Licencia de código — tu escudo de responsabilidad civil

Cuando publiques el repositorio, elige una licencia open source explícita
(no dejarlo sin licencia — eso legalmente significa "todos los derechos
reservados", nadie puede reutilizarlo, y además no te protege).

**Recomendación: MIT o Apache-2.0.** Ambas incluyen una cláusula de
exención de responsabilidad ("AS IS", sin garantía) que **te protege a ti
como autor** si alguien usa tu código y algo sale mal — la licencia deja
explícito que el software se entrega tal cual, sin garantías, y que el
autor no es responsable por el uso que otros le den.

Apache-2.0 añade además una cláusula explícita de concesión de patentes —
más relevante si en algún momento el proyecto tiene componentes
patentables (poco probable aquí, pero es la opción más "blindada").

## 3. Higiene del repositorio antes de hacerlo público

Como ingeniero, este es tu checklist antes de cualquier `git push` a un
repo público:

- [ ] Revisar **todo el historial de commits** (no solo el estado actual)
      en busca de archivos de `data/`, `data_gestos/`,
      `data_vivo_confirmada/` que se hayan subido por accidente.
- [ ] `.gitignore` con esas carpetas ANTES del primer commit al repo
      público — más fácil prevenir que limpiar historial después.
- [ ] Si algo sensible ya quedó en el historial: no basta con borrarlo y
      commitear de nuevo (sigue en el historial) — se necesita reescribir
      el historial (`git filter-repo` o similar) antes de hacerlo público.
- [ ] Ningún API key, credencial o `.env` en el código (aplica siempre,
      pero recuérdalo explícitamente antes de publicar).
- [ ] Etiqueta (`git tag`) la versión exacta del código que citas en
      cualquier artículo — si el código sigue cambiando después de
      publicar, un lector debe poder encontrar la versión exacta que
      generó tus resultados.

## 4. Propiedad intelectual al publicar en una revista

- **Nunca firmes transferencia total y exclusiva de derechos de autor**
  sin leerla. Prioriza revistas con licencia **CC-BY** (mantienes la
  autoría, permites reutilización con atribución) sobre las que piden
  cesión completa de copyright.
- **Cuidado con revistas depredadoras**: si te escriben invitándote a
  publicar rápido a cambio de una tarifa, sin revisión por pares real, es
  una señal de alerta. Verifica que la revista esté en **DOAJ**
  (Directory of Open Access Journals) antes de enviar nada.
- Como ya eres dueño del software por defecto (ver
  `ruta-financiera-posicionamiento.md`), publicar un artículo sobre él NO
  te hace ceder derechos sobre el código — son cosas separadas: el
  artículo (texto) y el software (código) tienen su propio régimen de
  derechos cada uno.

## 5. Dónde publicar — venues reales para un ingeniero de software

### Ruta A — Software (el código en sí, separado del hallazgo científico)

**Journal of Open Source Software (JOSS)** — la opción más natural para
ti como ingeniero:
- 100% gratis, revisión pública en GitHub, rápida (2-4 semanas).
- **Requisito importante:** el repositorio debe llevar **mínimo 6 meses
  de historial público** (commits, issues, releases) antes de enviarlo —
  planifica: haz el repo público ahora, mismo, y en 6 meses aplicas.
- El paper de JOSS es sobre el **software**, no sobre los resultados
  científicos con YP — eso va en un artículo aparte (el que ya armamos).
  Son dos publicaciones complementarias, no compiten entre sí.

### Ruta B — El hallazgo científico/técnico (interferencia cognitivo-motora)

**ACM ASSETS (SIGACCESS Conference on Computers and Accessibility)** — es
**la** conferencia de referencia mundial en tecnología y accesibilidad, y
tiene una **Student Research Competition** diseñada justo para trabajo
estudiantil como el tuyo.
- Ciclo 2026 ya cerró (límite fue 24 de junio de 2026) — objetivo
  realista: **ciclo 2027**. Vale la pena empezar a preparar con tiempo,
  es la venue de mayor prestigio de esta lista.
- Nota importante: **no es anónimo** (tu nombre va en el paper desde el
  envío) y exige formato de PDF accesible — coherente con el espíritu del
  proyecto.

**CLEI (Conferencia Latinoamericana de Informática)** — venue regional de
cómputo, con indexación IEEE Xplore.
- Ciclo 2026 (México, septiembre) ya cerró registro de resúmenes (19 de
  abril) — objetivo realista: **ciclo 2027**.
- Tienen competencias de tesis de maestría/doctorado si en el futuro
  formalizas el trabajo en ese nivel.

### Ruta C — Ya identificadas antes (clínica/salud), siguen vigentes

Revista Colombiana de Rehabilitación, Revista Mexicana de Ingeniería
Biomédica, Revista Ingeniería Biomédica (Colombia) — ver
`asesoria-legal-publicacion.md` para el detalle. Estas son más
apropiadas si el énfasis del artículo es clínico/salud; ASSETS/JOSS/CLEI
son más apropiadas si el énfasis es técnico/ingeniería. **No son
excluyentes** — puedes apuntar a una salud + una técnica con artículos
distintos sobre el mismo proyecto (el hallazgo de interferencia
cognitivo-motora, por ejemplo, interesa a ambas audiencias).

### Orden recomendado (realista, sin perder tiempo)

```
1. RedCOLSI (ahora, gratis, ya vigente)          — credibilidad inmediata
2. Repo público + 6 meses de historial            — arranca YA en paralelo
3. Artículo científico (salud/rehabilitación)      — cuando haya aval de ética
4. JOSS (software)                                 — a los 6 meses del repo
5. ASSETS / CLEI 2027                              — con tiempo de sobra para preparar
```

## 6. Checklist final de protección del ingeniero

- [ ] El sistema se describe SIEMPRE como prototipo de investigación / AAC,
      nunca como diagnóstico o tratamiento (protección INVIMA).
- [ ] Licencia MIT o Apache-2.0 aplicada antes de publicar el código.
- [ ] Historial de git limpio de datos sensibles antes de hacer el repo
      público.
- [ ] Versión exacta (`git tag`) referenciada en cualquier artículo.
- [ ] Ninguna cesión total de copyright firmada sin leerla — preferir
      CC-BY.
- [ ] Revista/venue verificada en DOAJ o de reputación conocida antes de
      enviar (evitar depredadoras).
- [ ] Disclaimer de "no es dispositivo médico" visible en README y en
      cualquier demo pública.
