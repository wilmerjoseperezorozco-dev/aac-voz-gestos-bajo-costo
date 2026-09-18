"""Tests de la matemática de persecución con la mirada (solo numpy)."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from mirada_modelo import (ajustar_ridge, metricas_persecucion,  # noqa: E402
                           predecir, puntos_calibracion, retardo_ms,
                           trayectoria_auto)

PANTALLA = (1920, 1080)


def test_ridge_recupera_mapeo_lineal_conocido():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(300, 5))
    W = rng.normal(size=(5, 2))
    Y = X @ W + np.array([100.0, -50.0])
    modelo = ajustar_ridge(X, Y, lam=1e-6)
    X_nuevo = rng.normal(size=(50, 5))
    esperado = X_nuevo @ W + np.array([100.0, -50.0])
    assert np.abs(predecir(modelo, X_nuevo) - esperado).max() < 1e-3


def test_retardo_detecta_desfase_conocido():
    t = np.arange(0, 20, 1 / 30)
    blanco = np.sin(2 * np.pi * t / 8)
    k = 6  # 200 ms a 30 fps
    pred = np.concatenate([np.full(k, blanco[0]), blanco[:-k]])
    assert abs(retardo_ms(pred, blanco, t) - 200.0) < 40.0


def test_metricas_persecucion_perfecta_y_ruidosa():
    t = np.arange(0, 20, 1 / 30)
    blanco = trayectoria_auto(t, PANTALLA)
    perfecta = metricas_persecucion(t, blanco, blanco.copy(), PANTALLA)
    assert perfecta["rmse_px"] < 1e-6
    assert perfecta["r_x"] > 0.999 and perfecta["mejora_vs_constante"] > 0.999

    rng = np.random.default_rng(1)
    ruidosa = blanco + rng.normal(0, 400, blanco.shape)
    m = metricas_persecucion(t, blanco, ruidosa, PANTALLA)
    assert m["rmse_px"] > 100 and m["r_x"] < perfecta["r_x"]


def test_puntos_calibracion_son_nueve_dentro_de_pantalla():
    pts = puntos_calibracion(PANTALLA)
    assert len(pts) == 9
    assert all(0 < x < PANTALLA[0] and 0 < y < PANTALLA[1] for x, y in pts)


def test_rasgos_mirada_15_valores_y_none_si_parpadea():
    from types import SimpleNamespace

    from mirada_modelo import BLEND_MIRADA, BLEND_PARPADEO, rasgos_mirada

    lm = [SimpleNamespace(x=0.5, y=0.5) for _ in range(478)]
    lm[33], lm[133] = SimpleNamespace(x=0.4, y=0.5), SimpleNamespace(x=0.5, y=0.5)
    lm[468] = SimpleNamespace(x=0.45, y=0.5)          # iris a mitad del ojo
    abierto = {n: 0.0 for n in BLEND_MIRADA + BLEND_PARPADEO}
    v = rasgos_mirada(lm, abierto)
    assert v.shape == (15,) and abs(v[0] - 0.5) < 1e-6
    cerrado = {**abierto, "eyeBlinkLeft": 0.9, "eyeBlinkRight": 0.9}
    assert rasgos_mirada(lm, cerrado) is None
