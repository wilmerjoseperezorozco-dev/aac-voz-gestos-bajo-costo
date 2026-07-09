"""Reducción a prototipos por clase: selecciona un subconjunto representativo
de las muestras de cada palabra/gesto para acotar el crecimiento de la
latencia de predicción (ver brechas-cientificas-y-escalamiento.md §7).

Método: k-medoids vía "punto más lejano" (farthest-point traversal) sobre
la matriz de distancias DTW de la clase. Se eligen prototipos REALES (no
promedios sintéticos) para que cada uno siga siendo una grabación
auditable — se puede escuchar cuál muestra quedó como representante.
"""

from __future__ import annotations

import numpy as np

from modelo import distancia_dtw


def matriz_distancias(secuencias: list[np.ndarray]) -> np.ndarray:
    n = len(secuencias)
    D = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            d = distancia_dtw(secuencias[i], secuencias[j])
            D[i, j] = D[j, i] = d
    return D


def seleccionar_prototipos(secuencias: list[np.ndarray], k: int) -> list[int]:
    """Devuelve los índices de las k muestras más representativas.

    Primer prototipo: el más central (menor distancia total a los demás).
    Siguientes: el punto más lejano al conjunto de prototipos ya elegidos,
    para maximizar la cobertura de la variabilidad real de la clase.
    """
    n = len(secuencias)
    if n <= k:
        return list(range(n))

    D = matriz_distancias(secuencias)
    elegidos = [int(np.argmin(D.sum(axis=1)))]

    while len(elegidos) < k:
        dist_al_conjunto = D[:, elegidos].min(axis=1)
        dist_al_conjunto[elegidos] = -1.0  # no volver a elegir
        elegidos.append(int(np.argmax(dist_al_conjunto)))

    return elegidos


def reducir_dataset(secuencias: list[np.ndarray], etiquetas: list[str],
                    k_por_clase: int) -> tuple[list[np.ndarray], list[str], dict]:
    """Aplica la reducción a prototipos clase por clase. Devuelve el
    dataset reducido y un mapa {clase: [índices originales elegidos]} para
    trazabilidad (saber qué archivos .wav quedaron como prototipo)."""
    clases = sorted(set(etiquetas))
    nuevas_secuencias, nuevas_etiquetas = [], []
    mapa_indices: dict[str, list[int]] = {}

    for clase in clases:
        indices_clase = [i for i, e in enumerate(etiquetas) if e == clase]
        secuencias_clase = [secuencias[i] for i in indices_clase]
        elegidos_local = seleccionar_prototipos(secuencias_clase, k_por_clase)
        elegidos_global = [indices_clase[i] for i in elegidos_local]
        mapa_indices[clase] = elegidos_global
        for i in elegidos_global:
            nuevas_secuencias.append(secuencias[i])
            nuevas_etiquetas.append(etiquetas[i])

    return nuevas_secuencias, nuevas_etiquetas, mapa_indices
