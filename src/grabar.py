"""Sesión de grabación guiada para construir el dataset de YP (alias YP).

Uso:
    python src/grabar.py                # sesión completa (todas las palabras)
    python src/grabar.py agua dolor     # solo palabras específicas

Cada muestra se guarda como WAV en data/<palabra>/<palabra>_NNN.wav
y se registra en registros/sesiones.csv para la trazabilidad del estudio.
"""

from __future__ import annotations

import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import sounddevice as sd
import soundfile as sf

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
CONFIG = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
SR = CONFIG["audio"]["frecuencia_muestreo"]
DURACION = CONFIG["audio"]["duracion_grabacion_seg"]
DIR_DATOS = RAIZ / "data"
DIR_REGISTROS = RAIZ / "registros"


def siguiente_numero(carpeta: Path, palabra: str) -> int:
    existentes = sorted(carpeta.glob(f"{palabra}_*.wav"))
    if not existentes:
        return 1
    ultimo = existentes[-1].stem.split("_")[-1]
    return int(ultimo) + 1


def grabar_muestra(palabra: str, emoji: str, numero: int) -> Path | None:
    print(f"\n  {emoji}  Palabra: «{palabra.upper()}»  (muestra {numero})")
    entrada = input("  Presiona ENTER para grabar (o 's' para saltar): ").strip()
    if entrada.lower() == "s":
        return None
    for cuenta in ("3", "2", "1"):
        print(f"  {cuenta}...", end=" ", flush=True)
        time.sleep(0.6)
    print("¡HABLA AHORA! 🎙️")
    audio = sd.rec(int(DURACION * SR), samplerate=SR, channels=1, dtype="float32")
    sd.wait()
    audio = audio.flatten()

    energia = float(np.sqrt(np.mean(audio ** 2)))
    rms_minimo = CONFIG["audio"].get("rms_minimo_voz", 0.003)
    if energia < rms_minimo:
        print(f"  ⚠️  Voz muy débil (rms {energia:.4f} < {rms_minimo}). "
              "Acércale el micrófono o pídele hablar más fuerte. Repetimos.")
        return grabar_muestra(palabra, emoji, numero)

    carpeta = DIR_DATOS / palabra
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta = carpeta / f"{palabra}_{numero:03d}.wav"
    sf.write(ruta, audio, SR)
    print(f"  ✅ Guardada: {ruta.name} (energía {energia:.4f})")
    return ruta


def registrar_sesion(filas: list[dict]) -> None:
    DIR_REGISTROS.mkdir(parents=True, exist_ok=True)
    archivo = DIR_REGISTROS / "sesiones.csv"
    nuevo = not archivo.exists()
    with archivo.open("a", newline="", encoding="utf-8") as f:
        campos = ["fecha_hora", "alias", "palabra", "archivo", "observaciones"]
        escritor = csv.DictWriter(f, fieldnames=campos)
        if nuevo:
            escritor.writeheader()
        escritor.writerows(filas)


def main() -> None:
    vocabulario = CONFIG["vocabulario"]
    seleccion = [p.lower() for p in sys.argv[1:]]
    if seleccion:
        vocabulario = [v for v in vocabulario if v["palabra"] in seleccion]
        if not vocabulario:
            print(f"Ninguna palabra coincide. Disponibles: "
                  f"{[v['palabra'] for v in CONFIG['vocabulario']]}")
            return

    objetivo = CONFIG["muestras_por_palabra_objetivo"]
    alias = CONFIG["participante"]["alias"]
    print("=" * 60)
    print("  SESIÓN DE GRABACIÓN — MVP predicción de voz")
    print(f"  Participante: {alias} | Objetivo: {objetivo} muestras/palabra")
    print("  Consejo: ambiente silencioso, micrófono a ~15 cm de la boca.")
    print("=" * 60)

    filas = []
    for item in vocabulario:
        palabra, emoji = item["palabra"], item["emoji"]
        carpeta = DIR_DATOS / palabra
        carpeta.mkdir(parents=True, exist_ok=True)
        actuales = len(list(carpeta.glob(f"{palabra}_*.wav")))
        print(f"\n▶ «{palabra}» — tienes {actuales}/{objetivo} muestras")
        while actuales < objetivo:
            numero = siguiente_numero(carpeta, palabra)
            ruta = grabar_muestra(palabra, emoji, numero)
            if ruta is None:
                break
            filas.append({
                "fecha_hora": datetime.now().isoformat(timespec="seconds"),
                "alias": alias, "palabra": palabra,
                "archivo": ruta.name, "observaciones": "",
            })
            actuales += 1

    if filas:
        registrar_sesion(filas)
        print(f"\n✅ Sesión terminada: {len(filas)} muestras nuevas registradas.")
        print("Siguiente paso:  python src/entrenar.py")
    else:
        print("\nSesión sin muestras nuevas.")


if __name__ == "__main__":
    main()
