"""Sesión de grabación de gestos con la cámara (espejo de grabar.py).

Uso:
    python src/gestos_grabar.py                    # todos los gestos
    python src/gestos_grabar.py si_mano_arriba     # solo uno

Cada muestra se guarda como .npz en data_gestos/<gesto>/ y se registra
en registros/sesiones_gestos.csv.
"""

from __future__ import annotations

import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from gestos_features import LectorGestos  # noqa: E402

CONFIG = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
DIR_DATOS = RAIZ / "data_gestos"
DIR_REGISTROS = RAIZ / "registros"
DURACION = CONFIG["camara"]["duracion_captura_seg"]


def siguiente_numero(carpeta: Path, gesto: str) -> int:
    existentes = sorted(carpeta.glob(f"{gesto}_*.npz"))
    if not existentes:
        return 1
    return int(existentes[-1].stem.split("_")[-1]) + 1


def main() -> None:
    gestos = CONFIG["gestos"]
    seleccion = [g.lower() for g in sys.argv[1:]]
    if seleccion:
        gestos = [g for g in gestos if g["gesto"] in seleccion]
        if not gestos:
            print(f"Gestos disponibles: {[g['gesto'] for g in CONFIG['gestos']]}")
            return

    lector = LectorGestos(RAIZ / CONFIG["camara"]["modelo_pose"],
                          CONFIG["camara"]["indice"])
    objetivo = CONFIG["muestras_por_gesto_objetivo"]
    print("=" * 60)
    print("  SESIÓN DE GRABACIÓN DE GESTOS — canal de cámara")
    print(f"  Objetivo: {objetivo} muestras por gesto")
    print("  YP frente a la cámara, buena luz, torso visible.")
    print("=" * 60)

    filas = []
    for item in gestos:
        gesto, descripcion = item["gesto"], item["descripcion"]
        carpeta = DIR_DATOS / gesto
        carpeta.mkdir(parents=True, exist_ok=True)
        actuales = len(list(carpeta.glob(f"{gesto}_*.npz")))
        print(f"\n▶ Gesto «{gesto}» ({descripcion}) — {actuales}/{objetivo}")
        while actuales < objetivo:
            numero = siguiente_numero(carpeta, gesto)
            entrada = input(f"  ENTER para capturar muestra {numero} "
                            "(s para saltar): ").strip().lower()
            if entrada == "s":
                break
            for cuenta in ("3", "2", "1"):
                print(f"  {cuenta}...", end=" ", flush=True)
                time.sleep(0.6)
            print("¡HAZ EL GESTO AHORA! 🎥")
            try:
                secuencia = lector.capturar(DURACION, mostrar=True,
                                            titulo=descripcion)
            except RuntimeError as error:
                print(f"  ⚠️  {error}. Repetimos.")
                continue
            ruta = carpeta / f"{gesto}_{numero:03d}.npz"
            np.savez_compressed(ruta, secuencia=secuencia)
            print(f"  ✅ Guardada: {ruta.name} ({len(secuencia)} frames)")
            filas.append({
                "fecha_hora": datetime.now().isoformat(timespec="seconds"),
                "alias": CONFIG["participante"]["alias"],
                "gesto": gesto, "archivo": ruta.name, "observaciones": "",
            })
            actuales += 1

    if filas:
        DIR_REGISTROS.mkdir(exist_ok=True)
        archivo = DIR_REGISTROS / "sesiones_gestos.csv"
        nuevo = not archivo.exists()
        with archivo.open("a", newline="", encoding="utf-8") as f:
            campos = ["fecha_hora", "alias", "gesto", "archivo", "observaciones"]
            w = csv.DictWriter(f, fieldnames=campos)
            if nuevo:
                w.writeheader()
            w.writerows(filas)
        print(f"\n✅ {len(filas)} muestras de gestos registradas.")
        print("Siguiente paso:  python src/gestos_entrenar.py")
    else:
        print("\nSesión sin muestras nuevas.")


if __name__ == "__main__":
    main()
