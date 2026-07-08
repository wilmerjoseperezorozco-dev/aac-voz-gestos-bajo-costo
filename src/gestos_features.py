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


class LectorGestos:
    """Abre la cámara y extrae la secuencia de rasgos de un gesto."""

    def __init__(self, ruta_modelo: Path, indice_camara: int = 0):
        opciones = vision.PoseLandmarkerOptions(
            base_options=mp_python.BaseOptions(
                model_asset_path=str(ruta_modelo)),
            running_mode=vision.RunningMode.VIDEO)
        self.detector = vision.PoseLandmarker.create_from_options(opciones)
        self.indice_camara = indice_camara
        self._t0 = time.monotonic()

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
        (frames, rasgos*2) con posiciones + velocidades, normalizada."""
        cap = cv2.VideoCapture(self.indice_camara, cv2.CAP_DSHOW)
        if not cap.isOpened():
            raise RuntimeError("No se pudo abrir la cámara")
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
