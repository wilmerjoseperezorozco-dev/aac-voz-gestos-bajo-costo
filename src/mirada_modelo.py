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


def error_cv_bloques(X: np.ndarray, Y: np.ndarray, k: int = 4,
                     lam: float = 1e-2) -> float:
    """Error medio (px) de una validación cruzada en k bloques CONTIGUOS de
    tiempo: cada bloque se predice con un modelo ajustado con los demás.
    Mide qué tan bien generaliza una calibración hecha con seguimiento."""
    n = len(X)
    if n < 4 * k:
        return float("nan")
    limites = np.linspace(0, n, k + 1).astype(int)
    errores = []
    for i in range(k):
        fuera = np.zeros(n, dtype=bool)
        fuera[limites[i]:limites[i + 1]] = True
        modelo = ajustar_ridge(X[~fuera], Y[~fuera], lam)
        errores.append(np.linalg.norm(predecir(modelo, X[fuera]) - Y[fuera],
                                      axis=1).mean())
    return float(np.mean(errores))


# --------------------------------------------------------------------------
# Tipo de movimiento: ¿sigue el ritmo del blanco, o es otra cosa?
# --------------------------------------------------------------------------

def r2_armonico(t: np.ndarray, y: np.ndarray, periodo: float) -> float:
    """Fracción de la varianza de y explicada por una sinusoide del período
    del blanco (cualquier fase). ~1 si la señal sigue el ritmo del blanco;
    ~0 si no tiene nada que ver, sin depender de calibración, signo ni fase."""
    w = 2 * np.pi / periodo
    diseno = np.column_stack([np.sin(w * t), np.cos(w * t), np.ones_like(t)])
    coef, *_ = np.linalg.lstsq(diseno, y, rcond=None)
    return float(1 - (y - diseno @ coef).var() / (y.var() + 1e-12))


def resumen_movimiento(t: np.ndarray, y: np.ndarray,
                       salto_grados_s: float = 60.0) -> dict:
    """Descripción del movimiento de una señal angular: reparto de potencia
    por bandas de frecuencia, frecuencia dominante y velocidades. Un
    seguimiento voluntario suave se concentra por debajo de ~0.3 Hz con
    velocidades bajas; movimientos bruscos o irregulares llenan bandas más
    altas. Solo descriptivo: no distingue por sí solo el origen del movimiento."""
    fs = 1.0 / float(np.median(np.diff(t)))
    y0 = y - y.mean()
    potencia = np.abs(np.fft.rfft(y0 * np.hanning(len(y0)))) ** 2
    f = np.fft.rfftfreq(len(y0), 1 / fs)
    total = potencia[f > 0.02].sum() + 1e-12

    def fraccion(a: float, b: float) -> float:
        return float(potencia[(f >= a) & (f < b)].sum() / total)

    banda = (f > 0.02) & (f < 2)
    velocidad = np.abs(np.gradient(y, t))
    return {
        "frecuencia_pico_hz": float(f[banda][np.argmax(potencia[banda])]),
        "pot_menor_015hz": fraccion(0.02, 0.15),
        "pot_015_05hz": fraccion(0.15, 0.5),
        "pot_05_3hz": fraccion(0.5, 3.0),
        "vel_media": float(velocidad.mean()),
        "vel_p99": float(np.percentile(velocidad, 99)),
        "saltos": int((velocidad > salto_grados_s).sum()),
    }


# --------------------------------------------------------------------------
# Tarea de escalones: el blanco salta entre izquierda / centro / derecha y se
# sostiene. No necesita calibración: se compara la postura de la cabeza en
# los tramos "izquierda" contra los de "derecha".
# --------------------------------------------------------------------------

# Orden fijo (mismo para todas las sesiones, así son comparables): 4 veces
# izquierda, 4 derecha y 2 centro; nunca dos iguales seguidos.
SECUENCIA_ESCALONES = ["C", "I", "D", "I", "D", "C", "D", "I", "D", "I"]


def analizar_escalones(t: np.ndarray, y: np.ndarray, escalones: list,
                       hold_s: float, analiza_desde_s: float) -> dict:
    """escalones: lista de (t_inicio, lado) con lado 'I', 'C' o 'D'. De cada
    tramo se toma la media de y desde `analiza_desde_s` (para dejar tiempo de
    moverse) hasta el final del tramo. Compara los tramos I contra los D con
    una prueba de permutación exacta (sin supuestos de distribución; no
    depende del signo de los ejes ni de calibración).

    Con 4 tramos I y 4 D, la separación completa por azar tiene p = 2/70."""
    medias: dict[str, list[float]] = {"I": [], "C": [], "D": []}
    estabilidad = []
    for t0, lado in escalones:
        m = (t >= t0 + analiza_desde_s) & (t < t0 + hold_s)
        if m.sum() >= 5:
            medias[lado].append(float(y[m].mean()))
            estabilidad.append(float(y[m].std()))
    izq, der = np.array(medias["I"]), np.array(medias["D"])
    salida = {"n_izq": len(izq), "n_der": len(der), "n_centro": len(medias["C"]),
              "media_izq": float(izq.mean()) if len(izq) else float("nan"),
              "media_der": float(der.mean()) if len(der) else float("nan"),
              "media_centro": float(np.mean(medias["C"])) if medias["C"] else float("nan"),
              "estabilidad_media": float(np.mean(estabilidad)) if estabilidad else float("nan"),
              "diferencia": float("nan"), "d_cohen": float("nan"),
              "separacion_completa": False, "p_permutacion": float("nan")}
    if len(izq) < 2 or len(der) < 2:
        return salida
    todos = np.concatenate([izq, der])
    observada = abs(izq.mean() - der.mean())
    extremas = 0
    combos = list(itertools.combinations(range(len(todos)), len(izq)))
    for c in combos:
        resto = np.delete(todos, list(c))
        if abs(todos[list(c)].mean() - resto.mean()) >= observada - 1e-12:
            extremas += 1
    sd = float(np.sqrt((izq.var(ddof=1) + der.var(ddof=1)) / 2))
    salida.update(
        diferencia=float(izq.mean() - der.mean()),
        d_cohen=float(observada / sd) if sd > 1e-9 else float("inf"),
        separacion_completa=bool(izq.min() > der.max() or izq.max() < der.min()),
        p_permutacion=extremas / len(combos))
    return salida
