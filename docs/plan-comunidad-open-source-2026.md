# Plan de comunidad y madurez open source (2026-2027)

Documento de organización para llevar el proyecto de "prototipo funcionando"
a "software que cualquier familia o profesional pueda instalar y usar",
manteniendo autoría única y respetando la privacidad de la participante en
todo momento. Alineado con el cronograma que ya se presenta en la
convocatoria MAPFRE, para que ambos esfuerzos avancen juntos, no en
paralelo desconectado.

## 1. Principios (no negociables)

1. **YP nunca se identifica públicamente.** Se documentan metodología,
   código, métricas y hallazgos en abierto; nunca su nombre real, rostro,
   voz sin consentimiento explícito para ese uso puntual, ni datos
   biométricos crudos. Esto ya está protegido por el `.gitignore` del
   repositorio y se mantiene sin excepción.
2. **Autoría y control únicos.** El código es de uso libre bajo licencia
   MIT (cualquiera puede descargarlo, ejecutarlo y adaptarlo para sí
   mismo), pero el repositorio oficial tiene un solo mantenedor —
   Wilmer José Pérez Orozco. No se aceptan Pull Requests externos al
   repositorio oficial. Los Issues quedan abiertos como canal de
   sugerencias y reportes, pero la decisión de incorporar algo es siempre
   del mantenedor.
3. **Rigor antes que alcance.** Cada mejora de accesibilidad o
   instalación se valida primero, se documenta con evidencia, y solo
   entonces se publica — mismo estándar que se ha seguido desde el inicio.

## 2. Gobernanza del repositorio (a implementar)

- **`CONTRIBUTING.md`** nuevo: explica explícitamente la política de "uso
  libre, contribución cerrada" — evita que alguien invierta tiempo en un
  PR que no será aceptado, y explica el canal correcto (Issues) para
  sugerencias.
- **Plantillas de Issues** (`.github/ISSUE_TEMPLATE/`): una para
  "reportar un problema" y otra para "sugerir una mejora", para que las
  sugerencias lleguen ya estructuradas.
- **Protección de la rama principal** en GitHub (branch protection en
  `main`): exige que todo cambio pase por el mantenedor, aunque él mismo
  siga pudiendo hacer push directo si así lo prefiere — evita fusiones
  accidentales de terceros incluso si alguien lograra abrir un PR.
- **`CODE_OF_CONDUCT.md`** breve: estándar en proyectos open source
  serios, da una señal de profesionalismo ante revisores (incluyendo
  MAPFRE) sin implicar apertura a colaboración de código.

## 3. Guía de usuario (nueva, pendiente de redactar)

Objetivo: que una familia o un profesional de la salud sin conocimientos
técnicos pueda instalar y usar el sistema siguiendo el documento, sin
depender de que Wilmer esté presente.

Estructura propuesta (`GUIA_USUARIO.md`, en español, sin jerga técnica):
1. Qué es el sistema y para quién es (en lenguaje llano, sin tecnicismos).
2. Qué se necesita (computador, cámara, micrófono — requisitos mínimos
   reales, no idealizados).
3. Instalación paso a paso para Windows, con capturas de pantalla.
4. Primer uso: cómo grabar las primeras muestras de voz/gestos de la
   persona que va a usarlo.
5. Uso diario: cómo abrir el tablero, cómo confirmar una frase, qué hacer
   si algo no funciona (sección de solución de problemas).
6. Cómo pedir ayuda (enlace a Issues de GitHub, sin exponer datos
   personales al reportar un problema).

## 4. Facilidad de instalación para otras personas (roadmap técnico)

Estado actual: requiere Python 3.12 instalado manualmente y conocer la
terminal — barrera real para el usuario objetivo (familias, no
programadores).

Mejoras priorizadas:
1. **Instalador empaquetado** (`.exe` con PyInstaller o similar) que
   incluya Python y las dependencias — doble clic, sin terminal.
2. **Detección y guía automática de hardware** (cámara/micrófono no
   detectado → mensaje claro, no un traceback de Python).
3. **Configuración inicial guiada** (asistente de primer uso: nombre del
   perfil, grabación de las primeras palabras) en vez de editar
   `config.json` a mano.
4. **Empaquetado multiplataforma** (evaluar viabilidad en Linux/Raspberry
   Pi, relevante para el hardware dedicado de bajo costo ya planteado en
   la memoria MAPFRE).

