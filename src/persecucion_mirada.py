"""Prueba de persecución: ¿YP sigue un blanco en pantalla, y con qué canal?

Uso:
    py -3.12 src/persecucion_mirada.py             # canal CABEZA (por defecto)
    py -3.12 src/persecucion_mirada.py --ojos      # canal mirada (iris)
    py -3.12 src/persecucion_mirada.py --mouse     # el blanco es TU mouse
    py -3.12 src/persecucion_mirada.py --ventana   # blanco en ventana, no pantalla completa
    py -3.12 src/persecucion_mirada.py --sin-monitor

Canal cabeza (por defecto): la observación de campo es que a YP le cuesta
mover los ojos y sigue los estímulos con la cabeza. Se mide el giro
(yaw) y la inclinación (pitch) de la cabeza contra la posición del blanco.
Canal ojos: rasgos de iris y mirada de MediaPipe (ver mirada_modelo.py).

Fase 1  Calibración: 9 puntos fijos; se ajusta una regresión ridge
        rasgos -> posición en pantalla.
Fase 2  Persecución: un blanco se mueve lento y suave (o tu mouse). La
        calibración no ve estos datos: las métricas miden generalización.

Mientras corre, una ventana pequeña "Monitor operador" (para ti, no para
YP) muestra qué está capturando el sistema y avisa de luz, distancia y
encuadre. Con 2+ monitores va al segundo; con uno, la prueba pasa a
ventana y el monitor queda al lado.

Cada sesión guarda métricas de resultado Y de entorno en
registros/sesiones_mirada.csv; `mirada_progreso.py` muestra la tendencia.
Los datos (biometría) van a data_mirada/, fuera de GitHub. ESC aborta.
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

import monitor_operador as mon  # noqa: E402
from mirada_modelo import (ajustar_ridge, angulos_cabeza,  # noqa: E402
                           error_calibracion_lopo, metricas_persecucion,
                           predecir, puntos_calibracion, rasgos_cabeza,
                           rasgos_mirada, suavizar, trayectoria_auto)

CONFIG = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
MODELO_CARA = RAIZ / "modelos" / "face_landmarker.task"
DIR_DATOS = RAIZ / "data_mirada"
DIR_REGISTROS = RAIZ / "registros"
VENTANA = "Persecucion"
MIN_FRAMES = 100
_T0 = time.monotonic()

# Tiempos por canal: la cabeza se mueve más lento que los ojos.
PARAMETROS = {
    "cabeza": dict(asentar=2.0, grabar=1.5, duracion=40.0,
                   periodos=(14.0, 20.0), max_retardo=2.0, n_rasgos=6),
    "ojos": dict(asentar=1.0, grabar=1.5, duracion=24.0,
                 periodos=(8.0, 12.0), max_retardo=1.0, n_rasgos=15),
}


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
            running_mode=vision.RunningMode.VIDEO, num_faces=1,
            output_face_blendshapes=True,
            output_facial_transformation_matrixes=True))


def extraer_ojos(res):
    if res.face_landmarks and res.face_blendshapes:
        blend = {c.category_name: c.score for c in res.face_blendshapes[0]}
        return rasgos_mirada(res.face_landmarks[0], blend)
    return None


def extraer_cabeza(res):
    if res.face_landmarks and res.facial_transformation_matrixes:
        return rasgos_cabeza(res.face_landmarks[0],
                             res.facial_transformation_matrixes[0])
    return None


class HiloCamara(threading.Thread):
    """Lee la cámara y detecta la cara en un hilo aparte, para que el blanco
    se dibuje fluido (~60 fps) aunque la cámara vaya a 20-30 fps. También
    acumula métricas del entorno y prepara la imagen del monitor."""

    def __init__(self, cap, cara, extractor, n_rasgos, con_monitor):
        super().__init__(daemon=True)
        self.cap, self.cara = cap, cara
        self.extractor, self.n_rasgos = extractor, n_rasgos
        self.con_monitor = con_monitor
        self.bloqueo = threading.Lock()
        self.fase = None            # (inicio, blanco_fn, grabar_desde)
        self.filas, self.total = [], 0
        self.cara_ok = False
        self.monitor = None
        self.fps = 0.0
        self.parar = False
        self.acum = dict(frames=0, cara=0, brillo=0.0, ancho=0.0,
                         con_aviso=0, t_ini=None, t_fin=None)

    def iniciar_fase(self, blanco_fn, grabar_desde=0.0):
        with self.bloqueo:
            self.filas, self.total = [], 0
            self.fase = (time.monotonic(), blanco_fn, grabar_desde)

    def resultado(self):
        with self.bloqueo:
            self.fase = None
            vacio = np.empty((0, 3 + self.n_rasgos))
            return (np.array(self.filas) if self.filas else vacio), self.total

    def estadisticas(self) -> dict:
        a = self.acum
        n = max(a["frames"], 1)
        dur = (a["t_fin"] - a["t_ini"]) if a["t_ini"] is not None else 0.0
        return {
            "fps": a["frames"] / dur if dur > 0 else 0.0,
            "tasa_cara": a["cara"] / n,
            "brillo": a["brillo"] / n,
            "ancho_cara_pct": 100.0 * a["ancho"] / max(a["cara"], 1),
            "pct_frames_con_aviso": 100.0 * a["con_aviso"] / n,
        }

    def _estado_monitor(self, frame, lm, res, ahora, previo):
        brillo = float(cv2.resize(frame, (160, 90)).mean())
        dt = ahora - previo
        if dt > 0:
            self.fps = 0.9 * self.fps + 0.1 / dt if self.fps else 1.0 / dt
        ancho, centrada, yaw, pitch, parp = None, True, None, None, None
        if lm is not None:
            ancho = abs(lm[454].x - lm[234].x)
            cx, cy = (lm[234].x + lm[454].x) / 2, lm[1].y
            centrada = 0.25 < cx < 0.75 and 0.2 < cy < 0.8
            if res.facial_transformation_matrixes:
                yaw, pitch, _ = angulos_cabeza(res.facial_transformation_matrixes[0])
            if res.face_blendshapes:
                b = {c.category_name: c.score for c in res.face_blendshapes[0]}
                parp = (b["eyeBlinkLeft"] + b["eyeBlinkRight"]) / 2
        avisos = mon.alertas(brillo, ancho, self.fps, centrada)
        return brillo, ancho, avisos, dict(
            fps=self.fps, brillo=brillo, yaw=yaw, pitch=pitch,
            parpadeo=parp, avisos=avisos)

    def run(self):
        previo = time.monotonic()
        while not self.parar:
            ok, frame = self.cap.read()
            if not ok:
                continue
            ahora = time.monotonic()
            imagen = mp.Image(image_format=mp.ImageFormat.SRGB,
                              data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            res = self.cara.detect_for_video(imagen, int((ahora - _T0) * 1000))
            lm = res.face_landmarks[0] if res.face_landmarks else None
            rasgos = self.extractor(res)
            self.cara_ok = rasgos is not None
            brillo, ancho, avisos, estado = self._estado_monitor(
                frame, lm, res, ahora, previo)
            previo = ahora
            if self.con_monitor:
                self.monitor = mon.anotar(frame, lm, estado)
            with self.bloqueo:
                if self.fase is None:
                    continue
                a = self.acum
                a["frames"] += 1
                a["cara"] += int(lm is not None)
                a["brillo"] += brillo
                a["ancho"] += ancho or 0.0
                a["con_aviso"] += int(bool(avisos))
                a["t_ini"] = a["t_ini"] if a["t_ini"] is not None else ahora
                a["t_fin"] = ahora
                inicio, blanco_fn, grabar_desde = self.fase
                t = ahora - inicio
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


def mostrar_monitor(hilo) -> None:
    if hilo.monitor is not None:
        cv2.imshow(mon.NOMBRE, hilo.monitor)


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
        mostrar_monitor(hilo)
        espera = max(1, int(1000 / 60 - (time.monotonic() - inicio - t) * 1000))
        if cv2.waitKey(espera) == 27:
            raise KeyboardInterrupt
    return hilo.resultado()


def esperar_espacio(hilo, pantalla, texto):
    """Pantalla de inicio DENTRO de la ventana; el operador puede acomodar
    a YP mirando el monitor antes de pulsar ESPACIO."""
    while True:
        cv2.imshow(VENTANA, dibujar(pantalla, None, None, texto, hilo.cara_ok))
        mostrar_monitor(hilo)
        tecla = cv2.waitKey(30)
        if tecla == 27:
            raise KeyboardInterrupt
        if tecla == 32:
            return


def agregar_csv(archivo: Path, fila: dict) -> None:
    """Agrega una fila; si el archivo tenía menos columnas, lo migra."""
    campos = list(fila)
    filas = []
    if archivo.exists():
        with archivo.open(newline="", encoding="utf-8") as fh:
            lector = csv.DictReader(fh)
            filas = list(lector)
            campos += [c for c in (lector.fieldnames or []) if c not in campos]
    filas.append(fila)
    with archivo.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=campos, restval="")
        w.writeheader()
        w.writerows(filas)


def main() -> None:
    args = sys.argv[1:]
    canal = "ojos" if "--ojos" in args else "cabeza"
    par = PARAMETROS[canal]
    modo_mouse = "--mouse" in args
    rapido = "--rapido" in args            # prueba corta (humo/depuración)
    sin_espera = "--sin-espera" in args
    con_monitor = "--sin-monitor" not in args
    # Con un solo monitor, el blanco a pantalla completa taparía el monitor
    # del operador: la prueba pasa a ventana.
    ventana = "--ventana" in args or (con_monitor and mon.num_monitores() <= 1)
    duracion = 4.0 if rapido else par["duracion"]
    if "--seg" in args:
        duracion = float(args[args.index("--seg") + 1])
    asentar, grabar = (0.3, 0.5) if rapido else (par["asentar"], par["grabar"])

    pantalla = (800, 450) if ventana else tamano_pantalla()
    cara = crear_detector()
    cap = cv2.VideoCapture(CONFIG["camara"]["indice"], cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise SystemExit("No se pudo abrir la cámara")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    extractor = extraer_cabeza if canal == "cabeza" else extraer_ojos
    hilo = HiloCamara(cap, cara, extractor, par["n_rasgos"], con_monitor)
    hilo.start()

    # Las ventanas se crean DESPUÉS de todo lo que usa la consola, y el inicio
    # se confirma con ESPACIO dentro de la ventana (a pantalla completa
    # tapa la consola: un input() aquí quedaría invisible).
    if ventana:
        cv2.namedWindow(VENTANA, cv2.WINDOW_AUTOSIZE)
        cv2.moveWindow(VENTANA, 0, 0)
    else:
        cv2.namedWindow(VENTANA, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(VENTANA, cv2.WND_PROP_FULLSCREEN,
                              cv2.WINDOW_FULLSCREEN)
    if con_monitor:
        mon.crear_ventana(*mon.posicion_ventana(pantalla[0], ventana))
    mouse = [pantalla[0] / 2, pantalla[1] / 2]
    cv2.setMouseCallback(
        VENTANA, lambda e, x, y, f, p: mouse.__setitem__(slice(0, 2), [x, y]))

    verbo = "Gira la cabeza hacia el punto" if canal == "cabeza" else "Mira el punto"
    seguir = ("Sigue el punto moviendo la CABEZA" if canal == "cabeza"
              else "Sigue el punto con la vista")
    print("=" * 60)
    print(f"  PERSECUCIÓN — canal {canal.upper()} — "
          + ("blanco = mouse" if modo_mouse else "blanco automático"))
    print("  Sigue las instrucciones EN LA VENTANA. ESC aborta.")
    if con_monitor:
        print("  El 'Monitor operador' es para ti: revisa sus avisos en rojo.")
    print("=" * 60)

    try:
        if not sin_espera:
            esperar_espacio(hilo, pantalla,
                            "Punto verde = cara detectada. ESPACIO para empezar")
        calib = []
        for i, (px, py) in enumerate(puntos_calibracion(pantalla), 1):
            f, _ = correr_fase(hilo, pantalla, asentar + grabar,
                               lambda t, px=px, py=py: (px, py),
                               f"{verbo}  {i}/9", grabar_desde=asentar)
            if len(f):
                calib.append(f)
        vacio = np.empty((0, 3 + par["n_rasgos"]))
        calib = np.vstack(calib) if calib else vacio
        min_frames = 30 if rapido else MIN_FRAMES
        if len(calib) < min_frames:
            print(f"\n❌ Solo {len(calib)} frames de calibración con cara "
                  "válida. Mejor luz y la cara centrada frente a la cámara.")
            return
        modelo = ajustar_ridge(calib[:, 3:], calib[:, 1:3])
        err_cal = float(np.sqrt(np.mean(np.linalg.norm(
            predecir(modelo, calib[:, 3:]) - calib[:, 1:3], axis=1) ** 2)))
        err_lopo = error_calibracion_lopo(calib[:, 3:], calib[:, 1:3])
        print(f"\n  Calibración: {len(calib)} frames | error de ajuste "
              f"{err_cal:.0f} px (optimista) | dejando un punto fuera "
              f"{err_lopo:.0f} px")

        centro = (pantalla[0] / 2, pantalla[1] / 2)
        correr_fase(hilo, pantalla, 1.5 if rapido else 3.0, lambda t: centro,
                    "Ahora sigue el punto que se mueve...")
        if modo_mouse:
            blanco_fn = lambda t: (mouse[0], mouse[1])  # noqa: E731
        else:
            px_, py_ = par["periodos"]
            blanco_fn = lambda t: tuple(  # noqa: E731
                trayectoria_auto(np.array([t]), pantalla, px_, py_)[0])
        datos, total = correr_fase(hilo, pantalla, duracion, blanco_fn, seguir)
    except KeyboardInterrupt:
        print("\nAbortado.")
        return
    finally:
        estadisticas = hilo.estadisticas()
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
    m = metricas_persecucion(t, blanco, pred, pantalla, par["max_retardo"])

    print("\n" + "=" * 60)
    print(f"  RESULTADO — canal {canal} (calibración y persecución: datos distintos)")
    print("=" * 60)
    print(f"  Frames válidos: {m['n_frames']} de {total} "
          f"({m['n_frames'] / total:.0%})")
    print(f"  Error medio: {m['rmse_px']:.0f} px = {m['rmse_pct_diagonal']:.1f}% "
          "de la diagonal de pantalla")
    print(f"  Línea base (apuntar siempre al centro): {m['rmse_linea_base_px']:.0f} px "
          f"-> mejora {m['mejora_vs_constante']:+.0%}")
    print(f"  Correlación con el blanco: x={m['r_x']:.2f}  y={m['r_y']:.2f}")
    print(f"  Retardo: x={m['retardo_x_ms']:.0f} ms  y={m['retardo_y_ms']:.0f} ms")
    print("  Entorno: "
          f"{estadisticas['fps']:.0f} fps | cara {estadisticas['tasa_cara']:.0%} | "
          f"brillo {estadisticas['brillo']:.0f} | "
          f"cara ocupa {estadisticas['ancho_cara_pct']:.0f}% del ancho | "
          f"{estadisticas['pct_frames_con_aviso']:.0f}% de frames con aviso")
    print("  Lectura: mejora > 0 y correlación alta = el canal sí sigue el blanco.")
    print("  Compara sesiones con:  py -3.12 src/mirada_progreso.py")

    if rapido:
        print("\n  (--rapido: prueba corta, no se guarda nada)")
        return
    DIR_DATOS.mkdir(exist_ok=True)
    sello = datetime.now().strftime("%Y%m%d_%H%M%S")
    np.savez_compressed(DIR_DATOS / f"persecucion_{sello}.npz",
                        calibracion=calib, persecucion=datos, prediccion=pred,
                        pantalla=np.array(pantalla), modo_mouse=modo_mouse,
                        canal=canal)
    DIR_REGISTROS.mkdir(exist_ok=True)
    agregar_csv(DIR_REGISTROS / "sesiones_mirada.csv", {
        "fecha_hora": datetime.now().isoformat(timespec="seconds"),
        "alias": CONFIG["participante"]["alias"], "canal": canal,
        "modo": "mouse" if modo_mouse else "auto", **m,
        "error_calib_px": err_cal, "error_calib_lopo_px": err_lopo,
        **{k: estadisticas[k] for k in ("fps", "tasa_cara", "brillo",
                                        "ancho_cara_pct", "pct_frames_con_aviso")}})
    print(f"\n  Guardado en data_mirada/persecucion_{sello}.npz")


if __name__ == "__main__":
    main()
