"""Captura simultánea de voz + gesto: mientras YP dice la palabra, también
hace el gesto, y ambas señales se graban en la misma ventana de tiempo.

La grabación de audio corre en segundo plano (sounddevice no bloquea) mientras
el hilo principal ejecuta el bucle de cámara — así las dos señales quedan
genuinamente alineadas en el tiempo, como ocurre en el uso real.
"""

from __future__ import annotations

import numpy as np
import sounddevice as sd

from gestos_features import LectorGestos


def capturar_par(lector: LectorGestos, duracion_seg: float, sr: int,
                 titulo: str = "Habla y haz el gesto") -> tuple[np.ndarray, np.ndarray]:
    """Devuelve (audio, secuencia_gestos) capturados en paralelo."""
    buffer_audio = sd.rec(int(duracion_seg * sr), samplerate=sr,
                          channels=1, dtype="float32")
    secuencia_gestos = lector.capturar(duracion_seg, mostrar=True, titulo=titulo)
    sd.wait()
    return buffer_audio.flatten(), secuencia_gestos
