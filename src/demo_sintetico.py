"""Prueba de extremo a extremo SIN micrófono: genera voces sintéticas tipo
formante para cada palabra del vocabulario, entrena y evalúa el pipeline.

Sirve para: (1) verificar que todo el sistema funciona en esta PC,
(2) tener una demo reproducible si el día de la presentación falla el mic.
Los audios van a data_demo/ y NO se mezclan con las grabaciones reales.

Uso:
    python src/demo_sintetico.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from audio_features import extraer_mfcc  # noqa: E402
from modelo import ClasificadorPalabras  # noqa: E402

CONFIG = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
SR = CONFIG["audio"]["frecuencia_muestreo"]
DIR_DEMO = RAIZ / "data_demo"
MUESTRAS = 6
SEMILLA = 42

# Cada "palabra" sintética = secuencia de sílabas con formantes distintos.
# Simula patrones vocálicos diferentes (como a-u-a en "agua", o-o en "dolor").
PATRONES = {
    "agua":  [(730, 1090), (300, 870), (730, 1090)],
    "si":    [(270, 2290)],
    "no":    [(500, 1000), (450, 800)],
    "dolor": [(500, 1000), (450, 800), (500, 1400)],
    "bano":  [(730, 1090), (270, 2290), (500, 1000)],
    "ayuda": [(730, 1090), (300, 870), (660, 1700)],
    "comer": [(500, 1000), (530, 1840)],
    "mama":  [(730, 1090), (730, 1090)],
}


def sintetizar(formantes: list[tuple[int, int]], rng: np.random.Generator,
               dur_silaba: float = 0.22) -> np.ndarray:
    """Genera una pseudo-palabra con vibración glotal + formantes + ruido."""
    partes = []
    f0 = rng.uniform(180, 220)  # tono base tipo voz femenina, con variación
    for f1, f2 in formantes:
        dur = dur_silaba * rng.uniform(0.8, 1.3)
        t = np.arange(int(SR * dur)) / SR
        fuente = np.sign(np.sin(2 * np.pi * f0 * t)) * 0.5  # pulso glotal
        j1 = f1 * rng.uniform(0.93, 1.07)
        j2 = f2 * rng.uniform(0.93, 1.07)
        silaba = (fuente * (np.sin(2 * np.pi * j1 * t)
                            + 0.6 * np.sin(2 * np.pi * j2 * t)))
        envolvente = np.hanning(len(silaba))
        partes.append(silaba * envolvente)
        partes.append(np.zeros(int(SR * 0.04)))  # micro-pausa entre sílabas
    señal = np.concatenate(partes)
    señal += rng.normal(0, 0.01, len(señal))  # ruido de ambiente
    silencio = np.zeros(int(SR * rng.uniform(0.05, 0.25)))
    señal = np.concatenate([silencio, señal, silencio])
    return (señal / np.max(np.abs(señal)) * 0.8).astype(np.float32)


def main() -> None:
    rng = np.random.default_rng(SEMILLA)
    palabras = [v["palabra"] for v in CONFIG["vocabulario"]]
    print(f"Generando {MUESTRAS} muestras sintéticas x {len(palabras)} palabras...")

    secuencias, etiquetas = [], []
    for palabra in palabras:
        carpeta = DIR_DEMO / palabra
        carpeta.mkdir(parents=True, exist_ok=True)
        for i in range(1, MUESTRAS + 1):
            audio = sintetizar(PATRONES[palabra], rng)
            sf.write(carpeta / f"{palabra}_{i:03d}.wav", audio, SR)
            secuencias.append(extraer_mfcc(audio, SR,
                                           n_mfcc=CONFIG["audio"]["n_mfcc"]))
            etiquetas.append(palabra)

    print("Entrenando clasificador k-NN + DTW y evaluando con LOOCV...")
    modelo = ClasificadorPalabras(k=CONFIG["modelo"]["k_vecinos"])
    modelo.entrenar(secuencias, etiquetas)
    reporte = modelo.evaluar_loocv()

    print(f"\n  Exactitud global (sintético): "
          f"{reporte['exactitud_global']*100:.1f}% "
          f"({reporte['total_muestras']} muestras)")
    for palabra, m in reporte["por_palabra"].items():
        print(f"   {palabra:>10}: {m['exactitud']*100:5.1f}% "
              f"({m['aciertos']}/{m['muestras']})")

    if reporte["exactitud_global"] >= 0.8:
        print("\n✅ PIPELINE VERIFICADO: el sistema distingue patrones de voz.")
        print("   Ahora graba la voz real:  python src/grabar.py")
    else:
        print("\n⚠️  Exactitud sintética baja — revisar extracción de rasgos.")


if __name__ == "__main__":
    main()
