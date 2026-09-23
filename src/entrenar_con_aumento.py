"""Compara LOOCV con y sin datos aumentados (perturbación de señal),
usando el mismo conjunto real como caso de prueba en ambos casos.

Uso:
    python src/aumento_datos_voz.py       # generar variantes primero
    python src/entrenar_con_aumento.py    # comparar

Por qué existe un script aparte de entrenar.py: mezclar copias sintéticas
de una grabación en el entrenamiento y usar el LOOCV simple de
entrenar.py (deja-uno-fuera por índice) dejaría en el set de
entrenamiento a los "hermanos" sintéticos de la muestra evaluada —
el modelo reconocería su propio casi-duplicado, no el patrón general, y
la exactitud saldría inflada. Este script usa
`ClasificadorPalabras.evaluar_loocv_agrupado()`, que excluye junto con
cada muestra real evaluada a todas sus variantes aumentadas.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

if sys.stdout is not None and sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from audio_features import extraer_mfcc  # noqa: E402
from modelo import ClasificadorPalabras  # noqa: E402

CONFIG = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
DIR_DATOS = RAIZ / "data"
DIR_AUMENTADO = RAIZ / "data_aumentado"
MANIFIESTO = RAIZ / "registros" / "aumento_datos_voz.csv"


def cargar_dataset_con_grupos() -> tuple[list[np.ndarray], list[str], list[str]]:
    """Igual que entrenar.cargar_dataset(), pero además devuelve el nombre
    de archivo de cada grabación como `grupo` — la misma clave que usan
    sus variantes aumentadas (archivo_original en el manifiesto), para
    poder excluirlas juntas en el LOOCV agrupado."""
    secuencias, etiquetas, grupos = [], [], []
    for carpeta in sorted(DIR_DATOS.iterdir()):
        if not carpeta.is_dir():
            continue
        for wav in sorted(carpeta.glob("*.wav")):
            if "_multi_" in wav.stem:
                continue
            senal, sr = sf.read(wav)
            if senal.ndim > 1:
                senal = senal.mean(axis=1)
            secuencias.append(extraer_mfcc(senal, sr,
                                           n_mfcc=CONFIG["audio"]["n_mfcc"]))
            etiquetas.append(carpeta.name)
            grupos.append(wav.name)
    return secuencias, etiquetas, grupos


def cargar_aumentado() -> tuple[list[np.ndarray], list[str], list[str]]:
    """Devuelve (secuencias, etiquetas, grupos) de las variantes sintéticas.
    `grupo` = archivo_original, la misma clave que su grabación real, para
    poder excluirlas juntas durante el LOOCV agrupado."""
    if not MANIFIESTO.exists():
        raise SystemExit(
            f"No existe {MANIFIESTO}. Corre primero: python src/aumento_datos_voz.py")
    secuencias, etiquetas, grupos = [], [], []
    with MANIFIESTO.open(encoding="utf-8") as fh:
        for fila in csv.DictReader(fh):
            ruta = DIR_AUMENTADO / fila["palabra"] / fila["archivo_generado"]
            senal, sr = sf.read(ruta)
            if senal.ndim > 1:
                senal = senal.mean(axis=1)
            secuencias.append(extraer_mfcc(senal, sr,
                                           n_mfcc=CONFIG["audio"]["n_mfcc"]))
            etiquetas.append(fila["palabra"])
            grupos.append(fila["archivo_original"])
    return secuencias, etiquetas, grupos


def main() -> None:
    print("Cargando grabaciones reales de data/ ...")
    seq_reales, et_reales, grupos_reales = cargar_dataset_con_grupos()
    print(f"  {len(seq_reales)} muestras reales")

    print("Cargando variantes aumentadas de data_aumentado/ ...")
    seq_aug, et_aug, grupos_aug = cargar_aumentado()
    print(f"  {len(seq_aug)} muestras sintéticas")

    modelo_base = ClasificadorPalabras(
        k=CONFIG["modelo"]["k_vecinos"],
        umbral_confianza=CONFIG["modelo"]["umbral_confianza"])
    modelo_base.entrenar(seq_reales, et_reales)
    print("\n--- LOOCV solo con datos reales (línea base) ---")
    reporte_base = modelo_base.evaluar_loocv()
    print(f"Exactitud global: {reporte_base['exactitud_global']*100:.1f}% "
          f"({reporte_base['total_muestras']} muestras)")

    modelo_aum = ClasificadorPalabras(
        k=CONFIG["modelo"]["k_vecinos"],
        umbral_confianza=CONFIG["modelo"]["umbral_confianza"])
    modelo_aum.entrenar(seq_reales + seq_aug, et_reales + et_aug)
    grupos = grupos_reales + grupos_aug
    evaluables = [True] * len(seq_reales) + [False] * len(seq_aug)
    print("\n--- LOOCV agrupado con datos reales + aumentados ---")
    print("(cada muestra real se evalúa sin sus propias variantes sintéticas")
    print(" en el entrenamiento — comparación justa con la línea base)")
    reporte_aum = modelo_aum.evaluar_loocv_agrupado(grupos, evaluables)
    print(f"Exactitud global: {reporte_aum['exactitud_global']*100:.1f}% "
          f"({reporte_aum['total_muestras_evaluadas']} muestras evaluadas, "
          f"{reporte_aum['total_muestras_entrenamiento']} en el pool de entrenamiento)")

    print("\n--- Comparación por palabra ---")
    for palabra in reporte_base["palabras"]:
        base = reporte_base["por_palabra"][palabra]["exactitud"] * 100
        aum = reporte_aum["por_palabra"].get(palabra, {}).get("exactitud", 0.0) * 100
        signo = "▲" if aum > base else ("▼" if aum < base else "=")
        print(f"   {palabra:>10}: base {base:5.1f}%  ->  aumentado {aum:5.1f}%  {signo}")

    diferencia = (reporte_aum["exactitud_global"] - reporte_base["exactitud_global"]) * 100
    print(f"\nDiferencia global: {diferencia:+.1f} puntos porcentuales")
    if diferencia <= 0:
        print("⚠️  El aumento de datos NO mejoró la exactitud honesta (LOOCV agrupado).")
        print("   Esto es un resultado válido para documentar en RESEARCH_LOG,")
        print("   no un fallo del script — el punto 1 del plan puede no aportar")
        print("   con este tamaño de muestra y debe reportarse tal cual salió.")

    DIR_REPORTES = RAIZ / "reportes"
    DIR_REPORTES.mkdir(exist_ok=True)
    from datetime import datetime
    marca = datetime.now().strftime("%Y%m%d_%H%M%S")
    salida = {
        "fecha": datetime.now().isoformat(timespec="seconds"),
        "base": reporte_base,
        "aumentado": reporte_aum,
        "diferencia_puntos_porcentuales": diferencia,
    }
    ruta = DIR_REPORTES / f"comparacion_aumento_{marca}.json"
    ruta.write_text(json.dumps(salida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ Comparación guardada en {ruta.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
