"""Valida la reducción a prototipos: ¿cuánta exactitud se pierde y cuánto
tiempo se gana al reemplazar el banco de referencias completo por k
prototipos por clase? Usa LOOCV metodológicamente correcta: los prototipos
de la clase de la muestra excluida se recalculan SIN ella en cada pliegue
(si no, "vería" su propia muestra durante la selección — fuga de datos).

Uso:
    python src/comparar_prototipos.py
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
RAIZ = Path(__file__).resolve().parent.parent

from audio_features import extraer_mfcc  # noqa: E402
from modelo import ClasificadorPalabras, distancia_dtw  # noqa: E402
from prototipos import matriz_distancias  # noqa: E402

CONFIG = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))


def cargar_dataset() -> tuple[list[np.ndarray], list[str]]:
    secuencias, etiquetas = [], []
    for carpeta in sorted((RAIZ / "data").iterdir()):
        if not carpeta.is_dir():
            continue
        for wav in sorted(carpeta.glob("*.wav")):
            if "_multi_" in wav.stem:
                continue
            senal, sr = sf.read(wav)
            if senal.ndim > 1:
                senal = senal.mean(axis=1)
            secuencias.append(extraer_mfcc(senal, sr, n_mfcc=CONFIG["audio"]["n_mfcc"]))
            etiquetas.append(carpeta.name)
    return secuencias, etiquetas


def elegir_desde_matriz(D: np.ndarray, k: int, excluir: int | None = None) -> list[int]:
    """k-medoids por punto-mas-lejano sobre una matriz de distancias ya
    calculada, opcionalmente excluyendo un indice (para LOOCV sin fuga)."""
    n = D.shape[0]
    indices_validos = [i for i in range(n) if i != excluir]
    if len(indices_validos) <= k:
        return indices_validos

    sub = D[np.ix_(indices_validos, indices_validos)]
    primero_local = int(np.argmin(sub.sum(axis=1)))
    elegidos_local = [primero_local]
    while len(elegidos_local) < k:
        dist_al_conjunto = sub[:, elegidos_local].min(axis=1)
        dist_al_conjunto[elegidos_local] = -1.0
        elegidos_local.append(int(np.argmax(dist_al_conjunto)))
    return [indices_validos[i] for i in elegidos_local]


def main() -> None:
    print("Cargando dataset de voz...")
    secuencias, etiquetas = cargar_dataset()
    clases = sorted(set(etiquetas))
    n_total = len(secuencias)
    print(f"Dataset: {n_total} muestras, {len(clases)} palabras\n")

    print("Calculando matrices de distancia DTW por clase (una sola vez)...")
    indices_por_clase = {c: [i for i, e in enumerate(etiquetas) if e == c] for c in clases}
    matrices_por_clase = {}
    for c in clases:
        secs_c = [secuencias[i] for i in indices_por_clase[c]]
        t0 = time.perf_counter()
        matrices_por_clase[c] = matriz_distancias(secs_c)
        print(f"  {c:>10}: {len(secs_c)} muestras, {time.perf_counter()-t0:.1f}s")

    umbral = CONFIG["modelo"]["k_vecinos"]

    print(f"\n{'k_proto':>8} | {'n total refs':>13} | {'exactitud LOOCV':>16} | {'ms/prediccion':>14}")
    print("-" * 62)

    resultados = []
    for k_proto in [3, 4, 5, 6, 8, None]:  # None = sin reduccion (linea base)
        aciertos = 0
        latencias = []

        # Prototipos de cada clase completa (para las clases que NO son la
        # de la muestra excluida en cada pliegue -- no cambian entre pliegues)
        prototipos_fijos = {}
        if k_proto is not None:
            for c in clases:
                elegidos_local = elegir_desde_matriz(matrices_por_clase[c], k_proto)
                prototipos_fijos[c] = [indices_por_clase[c][i] for i in elegidos_local]

        for idx_excluido in range(n_total):
            clase_excluida = etiquetas[idx_excluido]
            referencias_idx = []
            for c in clases:
                if c == clase_excluida:
                    if k_proto is None:
                        referencias_idx.extend(
                            i for i in indices_por_clase[c] if i != idx_excluido)
                    else:
                        pos_local_excluido = indices_por_clase[c].index(idx_excluido)
                        elegidos_local = elegir_desde_matriz(
                            matrices_por_clase[c], k_proto, excluir=pos_local_excluido)
                        referencias_idx.extend(
                            indices_por_clase[c][i] for i in elegidos_local)
                else:
                    referencias_idx.extend(
                        indices_por_clase[c] if k_proto is None else prototipos_fijos[c])

            modelo = ClasificadorPalabras(k=umbral, umbral_confianza=0.0)
            modelo.entrenar([secuencias[i] for i in referencias_idx],
                            [etiquetas[i] for i in referencias_idx])

            t0 = time.perf_counter()
            pred, _ = modelo.predecir(secuencias[idx_excluido])
            latencias.append(time.perf_counter() - t0)
            if pred == clase_excluida:
                aciertos += 1

        exactitud = aciertos / n_total
        ms_promedio = np.mean(latencias) * 1000
        etiqueta_k = "completo" if k_proto is None else str(k_proto)
        n_refs = n_total if k_proto is None else k_proto * len(clases)
        print(f"{etiqueta_k:>8} | {n_refs:>13} | {exactitud*100:>15.1f}% | {ms_promedio:>13.1f}")
        resultados.append({"k_proto": etiqueta_k, "n_referencias": n_refs,
                           "exactitud": exactitud, "ms_promedio": ms_promedio})

    ruta = RAIZ / "reportes" / "comparacion_prototipos.json"
    ruta.write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nGuardado: {ruta.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
