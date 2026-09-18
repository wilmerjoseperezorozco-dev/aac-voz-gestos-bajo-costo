"""Prueba de persecución con la mirada: ¿YP sigue un blanco con la vista?

Uso:
    py -3.12 src/persecucion_mirada.py            # blanco automático (24 s)
    py -3.12 src/persecucion_mirada.py --mouse    # el blanco es TU mouse
    py -3.12 src/persecucion_mirada.py --seg 40
    py -3.12 src/persecucion_mirada.py --ventana   # ventana en vez de pantalla completa

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
import threading
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


class HiloCamara(threading.Thread):
    """Lee la cámara y detecta la cara en un hilo aparte, para que el blanco
    se dibuje fluido (~60 fps) aunque la cámara vaya a 20-30 fps."""

    def __init__(self, cap, cara):
        super().__init__(daemon=True)
        self.cap, self.cara = cap, cara
        self.bloqueo = threading.Lock()
        self.fase = None            # (inicio, blanco_fn, grabar_desde)
        self.filas, self.total = [], 0
        self.cara_ok = False
        self.parar = False

    def iniciar_fase(self, blanco_fn, grabar_desde=0.0):
        with self.bloqueo:
            self.filas, self.total = [], 0
            self.fase = (time.monotonic(), blanco_fn, grabar_desde)

    def resultado(self):
        with self.bloqueo:
            self.fase = None
            filas = np.array(self.filas) if self.filas else np.empty((0, 18))
            return filas, self.total

    def run(self):
        while not self.parar:
            ok, frame = self.cap.read()
            if not ok:
                continue
            imagen = mp.Image(image_format=mp.ImageFormat.SRGB,
                              data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            res = self.cara.detect_for_video(
                imagen, int((time.monotonic() - _T0) * 1000))
            rasgos = None
            if res.face_landmarks and res.face_blendshapes:
                blend = {c.category_name: c.score for c in res.face_blendshapes[0]}
                rasgos = rasgos_mirada(res.face_landmarks[0], blend)
            self.cara_ok = rasgos is not None
            with self.bloqueo:
                if self.fase is None:
                    continue
                inicio, blanco_fn, grabar_desde = self.fase
                t = time.monotonic() - inicio
                self.total += 1
                if t >= grabar_desde and rasgos is not None:
                    bx, by = blanco_fn(t)
                    self.filas.append(np.concatenate([[t, bx, by], rasgos]))


def dibujar(pantalla, bx, by, texto, cara_ok):
    ancho, alto = pantalla
    lienzo = np.zeros((alto, ancho, 3), np.uint8)
    if bx is not None:
        cv2.circle(lienzo, (int(bx), int(by)), 26, (255, 255, 255), -1)
        cv2.circle(lienzo, (int(bx), int(by)), 9, (0, 0, 255), -1)
    cv2.putText(lienzo, texto, (30, 50), cv2.FONT_HERSHEY_SIMPLEX,
                0.9, (200, 200, 200), 2)
    cv2.circle(lienzo, (30, alto - 30), 8,
               (0, 200, 0) if cara_ok else (0, 0, 255), -1)  # cara detectada
    return lienzo


def correr_fase(hilo, pantalla, duracion, blanco_fn, texto, grabar_desde=0.0):
    """Dibuja el blanco `duracion` s a ~60 fps mientras el hilo captura."""
    hilo.iniciar_fase(blanco_fn, grabar_desde)
    inicio = time.monotonic()
    while True:
        t = time.monotonic() - inicio
        if t >= duracion:
            break
        bx, by = blanco_fn(t)
        cv2.imshow(VENTANA, dibujar(pantalla, bx, by, texto, hilo.cara_ok))
        espera = max(1, int(1000 / 60 - (time.monotonic() - inicio - t) * 1000))
        if cv2.waitKey(espera) == 27:
            raise KeyboardInterrupt
    return hilo.resultado()


def esperar_espacio(hilo, pantalla, texto):
    """Pantalla de inicio DENTRO de la ventana (la consola queda tapada)."""
    while True:
        cv2.imshow(VENTANA, dibujar(pantalla, None, None, texto, hilo.cara_ok))
        tecla = cv2.waitKey(30)
        if tecla == 27:
            raise KeyboardInterrupt
        if tecla == 32:
            return


def main() -> None:
    args = sys.argv[1:]
    modo_mouse = "--mouse" in args
    ventana = "--ventana" in args
    rapido = "--rapido" in args            # prueba corta (humo/depuración)
    sin_espera = "--sin-espera" in args
    duracion = 4.0 if rapido else 24.0
    if "--seg" in args:
        duracion = float(args[args.index("--seg") + 1])
    asentar, grabar = (0.3, 0.5) if rapido else (ASENTAR_SEG, GRABAR_SEG)

    pantalla = (960, 540) if ventana else tamano_pantalla()
    cara = crear_detector()
    cap = cv2.VideoCapture(CONFIG["camara"]["indice"], cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise SystemExit("No se pudo abrir la cámara")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    hilo = HiloCamara(cap, cara)
    hilo.start()

    # La ventana se crea DESPUÉS de todo lo que usa la consola, y el inicio
    # se confirma con ESPACIO dentro de la ventana (a pantalla completa
    # tapa la consola: un input() aquí quedaría invisible).
    if ventana:
        cv2.namedWindow(VENTANA, cv2.WINDOW_AUTOSIZE)
    else:
        cv2.namedWindow(VENTANA, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(VENTANA, cv2.WND_PROP_FULLSCREEN,
                              cv2.WINDOW_FULLSCREEN)
    mouse = [pantalla[0] / 2, pantalla[1] / 2]
    cv2.setMouseCallback(
        VENTANA, lambda e, x, y, f, p: mouse.__setitem__(slice(0, 2), [x, y]))

    print("=" * 60)
    print("  PERSECUCIÓN CON LA MIRADA — "
          + ("blanco = mouse" if modo_mouse else "blanco automático"))
    print("  Sigue las instrucciones EN LA VENTANA. ESC aborta.")
    print("=" * 60)

    try:
        if not sin_espera:
            esperar_espacio(hilo, pantalla,
                            "Punto verde = cara detectada. ESPACIO para empezar")
        calib = []
        for i, (px, py) in enumerate(puntos_calibracion(pantalla), 1):
            f, _ = correr_fase(hilo, pantalla, asentar + grabar,
                               lambda t, px=px, py=py: (px, py),
                               f"Mira el punto  {i}/9", grabar_desde=asentar)
            if len(f):
                calib.append(f)
        calib = np.vstack(calib) if calib else np.empty((0, 18))
        min_frames = 30 if rapido else MIN_FRAMES
        if len(calib) < min_frames:
            print(f"\n❌ Solo {len(calib)} frames de calibración con cara "
                  "válida. Mejor luz y la cara centrada frente a la cámara.")
            return
        modelo = ajustar_ridge(calib[:, 3:], calib[:, 1:3])
        err_cal = np.linalg.norm(
            predecir(modelo, calib[:, 3:]) - calib[:, 1:3], axis=1)
        print(f"\n  Calibración: {len(calib)} frames, error de ajuste "
              f"{np.sqrt(np.mean(err_cal ** 2)):.0f} px (optimista: mismos datos).")

        centro = (pantalla[0] / 2, pantalla[1] / 2)
        correr_fase(hilo, pantalla, 1.5 if rapido else 3.0, lambda t: centro,
                    "Ahora sigue el punto que se mueve...")
        if modo_mouse:
            blanco_fn = lambda t: (mouse[0], mouse[1])  # noqa: E731
        else:
            blanco_fn = lambda t: tuple(  # noqa: E731
                trayectoria_auto(np.array([t]), pantalla)[0])
        datos, total = correr_fase(hilo, pantalla, duracion, blanco_fn,
                                   "Sigue el punto con la vista")
    except KeyboardInterrupt:
        print("\nAbortado.")
        return
    finally:
        hilo.parar = True
        hilo.join(timeout=2)
        cap.release()
        cv2.destroyAllWindows()

    min_frames = 30 if rapido else MIN_FRAMES
    if len(datos) < min_frames:
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

    if rapido:
        print("\n  (--rapido: prueba corta, no se guarda nada)")
        return
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
