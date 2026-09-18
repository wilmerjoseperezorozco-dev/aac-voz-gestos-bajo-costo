"""Monitor del operador: vista pequeña para verificar la captura facial.

Es una ventana APARTE de la que ve YP. Muestra la cámara con los puntos
que usa el sistema (iris, párpados, nariz, mejillas), el cuadro de la cara,
y avisos de entorno: poca luz, cara lejos o cerca, fuera de centro, fps
bajos. Si hay un segundo monitor se coloca allí; con un solo monitor la
prueba pasa a ventana y el monitor se coloca al lado.
"""

from __future__ import annotations

import ctypes

import cv2
import numpy as np

ANCHO, ALTO = 480, 270
NOMBRE = "Monitor operador (no es para YP)"

# Umbrales de calidad del entorno (ancho de cara = fracción del ancho de imagen).
BRILLO_MIN, BRILLO_MAX = 70.0, 200.0
ANCHO_CARA_MIN, ANCHO_CARA_MAX = 0.15, 0.55
FPS_MIN = 15.0

_IRIS = (468, 473)
_OJOS = (33, 133, 362, 263, 159, 145, 386, 374)
_REFERENCIAS = (1, 234, 454, 152, 10)   # nariz, mejillas, mentón, frente

VERDE, AMARILLO, ROJO, CIAN = (0, 200, 0), (0, 200, 255), (0, 0, 255), (255, 255, 0)


def num_monitores() -> int:
    return int(ctypes.windll.user32.GetSystemMetrics(80))   # SM_CMONITORS


def posicion_ventana(ancho_estimulo: int, estimulo_en_ventana: bool) -> tuple[int, int]:
    """Dónde colocar el monitor. Con 2+ monitores y estímulo a pantalla
    completa va al segundo monitor; si no, al lado de la ventana de prueba."""
    u = ctypes.windll.user32
    if num_monitores() > 1 and not estimulo_en_ventana:
        origen_x = int(u.GetSystemMetrics(76))              # SM_XVIRTUALSCREEN
        if origen_x < 0:                                    # segundo monitor a la izquierda
            return origen_x + 20, 20
        return ancho_estimulo + 20, 20                      # a la derecha del principal
    return ancho_estimulo + 10, 10


def crear_ventana(x: int, y: int) -> None:
    cv2.namedWindow(NOMBRE, cv2.WINDOW_AUTOSIZE)
    cv2.moveWindow(NOMBRE, x, y)
    try:
        cv2.setWindowProperty(NOMBRE, cv2.WND_PROP_TOPMOST, 1)
    except cv2.error:
        pass


def alertas(brillo: float, ancho_cara: float | None, fps: float,
            centrada: bool) -> list[str]:
    """Avisos accionables para el operador."""
    if ancho_cara is None:
        return ["SIN CARA: acerca a YP o mejora la luz"]
    avisos = []
    if brillo < BRILLO_MIN:
        avisos.append("Poca luz: ilumina la cara de frente")
    elif brillo > BRILLO_MAX:
        avisos.append("Sobreexpuesto: baja la luz o evita contraluz")
    if ancho_cara < ANCHO_CARA_MIN:
        avisos.append("Cara lejos: acerca la camara o a YP")
    elif ancho_cara > ANCHO_CARA_MAX:
        avisos.append("Cara muy cerca: aleja un poco")
    if not centrada:
        avisos.append("Cara fuera de centro")
    if fps < FPS_MIN:
        avisos.append(f"FPS bajos ({fps:.0f})")
    return avisos


def anotar(frame: np.ndarray, landmarks, estado: dict) -> np.ndarray:
    """Devuelve la imagen pequeña anotada. `estado` trae fps, brillo,
    yaw/pitch, parpadeo y la lista de avisos."""
    pequeno = cv2.resize(frame, (ANCHO, ALTO))
    if landmarks is not None:
        pts = np.array([[p.x, p.y] for p in landmarks]) * (ANCHO, ALTO)
        x0, y0 = pts.min(0).astype(int)
        x1, y1 = pts.max(0).astype(int)
        cv2.rectangle(pequeno, (x0, y0), (x1, y1), VERDE, 1)
        for i in _OJOS:
            cv2.circle(pequeno, tuple(pts[i].astype(int)), 2, AMARILLO, -1)
        for i in _IRIS:
            cv2.circle(pequeno, tuple(pts[i].astype(int)), 3, CIAN, -1)
        for i in _REFERENCIAS:
            cv2.circle(pequeno, tuple(pts[i].astype(int)), 2, VERDE, -1)

    lineas = [f"FPS {estado['fps']:.0f}  brillo {estado['brillo']:.0f}"]
    if estado.get("yaw") is not None:
        lineas.append(f"cabeza yaw {estado['yaw']:+.0f}  pitch {estado['pitch']:+.0f}")
    if estado.get("parpadeo") is not None:
        lineas.append(f"parpadeo {estado['parpadeo']:.2f}")
    banda = 18 * (len(lineas) + len(estado["avisos"])) + 6
    capa = pequeno.copy()
    cv2.rectangle(capa, (0, 0), (ANCHO, banda), (0, 0, 0), -1)
    pequeno = cv2.addWeighted(capa, 0.55, pequeno, 0.45, 0)
    y = 16
    for texto in lineas:
        cv2.putText(pequeno, texto, (6, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (230, 230, 230), 1)
        y += 18
    for texto in estado["avisos"]:
        cv2.putText(pequeno, texto, (6, y), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, ROJO, 1)
        y += 18
    color = ROJO if estado["avisos"] else VERDE
    cv2.rectangle(pequeno, (0, 0), (ANCHO - 1, ALTO - 1), color, 3)
    return pequeno
