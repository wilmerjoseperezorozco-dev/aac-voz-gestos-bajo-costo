"""Calcula la métrica KSPC-equivalente ("Selecciones por Palabra
Comunicada", SPC) a partir de registros/predicciones_tablero.csv — ver
docs/metricas-fonoaudiologicas.md para la justificación y el resto de
métricas (tasa de comunicación, precisión semántica, naturalidad), que
requieren datos o evaluadores aún no disponibles.

No captura nada nuevo: solo lee lo que tablero_escaneo.py ya registra.

Uso (después de que haya sesiones reales con el tablero):
    python src/metricas_fonoaudiologicas.py
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
ARCHIVO_TABLERO = RAIZ / "registros" / "predicciones_tablero.csv"


def leer_intentos() -> list[dict]:
    if not ARCHIVO_TABLERO.exists():
        return []
    with ARCHIVO_TABLERO.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def spc_por_intento(fila: dict) -> float | None:
    """Selecciones de escaneo / palabras en la oración generada.

    None si la oración está vacía (no se puede dividir por cero).
    """
    n_simbolos = fila["simbolos_seleccionados"].count("+") + 1
    palabras = fila["oracion_generada"].split()
    if not palabras:
        return None
    return n_simbolos / len(palabras)


def main() -> None:
    intentos = leer_intentos()
    if not intentos:
        print("Aún no hay datos en registros/predicciones_tablero.csv "
              "(se generan al usar el tablero en sesiones reales).")
        return

    confirmados = [f for f in intentos if f.get("confirmada", "").strip().lower() == "si"]
    if not confirmados:
        print(f"{len(intentos)} intento(s) registrados, pero ninguno confirmado como correcto.")
        return

    valores_spc = [v for v in (spc_por_intento(f) for f in confirmados) if v is not None]
    promedio = sum(valores_spc) / len(valores_spc)

    print(f"Intentos confirmados analizados: {len(valores_spc)}")
    print(f"SPC promedio (selecciones por palabra generada): {promedio:.2f}")
    print("Referencia: teclado de escaneo letra por letra ≈ 1 selección "
          "por carácter (varias veces más selecciones por palabra que SPC).")


if __name__ == "__main__":
    main()
