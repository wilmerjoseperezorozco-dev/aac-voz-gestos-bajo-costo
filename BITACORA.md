# Bitácora del proyecto

Registro cronológico de avances, en orden desde el día 1. Cada entrada
resume lo logrado y remite al informe técnico correspondiente en
`reportes/` cuando existe. Los datos personales de la participante
(alias YP) permanecen ocultos en todo el proyecto público, sin excepción.

---

**2026-07-06 — Día 1.** Pipeline completo funcionando: grabación →
MFCC + DTW → clasificador k-NN → voz sintetizada. Primer entrenamiento
con voz real de YP: 77.5% LOOCV (80 muestras, 8 palabras), con
depuración documentada de muestras.

**2026-07-07 — Canal de gestos.** Reconocimiento de 3 gestos con webcam
y MediaPipe Pose (mismo clasificador): 80% LOOCV. La palabra «no»,
inconsistente en voz, se resolvió con una vocalización alternativa
elegida por YP (30%→70%).

**2026-07-08 — Hallazgo de interferencia y validación en vivo.** La
captura simultánea de voz + gesto degrada ambos canales de ~80% a
30-37% (interferencia cognitivo-motora de doble tarea; intervalos de
confianza sin traslape). Rediseño a captura secuencial. La validación en
vivo reveló además que el sistema solo es confiable con consenso
unánime de vecinos (92-100% de acierto): la política de decisión se
corrigió a umbral 0.99. Repositorio público creado.

**2026-07-09 — Protocolo de evaluador ciego y arquitectura de dos
capas.** Tercera confirmación del patrón de consenso unánime (5/5).
Optimización del DTW (4.2× más rápido, exactitud idéntica). Vocabulario
de voz ampliado a 11 palabras (79.7% LOOCV). Se diseñó y validó la
arquitectura de dos capas: tablero de vocabulario núcleo (Capa 1) +
expansión generativa con modelo de lenguaje 100% local (Capa 2), con
hallazgo documentado sobre few-shot en modelos pequeños.

**2026-07-10 — Primera sesión real del tablero.** YP aprendió a
reconocer los primeros símbolos y construyó sus primeras oraciones. La
precisión confirmada subió de 37.5% a 70.6% dentro de la misma sesión
tras dos correcciones (selección directa por clic, escaneo más lento).
Hallazgo de alucinación del generador documentado; salvaguarda
automática implementada y validada contra los intentos reales.
Clasificador diagnóstico entrenado con datos reales (84% LOOCV,
reportado como diagnóstico por tamaño de muestra). Verificación
acústica de locutora única en el corpus. Release v0.1.0 archivado en
Zenodo con DOI 10.5281/zenodo.21314646.

**2026-07-14 — Sesión de consolidación.** Nueva validación en vivo de
voz: consenso unánime nuevamente 6/6 (100%). Vocabulario del tablero
ampliado a 35 símbolos con lote personalizado (animales de su entorno).
Mejora conductual observada: identificación de pronombres, comprensión
emergente de secuencia (mejor con 2 símbolos que con 3+), resiliencia
ante errores (reintenta hasta lograr el resultado esperado) y
comunicación contextual interpretada por la familia. Corregidos un
fallo de lanzamiento de los modos de consola y la reproducción
intermitente del audio generado (crítico: la participante no lee).

**2026-07-16 — Fase 2: núcleo universal completo.** Vocabulario del
tablero ampliado a 126 símbolos en 10 categorías, basado en la lista
validada por pares de Soto & Cooper (2021) para léxico inicial en
español (AAC), con curaduría de dignidad de edad para una usuaria
adulta. Tablero rediseñado con navegación por categorías y escaneo de
dos niveles (estándar AAC de group-item scanning). Salvaguarda
anti-alucinación generada automáticamente desde el vocabulario (119
conceptos cubiertos), validada por regresión contra los 45 intentos
reales etiquetados (73% de concordancia con la confirmación de la
participante). Vocabulario de captura de voz preparado para ampliarse
de 11 a 15 palabras. Evaluación de madurez tecnológica: TRL 5-6, con
ruta documentada hacia fase madura (`docs/fase-madurez-software.md`).
