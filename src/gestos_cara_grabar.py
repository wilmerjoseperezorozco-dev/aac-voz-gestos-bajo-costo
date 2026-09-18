"""Sesión nueva de si/no/ayuda con captura pareada de pose + cara.

Uso:
    py -3.12 src/gestos_cara_grabar.py            # 10 muestras nuevas por gesto
    py -3.12 src/gestos_cara_grabar.py 5          # 5 muestras nuevas por gesto
    py -3.12 src/gestos_cara_grabar.py 5 si_mano_arriba

A diferencia de gestos_grabar.py, NO usa el contador de muestras
existentes: siempre captura N muestras nuevas, en una carpeta aparte
(data_gestos_cara/), para no mezclar esta exploración con los datos
del modelo validado.

Por cada muestra guarda en un .npz:
  secuencia     rasgos de pose, idénticos a los del pipeline validado
                (compatibles con modelos/modelo_gestos.npz)
  blendshapes   (frames, 52) coeficientes faciales de MediaPipe; incluye
                parpadeo, mirada (eyeLook*), párpado y cejas. NaN si no
                se detectó cara en ese frame.
  ojos          (frames, 12) puntos crudos x,y: iris A, esquinas de ese
                ojo, iris B, esquinas del otro ojo. NaN sin cara.
  nombres_blendshapes

Requiere modelos/face_landmarker.task (MediaPipe Face Landmarker).
La cara es un canal pasivo: YP solo hace el gesto de siempre.
"""

from __future__ import annotations

import csv
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

from gestos_features import LectorGestos  # noqa: E402

CONFIG = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
DIR_DATOS = RAIZ / "data_gestos_cara"
DIR_REGISTROS = RAIZ / "registros"
MODELO_CARA = RAIZ / "modelos" / "face_landmarker.task"
DURACION = CONFIG["camara"]["duracion_captura_seg"]
MUESTRAS_POR_DEFECTO = 10

# Iris (468, 473) y esquinas de cada ojo en la malla de 478 puntos.
_PUNTOS_OJOS = [468, 33, 133, 473, 362, 263]


def crear_detector_cara() -> vision.FaceLandmarker:
    if not MODELO_CARA.exists():
        raise SystemExit(
            f"Falta el modelo facial: {MODELO_CARA}\n"
            "Descárgalo (face_landmarker.task, ~3.7 MB, oficial de Google "
            "MediaPipe) y guárdalo en esa ruta.")
    opciones = vision.FaceLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(MODELO_CARA)),
        running_mode=vision.RunningMode.VIDEO,
        num_faces=1,
        output_face_blendshapes=True)
    return vision.FaceLandmarker.create_from_options(opciones)


