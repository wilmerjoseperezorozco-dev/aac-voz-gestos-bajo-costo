"""Captura de movimiento con la webcam: convierte los puntos del cuerpo
(MediaPipe Pose) en series temporales, análogas a los MFCC del canal de voz.

Cada frame se reduce a coordenadas relativas al torso (invariantes a la
posición frente a la cámara) y el mismo clasificador k-NN + DTW del canal
de voz aprende los gestos. Un solo motor, dos sentidos: oído y vista.
"""

from __future__ import annotations

import time
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

# Índices de PoseLandmarker: puntos del tren superior que capturan
# gestos de cabeza y brazos (los canales motores disponibles de YP)
PUNTOS = {
    "nariz": 0, "ojo_izq": 2, "ojo_der": 5,
    "hombro_izq": 11, "hombro_der": 12,
    "codo_izq": 13, "codo_der": 14,
    "muneca_izq": 15, "muneca_der": 16,
}


# Conexiones del esqueleto (pares de índices PoseLandmarker) para dibujar
# la silueta detectada sobre la imagen — permite verificar en vivo a
# quién está siguiendo el sistema cuando hay más de una persona en cuadro.
_HUESOS = [
    (0, 2), (0, 5),                    # nariz-ojos
    (11, 12),                          # hombro-hombro
    (11, 13), (13, 15),                # brazo izquierdo
    (12, 14), (14, 16),                # brazo derecho
]
_COLORES_PERSONA = [(0, 255, 0), (0, 140, 255), (255, 0, 255)]  # verde, naranja, magenta


