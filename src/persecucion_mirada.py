"""Prueba de persecución con la mirada: ¿YP sigue un blanco con la vista?

Uso:
    py -3.12 src/persecucion_mirada.py            # blanco automático (24 s)
    py -3.12 src/persecucion_mirada.py --mouse    # el blanco es TU mouse
    py -3.12 src/persecucion_mirada.py --seg 40

Fase 1  Calibración: 9 puntos fijos en pantalla; YP los mira uno a uno.
        Se ajusta una regresión rasgos-oculares -> posición en pantalla.
Fase 2  Persecución: un blanco se mueve suave (automático, o el mouse
        que mueves tú); YP lo sigue con la vista. La calibración no ve
        estos datos: las métricas miden generalización.

Reporta error (px y % de diagonal), mejora frente a predecir el centro,
correlación por eje y retardo de la mirada. Todo es exploratorio: una
webcam y una sola persona dan una estimación de mirada gruesa.

Requiere modelos/face_landmarker.task. Los datos (biometría ocular) se
guardan en data_mirada/, fuera de GitHub. ESC aborta.
"""

from __future__ import annotations

import csv
import ctypes
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

if sys.stdout is not None and sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from mirada_modelo import (ajustar_ridge, metricas_persecucion,  # noqa: E402
                           predecir, puntos_calibracion, rasgos_mirada,
                           suavizar, trayectoria_auto)

CONFIG = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
MODELO_CARA = RAIZ / "modelos" / "face_landmarker.task"
DIR_DATOS = RAIZ / "data_mirada"
DIR_REGISTROS = RAIZ / "registros"
VENTANA = "Persecucion con la mirada"
ASENTAR_SEG, GRABAR_SEG = 1.0, 1.5      # por punto de calibración
MIN_FRAMES = 100
_T0 = time.monotonic()


def tamano_pantalla() -> tuple[int, int]:
    u = ctypes.windll.user32
    return int(u.GetSystemMetrics(0)), int(u.GetSystemMetrics(1))


def crear_detector() -> vision.FaceLandmarker:
    if not MODELO_CARA.exists():
        raise SystemExit(
            f"Falta el modelo facial: {MODELO_CARA}\n"
            "Descarga face_landmarker.task (~3.7 MB, oficial de Google "
            "MediaPipe) y guárdalo en esa ruta.")
    return vision.FaceLandmarker.create_from_options(
        vision.FaceLandmarkerOptions(
            base_options=mp_python.BaseOptions(
                model_asset_path=str(MODELO_CARA)),
            running_mode=vision.RunningMode.VIDEO,
            num_faces=1, output_face_blendshapes=True))


