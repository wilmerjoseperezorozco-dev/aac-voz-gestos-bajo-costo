"""Diagnóstico de una sesión de persecución con la mirada.

Uso:
    py -3.12 src/mirada_diagnostico.py                 # última sesión
    py -3.12 src/mirada_diagnostico.py ruta/al/archivo.npz

Separa tres preguntas que el resumen final mezcla:
  1. Fijaciones (calibración): ¿los rasgos del iris cambian con el punto
     que se mira? Es la prueba más limpia: el ojo está quieto.
  2. Cabeza: ¿cuánto se mueve la cabeza entre puntos frente al iris?
  3. Persecución: ¿algún modelo (más simple) le gana a "mirar al centro"?
Sirve también para el CONTROL POSITIVO: si una persona sin condición
motora obtiene una relación clara en (1), el sistema funciona y el
problema estaría en el protocolo o en la persona evaluada.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

if sys.stdout is not None and sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from mirada_modelo import (ajustar_ridge, metricas_persecucion,  # noqa: E402
                           predecir, suavizar, _pearson)


def rejilla(valores, puntos, y, fmt):
    for r in range(3):
        celdas = []
        for c in range(3):
            m = np.all(np.round(y) == puntos[r * 3 + c], axis=1)
            celdas.append(fmt(valores[m]))
        print("    " + "   ".join(celdas))


def main() -> None:
    if len(sys.argv) > 1:
        ruta = Path(sys.argv[1])
    else:
        archivos = sorted((RAIZ / "data_mirada").glob("persecucion_*.npz"))
        if not archivos:
            raise SystemExit("No hay sesiones en data_mirada/")
        ruta = archivos[-1]
    z = np.load(ruta)
    cal, per = z["calibracion"], z["persecucion"]
    pant = tuple(int(v) for v in z["pantalla"])
    Fc, Yc = cal[:, 3:], cal[:, 1:3]
    t, blanco, F = per[:, 0], per[:, 1:3], per[:, 3:]
    xi_c, yi_c = (Fc[:, 0] + Fc[:, 1]) / 2, (Fc[:, 2] + Fc[:, 3]) / 2
    print(f"Sesión: {ruta.name} | pantalla {pant} | calibración {len(cal)} frames "
          f"| persecución {len(per)} frames")

    print("\n[1] FIJACIONES — ¿el iris cambia con el punto mirado?")
    r_x, r_y = _pearson(xi_c, Yc[:, 0]), _pearson(yi_c, Yc[:, 1])
    print(f"    r(iris-x, punto-x) = {r_x:+.2f}   r(iris-y, punto-y) = {r_y:+.2f}")
    print("    (esperado si mira los puntos: |r| alto; en imagen sin espejo, iris-x")
    print("     baja cuando el punto está a la derecha, así que r-x sale NEGATIVA)")
    puntos = sorted({(round(a), round(b)) for a, b in Yc}, key=lambda p: (p[1], p[0]))
    print("    iris-x medio por punto (filas: arriba/centro/abajo; columnas: izq/centro/der):")
    rejilla(xi_c, puntos, Yc, lambda v: f"{v.mean():.3f}")

    print("\n[2] CABEZA — giro medio por punto (0.5 = de frente)")
    rejilla(Fc[:, 6], puntos, Yc, lambda v: f"{v.mean():.3f}")
    print(f"    desv. del giro entre puntos: {np.std([Fc[np.all(np.round(Yc) == p, axis=1), 6].mean() for p in puntos]):.3f}"
          f"  | desv. del iris-x entre puntos: {np.std([xi_c[np.all(np.round(Yc) == p, axis=1)].mean() for p in puntos]):.3f}")

    print("\n[3] PERSECUCIÓN — modelos simples contra 'mirar al centro'")
    def evalua(nombre, cols):
        mod = ajustar_ridge(Fc[:, cols], Yc)
        m = metricas_persecucion(t, blanco, suavizar(predecir(mod, F[:, cols]), 5), pant)
        print(f"    {nombre:30s} error {m['rmse_px']:4.0f} px ({m['rmse_pct_diagonal']:.0f}%)  "
              f"mejora vs centro {m['mejora_vs_constante']:+.0%}  "
              f"r_x={m['r_x']:+.2f} r_y={m['r_y']:+.2f}")
    evalua("todos los rasgos", list(range(15)))
    evalua("sin posición/giro de cabeza", [0, 1, 2, 3] + list(range(7, 15)))
    evalua("solo iris (4 rasgos)", [0, 1, 2, 3])
    print("    (mejora > 0 = supera a predecir siempre el centro de la trayectoria)")


if __name__ == "__main__":
    main()