class LectorGestos:
    """Abre la cámara y extrae la secuencia de rasgos de un gesto."""

    def __init__(self, ruta_modelo: Path, indice_camara: int = 0,
                 max_personas: int = 2):
        opciones = vision.PoseLandmarkerOptions(
            base_options=mp_python.BaseOptions(
                model_asset_path=str(ruta_modelo)),
            running_mode=vision.RunningMode.VIDEO,
            num_poses=max_personas)
        self.detector = vision.PoseLandmarker.create_from_options(opciones)
        self.indice_camara = indice_camara
        self._t0 = time.monotonic()

    def _dibujar_personas(self, frame, lista_landmarks) -> None:
        """Dibuja el esqueleto de cada persona detectada, con un color
        distinto por persona (índice 0 = la que se usa para capturar, en
        verde). Convierte coordenadas normalizadas (0-1) a píxeles."""
        alto, ancho = frame.shape[:2]
        for idx_persona, lm in enumerate(lista_landmarks):
            color = _COLORES_PERSONA[idx_persona % len(_COLORES_PERSONA)]
            puntos_px = {}
            for nombre, i in PUNTOS.items():
                p = lm[i]
                puntos_px[i] = (int(p.x * ancho), int(p.y * alto))
                cv2.circle(frame, puntos_px[i], 5, color, -1)
            for a, b in _HUESOS:
                if a in puntos_px and b in puntos_px:
                    cv2.line(frame, puntos_px[a], puntos_px[b], color, 2)
            etiqueta = "YP (usada)" if idx_persona == 0 else f"persona {idx_persona + 1} (ignorada)"
            cv2.putText(frame, etiqueta, puntos_px.get(0, (10, 60 + 30 * idx_persona)),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    def _rasgos_de_frame(self, landmarks) -> np.ndarray | None:
        """Vector de rasgos por frame: coordenadas relativas al centro de
        hombros, escaladas por el ancho de hombros."""
        lm = landmarks[0]
        h_izq, h_der = lm[PUNTOS["hombro_izq"]], lm[PUNTOS["hombro_der"]]
        centro = np.array([(h_izq.x + h_der.x) / 2, (h_izq.y + h_der.y) / 2])
        escala = np.hypot(h_izq.x - h_der.x, h_izq.y - h_der.y)
        if escala < 1e-4:
            return None
        rasgos = []
        for nombre in PUNTOS:
            p = lm[PUNTOS[nombre]]
            rasgos.extend([(p.x - centro[0]) / escala,
                           (p.y - centro[1]) / escala])
        return np.array(rasgos)

    def capturar(self, duracion_seg: float, mostrar: bool = True,
                 titulo: str = "Capturando gesto") -> np.ndarray:
        """Captura `duracion_seg` de movimiento. Devuelve matriz
        (frames, rasgos*2) con posiciones + velocidades, normalizada.

        Si hay más de una persona en cuadro, siempre se usa la primera
        que reporta MediaPipe (índice 0) para los rasgos guardados — el
        resto se dibuja en pantalla solo para verificación visual, no se
        graba. Ver `_dibujar_personas`."""
        cap = cv2.VideoCapture(self.indice_camara, cv2.CAP_DSHOW)
        if not cap.isOpened():
            raise RuntimeError("No se pudo abrir la cámara")
        # Pide mayor resolución nativa a la cámara (si la soporta) en vez
        # de solo escalar la imagen — más nítido que un simple resize.
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        if mostrar:
            cv2.namedWindow("Camara - MVP gestos", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Camara - MVP gestos", 1280, 720)
        secuencia = []
        inicio = time.monotonic()
        try:
            while time.monotonic() - inicio < duracion_seg:
                ok, frame = cap.read()
                if not ok:
                    continue
                imagen = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                marca_ms = int((time.monotonic() - self._t0) * 1000)
                res = self.detector.detect_for_video(imagen, marca_ms)
                if res.pose_landmarks:
                    rasgos = self._rasgos_de_frame(res.pose_landmarks)
                    if rasgos is not None:
                        secuencia.append(rasgos)
                if mostrar:
                    if res.pose_landmarks:
                        self._dibujar_personas(frame, res.pose_landmarks)
                        if len(res.pose_landmarks) > 1:
                            cv2.putText(frame, f"! {len(res.pose_landmarks)} personas detectadas",
                                        (10, frame.shape[0] - 20),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                    restante = duracion_seg - (time.monotonic() - inicio)
                    cv2.putText(frame, f"{titulo} {restante:.1f}s",
                                (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                                0.8, (0, 255, 0), 2)
                    cv2.imshow("Camara - MVP gestos", frame)
                    cv2.waitKey(1)
        finally:
            cap.release()
            if mostrar:
                cv2.destroyAllWindows()

        if len(secuencia) < 5:
            raise RuntimeError(
                f"Solo {len(secuencia)} frames con persona detectada; "
                "verifica que YP esté frente a la cámara con buena luz")
        matriz = np.array(secuencia)
        velocidad = np.gradient(matriz, axis=0)
        caracteristicas = np.hstack([matriz, velocidad])
        media = caracteristicas.mean(axis=0)
        desv = caracteristicas.std(axis=0) + 1e-8
        return (caracteristicas - media) / desv

    def verificar_encuadre(self) -> None:
        """Vista previa en vivo, sin grabar nada — para comprobar antes
        de empezar la sesión que la cámara detecta a la persona correcta
        (verde = la que se usará) y ajustar el encuadre si hace falta.
        Presiona cualquier tecla en la ventana de la cámara para cerrar."""
        cap = cv2.VideoCapture(self.indice_camara, cv2.CAP_DSHOW)
        if not cap.isOpened():
            raise RuntimeError("No se pudo abrir la cámara")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        cv2.namedWindow("Verificar encuadre - ENTER para continuar", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Verificar encuadre - ENTER para continuar", 1280, 720)
        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    continue
                imagen = mp.Image(
                    image_format=mp.ImageFormat.SRGB,
                    data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                marca_ms = int((time.monotonic() - self._t0) * 1000)
                res = self.detector.detect_for_video(imagen, marca_ms)
                if res.pose_landmarks:
                    self._dibujar_personas(frame, res.pose_landmarks)
                cv2.putText(frame, "Verificando encuadre — pulsa una tecla para continuar",
                            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow("Verificar encuadre - ENTER para continuar", frame)
                if cv2.waitKey(1) != -1:
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()