def capturar_pareado(lector: LectorGestos, cara: vision.FaceLandmarker,
                     titulo: str):
    """Devuelve (secuencia_pose, blendshapes, ojos, nombres, tasa_cara)."""
    cap = cv2.VideoCapture(lector.indice_camara, cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise RuntimeError("No se pudo abrir la cámara")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    cv2.namedWindow("Camara - gestos + cara", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Camara - gestos + cara", 1280, 720)

    pose_frames, blend_frames, ojos_frames = [], [], []
    nombres: list[str] = []
    inicio = time.monotonic()
    try:
        while time.monotonic() - inicio < DURACION:
            ok, frame = cap.read()
            if not ok:
                continue
            imagen = mp.Image(image_format=mp.ImageFormat.SRGB,
                              data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            marca_ms = int((time.monotonic() - lector._t0) * 1000)
            res_pose = lector.detector.detect_for_video(imagen, marca_ms)
            res_cara = cara.detect_for_video(imagen, marca_ms)

            rasgos = (lector._rasgos_de_frame(res_pose.pose_landmarks)
                      if res_pose.pose_landmarks else None)
            if rasgos is not None:
                pose_frames.append(rasgos)
                if res_cara.face_blendshapes and res_cara.face_landmarks:
                    cats = res_cara.face_blendshapes[0]
                    if not nombres:
                        nombres = [c.category_name for c in cats]
                    blend_frames.append([c.score for c in cats])
                    lm = res_cara.face_landmarks[0]
                    ojos_frames.append(
                        [v for i in _PUNTOS_OJOS for v in (lm[i].x, lm[i].y)])
                else:
                    blend_frames.append([np.nan] * 52)
                    ojos_frames.append([np.nan] * 12)

            if res_pose.pose_landmarks:
                lector._dibujar_personas(frame, res_pose.pose_landmarks)
            if res_cara.face_landmarks:
                h, w = frame.shape[:2]
                for i in _PUNTOS_OJOS:
                    p = res_cara.face_landmarks[0][i]
                    cv2.circle(frame, (int(p.x * w), int(p.y * h)), 3,
                               (0, 255, 255), -1)
            restante = DURACION - (time.monotonic() - inicio)
            cv2.putText(frame, f"{titulo} {restante:.1f}s", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            cv2.imshow("Camara - gestos + cara", frame)
            cv2.waitKey(1)
    finally:
        cap.release()
        cv2.destroyAllWindows()

    if len(pose_frames) < 5:
        raise RuntimeError(
            f"Solo {len(pose_frames)} frames con persona detectada; "
            "verifica que YP esté frente a la cámara con buena luz")

    matriz = np.array(pose_frames)
    caracteristicas = np.hstack([matriz, np.gradient(matriz, axis=0)])
    secuencia = ((caracteristicas - caracteristicas.mean(axis=0))
                 / (caracteristicas.std(axis=0) + 1e-8))
    blend = np.array(blend_frames, dtype=float)
    ojos = np.array(ojos_frames, dtype=float)
    tasa_cara = float(np.mean(~np.isnan(blend[:, 0])))
    return secuencia, blend, ojos, nombres, tasa_cara


def main() -> None:
    args = sys.argv[1:]
    n_nuevas = MUESTRAS_POR_DEFECTO
    if args and args[0].isdigit():
        n_nuevas = int(args.pop(0))
    gestos = CONFIG["gestos"]
    if args:
        gestos = [g for g in gestos if g["gesto"] in args]
        if not gestos:
            print(f"Gestos disponibles: {[g['gesto'] for g in CONFIG['gestos']]}")
            return

    lector = LectorGestos(RAIZ / CONFIG["camara"]["modelo_pose"],
                          CONFIG["camara"]["indice"])
    cara = crear_detector_cara()
    print("=" * 60)
    print("  SESIÓN NUEVA — gestos si/no/ayuda + cara (canal pasivo)")
    print(f"  {n_nuevas} muestras NUEVAS por gesto, guardadas en data_gestos_cara/")
    print("  YP frente a la cámara, buena luz, cara y torso visibles.")
    print("=" * 60)
    lector.verificar_encuadre()

    filas = []
    for item in gestos:
        gesto, descripcion = item["gesto"], item["descripcion"]
        carpeta = DIR_DATOS / gesto
        carpeta.mkdir(parents=True, exist_ok=True)
        print(f"\n▶ Gesto «{gesto}» ({descripcion}) — {n_nuevas} muestras nuevas")
        hechas = 0
        while hechas < n_nuevas:
            existentes = sorted(carpeta.glob(f"{gesto}_*.npz"))
            numero = (int(existentes[-1].stem.split("_")[-1]) + 1) if existentes else 1
            entrada = input(f"  ENTER para capturar muestra {hechas + 1}/{n_nuevas} "
                            "(s para saltar el gesto): ").strip().lower()
            if entrada == "s":
                break
            for cuenta in ("3", "2", "1"):
                print(f"  {cuenta}...", end=" ", flush=True)
                time.sleep(0.6)
            print("¡HAZ EL GESTO AHORA! 🎥")
            try:
                secuencia, blend, ojos, nombres, tasa = capturar_pareado(
                    lector, cara, descripcion)
            except RuntimeError as error:
                print(f"  ⚠️  {error}. Repetimos.")
                continue
            ruta = carpeta / f"{gesto}_{numero:03d}.npz"
            np.savez_compressed(ruta, secuencia=secuencia, blendshapes=blend,
                                ojos=ojos, nombres_blendshapes=np.array(nombres))
            print(f"  ✅ {ruta.name}: {len(secuencia)} frames, "
                  f"cara detectada en {tasa:.0%}")
            filas.append({
                "fecha_hora": datetime.now().isoformat(timespec="seconds"),
                "alias": CONFIG["participante"]["alias"],
                "gesto": gesto, "archivo": ruta.name,
                "cara_detectada": f"{tasa:.2f}", "observaciones": "",
            })
            hechas += 1

    if filas:
        DIR_REGISTROS.mkdir(exist_ok=True)
        archivo = DIR_REGISTROS / "sesiones_gestos_cara.csv"
        nuevo = not archivo.exists()
        with archivo.open("a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
            if nuevo:
                w.writeheader()
            w.writerows(filas)
        print(f"\n✅ {len(filas)} muestras registradas.")
        print("Siguiente paso:  py -3.12 src/cara_analizar.py")
    else:
        print("\nSesión sin muestras nuevas.")


if __name__ == "__main__":
    main()
