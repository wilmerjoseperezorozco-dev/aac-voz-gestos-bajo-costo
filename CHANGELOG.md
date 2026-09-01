# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/),
versionado según [SemVer](https://semver.org/lang/es/).

## [0.2.0] — 2026-09-01

### Añadido
- Vocabulario núcleo del tablero ampliado a 126 símbolos en 10
  categorías, con base académica (Soto & Cooper, 2021), y escaneo de
  dos niveles (categoría → símbolo).
- Tablero de escaneo con layout horizontal sin scroll.
- Suite de tests automatizados (`tests/test_modelo.py`) sobre el
  clasificador k-NN + DTW, con integración continua en GitHub Actions
  en cada push/PR.
- Verificación visual de persona detectada en el canal de gestos:
  esqueleto dibujado en pantalla por persona, vista previa antes de
  grabar, ventana de cámara ampliada.
- Documentación de investigación: hallazgos científicos con
  estadística formal (interferencia cognitivo-motora, política de
  decisión por consenso), ruta de expansión a otras condiciones
  neurológicas, impacto económico y social con fuentes (OMS, Banco
  Mundial, DANE), plan de madurez open source a 12 meses.
- Gobernanza del repositorio: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
  plantillas de Issues, protección de la rama principal.
- Overview bilingüe (español/inglés) en el README, con la misma
  profundidad en ambos idiomas.
- Issues fijados de búsqueda de alianzas (fundaciones regionales y
  organizaciones especializadas por condición neurológica).

### Corregido
- Bug crítico: `sys.stdout.encoding` fallaba con `AttributeError` al
  ejecutar sin consola (`pythonw.exe`), rompiendo accesos directos de
  presentación/demo — corregido en 15 scripts.
- Reproducción de audio silenciosamente fallida en sesiones largas
  (reintento automático con motor de voz nuevo).
- Lanzadores `.bat` fijados a Python 3.12 explícito, blindados contra
  el conflicto de múltiples versiones de Python instaladas.

### Cambiado
- README reestructurado con tabla de estado del arte, hallazgos
  científicos visibles, e intervalos de confianza reales (antes:
  rangos aproximados).
- Reducción de lanzadores redundantes en la raíz del proyecto.

## [0.1.0] — 2026-07-11

Primer release público: pipeline de voz y gestos validado (k-NN + DTW
sobre MFCC y landmarks de postura), primera versión del tablero de
escaneo, licencia MIT, DOI de Zenodo.
