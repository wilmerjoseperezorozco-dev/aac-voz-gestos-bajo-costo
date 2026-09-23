# Changelog

Formato basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/),
versionado según [SemVer](https://semver.org/lang/es/).

## [Sin publicar]

### Añadido
- Aumento de datos de voz por perturbación de señal (`aumento_datos_voz.py`):
  velocidad 0.9x/1.1x + ruido leve sobre grabaciones reales, con
  trazabilidad a su archivo original. Validación cruzada agrupada
  (`ClasificadorPalabras.evaluar_loocv_agrupado()` en `modelo.py`,
  usada por `entrenar_con_aumento.py`) que excluye del entrenamiento
  las copias sintéticas de la muestra evaluada, para no inflar la
  exactitud. Resultado real (no el que salió antes de corregir un bug
  de fuga, ver RESEARCH_LOG 2026-09-22): +1.6 puntos porcentuales.
- Canal facial exploratorio: captura pareada pose + cara con MediaPipe
  Face Landmarker (`gestos_cara_grabar.py`, `cara_analizar.py`) y sesión
  unificada `SESION_NUEVA_YP.bat` (voz y luego gestos + cara, en
  secuencia, nunca a la vez).
- Prueba de persecución con puntero (`persecucion_mirada.py`): calibración
  de 9 puntos + blanco móvil, con canal cabeza (por defecto) o mirada.
  Métricas: error, mejora frente a apuntar al centro, correlación,
  retardo. Matemática aparte y con tests (`mirada_modelo.py`).
- Monitor del operador (`monitor_operador.py`): ventana pequeña con los
  puntos capturados y avisos de luz, distancia, encuadre y fps.
- Métricas de entorno por sesión y tendencia entre sesiones
  (`mirada_progreso.py`); diagnóstico reproducible por sesión
  (`mirada_diagnostico.py`).
- Persecución con calibración por seguimiento: la primera mitad del
  seguimiento calibra la regresión (yaw + pitch en cabeza) y la segunda
  la evalúa sin que el modelo la haya visto. `--puntos` agrega 9 puntos
  quietos solo para comparar. Nuevas métricas: relación cruda con el
  blanco (sin calibración) y validación cruzada por bloques.
- Tarea de escalones con la cabeza (`escalones_cabeza.py`, lanzador 15): tres
  círculos (izquierda, centro, derecha), uno se ilumina y se sostiene; la
  persona gira hacia él. Sin calibración: prueba de permutación exacta de la
  postura (yaw) en los tramos izquierda contra derecha. Pensada como elección
  discreta ("girar y sostener"), más cercana a un gesto que un seguimiento.
- Diagnóstico de tipo de movimiento (ajuste al ritmo del blanco, bandas de
  frecuencia, giros bruscos) y `--nota` para dejar una observación por sesión.
- `--alias` para registrar sesiones de control aparte, el alias visible en
  la pantalla de inicio, y `lanzadores/14_Persecucion_Control.bat` (CTRL1).
- `grabar.py --nuevas N`: graba N muestras nuevas por palabra aunque ya
  se haya alcanzado el objetivo de `config.json`.

### Retirado
- Calibración robusta (ventana más estable + descarte de puntos atípicos):
  afinada con una sola sesión, mejoró esa y empeoró las dos siguientes.

### Corregido
- Las grabadoras terminaban sin capturar cuando las muestras existentes
  ya superaban el objetivo de `config.json`.
- Persecución: la ventana a pantalla completa tapaba la consola y el
  inicio parecía colgado; el blanco se dibujaba a la velocidad de la
  cámara y se veía a saltos (ahora hilo de cámara aparte y ~60 fps).

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
