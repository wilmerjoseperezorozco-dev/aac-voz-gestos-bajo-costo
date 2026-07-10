"""Centro de comunicación YP — menú central que reúne los modos ya
validados en secciones seleccionables, en vez de tratarlos como
alternativas excluyentes:

  - Tablero núcleo (Capa 1+2): escala a vocabulario amplio, arma
    oraciones completas.
  - Voz directa (11 palabras, 79.7% LOOCV): reconoce la voz específica
    de YP, respuesta inmediata para necesidades urgentes.
  - Gestos (3 gestos, 80% LOOCV): canal alternativo cuando la voz no es
    viable ese día (fatiga, ronquera).
  - Voz + gestos combinados (captura secuencial, ver
    reportes/hallazgo_interferencia_20260708.md).

Cada botón lanza el script correspondiente como proceso independiente —
no se reescribe ni se altera ninguno de los modos ya validados.

Uso:
    python src/centro_comunicacion.py
"""

from __future__ import annotations

import subprocess
import sys
import tkinter as tk
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
SRC = RAIZ / "src"

SECCIONES = [
    {
        "titulo": "🧩 Tablero núcleo",
        "subtitulo": "Vocabulario amplio (31 símbolos) — arma oraciones completas",
        "script": "tablero_escaneo.py",
        "color": "#1F4E79",
    },
    {
        "titulo": "🗣️ Voz directa",
        "subtitulo": "11 palabras — respuesta inmediata para necesidades urgentes",
        "script": "predecir.py",
        "color": "#2E7D32",
    },
    {
        "titulo": "👋 Gestos",
        "subtitulo": "3 gestos — alternativa cuando la voz no es viable",
        "script": "gestos_predecir.py",
        "color": "#C05A00",
    },
    {
        "titulo": "🔀 Voz + gestos (secuencial)",
        "subtitulo": "Gesto como desempate cuando la voz no está segura",
        "script": "multimodal_predecir.py",
        "color": "#6A1B9A",
    },
]


def lanzar(nombre_script: str) -> None:
    ruta = SRC / nombre_script
    subprocess.Popen([sys.executable, str(ruta)], cwd=str(RAIZ))


def main() -> None:
    root = tk.Tk()
    root.title("Centro de comunicación — YP")
    root.geometry("640x520")

    tk.Label(root, text="Centro de comunicación", font=("Segoe UI", 18, "bold")).pack(pady=(20, 4))
    tk.Label(root, text="Elige una sección para practicar", font=("Segoe UI", 11),
             fg="#595959").pack(pady=(0, 20))

    for seccion in SECCIONES:
        marco = tk.Frame(root, relief="ridge", borderwidth=1)
        marco.pack(fill="x", padx=30, pady=8)

        boton = tk.Button(
            marco, text=seccion["titulo"], font=("Segoe UI", 14, "bold"),
            bg=seccion["color"], fg="white", anchor="w", padx=16, pady=10,
            command=lambda s=seccion["script"]: lanzar(s))
        boton.pack(fill="x")

        tk.Label(marco, text=seccion["subtitulo"], font=("Segoe UI", 10),
                 fg="#595959", anchor="w", padx=16).pack(fill="x", pady=(0, 6))

    tk.Label(root, text="Cada sección se abre en su propia ventana — puedes cerrarla\n"
                         "y volver aquí para elegir otra.",
             font=("Segoe UI", 9), fg="#8A8A8A", justify="center").pack(pady=16)

    root.mainloop()


if __name__ == "__main__":
    main()
