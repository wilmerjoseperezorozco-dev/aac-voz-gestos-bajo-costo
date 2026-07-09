"""Clasificador k-NN con distancia DTW sobre secuencias MFCC.

Elegido a propósito para el MVP: con ~10 muestras por palabra no hay datos
para redes profundas, pero DTW alinea temporalmente las emisiones (clave
cuando la persona alarga o fragmenta sílabas por la desconexión motora).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

BANDA_DTW = 40  # banda de Sakoe-Chiba: limita desalineación y acelera cómputo


def distancia_dtw(a: np.ndarray, b: np.ndarray, banda: int = BANDA_DTW) -> float:
    """DTW con banda de Sakoe-Chiba entre dos secuencias (tramas x coefs).

    Optimización: las n*m distancias euclidianas punto-a-punto se calculan
    una sola vez con broadcasting de numpy, en vez de llamar
    np.linalg.norm() por celda dentro del bucle de programación dinámica
    (ese era el costo dominante — mismo resultado, ~4-5x más rápido en
    secuencias típicas de este proyecto). La recurrencia de DTW en sí no
    se vectoriza porque cada celda depende de su vecina izquierda dentro
    de la misma fila (dependencia secuencial real, no solo de estilo)."""
    n, m = len(a), len(b)
    banda = max(banda, abs(n - m) + 1)

    diferencia = a[:, None, :] - b[None, :, :]  # (n, m, dim)
    distancias = np.sqrt(np.einsum("ijk,ijk->ij", diferencia, diferencia))  # (n, m)

    costo = np.full((n + 1, m + 1), np.inf)
    costo[0, 0] = 0.0
    for i in range(1, n + 1):
        j_ini = max(1, i - banda)
        j_fin = min(m, i + banda)
        fila_dist = distancias[i - 1, j_ini - 1:j_fin]
        for offset, j in enumerate(range(j_ini, j_fin + 1)):
            costo[i, j] = fila_dist[offset] + min(
                costo[i - 1, j], costo[i, j - 1], costo[i - 1, j - 1])
    return float(costo[n, m] / (n + m))  # normalizada por longitud


class ClasificadorPalabras:
    """k-NN sobre distancias DTW. El 'modelo' son las muestras de referencia."""

    def __init__(self, k: int = 3, umbral_confianza: float = 0.5):
        self.k = k
        self.umbral_confianza = umbral_confianza
        self.referencias: list[np.ndarray] = []
        self.etiquetas: list[str] = []

    def entrenar(self, secuencias: list[np.ndarray], etiquetas: list[str]) -> None:
        if len(secuencias) != len(etiquetas):
            raise ValueError("secuencias y etiquetas deben tener igual tamaño")
        self.referencias = list(secuencias)
        self.etiquetas = list(etiquetas)

    def predecir(self, secuencia: np.ndarray) -> tuple[str, float]:
        """Devuelve (palabra, confianza). Confianza = fracción de los k
        vecinos más cercanos que votan por la palabra ganadora."""
        if not self.referencias:
            raise RuntimeError("El modelo no tiene muestras de referencia")
        distancias = np.array(
            [distancia_dtw(secuencia, ref) for ref in self.referencias])
        orden = np.argsort(distancias)[: self.k]
        votos: dict[str, float] = {}
        for idx in orden:
            etiqueta = self.etiquetas[idx]
            votos[etiqueta] = votos.get(etiqueta, 0.0) + 1.0
        ganadora = max(votos, key=votos.get)
        confianza = votos[ganadora] / min(self.k, len(self.referencias))
        return ganadora, confianza

    def evaluar_loocv(self) -> dict:
        """Validación cruzada dejando-uno-fuera: métrica honesta con pocos
        datos. Devuelve exactitud global, por palabra y matriz de confusión."""
        palabras = sorted(set(self.etiquetas))
        indice = {p: i for i, p in enumerate(palabras)}
        confusion = np.zeros((len(palabras), len(palabras)), dtype=int)
        aciertos = 0
        for i, (seq, real) in enumerate(zip(self.referencias, self.etiquetas)):
            temporal = ClasificadorPalabras(self.k, self.umbral_confianza)
            temporal.entrenar(
                [s for j, s in enumerate(self.referencias) if j != i],
                [e for j, e in enumerate(self.etiquetas) if j != i])
            prediccion, _ = temporal.predecir(seq)
            confusion[indice[real], indice[prediccion]] += 1
            if prediccion == real:
                aciertos += 1
        total = len(self.referencias)
        por_palabra = {
            p: {
                "muestras": int(confusion[indice[p]].sum()),
                "aciertos": int(confusion[indice[p], indice[p]]),
                "exactitud": float(confusion[indice[p], indice[p]]
                                   / max(1, confusion[indice[p]].sum())),
            }
            for p in palabras
        }
        return {
            "exactitud_global": aciertos / max(1, total),
            "total_muestras": total,
            "palabras": palabras,
            "matriz_confusion": confusion.tolist(),
            "por_palabra": por_palabra,
        }

    def guardar(self, ruta: Path) -> None:
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        arreglos = {f"seq_{i}": s for i, s in enumerate(self.referencias)}
        np.savez_compressed(ruta.with_suffix(".npz"), **arreglos)
        meta = {"etiquetas": self.etiquetas, "k": self.k,
                "umbral_confianza": self.umbral_confianza}
        ruta.with_suffix(".json").write_text(
            json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def cargar(cls, ruta: Path) -> "ClasificadorPalabras":
        ruta = Path(ruta)
        meta = json.loads(ruta.with_suffix(".json").read_text(encoding="utf-8"))
        datos = np.load(ruta.with_suffix(".npz"))
        modelo = cls(k=meta["k"], umbral_confianza=meta["umbral_confianza"])
        secuencias = [datos[f"seq_{i}"] for i in range(len(meta["etiquetas"]))]
        modelo.entrenar(secuencias, meta["etiquetas"])
        return modelo
