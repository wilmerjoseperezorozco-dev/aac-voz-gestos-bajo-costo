"""Sesión de grabación combinada: YP dice la palabra Y hace el gesto al
mismo tiempo. Cada captura alimenta AMBOS datasets (voz y gestos), así que
también refuerza los modelos individuales, además de crear pares para
validar la fusión de canales.

Uso:
    python src/multimodal_grabar.py          # los 3 pares (sí, no, ayuda)
    python src/multimodal_grabar.py si       # solo uno
"""

from __future__ import annotations

import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import soundfile as sf

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from gestos_features import LectorGestos  # noqa: E402
from multimodal_captura import capturar_par  # noqa: E402

CONFIG = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
SR = CONFIG["audio"]["frecuencia_muestreo"]
RMS_MINIMO = CONFIG["audio"].get("rms_minimo_voz", 0.003)
DURACION = CONFIG["multimodal"]["duracion_captura_seg"]
DIR_REGISTROS = RAIZ / "registros"


def siguiente_numero(carpeta: Path, prefijo: str, extension: str) -> int:
    existentes = sorted(carpeta.glob(f"{prefijo}_multi_*.{extension}"))
    if not existentes:
        return 1
    return int(existentes[-1].stem.split("_")[-1]) + 1


def main() -> None:
    pares = CONFIG["fusion"]
    seleccion = [s.lower() for s in sys.argv[1:]]
    if seleccion:
        pares = [p for p in pares if p["significado"] in seleccion]
        if not pares:
            print(f"Significados disponibles: "
                  f"{[p['significado'] for p in CONFIG['fusion']]}")
            return

    lector = LectorGestos(RAIZ / CONFIG["camara"]["modelo_pose"],
                          CONFIG["camara"]["indice"])
    objetivo = CONFIG["multimodal"]["muestras_por_par_objetivo"]

    print("=" * 60)
    print("  SESIÓN MULTIMODAL — voz + gesto al mismo tiempo")
    print(f"  Objetivo: {objetivo} pares por significado")
    print("  YP dice la palabra Y hace el gesto simultáneamente.")
    print("=" * 60)

    filas = []
    for par in pares:
        significado = par["significado"]
        palabra, gesto, emoji = par["palabra"], par["gesto"], par["emoji"]
        carpeta_voz = RAIZ / "data" / palabra
        carpeta_gesto = RAIZ / "data_gestos" / gesto
        carpeta_voz.mkdir(parents=True, exist_ok=True)
        carpeta_gesto.mkdir(parents=True, exist_ok=True)

        actuales = len(list(carpeta_voz.glob(f"{palabra}_multi_*.wav")))
        print(f"\n▶ «{significado.upper()}» {emoji} — di «{palabra}» "
              f"mientras haces el gesto — {actuales}/{objetivo}")
        while actuales < objetivo:
            entrada = input(f"  ENTER para capturar par {actuales + 1} "
                            "(s para saltar): ").strip().lower()
            if entrada == "s":
                break
            for cuenta in ("3", "2", "1"):
                print(f"  {cuenta}...", end=" ", flush=True)
                time.sleep(0.6)
            print("¡AHORA! (habla + gesto) 🎙️🎥")
            audio, secuencia_gestos = capturar_par(
                lector, DURACION, SR, titulo=f"Di «{palabra}» + gesto")

            rms = float(np.sqrt(np.mean(audio ** 2)))
            if rms < RMS_MINIMO:
                print(f"  ⚠️  Voz muy débil (rms {rms:.4f}). Repetimos el par.")
                continue

            numero_v = siguiente_numero(carpeta_voz, palabra, "wav")
            ruta_wav = carpeta_voz / f"{palabra}_multi_{numero_v:03d}.wav"
            sf.write(ruta_wav, audio, SR)

            numero_g = siguiente_numero(carpeta_gesto, gesto, "npz")
            ruta_npz = carpeta_gesto / f"{gesto}_multi_{numero_g:03d}.npz"
            np.savez_compressed(ruta_npz, secuencia=secuencia_gestos)

            print(f"  ✅ Par guardado: {ruta_wav.name} + {ruta_npz.name}")
            filas.append({
                "fecha_hora": datetime.now().isoformat(timespec="seconds"),
                "alias": CONFIG["participante"]["alias"],
                "significado": significado,
                "archivo_audio": ruta_wav.name,
                "archivo_gesto": ruta_npz.name,
            })
            actuales += 1

    if filas:
        DIR_REGISTROS.mkdir(exist_ok=True)
        archivo = DIR_REGISTROS / "sesiones_multimodal.csv"
        nuevo = not archivo.exists()
        with archivo.open("a", newline="", encoding="utf-8") as f:
            campos = ["fecha_hora", "alias", "significado",
                      "archivo_audio", "archivo_gesto"]
            w = csv.DictWriter(f, fieldnames=campos)
            if nuevo:
                w.writeheader()
            w.writerows(filas)
        print(f"\n✅ {len(filas)} pares voz+gesto registrados.")
        print("Reentrena ambos canales:")
        print("  python src/entrenar.py")
        print("  python src/gestos_entrenar.py")
        print("Luego prueba la fusión:  python src/multimodal_predecir.py")
    else:
        print("\nSesión sin pares nuevos.")


if __name__ == "__main__":
    main()
