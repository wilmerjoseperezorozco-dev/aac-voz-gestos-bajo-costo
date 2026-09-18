"""Diagnóstico de una sesión de persecución (canal cabeza u ojos).

Uso:
    py -3.12 src/mirada_diagnostico.py                 # última sesión
    py -3.12 src/mirada_diagnostico.py ruta/al/archivo.npz

Responde tres preguntas que el resumen final mezcla:
  1. Relación cruda: ¿el rasgo (yaw/pitch o iris) sigue al blanco durante
     la persecución? No depende de ninguna calibración: es la prueba más
     limpia de que el canal funciona.
  2. Rango: cuánto se mueve la persona (ángulos de cabeza o razón del iris).
  3. Calibración: ¿con qué se entrena mejor el modelo? Se compara calibrar
     con la primera mitad de la persecución (seguimiento) contra 9 puntos
     quietos (si la sesión los tiene), y siempre se evalúa en la segunda
     mitad, que ningún modelo vio.
Sirve también para el CONTROL POSITIVO: si una persona sin condición
motora obtiene una relación cruda alta, el sistema funciona y el problema
estaría en el protocolo o en la persona evaluada.
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
                           predecir, r2_armonico, resumen_movimiento,
                           suavizar, _pearson)

COLS_MODELO = {"cabeza": [0, 1], "ojos": [0, 1, 2, 3]}
# Períodos del blanco automático por canal (sesiones anteriores a guardarlos).
PERIODOS = {"cabeza": (14.0, 20.0), "ojos": (8.0, 12.0)}
NIVELES = " ▁▂▃▄▅▆▇█"


def sparkline(t: np.ndarray, y: np.ndarray) -> str:
    """Media por segundo dibujada con bloques; escala propia de la sesión."""
    medias = np.array([y[(t >= s) & (t < s + 1)].mean() if ((t >= s) & (t < s + 1)).any()
                       else np.nan for s in range(int(t.max()))])
    medias = np.nan_to_num(medias, nan=np.nanmean(medias))
    lo, hi = np.percentile(medias, 2), np.percentile(medias, 98)
    escala = np.clip((medias - lo) / (hi - lo + 1e-9), 0, 0.999)
    return "".join(NIVELES[int(v * 9)] for v in escala)


def crudo(canal: str, F: np.ndarray):
    """(x, y) crudos: yaw/pitch en cabeza; promedio de ambos iris en ojos."""
    if canal == "cabeza":
        return F[:, 0], F[:, 1]
    return (F[:, 0] + F[:, 1]) / 2, (F[:, 2] + F[:, 3]) / 2


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
    alias = str(z["alias"]) if "alias" in z.files else "?"
    cal, per = z["calibracion"], z["persecucion"]
    pant = tuple(int(v) for v in z["pantalla"])
    cols = (list(z["columnas_modelo"]) if "columnas_modelo" in z.files
            else COLS_MODELO[canal])
    t, blanco, F = per[:, 0], per[:, 1:3], per[:, 3:]
    print(f"Sesión: {ruta.name} | {alias} | canal {canal} | pantalla {pant} | "
          f"persecución {len(per)} frames | calibración con puntos "
          f"{len(cal)} frames")

    x_c, y_c = crudo(canal, F)
    unidad = "°" if canal == "cabeza" else ""
    etiqueta_x, etiqueta_y = ("yaw", "pitch") if canal == "cabeza" else ("iris-x", "iris-y")
    print("\n[1] RELACIÓN CRUDA en toda la persecución (sin calibración)")
    print(f"    r({etiqueta_x}, blanco-x) = {_pearson(x_c, blanco[:, 0]):+.2f}   "
          f"r({etiqueta_y}, blanco-y) = {_pearson(y_c, blanco[:, 1]):+.2f}")
    print("    (el signo depende de la convención de ejes; importa que |r| sea alto,")
    print("     cerca de 1 = el rasgo sigue al blanco; cerca de 0 = no lo sigue)")

    print("\n[2] RANGO logrado durante la persecución")
    print(f"    {etiqueta_x}: {x_c.min():.2f}{unidad} a {x_c.max():.2f}{unidad}  "
          f"(desv. {x_c.std():.2f})   {etiqueta_y}: {y_c.min():.2f}{unidad} a "
          f"{y_c.max():.2f}{unidad}  (desv. {y_c.std():.2f})")
    if canal == "ojos":
        print("    (con el iris, rangos muy chicos suelen indicar que casi no hay movimiento ocular)")

    print("\n[2b] TIPO DE MOVIMIENTO")
    mov = resumen_movimiento(t, x_c)
    print(f"    potencia de {etiqueta_x} por banda: <0.15 Hz {mov['pot_menor_015hz']:.0%} | "
          f"0.15-0.5 Hz {mov['pot_015_05hz']:.0%} | 0.5-3 Hz {mov['pot_05_3hz']:.0%}   "
          f"(pico {mov['frecuencia_pico_hz']:.2f} Hz)")
    if canal == "cabeza":
        print(f"    velocidad del giro: media {mov['vel_media']:.1f} °/s, p99 "
              f"{mov['vel_p99']:.0f} °/s, giros bruscos (>60 °/s): {mov['saltos']}")
    modo_mouse = bool(z["modo_mouse"]) if "modo_mouse" in z.files else False
    if not modo_mouse:
        px_, py_ = (z["periodos"] if "periodos" in z.files else PERIODOS[canal])
        print(f"    ajuste al ritmo del blanco (1 = lo sigue, 0 = nada que ver): "
              f"{etiqueta_x} {r2_armonico(t, x_c, float(px_)):.2f} (período {float(px_):.0f} s)   "
              f"{etiqueta_y} {r2_armonico(t, y_c, float(py_)):.2f} (período {float(py_):.0f} s)")
        print("    (un seguimiento suave da ~0.9 y casi toda la potencia bajo 0.15 Hz;")
        print("     una postura casi fija con movimientos bruscos da un ajuste bajo)")
    print(f"    {etiqueta_x} por segundo: {sparkline(t, x_c)}")

    corte = float(t.max()) / 2
    A, B = per[t <= corte], per[t > corte]
    print(f"\n[3] CALIBRACIÓN — evaluada en la 2ª mitad ({len(B)} frames) que ningún modelo vio")
    opciones = {"1ª mitad de la persecución (seguimiento)":
                (A[:, 3:][:, cols], A[:, 1:3])}
    if len(cal) >= 30:
        opciones["9 puntos quietos"] = (cal[:, 3:][:, cols], cal[:, 1:3])
        opciones["9 puntos + 1ª mitad"] = (
            np.vstack([cal[:, 3:][:, cols], A[:, 3:][:, cols]]),
            np.vstack([cal[:, 1:3], A[:, 1:3]]))
    max_ret = 2.0 if canal == "cabeza" else 1.0
    for nombre, (X, Y) in opciones.items():
        pred = suavizar(predecir(ajustar_ridge(X, Y), B[:, 3:][:, cols]), 5)
        m = metricas_persecucion(B[:, 0], B[:, 1:3], pred, pant, max_ret)
        print(f"    {nombre:40s} error {m['rmse_pct_diagonal']:4.0f}%  "
              f"mejora vs centro {m['mejora_vs_constante']:+5.0%}  "
              f"r_x={m['r_x']:+.2f} r_y={m['r_y']:+.2f}")
    print("    (mejora > 0 = supera a apuntar siempre al centro de la trayectoria)")


if __name__ == "__main__":
    main()
