"""Analiza la sesión pareada pose + cara: ¿hay señal ocular por gesto?

Uso:  py -3.12 src/cara_analizar.py

Para cada gesto reporta, sobre las muestras de data_gestos_cara/:
  - tasa de detección de cara
  - parpadeos por muestra (cruces ascendentes de eyeBlink > 0.5)
  - apertura de párpado y desplazamiento de mirada (medias y desviaciones)
Y una prueba de discriminabilidad: clasificación 1-NN con LOOCV usando
SOLO rasgos oculares, con intervalo exacto de Clopper-Pearson, frente al
azar (1 / n_gestos). Es exploratorio: pocas muestras, una sola persona.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

if sys.stdout is not None and sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
DIR_DATOS = RAIZ / "data_gestos_cara"
UMBRAL_PARPADEO = 0.5

# Blendshapes oculares de MediaPipe (subconjunto que describe ojos/cejas).
CLAVES_OCULARES = [
    "eyeBlinkLeft", "eyeBlinkRight", "eyeWideLeft", "eyeWideRight",
    "eyeSquintLeft", "eyeSquintRight",
    "eyeLookInLeft", "eyeLookInRight", "eyeLookOutLeft", "eyeLookOutRight",
    "eyeLookUpLeft", "eyeLookUpRight", "eyeLookDownLeft", "eyeLookDownRight",
    "browInnerUp", "browDownLeft", "browDownRight",
]


def cargar():
    datos = {}
    for carpeta in sorted(p for p in DIR_DATOS.glob("*") if p.is_dir()):
        muestras = []
        for f in sorted(carpeta.glob("*.npz")):
            z = np.load(f, allow_pickle=False)
            muestras.append({"blend": z["blendshapes"], "ojos": z["ojos"],
                             "nombres": [str(n) for n in z["nombres_blendshapes"]]})
        if muestras:
            datos[carpeta.name] = muestras
    return datos


def parpadeos(serie: np.ndarray) -> int:
    ojo = serie[~np.isnan(serie)] > UMBRAL_PARPADEO
    return int(np.sum(ojo[1:] & ~ojo[:-1])) if len(ojo) > 1 else 0


def ratio_mirada(ojos: np.ndarray) -> np.ndarray:
    """Posición horizontal del iris entre las esquinas de cada ojo (0-1),
    promedio de ambos ojos. Cambia con la mirada Y con el giro de cabeza."""
    a = (ojos[:, 0] - ojos[:, 2]) / (ojos[:, 4] - ojos[:, 2] + 1e-9)
    b = (ojos[:, 6] - ojos[:, 8]) / (ojos[:, 10] - ojos[:, 8] + 1e-9)
    return (a + b) / 2


def rasgos_muestra(m) -> np.ndarray:
    idx = [m["nombres"].index(c) for c in CLAVES_OCULARES if c in m["nombres"]]
    b = m["blend"][:, idx]
    b = b[~np.isnan(b).any(axis=1)]
    if len(b) < 3:
        return np.full(len(idx) * 3 + 2, np.nan)
    r = ratio_mirada(m["ojos"])
    r = r[~np.isnan(r)]
    return np.concatenate([b.mean(0), b.std(0), b.max(0),
                           [r.mean(), r.std()]])


def clopper_pearson(k: int, n: int, alfa: float = 0.05):
    try:
        from scipy.stats import beta
    except ImportError:
        return None
    bajo = 0.0 if k == 0 else beta.ppf(alfa / 2, k, n - k + 1)
    alto = 1.0 if k == n else beta.ppf(1 - alfa / 2, k + 1, n - k)
    return bajo, alto


def loocv_1nn(X: np.ndarray, y: list[str]):
    mu, sd = X.mean(0), X.std(0) + 1e-9
    Z = (X - mu) / sd
    aciertos = 0
    for i in range(len(Z)):
        d = np.linalg.norm(Z - Z[i], axis=1)
        d[i] = np.inf
        aciertos += y[int(np.argmin(d))] == y[i]
    return aciertos, len(Z)


def main() -> None:
    datos = cargar()
    if not datos:
        print(f"No hay datos en {DIR_DATOS}. Graba antes con gestos_cara_grabar.py")
        return

    print("=" * 66)
    print("  SEÑALES OCULARES POR GESTO (sesión pareada pose + cara)")
    print("=" * 66)
    X, y = [], []
    for gesto, muestras in datos.items():
        det, parp, mir = [], [], []
        for m in muestras:
            nombres = m["nombres"]
            det.append(np.mean(~np.isnan(m["blend"][:, 0])))
            i_izq, i_der = nombres.index("eyeBlinkLeft"), nombres.index("eyeBlinkRight")
            parp.append(parpadeos(np.nanmean(m["blend"][:, [i_izq, i_der]], axis=1)))
            r = ratio_mirada(m["ojos"])
            mir.append(np.nanmean(r) if not np.all(np.isnan(r)) else np.nan)
            f = rasgos_muestra(m)
            if not np.isnan(f).any():
                X.append(f)
                y.append(gesto)
        print(f"\n▶ {gesto}  (n={len(muestras)})")
        print(f"   cara detectada: {np.mean(det):.0%} de los frames")
        print(f"   parpadeos/muestra: media {np.mean(parp):.2f}, máx {max(parp)}")
        print(f"   ratio de mirada (0-1): media {np.nanmean(mir):.3f} ± {np.nanstd(mir):.3f}")

    print("\n" + "-" * 66)
    clases = sorted(set(y))
    if len(clases) < 2 or len(y) < 6:
        print("Muy pocas muestras con cara válida para la prueba LOOCV.")
        return
    k, n = loocv_1nn(np.array(X), y)
    azar = 1 / len(clases)
    print(f"Prueba 1-NN LOOCV solo con rasgos oculares: {k}/{n} = {k / n:.1%}")
    ic = clopper_pearson(k, n)
    if ic:
        print(f"   IC 95% Clopper-Pearson: {ic[0]:.1%} – {ic[1]:.1%}")
        print(f"   Azar = {azar:.1%}. "
              + ("El IC excluye el azar: hay señal ocular." if ic[0] > azar
                 else "El IC incluye el azar: NO se puede afirmar señal ocular."))
    print("\nNota: 'no' implica giro de cabeza, que también mueve el iris en la")
    print("imagen. Una señal ocular aquí puede ser postura de cabeza, no mirada.")


if __name__ == "__main__":
    main()
