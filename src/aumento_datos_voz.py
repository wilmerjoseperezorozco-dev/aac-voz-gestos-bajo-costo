"""Aumento de datos de voz por perturbación de señal (sin sesión nueva).

Uso:
    python src/aumento_datos_voz.py

Genera, a partir de cada grabación real en data/<palabra>/, variantes
sintéticas guardadas en data_aumentado/<palabra>/ (carpeta aparte, nunca
se mezcla con las grabaciones reales). Dos técnicas, ambas establecidas
en la literatura de aumento de datos para reconocimiento de voz, no
inventadas para este proyecto:

- Perturbación de velocidad (speed perturbation): remuestrea la señal a
  0.9x y 1.1x. Cambia velocidad Y tono a la vez — es justo la técnica
  estándar de Ko et al. (2015), "Audio Augmentation for Speech
  Recognition", ampliamente usada en Kaldi y trabajos posteriores.
- Ruido gaussiano leve: simula variabilidad de micrófono/ambiente sin
  alterar el contenido articulatorio.

Cada archivo generado registra de qué grabación real proviene
(`registros/aumento_datos_voz.csv`), para que la validación cruzada
pueda excluir juntas una grabación real y sus derivados — si no se hace
así, el número de exactitud queda inflado (las copias no son
independientes de su original).
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy.signal import resample

if sys.stdout is not None and sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
DIR_DATOS = RAIZ / "data"
DIR_AUMENTADO = RAIZ / "data_aumentado"
DIR_REGISTROS = RAIZ / "registros"

TASAS_VELOCIDAD = (0.9, 1.1)
NIVEL_RUIDO = 0.003  # relativo a la amplitud ya normalizada de la señal


def perturbar_velocidad(senal: np.ndarray, tasa: float) -> np.ndarray:
    """Remuestrea la señal a `tasa`x: cambia velocidad y tono juntos
    (speed perturbation, Ko et al. 2015), no solo el tono."""
    n_nuevo = max(1, int(round(len(senal) / tasa)))
    return resample(senal, n_nuevo).astype(senal.dtype)


def agregar_ruido(senal: np.ndarray, rng: np.random.Generator,
                  nivel: float = NIVEL_RUIDO) -> np.ndarray:
    return (senal + rng.normal(0, nivel, size=senal.shape)).astype(senal.dtype)


def generar_variantes(senal: np.ndarray, sr: int,
                      rng: np.random.Generator) -> dict[str, np.ndarray]:
    variantes = {}
    for tasa in TASAS_VELOCIDAD:
        etiqueta = f"vel{int(tasa * 100)}"
        variantes[etiqueta] = perturbar_velocidad(senal, tasa)
    variantes["ruido"] = agregar_ruido(senal, rng)
    return variantes


def main() -> None:
    if not DIR_DATOS.exists():
        raise SystemExit(f"No existe {DIR_DATOS}. Graba primero con grabar.py")
    rng = np.random.default_rng(0)  # reproducible: mismas variantes cada corrida
    filas = []
    total_generados = 0

    for carpeta in sorted(p for p in DIR_DATOS.iterdir() if p.is_dir()):
        wavs = sorted(w for w in carpeta.glob("*.wav") if "_multi_" not in w.stem)
        if not wavs:
            continue
        destino = DIR_AUMENTADO / carpeta.name
        destino.mkdir(parents=True, exist_ok=True)
        for wav in wavs:
            senal, sr = sf.read(wav)
            if senal.ndim > 1:
                senal = senal.mean(axis=1)
            for etiqueta, variante in generar_variantes(senal, sr, rng).items():
                nombre = f"{wav.stem}_aug_{etiqueta}.wav"
                sf.write(destino / nombre, variante, sr)
                filas.append({"palabra": carpeta.name, "archivo_original": wav.name,
                             "archivo_generado": nombre, "tecnica": etiqueta})
                total_generados += 1
        print(f"  {carpeta.name}: {len(wavs)} reales -> "
              f"{len(wavs) * len(TASAS_VELOCIDAD + ('ruido',))} generadas")

    DIR_REGISTROS.mkdir(exist_ok=True)
    ruta_csv = DIR_REGISTROS / "aumento_datos_voz.csv"
    with ruta_csv.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["palabra", "archivo_original",
                                           "archivo_generado", "tecnica"])
        w.writeheader()
        w.writerows(filas)

    print(f"\n✅ {total_generados} muestras sintéticas generadas en "
          f"data_aumentado/ (fuera de GitHub, igual que data/)")
    print(f"✅ Trazabilidad guardada en {ruta_csv.relative_to(RAIZ)}")
    print("\nSiguiente paso:  python src/entrenar_con_aumento.py")
    print("(compara LOOCV con y sin datos aumentados, sin filtración entre grupos)")


if __name__ == "__main__":
    main()