def correr_fase(cap, cara, pantalla, duracion, blanco_fn, texto, grabar_desde=0.0):
    """Muestra el blanco `duracion` s y captura rasgos de mirada.
    Devuelve (matriz [t, bx, by, rasgos...], total_frames)."""
    ancho, alto = pantalla
    filas, total, inicio = [], 0, time.monotonic()
    while True:
        t = time.monotonic() - inicio
        if t >= duracion:
            break
        bx, by = blanco_fn(t)
        ok, frame = cap.read()
        if not ok:
            continue
        total += 1
        imagen = mp.Image(image_format=mp.ImageFormat.SRGB,
                          data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        res = cara.detect_for_video(imagen, int((time.monotonic() - _T0) * 1000))
        rasgos = None
        if res.face_landmarks and res.face_blendshapes:
            blend = {c.category_name: c.score for c in res.face_blendshapes[0]}
            rasgos = rasgos_mirada(res.face_landmarks[0], blend)
        if t >= grabar_desde and rasgos is not None:
            filas.append(np.concatenate([[t, bx, by], rasgos]))

        lienzo = np.zeros((alto, ancho, 3), np.uint8)
        cv2.circle(lienzo, (int(bx), int(by)), 26, (255, 255, 255), -1)
        cv2.circle(lienzo, (int(bx), int(by)), 9, (0, 0, 255), -1)
        cv2.putText(lienzo, texto, (30, 50), cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, (200, 200, 200), 2)
        color = (0, 200, 0) if rasgos is not None else (0, 0, 255)
        cv2.circle(lienzo, (30, alto - 30), 8, color, -1)   # cara detectada
        cv2.imshow(VENTANA, lienzo)
        if cv2.waitKey(1) == 27:
            raise KeyboardInterrupt
    return (np.array(filas) if filas else np.empty((0, 18))), total


def main() -> None:
    args = sys.argv[1:]
    modo_mouse = "--mouse" in args
    duracion = 24.0
    if "--seg" in args:
        duracion = float(args[args.index("--seg") + 1])

    pantalla = tamano_pantalla()
    cara = crear_detector()
    cap = cv2.VideoCapture(CONFIG["camara"]["indice"], cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise SystemExit("No se pudo abrir la cámara")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    cv2.namedWindow(VENTANA, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(VENTANA, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    mouse = [pantalla[0] / 2, pantalla[1] / 2]
    cv2.setMouseCallback(VENTANA, lambda e, x, y, f, p: mouse.__setitem__(slice(0, 2), [x, y]))

    print("=" * 60)
    print("  PERSECUCIÓN CON LA MIRADA — "
          + ("blanco = mouse" if modo_mouse else "blanco automático"))
    print("  YP frente a la pantalla, cara bien iluminada, cabeza cómoda.")
    print("  Punto verde abajo-izquierda = cara detectada. ESC aborta.")
    print("=" * 60)
    input("  ENTER para empezar la calibración...")

    try:
        calib = []
        for i, (px, py) in enumerate(puntos_calibracion(pantalla), 1):
            fija = lambda t, px=px, py=py: (px, py)  # noqa: E731
            f, _ = correr_fase(cap, cara, pantalla, ASENTAR_SEG + GRABAR_SEG,
                               fija, f"Mira el punto  {i}/9",
                               grabar_desde=ASENTAR_SEG)
            if len(f):
                calib.append(f)
        calib = np.vstack(calib) if calib else np.empty((0, 18))
        if len(calib) < MIN_FRAMES:
            print(f"\n❌ Solo {len(calib)} frames de calibración con cara "
                  "válida. Mejor luz y la cara centrada frente a la cámara.")
            return
        modelo = ajustar_ridge(calib[:, 3:], calib[:, 1:3])
        err_cal = np.linalg.norm(predecir(modelo, calib[:, 3:]) - calib[:, 1:3], axis=1)
        print(f"\n  Calibración: {len(calib)} frames, error de ajuste "
              f"{np.sqrt(np.mean(err_cal ** 2)):.0f} px (optimista: mismos datos).")

        f, _ = correr_fase(cap, cara, pantalla, 3.0,
                           lambda t: (pantalla[0] / 2, pantalla[1] / 2),
                           "Ahora sigue el punto que se mueve...")
        if modo_mouse:
            blanco_fn = lambda t: (mouse[0], mouse[1])  # noqa: E731
        else:
            blanco_fn = lambda t: tuple(trayectoria_auto(np.array([t]), pantalla)[0])  # noqa: E731
        datos, total = correr_fase(cap, cara, pantalla, duracion, blanco_fn,
                                   "Sigue el punto con la vista")
    except KeyboardInterrupt:
        print("\nAbortado.")
        return
    finally:
        cap.release()
        cv2.destroyAllWindows()

    if len(datos) < MIN_FRAMES:
        print(f"\n❌ Solo {len(datos)} frames válidos en la persecución "
              f"(de {total}). No alcanza para analizar.")
        return
    t, blanco = datos[:, 0], datos[:, 1:3]
    pred = suavizar(predecir(modelo, datos[:, 3:]), 5)
    m = metricas_persecucion(t, blanco, pred, pantalla)

    print("\n" + "=" * 60)
    print("  RESULTADO (calibración y persecución son datos distintos)")
    print("=" * 60)
    print(f"  Frames válidos: {m['n_frames']} de {total} "
          f"({m['n_frames'] / total:.0%}; el resto: parpadeo o sin cara)")
    print(f"  Error medio: {m['rmse_px']:.0f} px = {m['rmse_pct_diagonal']:.1f}% "
          "de la diagonal de pantalla")
    print(f"  Línea base (mirar siempre al centro): {m['rmse_linea_base_px']:.0f} px "
          f"-> mejora {m['mejora_vs_constante']:.0%}")
    print(f"  Correlación con el blanco: x={m['r_x']:.2f}  y={m['r_y']:.2f}")
    print(f"  Retardo de la mirada: x={m['retardo_x_ms']:.0f} ms  "
          f"y={m['retardo_y_ms']:.0f} ms")
    print("  Lectura: correlación alta + mejora positiva = sí hay persecución")
    print("  detectable; el error en px dice qué tan fina es la estimación.")

    DIR_DATOS.mkdir(exist_ok=True)
    sello = datetime.now().strftime("%Y%m%d_%H%M%S")
    np.savez_compressed(DIR_DATOS / f"persecucion_{sello}.npz",
                        calibracion=calib, persecucion=datos, prediccion=pred,
                        pantalla=np.array(pantalla), modo_mouse=modo_mouse)
    DIR_REGISTROS.mkdir(exist_ok=True)
    archivo = DIR_REGISTROS / "sesiones_mirada.csv"
    nuevo = not archivo.exists()
    with archivo.open("a", newline="", encoding="utf-8") as fh:
        campos = {"fecha_hora": datetime.now().isoformat(timespec="seconds"),
                  "alias": CONFIG["participante"]["alias"],
                  "modo": "mouse" if modo_mouse else "auto", **m}
        w = csv.DictWriter(fh, fieldnames=list(campos))
        if nuevo:
            w.writeheader()
        w.writerow(campos)
    print(f"\n  Guardado en data_mirada/persecucion_{sello}.npz")


if __name__ == "__main__":
    main()
