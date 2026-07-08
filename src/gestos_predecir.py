"""Predicción de gestos en vivo con voz sintetizada (espejo de predecir.py).

Uso:
    python src/gestos_predecir.py
Registra cada intento en registros/predicciones_gestos.csv.
"""

from __future__ import annotations

import csv
import json
import sys
import time
from datetime import datetime
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from gestos_features import LectorGestos  # noqa: E402
from modelo import ClasificadorPalabras  # noqa: E402
from predecir import iniciar_tts, hablar  # noqa: E402

CONFIG = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
SIGNIFICADOS = {g["gesto"]: g["significado"] for g in CONFIG["gestos"]}
DIR_REGISTROS = RAIZ / "registros"


def registrar(fila: dict) -> None:
    DIR_REGISTROS.mkdir(exist_ok=True)
    archivo = DIR_REGISTROS / "predicciones_gestos.csv"
    nuevo = not archivo.exists()
    with archivo.open("a", newline="", encoding="utf-8") as f:
        campos = ["fecha_hora", "gesto", "significado", "confianza", "correcta"]
        w = csv.DictWriter(f, fieldnames=campos)
        if nuevo:
            w.writeheader()
        w.writerow(fila)


def main() -> None:
    ruta_modelo = RAIZ / "modelos" / "modelo_gestos"
    if not ruta_modelo.with_suffix(".npz").exists():
        print("❌ No hay modelo. Primero: python src/gestos_entrenar.py")
        return
    modelo = ClasificadorPalabras.cargar(ruta_modelo)
    lector = LectorGestos(RAIZ / CONFIG["camara"]["modelo_pose"],
                          CONFIG["camara"]["indice"])
    motor = iniciar_tts()

    print("=" * 60)
    print("  PREDICCIÓN DE GESTOS EN VIVO")
    print(f"  Gestos: {sorted(set(modelo.etiquetas))}")
    print("  ENTER = capturar | q + ENTER = salir")
    print("=" * 60)

    while True:
        orden = input("\nENTER para capturar gesto... ").strip().lower()
        if orden == "q":
            break
        print("🎥 Capturando...", flush=True)
        try:
            secuencia = lector.capturar(
                CONFIG["camara"]["duracion_captura_seg"], mostrar=True,
                titulo="¡Haz el gesto!")
        except RuntimeError as error:
            print(f"  ⚠️  {error}")
            continue

        inicio = time.perf_counter()
        gesto, confianza = modelo.predecir(secuencia)
        latencia = time.perf_counter() - inicio
        significado = SIGNIFICADOS.get(gesto, gesto)

        if confianza >= modelo.umbral_confianza:
            print(f"\n  ➤ «{significado.upper()}» (gesto {gesto}, "
                  f"confianza {confianza*100:.0f}%, {latencia:.2f}s)")
            hablar(motor, significado)
        else:
            print(f"\n  ➤ No estoy seguro (mejor opción: {gesto}, "
                  f"{confianza*100:.0f}%).")

        resp = input("  ¿Fue correcto? (s/n/ENTER omite): ").strip().lower()
        registrar({
            "fecha_hora": datetime.now().isoformat(timespec="seconds"),
            "gesto": gesto, "significado": significado,
            "confianza": round(confianza, 3),
            "correcta": {"s": "si", "n": "no"}.get(resp, ""),
        })

    print("\nSesión terminada. Registros en registros/predicciones_gestos.csv")


if __name__ == "__main__":
    main()
