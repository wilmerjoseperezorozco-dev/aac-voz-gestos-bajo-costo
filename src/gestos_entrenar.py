"""Entrena el clasificador de gestos con data_gestos/ (espejo de entrenar.py).
Reutiliza el mismo k-NN + DTW del canal de voz.

Uso:
    python src/gestos_entrenar.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from modelo import ClasificadorPalabras  # noqa: E402

CONFIG = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
DIR_DATOS = RAIZ / "data_gestos"
DIR_MODELOS = RAIZ / "modelos"
DIR_REPORTES = RAIZ / "reportes"


def main() -> None:
    # Excluye "_multi_" (gesto + habla simultáneos): la doble tarea degrada
    # el gesto de 80% a 30% (interferencia cognitivo-motora). Se archivan
    # para el estudio de interferencia, no para entrenar el canal solo.
    secuencias, etiquetas = [], []
    if DIR_DATOS.exists():
        for carpeta in sorted(DIR_DATOS.iterdir()):
            if not carpeta.is_dir():
                continue
            for npz in sorted(carpeta.glob("*.npz")):
                if "_multi_" in npz.stem:
                    continue
                secuencias.append(np.load(npz)["secuencia"])
                etiquetas.append(carpeta.name)
    if not secuencias:
        print("❌ No hay gestos grabados. Primero: python src/gestos_grabar.py")
        return

    conteo: dict[str, int] = {}
    for e in etiquetas:
        conteo[e] = conteo.get(e, 0) + 1
    print(f"Dataset de gestos: {len(secuencias)} muestras, {len(conteo)} gestos")
    for gesto, n in sorted(conteo.items()):
        print(f"   {gesto:>18}: {n} muestras")

    modelo = ClasificadorPalabras(k=CONFIG["modelo"]["k_vecinos"],
                                  umbral_confianza=CONFIG["modelo"]["umbral_confianza"])
    modelo.entrenar(secuencias, etiquetas)

    print("\nEvaluando con LOOCV...")
    reporte = modelo.evaluar_loocv()
    print(f"\n  Exactitud global: {reporte['exactitud_global']*100:.1f}% "
          f"({reporte['total_muestras']} muestras)")
    for gesto, m in reporte["por_palabra"].items():
        print(f"   {gesto:>18}: {m['exactitud']*100:5.1f}% "
              f"({m['aciertos']}/{m['muestras']})")

    DIR_MODELOS.mkdir(exist_ok=True)
    DIR_REPORTES.mkdir(exist_ok=True)
    modelo.guardar(DIR_MODELOS / "modelo_gestos")

    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    reporte["fecha"] = datetime.now().isoformat(timespec="seconds")
    reporte["canal"] = "gestos"
    (DIR_REPORTES / f"validacion_gestos_{marca}.json").write_text(
        json.dumps(reporte, ensure_ascii=False, indent=2), encoding="utf-8")

    gestos = reporte["palabras"]
    matriz = np.array(reporte["matriz_confusion"])
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(matriz, cmap="Greens")
    ax.set_xticks(range(len(gestos)), gestos, rotation=30, ha="right")
    ax.set_yticks(range(len(gestos)), gestos)
    ax.set_xlabel("Predicción")
    ax.set_ylabel("Gesto real")
    ax.set_title(f"Confusión gestos (LOOCV) — "
                 f"{reporte['exactitud_global']*100:.1f}%")
    for i in range(len(gestos)):
        for j in range(len(gestos)):
            if matriz[i, j] > 0:
                ax.text(j, i, str(matriz[i, j]), ha="center", va="center")
    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout()
    fig.savefig(DIR_REPORTES / f"confusion_gestos_{marca}.png", dpi=150)

    print(f"\n✅ Modelo de gestos guardado en modelos/modelo_gestos.npz")
    print(f"✅ Reporte: reportes/validacion_gestos_{marca}.json")
    print("\nSiguiente paso:  python src/gestos_predecir.py")


if __name__ == "__main__":
    main()
