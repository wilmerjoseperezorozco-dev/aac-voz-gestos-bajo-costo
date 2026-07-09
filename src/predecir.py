"""Predicción en vivo: escucha una emisión de voz, predice la palabra y la
pronuncia con voz sintetizada (el "puente" comunicativo del MVP).

Uso:
    python src/predecir.py
Cada intento queda registrado en registros/predicciones.csv para medir la
efectividad real del sistema durante las sesiones de validación.
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
sys.path.insert(0, str(RAIZ / "src"))

from audio_features import extraer_mfcc  # noqa: E402
from modelo import ClasificadorPalabras  # noqa: E402

DIR_AUDIOS_VIVO = RAIZ / "data_vivo_confirmada"

CONFIG = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
SR = CONFIG["audio"]["frecuencia_muestreo"]
DURACION = CONFIG["audio"]["duracion_grabacion_seg"]
EMOJIS = {v["palabra"]: v["emoji"] for v in CONFIG["vocabulario"]}
DIR_REGISTROS = RAIZ / "registros"


def iniciar_tts():
    try:
        import pyttsx3
        motor = pyttsx3.init()
        for voz in motor.getProperty("voices"):
            if "spanish" in voz.name.lower() or "es-" in str(voz.id).lower() \
                    or "sabina" in voz.name.lower() or "helena" in voz.name.lower():
                motor.setProperty("voice", voz.id)
                break
        motor.setProperty("rate", 145)
        return motor
    except Exception as error:  # TTS es opcional: sin él, solo texto en pantalla
        print(f"⚠️  Voz sintetizada no disponible ({error}). Continúo sin audio.")
        return None


def hablar(motor, texto: str) -> None:
    if motor is None:
        return
    try:
        motor.say(texto)
        motor.runAndWait()
    except Exception:
        pass


def archivar_si_esquema_cambio(archivo: Path, campos_esperados: list[str]) -> None:
    """Si el CSV existente tiene un encabezado distinto (esquema viejo), lo
    archiva con marca de tiempo en vez de romper el archivo con columnas
    desalineadas — así el cambio de esquema nunca corrompe datos previos."""
    if not archivo.exists():
        return
    with archivo.open(encoding="utf-8") as f:
        encabezado = f.readline().strip().split(",")
    if encabezado != campos_esperados:
        marca = datetime.now().strftime("%Y%m%d_%H%M%S")
        destino = archivo.with_name(f"{archivo.stem}_previo_{marca}{archivo.suffix}")
        archivo.rename(destino)
        print(f"  (esquema de registro actualizado; historial anterior en {destino.name})")


def registrar(fila: dict) -> None:
    DIR_REGISTROS.mkdir(parents=True, exist_ok=True)
    archivo = DIR_REGISTROS / "predicciones.csv"
    campos = ["fecha_hora", "prediccion_evaluador_ciego", "prediccion",
              "confianza", "correcta"]
    archivar_si_esquema_cambio(archivo, campos)
    nuevo = not archivo.exists()
    with archivo.open("a", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        if nuevo:
            escritor.writeheader()
        escritor.writerow(fila)


def guardar_audio_vivo(audio: np.ndarray, palabra_real: str, sufijo: str) -> None:
    """Añade la grabación confirmada al dataset de entrenamiento, con
    condiciones reales de uso (no solo la sesión inicial de grabación)."""
    carpeta = RAIZ / "data" / palabra_real
    carpeta.mkdir(parents=True, exist_ok=True)
    existentes = len(list(carpeta.glob(f"{palabra_real}_vivo_{sufijo}_*.wav")))
    ruta = carpeta / f"{palabra_real}_vivo_{sufijo}_{existentes + 1:03d}.wav"
    sf.write(ruta, audio, SR)
    print(f"  📥 Añadida a data/{palabra_real}/ como refuerzo ({ruta.name})")


def main() -> None:
    ruta_modelo = RAIZ / "modelos" / "modelo_yp"
    if not ruta_modelo.with_suffix(".npz").exists():
        print("❌ No hay modelo entrenado. Primero ejecuta: python src/entrenar.py")
        return
    modelo = ClasificadorPalabras.cargar(ruta_modelo)
    motor = iniciar_tts()
    umbral = modelo.umbral_confianza
    vocabulario = sorted(set(modelo.etiquetas))

    print("=" * 60)
    print("  PREDICCIÓN EN VIVO — MVP predicción de voz")
    print(f"  Vocabulario: {vocabulario}")
    print("  ENTER = escuchar | q + ENTER = salir")
    print("=" * 60)

    while True:
        orden = input("\nPresiona ENTER para escuchar... ").strip().lower()
        if orden == "q":
            break
        print("🎙️  Escuchando...", flush=True)
        audio = sd.rec(int(DURACION * SR), samplerate=SR, channels=1,
                       dtype="float32")
        sd.wait()
        audio = audio.flatten()
        if float(np.sqrt(np.mean(audio ** 2))) < 1e-4:
            print("  (silencio — no se detectó voz)")
            continue

        prediccion_ciego = input(
            "  👁️  Evaluador ciego (sin ver pantalla): ¿qué palabra cree que "
            "dijo? (ENTER si no hay evaluador hoy): ").strip().lower()

        inicio = time.perf_counter()
        secuencia = extraer_mfcc(audio, SR, n_mfcc=CONFIG["audio"]["n_mfcc"])
        palabra, confianza = modelo.predecir(secuencia)
        latencia = time.perf_counter() - inicio

        emoji = EMOJIS.get(palabra, "")
        if confianza >= umbral:
            print(f"\n  ➤ {emoji}  «{palabra.upper()}»  "
                  f"(confianza {confianza*100:.0f}%, {latencia:.2f}s)")
            hablar(motor, palabra)
        else:
            print(f"\n  ➤ No estoy seguro (mejor opción: {palabra}, "
                  f"{confianza*100:.0f}%). Intenta de nuevo.")

        respuesta = input("  ¿Fue correcta? (s/n/ENTER para omitir): ").strip().lower()
        correcta = {"s": "si", "n": "no"}.get(respuesta, "")
        registrar({
            "fecha_hora": datetime.now().isoformat(timespec="seconds"),
            "prediccion_evaluador_ciego": prediccion_ciego,
            "prediccion": palabra,
            "confianza": round(confianza, 3),
            "correcta": correcta,
        })

        if correcta == "si":
            guardar_audio_vivo(audio, palabra, "ok")
        elif correcta == "no":
            print(f"  Vocabulario: {', '.join(vocabulario)}")
            real = input("  ¿Qué palabra dijo en realidad? "
                         "(nombre exacto o ENTER si no sabes): ").strip().lower()
            if real in vocabulario:
                guardar_audio_vivo(audio, real, "correccion")

    print("\nSesión terminada. Registros en registros/predicciones.csv")
    print("Si añadiste refuerzos, reentrena con:  python src/entrenar.py")


if __name__ == "__main__":
    main()
