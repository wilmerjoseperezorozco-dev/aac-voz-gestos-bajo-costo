"""Matemática de la prueba de persecución con la mirada (solo numpy).

Flujo: se calibra una regresión ridge rasgos-oculares -> posición en
pantalla con 9 puntos fijos, y luego se evalúa en una tarea distinta
(un blanco que se mueve suave): la calibración NO ve los datos de la
persecución, así que las métricas son de generalización, no de ajuste.
"""

from __future__ import annotations

import itertools

import numpy as np

# Índices de la malla facial de 478 puntos (MediaPipe Face Landmarker).
IRIS_A, ESQ_EXT_A, ESQ_INT_A, PARP_SUP_A, PARP_INF_A = 468, 33, 133, 159, 145
IRIS_B, ESQ_INT_B, ESQ_EXT_B, PARP_SUP_B, PARP_INF_B = 473, 362, 263, 386, 374
NARIZ, MEJILLA_A, MEJILLA_B = 1, 234, 454

# Blendshapes de mirada que se agregan como rasgos (8) y de parpadeo (2).
BLEND_MIRADA = [
    "eyeLookInLeft", "eyeLookInRight", "eyeLookOutLeft", "eyeLookOutRight",
    "eyeLookUpLeft", "eyeLookUpRight", "eyeLookDownLeft", "eyeLookDownRight",
]
BLEND_PARPADEO = ["eyeBlinkLeft", "eyeBlinkRight"]
UMBRAL_PARPADEO = 0.5


def _razon(valor: float, a: float, b: float) -> float:
    return (valor - a) / (b - a + 1e-9)


def rasgos_mirada(lm, blend: dict[str, float]) -> np.ndarray | None:
    """Vector de 15 rasgos de un frame, o None si está parpadeando.

    lm: lista de 478 landmarks con .x/.y; blend: nombre -> score."""
    if np.mean([blend[n] for n in BLEND_PARPADEO]) > UMBRAL_PARPADEO:
        return None
    x_a = _razon(lm[IRIS_A].x, lm[ESQ_EXT_A].x, lm[ESQ_INT_A].x)
    x_b = _razon(lm[IRIS_B].x, lm[ESQ_INT_B].x, lm[ESQ_EXT_B].x)
    y_a = _razon(lm[IRIS_A].y, lm[PARP_SUP_A].y, lm[PARP_INF_A].y)
    y_b = _razon(lm[IRIS_B].y, lm[PARP_SUP_B].y, lm[PARP_INF_B].y)
    giro = _razon(lm[NARIZ].x, lm[MEJILLA_A].x, lm[MEJILLA_B].x)
    return np.array([x_a, x_b, y_a, y_b, lm[NARIZ].x, lm[NARIZ].y, giro]
                    + [blend[n] for n in BLEND_MIRADA])


def ajustar_ridge(X: np.ndarray, Y: np.ndarray, lam: float = 1e-2):
    """Regresión ridge con sesgo. Devuelve (pesos, media, desviación)."""
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Z = np.hstack([(X - mu) / sd, np.ones((len(X), 1))])
    reg = lam * np.eye(Z.shape[1])
    reg[-1, -1] = 0.0  # el sesgo no se penaliza
    pesos = np.linalg.solve(Z.T @ Z + reg, Z.T @ Y)
    return pesos, mu, sd


def predecir(modelo, X: np.ndarray) -> np.ndarray:
    pesos, mu, sd = modelo
    Z = np.hstack([(X - mu) / sd, np.ones((len(X), 1))])
    return Z @ pesos


def _pearson(a: np.ndarray, b: np.ndarray) -> float:
    if a.std() < 1e-9 or b.std() < 1e-9:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def retardo_ms(pred: np.ndarray, blanco: np.ndarray, t: np.ndarray,
               max_seg: float = 1.0) -> float:
    """Retardo (ms) de la mirada respecto al blanco: desplazamiento de la
    predicción que maximiza la correlación. Positivo = la mirada llega
    después del blanco (lo esperable en persecución)."""
    dt = float(np.median(np.diff(t)))
    max_k = int(max_seg / dt)
    mejor_k, mejor_r = 0, -np.inf
    for k in range(-max_k, max_k + 1):
        if k >= 0:
            a, b = pred[k:], blanco[:len(blanco) - k]
        else:
            a, b = pred[:k], blanco[-k:]
        if len(a) < 10:
            continue
        r = _pearson(a, b)
        if not np.isnan(r) and r > mejor_r:
            mejor_r, mejor_k = r, k
    return mejor_k * dt * 1000.0


