"""Clasificador de calidad de la oración generada, entrenado con datos
reales de uso (registros/predicciones_tablero.csv) en vez de reglas
escritas a mano -- la evolución natural de la salvaguarda de
generador_llm.py una vez hay suficientes sesiones reales con YP.

Honestidad metodológica: con pocos ejemplos etiquetados (hoy: ~25),
cualquier clasificador entrenado aquí es DIAGNÓSTICO, no un modelo listo
para producción -- reportar una sola partición train/test con este
tamaño de muestra sería engañoso. Se evalúa con LOOCV (el mismo estándar
ya usado en todo el proyecto para validar con pocos datos, ver
modelo.py) precisamente para no inflar la confianza. UMBRAL_DATOS_MINIMO
marca el punto a partir del cual este resultado empieza a ser confiable.

Uso (después de acumular sesiones reales con el tablero):
    python src/clasificador_calidad_oracion.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import numpy as np

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from generador_llm import _detectar_alucinacion  # noqa: E402

ARCHIVO_TABLERO = RAIZ / "registros" / "predicciones_tablero.csv"
UMBRAL_DATOS_MINIMO = 100  # por debajo de esto, el resultado es solo diagnóstico
PRONOMBRES_SIN_HUELLA_LEXICA = {"yo", "tu"}


def extraer_ejemplos() -> tuple[np.ndarray, np.ndarray]:
    """Lee predicciones_tablero.csv y devuelve (X, y) solo con los
    intentos que YP confirmó explícitamente como correctos o incorrectos."""
    if not ARCHIVO_TABLERO.exists():
        return np.empty((0, 4)), np.empty(0)

    with ARCHIVO_TABLERO.open(encoding="utf-8") as f:
        filas = list(csv.DictReader(f))

    X, y = [], []
    for fila in filas:
        confirmada = fila.get("confirmada", "").strip().lower()
        if confirmada not in ("si", "no"):
            continue
        simbolos = [s.strip() for s in fila["simbolos_seleccionados"].split("+")]
        oracion = fila["oracion_generada"]
        X.append(_extraer_caracteristicas(simbolos, oracion))
        y.append(1.0 if confirmada == "si" else 0.0)

    return np.array(X), np.array(y)


def _extraer_caracteristicas(simbolos: list[str], oracion: str) -> list[float]:
    from generador_llm import VARIANTES_CONCEPTO
    import re

    texto = oracion.lower()
    conceptos_verificables = [s for s in simbolos if s in VARIANTES_CONCEPTO]
    if conceptos_verificables:
        reflejados = sum(
            1 for c in conceptos_verificables
            if any(re.search(p, texto) for p in VARIANTES_CONCEPTO[c])
        )
        cobertura = reflejados / len(conceptos_verificables)
    else:
        cobertura = 1.0  # nada verificable (solo pronombres) -> no penaliza

    alucinacion = 1.0 if _detectar_alucinacion(simbolos, oracion) else 0.0
    n_simbolos = float(len(simbolos))
    n_palabras = float(len(oracion.split()))
    return [cobertura, alucinacion, n_simbolos, n_palabras]


def _sigmoide(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -30, 30)))


def _entrenar_regresion_logistica(X: np.ndarray, y: np.ndarray,
                                   tasa_aprendizaje: float = 0.1,
                                   iteraciones: int = 2000) -> tuple[np.ndarray, float]:
    """Regresión logística simple vía descenso de gradiente -- sin
    dependencias de ML pesadas (numpy puro), consistente con el resto
    del proyecto (ver modelo.py)."""
    medias, desviaciones = X.mean(axis=0), X.std(axis=0) + 1e-8
    X_norm = (X - medias) / desviaciones

    pesos = np.zeros(X.shape[1])
    sesgo = 0.0
    n = len(y)
    for _ in range(iteraciones):
        z = X_norm @ pesos + sesgo
        pred = _sigmoide(z)
        error = pred - y
        pesos -= tasa_aprendizaje * (X_norm.T @ error) / n
        sesgo -= tasa_aprendizaje * error.mean()
    return pesos, sesgo, medias, desviaciones  # type: ignore[return-value]


def _predecir(x: np.ndarray, pesos: np.ndarray, sesgo: float,
              medias: np.ndarray, desviaciones: np.ndarray) -> float:
    x_norm = (x - medias) / desviaciones
    return float(_sigmoide(x_norm @ pesos + sesgo))


def evaluar_loocv(X: np.ndarray, y: np.ndarray) -> float:
    """Exactitud vía leave-one-out cross-validation -- mismo estándar de
    validación ya usado en modelo.py para datasets pequeños."""
    aciertos = 0
    for i in range(len(y)):
        X_entreno = np.delete(X, i, axis=0)
        y_entreno = np.delete(y, i)
        pesos, sesgo, medias, desviaciones = _entrenar_regresion_logistica(X_entreno, y_entreno)
        prob = _predecir(X[i], pesos, sesgo, medias, desviaciones)
        prediccion = 1.0 if prob >= 0.5 else 0.0
        if prediccion == y[i]:
            aciertos += 1
    return aciertos / len(y)


def main() -> None:
    X, y = extraer_ejemplos()
    print(f"Ejemplos etiquetados disponibles: {len(y)}")

    if len(y) < 5:
        print("Muy pocos ejemplos para siquiera un diagnóstico LOOCV "
              "(se necesitan al menos 5). Sigue practicando con el tablero.")
        return

    exactitud = evaluar_loocv(X, y)
    print(f"Exactitud LOOCV: {exactitud:.1%}")

    if len(y) < UMBRAL_DATOS_MINIMO:
        print(f"\n⚠️  DIAGNÓSTICO, NO PRODUCCIÓN: con {len(y)} ejemplos "
              f"(umbral recomendado: {UMBRAL_DATOS_MINIMO}+), este resultado "
              "mide qué tan separables son las clases con las características "
              "actuales, no un modelo listo para reemplazar la salvaguarda "
              "de generador_llm.py todavía. Sigue acumulando sesiones reales.")
    else:
        print(f"\n{len(y)} ejemplos supera el umbral mínimo recomendado "
              f"({UMBRAL_DATOS_MINIMO}) -- resultado interpretable como "
              "estimación real de desempeño.")


if __name__ == "__main__":
    main()
