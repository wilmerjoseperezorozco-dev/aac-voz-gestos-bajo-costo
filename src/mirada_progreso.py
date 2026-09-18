"""Tendencia entre sesiones: ¿mejora el resultado y mejora el entorno?

Uso:  py -3.12 src/mirada_progreso.py

Lee registros/sesiones_mirada.csv (persecución) y
registros/sesiones_gestos_cara.csv (gestos + cara) y muestra, sesión por
sesión, las métricas de resultado y de entorno, con el cambio frente a la
sesión anterior del mismo canal y recomendaciones para la próxima.

Solo son tendencias de una persona y pocas sesiones: sirven para decidir
qué ajustar (luz, distancia, canal), no para afirmar eficacia.
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path

if sys.stdout is not None and sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import monitor_operador as mon  # noqa: E402  (umbrales de entorno)

REG = RAIZ / "registros"


def leer(nombre: str) -> list[dict]:
    ruta = REG / nombre
    if not ruta.exists():
        return []
    with ruta.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def num(fila: dict, clave: str) -> float | None:
    try:
        v = fila.get(clave, "")
        return float(v) if v not in ("", None) else None
    except ValueError:
        return None


def fmt(v: float | None, plantilla: str = "{:.2f}") -> str:
    return "  -  " if v is None else plantilla.format(v)


def flecha(actual, previo, mayor_es_mejor: bool, umbral: float) -> str:
    if actual is None or previo is None:
        return " "
    d = actual - previo
    if abs(d) < umbral:
        return "≈"
    return "↑" if (d > 0) == mayor_es_mejor else "↓"


def persecucion() -> None:
    filas = leer("sesiones_mirada.csv")
    print("=" * 100)
    print("  PERSECUCIÓN (blanco en pantalla)   ↑ mejor que la sesión previa de la misma persona y canal · ↓ peor · ≈ igual")
    print("=" * 100)
    if not filas:
        print("  Aún no hay sesiones. Corre lanzadores\\12_Persecucion_Mirada.bat")
        return
    print(f"  {'fecha':16s} {'quien':6s} {'canal':7s} {'mejora':>8s}  {'error%':>7s}  {'r_x':>5s} {'r_y':>5s}  "
          f"{'calibLOPO':>9s}  {'fps':>4s} {'cara':>5s} {'brillo':>6s} {'ancho':>6s} {'avisos':>6s}")
    previo: dict[str, dict] = {}
    for f in filas:
        canal = f.get("canal") or "ojos"     # sesiones anteriores al canal cabeza
        quien = f.get("alias") or "?"
        p = previo.get((quien, canal), {})
        mejora, error = num(f, "mejora_vs_constante"), num(f, "rmse_pct_diagonal")
        rx, ry = num(f, "r_x"), num(f, "r_y")
        lopo = num(f, "error_calib_lopo_px")
        print(f"  {f['fecha_hora'][:16].replace('T', ' '):16s} {quien:6s} {canal:7s} "
              f"{fmt(None if mejora is None else mejora * 100, '{:+.0f}%'):>7s}{flecha(mejora, num(p, 'mejora_vs_constante'), True, 0.03)} "
              f"{fmt(error, '{:.0f}%'):>6s}{flecha(error, num(p, 'rmse_pct_diagonal'), False, 1.0)} "
              f"{fmt(rx):>5s} {fmt(ry):>5s}  "
              f"{fmt(lopo, '{:.0f}px'):>8s}{flecha(lopo, num(p, 'error_calib_lopo_px'), False, 20.0)} "
              f"{fmt(num(f, 'fps'), '{:.0f}'):>4s} "
              f"{fmt(None if num(f, 'tasa_cara') is None else num(f, 'tasa_cara') * 100, '{:.0f}%'):>5s} "
              f"{fmt(num(f, 'brillo'), '{:.0f}'):>6s} "
              f"{fmt(num(f, 'ancho_cara_pct'), '{:.0f}%'):>6s} "
              f"{fmt(num(f, 'pct_frames_con_aviso'), '{:.0f}%'):>6s}")
        previo[(quien, canal)] = f

    print("\n  Lectura: 'mejora' > 0 = el canal le gana a apuntar siempre al centro.")
    ultima = filas[-1]
    consejos = []
    brillo, ancho, fps = num(ultima, "brillo"), num(ultima, "ancho_cara_pct"), num(ultima, "fps")
    avisos, cara = num(ultima, "pct_frames_con_aviso"), num(ultima, "tasa_cara")
    if brillo is not None and brillo < mon.BRILLO_MIN:
        consejos.append("Poca luz en la última sesión: ilumina la cara de frente.")
    if brillo is not None and brillo > mon.BRILLO_MAX:
        consejos.append("Imagen sobreexpuesta: evita contraluz y luz directa al lente.")
    if ancho is not None and ancho < 100 * mon.ANCHO_CARA_MIN:
        consejos.append("La cara ocupó poco encuadre: acerca la cámara o a YP.")
    if ancho is not None and ancho > 100 * mon.ANCHO_CARA_MAX:
        consejos.append("La cara quedó demasiado cerca de la cámara.")
    if fps is not None and fps < mon.FPS_MIN:
        consejos.append("Pocos fps: cierra otras apps o baja la resolución de cámara.")
    if cara is not None and cara < 0.9:
        consejos.append(f"Cara detectada solo {cara:.0%} del tiempo: revisa encuadre y luz.")
    if avisos is not None and avisos > 30:
        consejos.append(f"El monitor mostró avisos en {avisos:.0f}% de los frames.")
    print("  Para la próxima sesión:")
    if all(v is None for v in (brillo, ancho, fps, avisos, cara)):
        consejos = ["La última sesión es anterior al monitor: no tiene métricas "
                    "de entorno. Desde la próxima se registran solas."]
    for c in consejos or ["El entorno de la última sesión se ve dentro de los umbrales."]:
        print(f"    · {c}")


def gestos_cara() -> None:
    filas = leer("sesiones_gestos_cara.csv")
    print("\n" + "=" * 100)
    print("  GESTOS + CARA (calidad de captura por día)")
    print("=" * 100)
    if not filas:
        print("  Aún no hay sesiones de gestos con cara.")
        return
    por_dia: dict[str, list[float]] = defaultdict(list)
    for f in filas:
        v = num(f, "cara_detectada")
        if v is not None:
            por_dia[f["fecha_hora"][:10]].append(v)
    print(f"  {'día':12s} {'muestras':>8s} {'cara media':>11s} {'cara mín':>9s} {'<80%':>6s}")
    for dia, vs in sorted(por_dia.items()):
        bajas = sum(v < 0.8 for v in vs)
        print(f"  {dia:12s} {len(vs):8d} {sum(vs) / len(vs):11.0%} {min(vs):9.0%} {bajas:6d}")
    print("  (muestras con cara <80% suelen ser manos tapando el rostro o poca luz)")


def main() -> None:
    persecucion()
    gestos_cara()


if __name__ == "__main__":
    main()