def metricas_persecucion(t: np.ndarray, blanco: np.ndarray,
                         pred: np.ndarray, pantalla: tuple[int, int],
                         max_retardo_s: float = 1.0) -> dict:
    """Métricas de la persecución. blanco y pred: (n, 2) en píxeles."""
    ancho, alto = pantalla
    diagonal = float(np.hypot(ancho, alto))
    error = np.linalg.norm(pred - blanco, axis=1)
    rmse = float(np.sqrt(np.mean(error ** 2)))
    # Línea base: predecir siempre el centro de trayectoria del blanco.
    rmse_const = float(np.sqrt(np.mean(
        np.sum((blanco - blanco.mean(0)) ** 2, axis=1))))
    return {
        "n_frames": int(len(t)),
        "rmse_px": rmse,
        "rmse_pct_diagonal": 100.0 * rmse / diagonal,
        "rmse_linea_base_px": rmse_const,
        "mejora_vs_constante": 1.0 - rmse / (rmse_const + 1e-9),
        "r_x": _pearson(pred[:, 0], blanco[:, 0]),
        "r_y": _pearson(pred[:, 1], blanco[:, 1]),
        "retardo_x_ms": retardo_ms(pred[:, 0], blanco[:, 0], t, max_retardo_s),
        "retardo_y_ms": retardo_ms(pred[:, 1], blanco[:, 1], t, max_retardo_s),
    }


def trayectoria_auto(t: np.ndarray, pantalla: tuple[int, int],
                     periodo_x: float = 8.0, periodo_y: float = 12.0):
    """Blanco automático suave (Lissajous lento), en píxeles."""
    ancho, alto = pantalla
    x = ancho / 2 + 0.38 * ancho * np.sin(2 * np.pi * t / periodo_x)
    y = alto / 2 + 0.34 * alto * np.sin(2 * np.pi * t / periodo_y + 0.6)
    return np.stack([x, y], axis=1)


def puntos_calibracion(pantalla: tuple[int, int], margen: float = 0.1):
    """Rejilla 3x3 de puntos fijos (píxeles), en orden de lectura."""
    ancho, alto = pantalla
    xs = [margen * ancho, 0.5 * ancho, (1 - margen) * ancho]
    ys = [margen * alto, 0.5 * alto, (1 - margen) * alto]
    return [(x, y) for y in ys for x in xs]


