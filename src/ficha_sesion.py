"""Ficha de sesión: registra el checklist de entorno (anexo B del protocolo)
con fecha y hora ANTES de empezar a grabar. Convierte el checklist de papel
en un registro real, verificable, con marca de tiempo.

Uso (correr una vez al inicio de cada sesión, antes de grabar.py/predecir.py):
    python src/ficha_sesion.py
"""

from __future__ import annotations

import csv
import sys
from datetime import datetime
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
DIR_REGISTROS = RAIZ / "registros"

CHECKLIST = [
    ("mic_fijo", "Micrófono en posición fija (audífonos/solapa puestos o boom ajustado)"),
    ("ruido_apagado", "Ventilador/TV/aire acondicionado apagados"),
    ("fondo_liso", "Fondo liso detrás de YP, sin gente ni movimiento"),
    ("luz_frontal", "Luz de frente, no a contraluz"),
    ("marcas_piso", "Silla y cámara en las marcas de cinta del piso"),
    ("evaluador_ciego", "Evaluador ciego presente (persona que confirma sin ver la pantalla)"),
    ("celular_lateral", "Celular lateral grabando como respaldo (opcional)"),
]


def preguntar_si_no(texto: str) -> str:
    while True:
        r = input(f"  [ ] {texto} — ¿listo? (s/n): ").strip().lower()
        if r in ("s", "n"):
            return "si" if r == "s" else "no"
        print("    responde 's' o 'n'")


def main() -> None:
    print("=" * 60)
    print("  FICHA DE SESIÓN — checklist de entorno (anexo B)")
    print("=" * 60)

    fila = {"fecha_hora": datetime.now().isoformat(timespec="seconds")}
    for clave, texto in CHECKLIST:
        fila[clave] = preguntar_si_no(texto)

    fila["presentes"] = input("\n  ¿Quién está presente hoy? ").strip()
    fila["animo_yp"] = input("  ¿Cómo se ve el ánimo/fatiga de YP hoy?: ").strip()
    fila["notas"] = input("  Observaciones adicionales (ENTER si ninguna): ").strip()

    faltantes = [texto for clave, texto in CHECKLIST
                 if fila[clave] == "no" and clave != "celular_lateral"]
    if faltantes:
        print("\n  ⚠️  Pendientes antes de grabar:")
        for f in faltantes:
            print(f"     - {f}")
    else:
        print("\n  ✅ Entorno listo. Puedes iniciar grabar.py / predecir.py")

    DIR_REGISTROS.mkdir(parents=True, exist_ok=True)
    archivo = DIR_REGISTROS / "fichas_sesion.csv"
    nuevo = not archivo.exists()
    campos = ["fecha_hora"] + [c for c, _ in CHECKLIST] + ["presentes", "animo_yp", "notas"]
    with archivo.open("a", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=campos)
        if nuevo:
            escritor.writeheader()
        escritor.writerow(fila)

    print(f"\nFicha guardada en {archivo.relative_to(RAIZ)}")


if __name__ == "__main__":
    main()
