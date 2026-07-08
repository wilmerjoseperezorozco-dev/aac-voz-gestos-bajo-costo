"""Extracción de características acústicas (MFCC) sin dependencias pesadas.

Implementación propia con numpy + scipy: filtros mel, DCT y recorte por energía.
Diseñado para vocabularios pequeños y muestras cortas (2 s) de una sola persona.
"""

from __future__ import annotations

import numpy as np
from scipy.fftpack import dct
from scipy.signal import get_window

FRECUENCIA_MUESTREO = 16000
PRE_ENFASIS = 0.97
PISO_LOG = 1e-10


def _hz_a_mel(hz: np.ndarray | float) -> np.ndarray | float:
    return 2595.0 * np.log10(1.0 + np.asarray(hz) / 700.0)


def _mel_a_hz(mel: np.ndarray | float) -> np.ndarray | float:
    return 700.0 * (10.0 ** (np.asarray(mel) / 2595.0) - 1.0)


def _banco_filtros_mel(n_filtros: int, n_fft: int, sr: int) -> np.ndarray:
    """Banco de filtros triangulares en escala mel (n_filtros x n_fft//2+1)."""
    mel_min, mel_max = _hz_a_mel(0.0), _hz_a_mel(sr / 2.0)
    puntos_mel = np.linspace(mel_min, mel_max, n_filtros + 2)
    puntos_hz = _mel_a_hz(puntos_mel)
    bins = np.floor((n_fft + 1) * puntos_hz / sr).astype(int)

    banco = np.zeros((n_filtros, n_fft // 2 + 1))
    for i in range(1, n_filtros + 1):
        izq, centro, der = bins[i - 1], bins[i], bins[i + 1]
        for j in range(izq, centro):
            if centro > izq:
                banco[i - 1, j] = (j - izq) / (centro - izq)
        for j in range(centro, der):
            if der > centro:
                banco[i - 1, j] = (der - j) / (der - centro)
    return banco


def recortar_silencio(senal: np.ndarray, sr: int = FRECUENCIA_MUESTREO,
                      umbral_db: float = 30.0) -> np.ndarray:
    """Recorta silencio inicial/final usando energía por tramas (VAD simple)."""
    tam_trama = int(sr * 0.02)
    if len(senal) < tam_trama * 3:
        return senal
    n_tramas = len(senal) // tam_trama
    tramas = senal[: n_tramas * tam_trama].reshape(n_tramas, tam_trama)
    energia = 10.0 * np.log10(np.mean(tramas ** 2, axis=1) + PISO_LOG)
    umbral = energia.max() - umbral_db
    activas = np.where(energia > umbral)[0]
    if len(activas) == 0:
        return senal
    ini = max(0, (activas[0] - 2) * tam_trama)
    fin = min(len(senal), (activas[-1] + 3) * tam_trama)
    return senal[ini:fin]


def extraer_mfcc(senal: np.ndarray, sr: int = FRECUENCIA_MUESTREO,
                 n_mfcc: int = 13, ventana_ms: float = 25.0,
                 salto_ms: float = 10.0, n_filtros: int = 26) -> np.ndarray:
    """Devuelve matriz (n_tramas, n_mfcc*2) = MFCC + deltas, normalizada."""
    senal = senal.astype(np.float64)
    maximo = np.max(np.abs(senal))
    if maximo > 0:
        senal = senal / maximo
    senal = recortar_silencio(senal, sr)
    senal = np.append(senal[0], senal[1:] - PRE_ENFASIS * senal[:-1])

    tam_ventana = int(sr * ventana_ms / 1000.0)
    tam_salto = int(sr * salto_ms / 1000.0)
    n_fft = 512
    if len(senal) < tam_ventana:
        senal = np.pad(senal, (0, tam_ventana - len(senal)))

    n_tramas = 1 + (len(senal) - tam_ventana) // tam_salto
    ventana = get_window("hamming", tam_ventana)
    indices = (np.tile(np.arange(tam_ventana), (n_tramas, 1))
               + np.tile(np.arange(n_tramas) * tam_salto, (tam_ventana, 1)).T)
    tramas = senal[indices] * ventana

    espectro = np.abs(np.fft.rfft(tramas, n_fft)) ** 2 / n_fft
    banco = _banco_filtros_mel(n_filtros, n_fft, sr)
    energia_mel = np.log(espectro @ banco.T + PISO_LOG)
    mfcc = dct(energia_mel, type=2, axis=1, norm="ortho")[:, :n_mfcc]

    # Deltas (primera derivada temporal) para capturar dinámica articulatoria
    delta = np.gradient(mfcc, axis=0)
    caracteristicas = np.hstack([mfcc, delta])

    # Normalización por locutor/grabación (media-varianza por coeficiente)
    media = caracteristicas.mean(axis=0)
    desv = caracteristicas.std(axis=0) + 1e-8
    return (caracteristicas - media) / desv
