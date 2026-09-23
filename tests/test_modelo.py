"""Tests de humo del clasificador k-NN + DTW (src/modelo.py).

No usan datos reales de YP — solo secuencias sintéticas — para poder
correr en cualquier máquina y en CI sin depender de datos privados
excluidos del repositorio.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from modelo import ClasificadorPalabras, distancia_dtw  # noqa: E402


def _secuencia_aleatoria(rng: np.random.Generator, largo: int = 20, dim: int = 13):
    return rng.standard_normal((largo, dim))


def test_dtw_no_negativa_y_simetrica():
    """DTW debe ser no-negativa y aproximadamente simétrica."""
    rng = np.random.default_rng(0)
    a = _secuencia_aleatoria(rng, 20)
    b = _secuencia_aleatoria(rng, 15)

    dist_ab = distancia_dtw(a, b)
    dist_ba = distancia_dtw(b, a)

    assert dist_ab >= 0
    assert abs(dist_ab - dist_ba) < 1e-6


def test_dtw_distancia_cero_para_secuencia_identica():
    """La distancia de una secuencia consigo misma debe ser cero."""
    rng = np.random.default_rng(1)
    a = _secuencia_aleatoria(rng, 20)
    assert distancia_dtw(a, a) == pytest.approx(0.0, abs=1e-9)


def test_clasificador_predice_la_clase_mas_cercana():
    """Con dos clústeres bien separados, el k-NN debe acertar la clase."""
    rng = np.random.default_rng(2)
    base_a = np.full((20, 13), 0.0)
    base_b = np.full((20, 13), 10.0)

    secuencias = [base_a + rng.standard_normal((20, 13)) * 0.05 for _ in range(5)]
    secuencias += [base_b + rng.standard_normal((20, 13)) * 0.05 for _ in range(5)]
    etiquetas = ["a"] * 5 + ["b"] * 5

    clf = ClasificadorPalabras(k=3)
    clf.entrenar(secuencias, etiquetas)

    prueba = base_a + rng.standard_normal((20, 13)) * 0.05
    prediccion, confianza = clf.predecir(prueba)

    assert prediccion == "a"
    assert 0.0 < confianza <= 1.0


def test_loocv_supera_el_azar_en_clases_bien_separadas():
    """LOOCV sobre clases claramente separables debe superar ampliamente
    el azar (1/n_clases), sin exigir un umbral irreal de exactitud."""
    rng = np.random.default_rng(3)
    base_a = np.full((20, 13), 0.0)
    base_b = np.full((20, 13), 10.0)

    secuencias = [base_a + rng.standard_normal((20, 13)) * 0.05 for _ in range(8)]
    secuencias += [base_b + rng.standard_normal((20, 13)) * 0.05 for _ in range(8)]
    etiquetas = ["a"] * 8 + ["b"] * 8

    clf = ClasificadorPalabras(k=3)
    clf.entrenar(secuencias, etiquetas)
    metricas = clf.evaluar_loocv()

    assert metricas["exactitud_global"] > 0.7
    assert metricas["total_muestras"] == 16


def test_entrenar_valida_igual_tamano():
    """entrenar() debe rechazar listas de tamaños distintos, no fallar
    en silencio ni más adelante en predecir()."""
    clf = ClasificadorPalabras()
    with pytest.raises(ValueError):
        clf.entrenar([np.zeros((5, 13))], ["a", "b"])


def test_predecir_sin_entrenar_lanza_error_claro():
    """predecir() sin referencias debe fallar con un mensaje claro, no
    con un error críptico de numpy."""
    clf = ClasificadorPalabras()
    with pytest.raises(RuntimeError):
        clf.predecir(np.zeros((5, 13)))


def test_loocv_agrupado_excluye_duplicados_del_mismo_grupo():
    """Si una muestra tiene un "hermano" casi idéntico en su mismo grupo
    (p. ej. una copia aumentada de la misma grabación) pero las demás
    clases están mezcladas al azar, evaluar_loocv() simple debe acertar
    por fuga de información (el duplicado sigue en el set de
    entrenamiento), mientras que evaluar_loocv_agrupado() -que excluye
    el grupo completo- debe fallar sistemáticamente en ese caso, porque
    sin su duplicado ni patrón real que aprender, el ruido puro no
    ofrece señal de clase.

    Esto reproduce, de forma controlada y sin datos reales, el bug de
    fuga (claves de grupo que nunca coincidían) que se encontró y
    corrigió al validar el aumento de datos con datos reales de YP."""
    rng = np.random.default_rng(4)
    ruido_a = rng.standard_normal((20, 13))
    ruido_b = rng.standard_normal((20, 13))

    secuencias = [ruido_a, ruido_a + rng.standard_normal((20, 13)) * 0.001,
                 ruido_b, ruido_b + rng.standard_normal((20, 13)) * 0.001]
    etiquetas = ["a", "a", "b", "b"]
    grupos = ["g_a", "g_a", "g_b", "g_b"]

    clf = ClasificadorPalabras(k=1)
    clf.entrenar(secuencias, etiquetas)

    simple = clf.evaluar_loocv()
    assert simple["exactitud_global"] == pytest.approx(1.0)

    evaluables = [True, False, True, False]
    agrupado = clf.evaluar_loocv_agrupado(grupos, evaluables)
    assert agrupado["total_muestras_evaluadas"] == 2
    assert agrupado["exactitud_global"] < 1.0