def suavizar(pred: np.ndarray, k: int = 5) -> np.ndarray:
    """Media móvil centrada de k frames por columna (bordes replicados)."""
    if k <= 1 or len(pred) < k:
        return pred
    relleno = np.pad(pred, ((k // 2, k - 1 - k // 2), (0, 0)), mode="edge")
    nucleo = np.ones(k) / k
    return np.stack([np.convolve(relleno[:, j], nucleo, mode="valid")
                     for j in range(pred.shape[1])], axis=1)


# --------------------------------------------------------------------------
# Puntero con la cabeza (canal alternativo cuando mover los ojos es difícil)
# --------------------------------------------------------------------------

def angulos_cabeza(R: np.ndarray) -> tuple[float, float, float]:
    """(yaw, pitch, roll) en grados de una matriz de rotación 3x3, con la
    convención R = Rz(roll) @ Ry(yaw) @ Rx(pitch). Normaliza las columnas
    para tolerar la escala que trae la matriz de MediaPipe."""
    R = np.asarray(R, dtype=float)[:3, :3]
    R = R / (np.linalg.norm(R, axis=0) + 1e-12)
    yaw = np.degrees(np.arcsin(np.clip(-R[2, 0], -1.0, 1.0)))
    pitch = np.degrees(np.arctan2(R[2, 1], R[2, 2]))
    roll = np.degrees(np.arctan2(R[1, 0], R[0, 0]))
    return float(yaw), float(pitch), float(roll)


def rasgos_cabeza(lm, matriz: np.ndarray) -> np.ndarray:
    """Vector de 6 rasgos de cabeza: yaw, pitch, roll (grados), posición de
    la nariz (x, y) y razón de giro entre mejillas."""
    yaw, pitch, roll = angulos_cabeza(matriz)
    giro = _razon(lm[NARIZ].x, lm[MEJILLA_A].x, lm[MEJILLA_B].x)
    return np.array([yaw, pitch, roll, lm[NARIZ].x, lm[NARIZ].y, giro])


def error_calibracion_lopo(X: np.ndarray, Y: np.ndarray,
                           lam: float = 1e-2) -> float:
    """Error medio (px) de la calibración dejando cada punto fuera. Es una
    medida conservadora (los puntos de las esquinas se extrapolan) pensada
    para comparar sesiones entre sí, no como error absoluto de uso."""
    puntos = np.unique(np.round(Y, 0), axis=0)
    errores = []
    for p in puntos:
        fuera = np.all(np.round(Y, 0) == p, axis=1)
        if fuera.all() or not fuera.any():
            continue
        modelo = ajustar_ridge(X[~fuera], Y[~fuera], lam)
        errores.append(np.linalg.norm(predecir(modelo, X[fuera]) - Y[fuera],
                                      axis=1).mean())
    return float(np.mean(errores)) if errores else float("nan")


# --------------------------------------------------------------------------
# Calibración robusta: ventana más estable y descarte de puntos inconsistentes
# --------------------------------------------------------------------------

def _mascara_puntos(Y: np.ndarray, puntos) -> np.ndarray:
    claves = np.round(Y, 0)
    mascara = np.zeros(len(Y), dtype=bool)
    for p in puntos:
        mascara |= np.all(claves == np.array(p), axis=1)
    return mascara


def _rmse(modelo, X: np.ndarray, Y: np.ndarray) -> float:
    return float(np.sqrt(np.mean(
        np.linalg.norm(predecir(modelo, X) - Y, axis=1) ** 2)))


def ajustar_robusto(X: np.ndarray, Y: np.ndarray, lam: float = 1e-2,
                    max_excluir: int = 2, factor_atipico: float = 3.0,
                    mejora_minima: float = 0.7):
    """Ajusta el ridge probando qué subconjunto de puntos de calibración es
    más consistente (se busca entre todos los que quitan hasta
    `max_excluir` puntos; nunca quedan menos de 5). Un descarte se acepta
    solo si (a) el error de los puntos que se quedan baja a <= mejora_minima
    x el del ajuste con todos y (b) los puntos quitados quedan >=
    factor_atipico veces peor que los que se quedan bajo ese ajuste: es
    decir, si son claramente atípicos y no simple ruido.

    Solo usa datos de calibración (nunca la persecución).
    Devuelve (modelo, puntos_excluidos, mascara_de_frames_usados)."""
    claves = np.round(Y, 0)
    puntos = [tuple(float(v) for v in p) for p in np.unique(claves, axis=0)]
    todos = ajustar_ridge(X, Y, lam)
    base = _rmse(todos, X, Y)
    mejor = (todos, [], np.ones(len(X), dtype=bool))
    for d in range(min(max_excluir, len(puntos) - 5), 0, -1):
        candidato = None
        for fuera in itertools.combinations(puntos, d):
            quitar = _mascara_puntos(Y, fuera)
            modelo = ajustar_ridge(X[~quitar], Y[~quitar], lam)
            dentro = _rmse(modelo, X[~quitar], Y[~quitar])
            afuera = _rmse(modelo, X[quitar], Y[quitar])
            if candidato is None or dentro < candidato[0]:
                candidato = (dentro, afuera, modelo, list(fuera), ~quitar)
        dentro, afuera, modelo, fuera, mascara = candidato
        if (dentro <= mejora_minima * base
                and afuera >= factor_atipico * max(dentro, 1e-9)):
            return modelo, fuera, mascara
    return mejor


def ventana_mas_estable(frames: np.ndarray, columnas: list[int],
                        n_ventana: int) -> tuple[np.ndarray, float]:
    """Elige, dentro de la captura de un punto, la ventana de n_ventana
    frames con menor variación de los rasgos `columnas` (posición estable
    de la cabeza/ojos). Solo mira estabilidad, nunca la posición del
    blanco. Devuelve (frames_elegidos, desviación_media)."""
    if len(frames) == 0:
        return frames, float("nan")
    if len(frames) <= n_ventana:
        return frames, float(frames[:, columnas].std(axis=0).mean())
    mejor, mejor_sd = 0, np.inf
    for i in range(len(frames) - n_ventana + 1):
        sd = float(frames[i:i + n_ventana][:, columnas].std(axis=0).mean())
        if sd < mejor_sd:
            mejor, mejor_sd = i, sd
    return frames[mejor:mejor + n_ventana], mejor_sd
