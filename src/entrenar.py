"""Entrena el clasificador con las grabaciones de data/ y genera el reporte
de validación (métricas + matriz de confusión) para la documentación.

Uso:
    python src/entrenar.py
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
import soundfile as sf

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from audio_features import extraer_mfcc  # noqa: E402
from modelo import ClasificadorPalabras  # noqa: E402

CONFIG = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
DIR_DATOS = RAIZ / "data"
DIR_MODELOS = RAIZ / "modelos"
DIR_REPORTES = RAIZ / "reportes"


def cargar_dataset() -> tuple[list[np.ndarray], list[str]]:
    """Excluye las muestras "_multi_" (habla+gesto simultáneos): se probó
    que la doble tarea degrada la voz de 80.6% a 36.7% (interferencia
    cognitivo-motora); mezclarlas contamina el modelo de un solo canal.
    Quedan archivadas para el estudio de interferencia, no para entrenar."""
    secuencias, etiquetas = [], []
    for carpeta in sorted(DIR_DATOS.iterdir()):
        if not carpeta.is_dir():
            continue
        for wav in sorted(carpeta.glob("*.wav")):
            if "_multi_" in wav.stem:
                continue
            senal, sr = sf.read(wav)
            if senal.ndim > 1:
                senal = senal.mean(axis=1)
            secuencias.append(extraer_mfcc(senal, sr,
                                           n_mfcc=CONFIG["audio"]["n_mfcc"]))
            etiquetas.append(carpeta.name)
    return secuencias, etiquetas


def graficar_confusion(reporte: dict, ruta: Path) -> None:
    palabras = reporte["palabras"]
    matriz = np.array(reporte["matriz_confusion"])
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(matriz, cmap="Blues")
    ax.set_xticks(range(len(palabras)), palabras, rotation=45, ha="right")
    ax.set_yticks(range(len(palabras)), palabras)
    ax.set_xlabel("Predicción")
    ax.set_ylabel("Palabra real")
    exactitud = reporte["exactitud_global"] * 100
    ax.set_title(f"Matriz de confusión (LOOCV) — exactitud {exactitud:.1f}%")
    for i in range(len(palabras)):
        for j in range(len(palabras)):
            if matriz[i, j] > 0:
                color = "white" if matriz[i, j] > matriz.max() / 2 else "black"
                ax.text(j, i, str(matriz[i, j]), ha="center", va="center",
                        color=color)
    fig.colorbar(im, ax=ax, shrink=0.8)
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)


def main() -> None:
    print("Cargando grabaciones de data/ ...")
    secuencias, etiquetas = cargar_dataset()
    if not secuencias:
        print("❌ No hay grabaciones. Primero ejecuta: python src/grabar.py")
        print("   (o python src/demo_sintetico.py para probar sin micrófono)")
        return

    conteo: dict[str, int] = {}
    for e in etiquetas:
        conteo[e] = conteo.get(e, 0) + 1
    print(f"Dataset: {len(secuencias)} muestras, {len(conteo)} palabras")
    for palabra, n in sorted(conteo.items()):
        print(f"   {palabra:>10}: {n} muestras")
    escasas = [p for p, n in conteo.items() if n < 3]
    if escasas:
        print(f"⚠️  Palabras con <3 muestras (poca confiabilidad): {escasas}")

    modelo = ClasificadorPalabras(
        k=CONFIG["modelo"]["k_vecinos"],
        umbral_confianza=CONFIG["modelo"]["umbral_confianza"])
    modelo.entrenar(secuencias, etiquetas)

    print("\nEvaluando con validación cruzada dejando-uno-fuera (LOOCV)...")
    reporte = modelo.evaluar_loocv()
    print(f"\n  Exactitud global: {reporte['exactitud_global']*100:.1f}% "
          f"({reporte['total_muestras']} muestras)")
    for palabra, m in reporte["por_palabra"].items():
        print(f"   {palabra:>10}: {m['exactitud']*100:5.1f}% "
              f"({m['aciertos']}/{m['muestras']})")

    DIR_MODELOS.mkdir(exist_ok=True)
    DIR_REPORTES.mkdir(exist_ok=True)
    modelo.guardar(DIR_MODELOS / "modelo_yp")

    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    reporte["fecha"] = datetime.now().isoformat(timespec="seconds")
    reporte["config"] = CONFIG["modelo"] | CONFIG["audio"]
    ruta_json = DIR_REPORTES / f"validacion_{marca}.json"
    ruta_json.write_text(json.dumps(reporte, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    ruta_png = DIR_REPORTES / f"confusion_{marca}.png"
    graficar_confusion(reporte, ruta_png)

    print(f"\n✅ Modelo guardado en modelos/modelo_yp.npz")
    print(f"✅ Reporte de validación: {ruta_json.relative_to(RAIZ)}")
    print(f"✅ Matriz de confusión:   {ruta_png.relative_to(RAIZ)}")
    print("\nSiguiente paso:  python src/predecir.py")


if __name__ == "__main__":
    main()
