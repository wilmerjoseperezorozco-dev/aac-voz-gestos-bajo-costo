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


def _rotacion(yaw, pitch, roll):
    y, p, r = np.radians([yaw, pitch, roll])
    rx = np.array([[1, 0, 0], [0, np.cos(p), -np.sin(p)], [0, np.sin(p), np.cos(p)]])
    ry = np.array([[np.cos(y), 0, np.sin(y)], [0, 1, 0], [-np.sin(y), 0, np.cos(y)]])
    rz = np.array([[np.cos(r), -np.sin(r), 0], [np.sin(r), np.cos(r), 0], [0, 0, 1]])
    return rz @ ry @ rx


def test_angulos_cabeza_recupera_angulos_conocidos_y_tolera_escala():
    from mirada_modelo import angulos_cabeza

    for yaw, pitch, roll in [(20, -10, 5), (-30, 15, -8), (0, 0, 0), (45, 25, 10)]:
        R = 1.7 * _rotacion(yaw, pitch, roll)      # con escala, como MediaPipe
        got = angulos_cabeza(R)
        assert np.allclose(got, (yaw, pitch, roll), atol=1e-6)


def test_rasgos_cabeza_6_valores():
    from types import SimpleNamespace

    from mirada_modelo import rasgos_cabeza

    lm = [SimpleNamespace(x=0.5, y=0.5) for _ in range(478)]
    v = rasgos_cabeza(lm, np.eye(4))
    assert v.shape == (6,) and np.allclose(v[:3], 0.0)


def test_error_lopo_bajo_si_la_calibracion_generaliza_y_alto_si_es_ruido():
    from mirada_modelo import error_calibracion_lopo, puntos_calibracion

    rng = np.random.default_rng(3)
    pts = np.array(puntos_calibracion(PANTALLA))
    Y = np.repeat(pts, 40, axis=0)
    X_bueno = np.hstack([Y / 1000.0, rng.normal(0, 0.01, (len(Y), 2))])
    X_ruido = rng.normal(size=(len(Y), 4))
    assert error_calibracion_lopo(X_bueno, Y) < 0.25 * error_calibracion_lopo(X_ruido, Y)


def test_error_cv_bloques_bajo_con_relacion_estable_y_alto_con_ruido():
    from mirada_modelo import error_cv_bloques

    rng = np.random.default_rng(8)
    tt = np.arange(0, 20, 1 / 30)
    Y = trayectoria_auto(tt, PANTALLA)
    X_bueno = np.column_stack([-(Y[:, 0] - 960) / 40.0, (Y[:, 1] - 540) / 40.0])         + rng.normal(0, 0.2, (len(tt), 2))
    X_ruido = rng.normal(size=(len(tt), 2))
    assert error_cv_bloques(X_bueno, Y) < 0.3 * error_cv_bloques(X_ruido, Y)
