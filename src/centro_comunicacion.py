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
        "subtitulo": "Vocabulario amplio (35 símbolos) — arma oraciones completas",
        "script": "tablero_escaneo.py",
        "color": "#1F4E79",
        "consola": False,  # ventana propia (Tkinter)
    },
    {
        "titulo": "🗣️ Voz directa",
        "subtitulo": "11 palabras — respuesta inmediata para necesidades urgentes",
        "script": "predecir.py",
        "color": "#2E7D32",
        "consola": True,  # pide ENTER en terminal -- necesita consola propia
    },
    {
        "titulo": "👋 Gestos",
        "subtitulo": "3 gestos — alternativa cuando la voz no es viable",
        "script": "gestos_predecir.py",
        "color": "#C05A00",
        "consola": True,
    },
    {
        "titulo": "🔀 Voz + gestos (secuencial)",
        "subtitulo": "Gesto como desempate cuando la voz no está segura",
        "script": "multimodal_predecir.py",
        "color": "#6A1B9A",
        "consola": True,
    },
]


procesos_activos: dict[str, subprocess.Popen] = {}


def esta_corriendo(nombre_script: str) -> bool:
    proceso = procesos_activos.get(nombre_script)
    return proceso is not None and proceso.poll() is None


def lanzar(nombre_script: str, boton: tk.Button, texto_original: str, consola: bool) -> None:
    """Evita abrir el mismo modo dos veces -- hallazgo 2026-07-14: varios
    clics accidentales sobre el mismo botón lanzaron 4 copias de
    multimodal_predecir.py compitiendo por el mismo micrófono/cámara,
    causando confusión real durante la sesión con YP.

    Los scripts de consola (predecir.py, gestos_predecir.py,
    multimodal_predecir.py) usan input() para esperar ENTER -- lanzados
    sin consola propia mueren de inmediato con EOFError (causa raíz real
    de la confusión de hoy, no solo los clics duplicados). En Windows
    necesitan CREATE_NEW_CONSOLE para heredar un stdin interactivo real."""
    if esta_corriendo(nombre_script):
        return
    ruta = SRC / nombre_script
    kwargs = {}
    if consola and sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
    procesos_activos[nombre_script] = subprocess.Popen(
        [sys.executable, str(ruta)], cwd=str(RAIZ), **kwargs)
    boton.config(text=f"{texto_original}  (abierto ✓)", state="disabled")


def main() -> None:
    root = tk.Tk()
    root.title("Centro de comunicación — YP")
    root.geometry("640x520")

    tk.Label(root, text="Centro de comunicación", font=("Segoe UI", 18, "bold")).pack(pady=(20, 4))
    tk.Label(root, text="Elige una sección para practicar", font=("Segoe UI", 11),
             fg="#595959").pack(pady=(0, 20))

    botones: dict[str, tk.Button] = {}
    for seccion in SECCIONES:
        marco = tk.Frame(root, relief="ridge", borderwidth=1)
        marco.pack(fill="x", padx=30, pady=8)

        boton = tk.Button(
            marco, text=seccion["titulo"], font=("Segoe UI", 14, "bold"),
            bg=seccion["color"], fg="white", anchor="w", padx=16, pady=10)
        boton.config(command=lambda s=seccion["script"], b=boton, t=seccion["titulo"], c=seccion["consola"]:
                     lanzar(s, b, t, c))
        boton.pack(fill="x")
        botones[seccion["script"]] = boton

        tk.Label(marco, text=seccion["subtitulo"], font=("Segoe UI", 10),
                 fg="#595959", anchor="w", padx=16).pack(fill="x", pady=(0, 6))

    tk.Label(root, text="Cada sección se abre en su propia ventana — ciérrala antes\n"
                         "de volver a presionar el mismo botón.",
             font=("Segoe UI", 9), fg="#8A8A8A", justify="center").pack(pady=16)

    def revisar_procesos_cerrados() -> None:
        for seccion in SECCIONES:
            script = seccion["script"]
            if script in procesos_activos and not esta_corriendo(script):
                botones[script].config(text=seccion["titulo"], state="normal")
                del procesos_activos[script]
        root.after(1000, revisar_procesos_cerrados)

    revisar_procesos_cerrados()
    root.mainloop()


if __name__ == "__main__":
    main()
