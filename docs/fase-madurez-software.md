# Fase de madurez del software — evaluación TRL y ruta hacia rigurosidad científica

Este documento evalúa el nivel de madurez tecnológica del sistema según
el marco estándar de la industria y la academia, y define la ruta
concreta para llevar el software de prototipo de investigación a una
fase madura, citable y auditable.

## 1. Marco de referencia: Technology Readiness Levels (TRL)

El marco TRL (NASA, adoptado por la Unión Europea y por el marco
MLTRL para sistemas de aprendizaje automático, Lavin et al., *Nature
Communications* 2022) clasifica la madurez tecnológica en 9 niveles:
TRL 1-3 corresponden a investigación básica y prueba de concepto,
TRL 4-6 a validación y demostración en entornos relevantes, y TRL 7-9 a
despliegue operacional.

## 2. Evaluación honesta del estado actual: TRL 5-6

| Criterio | Evidencia | Nivel |
|---|---|---|
| Prueba de concepto validada en laboratorio (TRL 4) | LOOCV 79.7% voz, 80% gestos con datos reales | Superado |
| Prototipo validado en entorno relevante (TRL 5) | 4 sesiones reales en el hogar de la participante, con protocolo de entorno estandarizado (Anexo B) | Superado |
| Demostración en entorno real con usuaria final (TRL 6) | Tablero de escaneo + expansión generativa usado por la participante con confirmación funcional (64.7-70.6% de oraciones confirmadas); hallazgos de uso real documentados | **Nivel actual** |
| Demostración en entorno operacional sostenido (TRL 7) | Requiere uso autónomo regular sin presencia del investigador, hardware dedicado (Raspberry Pi + pantalla táctil), y más participantes | Pendiente |

El sistema NO debe describirse por encima de TRL 6: no existe despliegue
operacional autónomo, la serie de casos es n=1, y no hay certificación de
ningún tipo (ver descargo INVIMA en el README).

## 3. Ruta hacia la fase madura — recomendaciones priorizadas

### Nivel A — Rigor de ingeniería (alcanzable de inmediato, sin costo)

1. **Suite de pruebas automatizadas versionada en el repositorio**: las
   pruebas de humo y regresión existen pero viven fuera del control de
   versiones; migrarlas a `tests/` con `pytest` y ejecutarlas antes de
   cada publicación. Meta: cobertura de las rutas críticas
   (extracción MFCC, DTW, clasificador, salvaguarda anti-alucinación).
2. **Integración continua (GitHub Actions)**: ejecutar la suite en cada
   push. Es el estándar mínimo que revisores de JOSS y ASSETS esperan.
3. **Versionado semántico disciplinado con DOI por versión**: ya iniciado
   (v0.1.0, DOI 10.5281/zenodo.21314646); cada hito funcional debe
   producir un release etiquetado — Zenodo archiva cada uno
   automáticamente.
4. **Registro estructurado (logging) en lugar de impresiones sueltas**,
   con niveles y archivo rotativo: precondición para diagnosticar fallos
   en uso no supervisado.

### Nivel B — Rigor científico (semanas, en paralelo con el aval de ética)

5. **Congelar una "versión de estudio"**: etiquetar la versión exacta del
   software con la que se recolectan los datos del artículo, y no
   modificarla durante la recolección — separa el desarrollo de la
   evaluación (requisito de reproducibilidad).
6. **Instrumentación de métricas fonoaudiológicas** (ver
   `metricas-fonoaudiologicas.md`): registrar tiempo de inicio de
   selección para calcular palabras/minuto; el resto ya es calculable.
7. **Formalizar el pipeline de evaluación**: un solo comando que
   reproduzca todas las métricas del artículo desde los registros crudos
   (los revisores lo valoran como evidencia de reproducibilidad).

### Nivel C — Madurez de producto asistivo (meses, tras el aval)

8. **Hardware dedicado**: migración a Raspberry Pi 5 + pantalla táctil
   (ya planificada en `propuesta-expansion.md`) — condición necesaria
   para TRL 7 (uso operacional sin el computador del investigador).
9. **Pictogramas ARASAAC cacheados sin conexión** en reemplazo de emoji:
   estándar de facto en AAC hispanohablante, mejora la validez ecológica.
10. **Accesibilidad formal**: auditoría contra WCAG 2.2 (tamaños de
    blanco táctil, contraste, tiempos ajustables) — el estándar citable
    en accesibilidad de interfaces.
11. **Estudio de usabilidad estructurado** (ISO 9241-11: eficacia,
    eficiencia, satisfacción) con la serie de casos ampliada — la
    evidencia que separa un prototipo demostrado de una tecnología
    asistiva evaluada.

## 4. Lo que NO corresponde todavía

- Certificación de dispositivo médico (IEC 62304 / registro INVIMA): solo
  aplicaría si el propósito declarado cambiara a diagnóstico, monitoreo o
  tratamiento — el proyecto declara explícitamente lo contrario.
- Escalamiento comercial: precede al aval de ética, la serie de casos y
  la publicación (ver `ruta-financiera-posicionamiento.md`).

## Referencias

- NASA, Technology Readiness Levels: nasa.gov/directorates/somd/space-communications-navigation-program/technology-readiness-levels
- Lavin, A. et al. (2022). Technology readiness levels for machine
  learning systems. *Nature Communications* 13, 6039.
- Soto, G. & Cooper, B. (2021). An early Spanish vocabulary for children
  who use AAC. *Augmentative and Alternative Communication*,
  doi:10.1080/07434618.2021.1881822 (base del vocabulario núcleo Fase 2).