## 5. Mejoras específicas para personas con discapacidad motora

> **Ya resuelto (2026-08-21):** verificación visual de qué persona está
> siguiendo la cámara en el canal de gestos — esqueleto dibujado en vivo,
> distinguiendo a la persona usuaria de cualquier cuidador presente en
> cuadro, con vista previa antes de grabar. Relevante para cualquier
> cuidador que use el sistema con otra persona, no solo para este caso —
> ver `RESEARCH_LOG.md` (2026-08-21) para el detalle técnico completo.


Más allá de lo ya construido (reconocimiento personalizado, tablero de
escaneo, expansión de frases), líneas concretas de mejora:

1. **Acceso por switch/pulsador único**: muchas personas con compromiso
   motor severo no pueden usar mouse ni tocar pantalla con precisión —
   soporte para escaneo automático con un solo botón físico es el
   estándar de accesibilidad en AAC (Tobii, Proloquo) y hoy no está
   implementado.
2. **Ajuste de velocidad de escaneo por persona**: la velocidad de
   escaneo del tablero debe ser configurable individualmente, no fija.
3. **Contraste y tamaño de icono ajustables**: WCAG 2.2 como estándar de
   referencia (ya recomendado en `fase-madurez-software.md`). **Auditoría
   de contraste ya realizada (2026-09):** los 7 pares de color usados en
   `tablero_escaneo.py` (categorías, selección, resaltado de escaneo,
   botones de confirmar/cancelar, texto secundario) pasan WCAG AA — el
   más ajustado es el verde de confirmación (`#2E7D32` sobre blanco,
   5.13:1, mínimo exigido 4.5:1). Pendiente real: el **tamaño** de
   icono/botón ajustable, que sí falta.
4. **Confirmación por vía redundante**: si el reconocimiento de voz falla
   por fatiga vocal (común en sesiones largas), poder confirmar por
   gesto o por el tablero sin perder el progreso de la frase.
5. **Modo de bajo esfuerzo motor**: reducir movimientos necesarios para
   completar una oración en los momentos de mayor fatiga, detectado por
   patrones de la propia sesión (más lento, más errores → simplificar).

## 6. Ruta ejecutable a 12 meses (software, en paralelo al cronograma MAPFRE)

| Mes | Entrega de software/comunidad |
|---|---|
| 1-2 | `CONTRIBUTING.md`, plantillas de Issues, `CODE_OF_CONDUCT.md`, protección de rama principal |
| 2-3 | Primera versión de `GUIA_USUARIO.md` con capturas reales |
| 3-5 | Instalador empaquetado para Windows (sin terminal) |
| 5-7 | Soporte de acceso por switch/pulsador único; velocidad de escaneo configurable |
| 7-9 | Contraste/tamaño ajustable (WCAG 2.2); confirmación por vía redundante |
| 9-10 | Piloto de instalación con un usuario externo real (primer caso fuera de YP), documentado como evidencia de usabilidad |
| 10-12 | Modo de bajo esfuerzo motor; consolidación de métricas de comunidad para el informe final MAPFRE |

Nota: esta ruta corre en paralelo al cronograma de investigación de la
memoria MAPFRE (ampliación de la serie de casos, indicadores clínicos) —
comparten el mismo periodo de 12 meses porque son parte del mismo
proyecto, no dos iniciativas separadas.

## 7. Qué se mide (para el informe final, alineado con la convocatoria)

- Métricas de comunidad: estrellas, forks, Issues abiertos/resueltos,
  descargas del instalador — evidencia de alcance real, no solo
  intención.
- Métrica de accesibilidad: cumplimiento WCAG 2.2 antes/después.
- Métrica de instalación: tiempo que le toma a una persona sin
  conocimientos técnicos instalar y hacer la primera grabación
  (cronometrado en el piloto del mes 9-10).
- Métricas ya definidas en la memoria MAPFRE (autonomía comunicativa,
  satisfacción, carga del cuidador) — sin duplicar, se referencian desde
  ahí.

## 8. Pendiente de decidir con Wilmer

- [ ] Nombre definitivo del instalador/release (¿mantiene el nombre del
      repo actual o se re-marca para el público general?).
- [ ] Si el piloto del mes 9-10 usa a un participante de la serie de
      casos ampliada de MAPFRE o a alguien completamente externo al
      estudio.
