"""Predicción combinando voz + gesto — CAPTURA SECUENCIAL, no simultánea.

Se midió que pedirle a YP hablar y gesticular al mismo tiempo degrada
ambos canales de ~80% a ~30-37% (interferencia cognitivo-motora de doble
tarea, ver reportes/hallazgo_interferencia_20260708.md). El diseño correcto
es usar el gesto como DESEMPATE cuando la voz no está segura, cada uno con
toda la atención de YP, nunca a la vez.

Uso:
    python src/multimodal_predecir.py
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

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from audio_features import extraer_mfcc  # noqa: E402
from gestos_features import LectorGestos  # noqa: E402
from modelo import ClasificadorPalabras  # noqa: E402
from predecir import archivar_si_esquema_cambio, hablar, iniciar_tts  # noqa: E402

CONFIG = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
SR = CONFIG["audio"]["frecuencia_muestreo"]
DURACION_VOZ = CONFIG["audio"]["duracion_grabacion_seg"]
DURACION_GESTO = CONFIG["camara"]["duracion_captura_seg"]
EMOJIS_VOZ = {v["palabra"]: v["emoji"] for v in CONFIG["vocabulario"]}
GESTO_A_SIGNIFICADO = {g["gesto"]: g["significado"] for g in CONFIG["gestos"]}
DIR_REGISTROS = RAIZ / "registros"


def registrar(fila: dict) -> None:
    DIR_REGISTROS.mkdir(exist_ok=True)
    archivo = DIR_REGISTROS / "predicciones_multimodal.csv"
    campos = ["fecha_hora", "prediccion_evaluador_ciego", "modo",
              "prediccion_voz", "confianza_voz", "prediccion_gesto",
              "confianza_gesto", "resultado_fusion", "correcta"]
    archivar_si_esquema_cambio(archivo, campos)
    nuevo = not archivo.exists()
    with archivo.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        if nuevo:
            w.writeheader()
        w.writerow(fila)


def capturar_voz() -> np.ndarray:
    audio = sd.rec(int(DURACION_VOZ * SR), samplerate=SR, channels=1,
                   dtype="float32")
    sd.wait()
    return audio.flatten()


def main() -> None:
    ruta_voz = RAIZ / "modelos" / "modelo_yp"
    ruta_gestos = RAIZ / "modelos" / "modelo_gestos"
    if not ruta_voz.with_suffix(".npz").exists():
        print("❌ Falta el modelo de voz. Ejecuta: python src/entrenar.py")
        return
    if not ruta_gestos.with_suffix(".npz").exists():
        print("❌ Falta el modelo de gestos. Ejecuta: python src/gestos_entrenar.py")
        return

    modelo_voz = ClasificadorPalabras.cargar(ruta_voz)
    modelo_gestos = ClasificadorPalabras.cargar(ruta_gestos)
    lector = LectorGestos(RAIZ / CONFIG["camara"]["modelo_pose"],
                          CONFIG["camara"]["indice"])
    motor = iniciar_tts()

    print("=" * 60)
    print("  PREDICCIÓN COMBINADA — voz primero, gesto como desempate")
    print(f"  Vocabulario voz: {sorted(set(modelo_voz.etiquetas))}")
    print(f"  Gestos disponibles: {sorted(set(modelo_gestos.etiquetas))}")
    print("  ENTER = intentar | q + ENTER = salir")
    print("=" * 60)

    while True:
        orden = input("\nENTER para hablar... ").strip().lower()
        if orden == "q":
            break

        print("🎙️  Escuchando (solo voz)...", flush=True)
        inicio = time.perf_counter()
        audio = capturar_voz()
        if float(np.sqrt(np.mean(audio ** 2))) < 1e-4:
            print("  (silencio — no se detectó voz)")
            continue

        prediccion_ciego = input(
            "  👁️  Evaluador ciego (sin ver pantalla): ¿qué cree que "
            "dijo/hizo? (ENTER si no hay evaluador hoy): ").strip().lower()

        secuencia_voz = extraer_mfcc(audio, SR, n_mfcc=CONFIG["audio"]["n_mfcc"])
        palabra_voz, conf_voz = modelo_voz.predecir(secuencia_voz)
        latencia = time.perf_counter() - inicio

        resultado, modo = None, "voz_sola"
        gesto, conf_gesto = "", 0.0

        if conf_voz >= modelo_voz.umbral_confianza:
            resultado = palabra_voz
        else:
            print(f"  [voz: «{palabra_voz}» {conf_voz*100:.0f}% — no es suficiente]")
            print("  🎥 Ahora SOLO el gesto (sin hablar) para desempatar...")
            try:
                secuencia_gesto = lector.capturar(
                    DURACION_GESTO, mostrar=True, titulo="Solo el gesto")
                gesto, conf_gesto = modelo_gestos.predecir(secuencia_gesto)
                significado_gesto = GESTO_A_SIGNIFICADO.get(gesto, gesto)
                modo = "gesto_desempate"
                if conf_gesto >= modelo_gestos.umbral_confianza:
                    resultado = significado_gesto
            except RuntimeError as error:
                print(f"  ⚠️  {error}")

        if resultado:
            emoji = EMOJIS_VOZ.get(resultado, "")
            print(f"\n  ➤ {emoji}  «{resultado.upper()}»  ({modo}, {latencia:.2f}s)")
            hablar(motor, resultado)
        else:
            modo = "sin_confianza"
            print(f"\n  ➤ No estoy seguro por ningún canal. Intenta de nuevo.")

        resp = input("  ¿Fue correcto? (s/n/ENTER omite): ").strip().lower()
        registrar({
            "fecha_hora": datetime.now().isoformat(timespec="seconds"),
            "prediccion_evaluador_ciego": prediccion_ciego,
            "modo": modo,
            "prediccion_voz": palabra_voz, "confianza_voz": round(conf_voz, 3),
            "prediccion_gesto": GESTO_A_SIGNIFICADO.get(gesto, gesto),
            "confianza_gesto": round(conf_gesto, 3),
            "resultado_fusion": resultado or "",
            "correcta": {"s": "si", "n": "no"}.get(resp, ""),
        })

    print("\nSesión terminada. Registros en registros/predicciones_multimodal.csv")


if __name__ == "__main__":
    main()
