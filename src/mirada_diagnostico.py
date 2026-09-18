"""Diagnóstico de una sesión de persecución (canal cabeza u ojos).

Uso:
    py -3.12 src/mirada_diagnostico.py                 # última sesión
    py -3.12 src/mirada_diagnostico.py ruta/al/archivo.npz

Separa tres preguntas que el resumen final mezcla:
  1. Fijaciones (calibración): ¿los rasgos cambian con el punto que se
     mira/apunta? Es la prueba más limpia: el objetivo está quieto.
  2. Contexto: en canal ojos, cuánto se mueve la cabeza frente al iris;
     en canal cabeza, el rango de giro e inclinación que logra la persona.
  3. Persecución: ¿algún modelo simple le gana a "apuntar al centro"?
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

from mirada_modelo import (ajustar_ridge, ajustar_robusto,  # noqa: E402
                           metricas_persecucion,
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
    canal = str(z["canal"]) if "canal" in z.files else "ojos"
    cal, per = z["calibracion"], z["persecucion"]
    pant = tuple(int(v) for v in z["pantalla"])
    Fc, Yc = cal[:, 3:], cal[:, 1:3]
    t, blanco, F = per[:, 0], per[:, 1:3], per[:, 3:]
    puntos = sorted({(round(a), round(b)) for a, b in Yc}, key=lambda p: (p[1], p[0]))
    print(f"Sesión: {ruta.name} | canal {canal} | pantalla {pant} | "
          f"calibración {len(cal)} frames | persecución {len(per)} frames")

    if canal == "cabeza":
        # rasgos: yaw, pitch, roll, nariz-x, nariz-y, giro
        print("\n[1] FIJACIONES — ¿el ángulo de la cabeza cambia con el punto apuntado?")
        print(f"    r(yaw, punto-x) = {_pearson(Fc[:, 0], Yc[:, 0]):+.2f}   "
              f"r(pitch, punto-y) = {_pearson(Fc[:, 1], Yc[:, 1]):+.2f}")
        print("    (el signo depende de la convención de ejes; importa que |r| sea alto)")
        print("    yaw medio por punto (filas: arriba/centro/abajo; columnas: izq/centro/der):")
        rejilla(Fc[:, 0], puntos, Yc, lambda v: f"{v.mean():+6.1f}°")
        print("    pitch medio por punto:")
        rejilla(Fc[:, 1], puntos, Yc, lambda v: f"{v.mean():+6.1f}°")
        print("\n[2] RANGO — giro logrado")
        print(f"    yaw: {Fc[:, 0].min():+.0f}° a {Fc[:, 0].max():+.0f}°   "
              f"pitch: {Fc[:, 1].min():+.0f}° a {Fc[:, 1].max():+.0f}°  (calibración)")
        modelos = [("todos los rasgos", list(range(6))),
                   ("solo yaw + pitch", [0, 1]),
                   ("yaw + pitch + nariz", [0, 1, 3, 4])]
    else:
        xi_c, yi_c = (Fc[:, 0] + Fc[:, 1]) / 2, (Fc[:, 2] + Fc[:, 3]) / 2
        print("\n[1] FIJACIONES — ¿el iris cambia con el punto mirado?")
        print(f"    r(iris-x, punto-x) = {_pearson(xi_c, Yc[:, 0]):+.2f}   "
              f"r(iris-y, punto-y) = {_pearson(yi_c, Yc[:, 1]):+.2f}")
        print("    (en imagen sin espejo, iris-x baja cuando el punto está a la")
        print("     derecha, así que r-x sale NEGATIVA si mira los puntos)")
        print("    iris-x medio por punto (filas: arriba/centro/abajo; columnas: izq/centro/der):")
        rejilla(xi_c, puntos, Yc, lambda v: f"{v.mean():.3f}")
        print("\n[2] CABEZA — giro medio por punto (0.5 = de frente)")
        rejilla(Fc[:, 6], puntos, Yc, lambda v: f"{v.mean():.3f}")
        print(f"    desv. del giro entre puntos: "
              f"{np.std([Fc[np.all(np.round(Yc) == p, axis=1), 6].mean() for p in puntos]):.3f}"
              f"  | desv. del iris-x entre puntos: "
              f"{np.std([xi_c[np.all(np.round(Yc) == p, axis=1)].mean() for p in puntos]):.3f}")
        modelos = [("todos los rasgos", list(range(15))),
                   ("sin posición/giro de cabeza", [0, 1, 2, 3] + list(range(7, 15))),
                   ("solo iris (4 rasgos)", [0, 1, 2, 3])]

    print("\n[3] PERSECUCIÓN — modelos simples contra 'apuntar al centro'")
    max_ret = 2.0 if canal == "cabeza" else 1.0
    for nombre, cols in modelos:
        variantes = [("", ajustar_ridge(Fc[:, cols], Yc), [])]
        mod_r, excluidos, _ = ajustar_robusto(Fc[:, cols], Yc)
        if excluidos:
            variantes.append((" + robusto", mod_r, excluidos))
        for sufijo, mod, exc in variantes:
            m = metricas_persecucion(t, blanco, suavizar(predecir(mod, F[:, cols]), 5),
                                     pant, max_ret)
            print(f"    {nombre + sufijo:30s} error {m['rmse_px']:4.0f} px ({m['rmse_pct_diagonal']:.0f}%)  "
                  f"mejora vs centro {m['mejora_vs_constante']:+.0%}  "
                  f"r_x={m['r_x']:+.2f} r_y={m['r_y']:+.2f}  "
                  f"retardo x={m['retardo_x_ms']:.0f} ms")
            if exc:
                print(f"       descarta puntos de calibración: "
                      f"{[(int(a), int(b)) for a, b in exc]} (atípicos: no se alcanzaron)")
    print("    (mejora > 0 = supera a apuntar siempre al centro de la trayectoria)")


if __name__ == "__main__":
    main()
