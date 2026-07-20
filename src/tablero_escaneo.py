"""Capa 1 — Interfaz de escaneo del tablero núcleo.

El sistema resalta símbolos en secuencia; YP confirma la selección con
una señal ya validada. Al reunir 2-5 símbolos, la Capa 2 (LLM local,
generador_llm.py) expande la selección en una oración, que se pronuncia
por TTS y SIEMPRE debe ser confirmada por YP antes de darse por válida
— ningún resultado generado se comunica sin esa confirmación (ver
reportes/hallazgo_generador_llm_20260709.md: ~20% de margen de error
real, la confirmación no es opcional).

Tres formas de seleccionar un símbolo, disponibles simultáneamente:
  - "teclado" (predeterminado, recomendado para la primera prueba):
    barra espaciadora confirma el símbolo resaltado por el escaneo
    automático. Rápido, confiable, sin depender de latencia de
    reconocimiento de voz.
  - "clic directo": hacer clic con el mouse en cualquier símbolo lo
    selecciona de inmediato, sin esperar a que el escaneo llegue hasta
    ahí. Agregado tras la sesión 2026-07-10: el orden fijo del escaneo
    (fila por fila) no coincide con el orden en que YP piensa la frase
    — si "baño" está en la primera fila y "yo" varias filas más abajo,
    esperar el ciclo completo del escaneo para juntarlos es lento y
    confuso. El clic directo permite construir la selección en cualquier
    orden, útil también como modo de aprendizaje guiado.
  - "voz" (experimental): reutiliza el modelo de voz ya validado
    (modelo_yp.npz) escuchando "sí" en cada símbolo resaltado. Nota
    honesta: con ~150 referencias la verificación puede tardar 2-3s por
    símbolo — se siente más lento que el modo teclado. Probar con
    cautela antes de usarlo con YP en la sesión real.

Uso:
    python src/tablero_escaneo.py            # modo teclado
    python src/tablero_escaneo.py --voz       # modo voz (experimental)
"""

from __future__ import annotations

import csv
import sys
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

from vocabulario_nucleo import CATEGORIAS, simbolos_por_categoria  # noqa: E402
from generador_llm import GeneradorOraciones  # noqa: E402
from predecir import archivar_si_esquema_cambio, hablar, iniciar_tts  # noqa: E402

DIR_REGISTROS = RAIZ / "registros"
MIN_SIMBOLOS = 2
MAX_SIMBOLOS = 5
INTERVALO_TECLADO_MS = 2800  # subido de 1800 tras la sesión 2026-07-10: YP necesitó más tiempo de reacción
UMBRAL_CONFIANZA_VOZ = 0.99  # mismo criterio que predecir.py: consenso unánime


def registrar_intento(fila: dict) -> None:
    DIR_REGISTROS.mkdir(exist_ok=True)
    archivo = DIR_REGISTROS / "predicciones_tablero.csv"
    campos = ["fecha_hora", "simbolos_seleccionados", "contexto",
              "oracion_generada", "confirmada"]
    archivar_si_esquema_cambio(archivo, campos)
    nuevo = not archivo.exists()
    with archivo.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        if nuevo:
            w.writeheader()
        w.writerow(fila)


class TableroEscaneo:
    def __init__(self, root: tk.Tk, modo_voz: bool = False):
        self.root = root
        self.modo_voz = modo_voz
        self.categoria_actual = CATEGORIAS[0]
        self.simbolos = simbolos_por_categoria(self.categoria_actual)
        self.indice_resaltado = 0
        self.seleccionados: list[str] = []
        self.escaneando = False
        # Escaneo de dos niveles (estándar AAC "group-item scanning"):
        # primero se escanean las categorías; al confirmar una, se escanean
        # sus símbolos. Necesario desde la ampliación al núcleo universal
        # completo (~130 símbolos, Soto & Cooper 2021) — un escaneo plano
        # sobre 130 celdas tomaría >6 min por ciclo a 2.8 s/símbolo.
        self.fase_escaneo = "categorias"

        self.root.title("Tablero núcleo — MVP comunicación YP")
        self.root.geometry("900x600")
        self.root.minsize(700, 400)

        self.etiqueta_estado = tk.Label(
            root, text="Presiona INICIAR para escanear, o haz clic directo en un símbolo",
            font=("Segoe UI", 14, "bold"))
        self.etiqueta_estado.pack(side="top", pady=8)

        # Botones, semilla y modo van FIJOS abajo (nunca se ocultan por
        # falta de espacio) -- se empacan primero, en orden de abajo hacia
        # arriba, para reservar su lugar antes de que el canvas tome el
        # espacio restante.
        self.etiqueta_modo = tk.Label(
            root, text=f"Modo de confirmación: {'VOZ (experimental)' if modo_voz else 'TECLADO (barra espaciadora)'}",
            font=("Segoe UI", 10), fg="#595959")
        self.etiqueta_modo.pack(side="bottom", pady=4)

        marco_botones = tk.Frame(root)
        marco_botones.pack(side="bottom", pady=6)
        tk.Button(marco_botones, text="INICIAR ESCANEO", command=self.iniciar,
                  font=("Segoe UI", 12), bg="#1F4E79", fg="white").pack(side="left", padx=6)
        tk.Button(marco_botones, text="GENERAR ORACIÓN (con lo seleccionado)",
                  command=self.generar, font=("Segoe UI", 12),
                  bg="#2E7D32", fg="white").pack(side="left", padx=6)
        tk.Button(marco_botones, text="REINICIAR", command=self.reiniciar,
                  font=("Segoe UI", 12)).pack(side="left", padx=6)

        self.etiqueta_semilla = tk.Label(
            root, text="Seleccionados: (ninguno)", font=("Segoe UI", 13))
        self.etiqueta_semilla.pack(side="bottom", pady=6)

        # Barra de categorías: una página de símbolos a la vez (Fase 2,
        # núcleo universal completo). Clic directo en una categoría la
        # abre; el escaneo automático también las recorre (nivel 1).
        self.marco_categorias = tk.Frame(root)
        self.marco_categorias.pack(side="top", pady=(0, 4))
        self.botones_categoria: dict[str, tk.Button] = {}
        for nombre in CATEGORIAS:
            boton = tk.Button(
                self.marco_categorias, text=nombre, font=("Segoe UI", 10, "bold"),
                bg="#E8EEF5", cursor="hand2", padx=6, pady=3,
                command=lambda n=nombre: self._clic_categoria(n))
            boton.pack(side="left", padx=2)
            self.botones_categoria[nombre] = boton

        # Grid de la página actual (con scroll de respaldo por si alguna
        # categoría crece más allá de lo que cabe en pantalla).
        marco_scroll = tk.Frame(root)
        marco_scroll.pack(side="top", fill="both", expand=True, padx=8)
        canvas = tk.Canvas(marco_scroll, highlightthickness=0)
        barra = tk.Scrollbar(marco_scroll, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=barra.set)
        barra.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.marco_grid = tk.Frame(canvas)
        ventana_grid = canvas.create_window((0, 0), window=self.marco_grid, anchor="n")

        def _actualizar_scrollregion(_evento=None) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.coords(ventana_grid, canvas.winfo_width() / 2, 0)

        self.marco_grid.bind("<Configure>", _actualizar_scrollregion)
        canvas.bind("<Configure>", _actualizar_scrollregion)
        canvas.bind_all("<MouseWheel>",
                         lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        self.celdas: list[tk.Label] = []
        self._construir_pagina()

        self.root.bind("<space>", self._confirmar_teclado)

        self.motor_tts = iniciar_tts()
        self.generador = None  # carga perezosa: el LLM pesa, solo al primer uso
        self.modelo_voz = None
        if self.modo_voz:
            from modelo import ClasificadorPalabras
            self.modelo_voz = ClasificadorPalabras.cargar(RAIZ / "modelos" / "modelo_yp")

    def _construir_pagina(self) -> None:
        """(Re)construye la cuadrícula con los símbolos de la categoría
        actual y resalta la pestaña activa en la barra de categorías."""
        import math

        for celda in self.celdas:
            celda.destroy()
        self.celdas = []
        self.simbolos = simbolos_por_categoria(self.categoria_actual)

        columnas = max(1, math.ceil(math.sqrt(max(len(self.simbolos), 1) * 16 / 9)))
        for i, simbolo in enumerate(self.simbolos):
            texto = f"{simbolo['emoji']}\n{simbolo['palabra']}"
            fondo = "#81C784" if simbolo["palabra"] in self.seleccionados else "white"
            celda = tk.Label(self.marco_grid, text=texto, font=("Segoe UI", 12),
                             width=9, height=3, relief="ridge", borderwidth=2,
                             bg=fondo, cursor="hand2")
            celda.grid(row=i // columnas, column=i % columnas, padx=3, pady=3)
            celda.bind("<Button-1>", lambda _evento, indice=i: self._seleccionar_por_clic(indice))
            self.celdas.append(celda)

        for nombre, boton in self.botones_categoria.items():
            activo = nombre == self.categoria_actual
            boton.config(bg="#1F4E79" if activo else "#E8EEF5",
                         fg="white" if activo else "black")

    def _clic_categoria(self, nombre: str) -> None:
        self.escaneando = False
        self.categoria_actual = nombre
        self.indice_resaltado = 0
        self._construir_pagina()

    def iniciar(self) -> None:
        if self.escaneando:
            return
        self.escaneando = True
        self.fase_escaneo = "categorias"
        self.indice_resaltado = 0
        self.etiqueta_estado.config(
            text="Escaneando categorías... (barra espaciadora elige)" if not self.modo_voz
            else "Escaneando... (di «sí» cuando se resalte tu opción)")
        self._ciclo_escaneo()

    def _limpiar_resaltados(self) -> None:
        for i, celda in enumerate(self.celdas):
            fondo = "#81C784" if self.simbolos[i]["palabra"] in self.seleccionados else "white"
            celda.config(bg=fondo)
        for nombre, boton in self.botones_categoria.items():
            activo = nombre == self.categoria_actual
            boton.config(bg="#1F4E79" if activo else "#E8EEF5",
                         fg="white" if activo else "black")

    def _ciclo_escaneo(self) -> None:
        if not self.escaneando:
            return
        self._limpiar_resaltados()
        if self.fase_escaneo == "categorias":
            nombre = CATEGORIAS[self.indice_resaltado % len(CATEGORIAS)]
            self.botones_categoria[nombre].config(bg="#FFEB3B", fg="black")
        else:
            self.celdas[self.indice_resaltado % len(self.simbolos)].config(bg="#FFEB3B")

        if self.modo_voz:
            self.root.update()
            confirmado = self._verificar_voz()
            if confirmado:
                self._confirmar_escaneo()
            else:
                self._avanzar_indice()
            self.root.after(200, self._ciclo_escaneo)
        else:
            self.root.after(INTERVALO_TECLADO_MS, self._avanzar_teclado)

    def _avanzar_indice(self) -> None:
        limite = len(CATEGORIAS) if self.fase_escaneo == "categorias" else len(self.simbolos)
        self.indice_resaltado = (self.indice_resaltado + 1) % max(limite, 1)

    def _avanzar_teclado(self) -> None:
        if not self.escaneando:
            return
        self._avanzar_indice()
        self._ciclo_escaneo()

    def _confirmar_escaneo(self) -> None:
        """Confirmación durante el escaneo: en fase de categorías abre la
        categoría resaltada y pasa a escanear sus símbolos; en fase de
        símbolos selecciona el símbolo resaltado."""
        if self.fase_escaneo == "categorias":
            self.categoria_actual = CATEGORIAS[self.indice_resaltado % len(CATEGORIAS)]
            self._construir_pagina()
            self.fase_escaneo = "simbolos"
            self.indice_resaltado = 0
            self.etiqueta_estado.config(
                text=f"Escaneando {self.categoria_actual}... (barra espaciadora elige; "
                     "al seleccionar vuelve a categorías)")
        else:
            self._seleccionar_actual()
            self.fase_escaneo = "categorias"
            self.indice_resaltado = CATEGORIAS.index(self.categoria_actual)

    def _confirmar_teclado(self, evento=None) -> None:
        if not self.escaneando or self.modo_voz:
            return
        self._confirmar_escaneo()

    def _verificar_voz(self) -> bool:
        """Captura ~1.2s de audio y verifica si coincide con 'sí' al
        umbral de consenso unánime. Nota: con el banco de referencias
        actual esto puede tardar 2-3s (ver docstring del módulo)."""
        import numpy as np
        import sounddevice as sd
        from audio_features import extraer_mfcc

        audio = sd.rec(int(1.2 * 16000), samplerate=16000, channels=1, dtype="float32")
        sd.wait()
        audio = audio.flatten()
        if float(np.sqrt(np.mean(audio ** 2))) < 1e-4:
            return False
        secuencia = extraer_mfcc(audio, 16000, n_mfcc=13)
        palabra, confianza = self.modelo_voz.predecir(secuencia)
        return palabra == "si" and confianza >= UMBRAL_CONFIANZA_VOZ

    def _seleccionar_actual(self) -> None:
        self._seleccionar_indice(self.indice_resaltado % max(len(self.simbolos), 1))

    def _seleccionar_por_clic(self, indice: int) -> None:
        """Selección directa con el mouse: permite armar la oración en el
        orden en que YP la piensa, sin depender del orden fijo del
        escaneo (hallazgo 2026-07-10: esperar varios ciclos completos
        para juntar símbolos distantes en la cuadrícula es lento y
        confuso). Funciona esté o no activo el escaneo automático."""
        self.escaneando = False
        self._seleccionar_indice(indice)

    def _seleccionar_indice(self, indice: int) -> None:
        simbolo = self.simbolos[indice]["palabra"]
        if len(self.seleccionados) >= MAX_SIMBOLOS:
            return
        self.seleccionados.append(simbolo)
        self.etiqueta_semilla.config(
            text=f"Seleccionados: {' + '.join(self.seleccionados)}")
        self.celdas[indice].config(bg="#81C784")
        if len(self.seleccionados) >= MAX_SIMBOLOS:
            self.escaneando = False
            self.etiqueta_estado.config(
                text=f"Máximo de {MAX_SIMBOLOS} alcanzado — presiona GENERAR")

    def reiniciar(self) -> None:
        self.escaneando = False
        self.fase_escaneo = "categorias"
        self.seleccionados = []
        self.etiqueta_semilla.config(text="Seleccionados: (ninguno)")
        self._limpiar_resaltados()
        self.etiqueta_estado.config(text="Presiona INICIAR para escanear, o haz clic directo en un símbolo")

    def generar(self) -> None:
        self.escaneando = False
        if len(self.seleccionados) < MIN_SIMBOLOS:
            self.etiqueta_estado.config(
                text=f"Selecciona al menos {MIN_SIMBOLOS} símbolos antes de generar")
            return

        if self.generador is None:
            self.etiqueta_estado.config(text="Cargando modelo de lenguaje local...")
            self.root.update()
            self.generador = GeneradorOraciones()

        oracion = self.generador.generar(self.seleccionados)
        self.etiqueta_estado.config(text=f"Oración generada: «{oracion}»")
        hablar(self.motor_tts, oracion)

        respuesta = self._pedir_confirmacion(oracion)
        registrar_intento({
            "fecha_hora": datetime.now().isoformat(timespec="seconds"),
            "simbolos_seleccionados": " + ".join(self.seleccionados),
            "contexto": "",
            "oracion_generada": oracion,
            "confirmada": respuesta,
        })
        self.reiniciar()

    def _pedir_confirmacion(self, oracion: str) -> str:
        """Ventana modal simple: ¿la oración expresa lo que YP quiso decir?
        NUNCA se omite este paso — es la salvaguarda obligatoria dado el
        ~20% de margen de error medido en generador_llm.py."""
        ventana = tk.Toplevel(self.root)
        ventana.title("Confirmar")
        ventana.geometry("500x180")
        tk.Label(ventana, text=f"«{oracion}»", font=("Segoe UI", 14, "bold"),
                wraplength=460).pack(pady=16)
        tk.Label(ventana, text="¿Esto es lo que YP quiso decir?",
                font=("Segoe UI", 12)).pack(pady=4)

        resultado = {"valor": ""}

        def responder(valor: str) -> None:
            resultado["valor"] = valor
            ventana.destroy()

        marco = tk.Frame(ventana)
        marco.pack(pady=12)
        tk.Button(marco, text="SÍ, correcto", command=lambda: responder("si"),
                  bg="#2E7D32", fg="white", font=("Segoe UI", 12), width=12).pack(side="left", padx=8)
        tk.Button(marco, text="NO, incorrecto", command=lambda: responder("no"),
                  bg="#C62828", fg="white", font=("Segoe UI", 12), width=12).pack(side="left", padx=8)
        ventana.grab_set()
        self.root.wait_window(ventana)
        return resultado["valor"]


def main() -> None:
    if sys.platform == "win32":
        import ctypes
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            pass

    modo_voz = "--voz" in sys.argv
    root = tk.Tk()
    TableroEscaneo(root, modo_voz=modo_voz)
    root.update_idletasks()
    ancho = root.winfo_screenwidth()
    alto = root.winfo_screenheight()
    root.geometry(f"{ancho}x{alto - 70}+0+0")
    if sys.platform == "win32":
        try:
            root.state("zoomed")
        except tk.TclError:
            pass
    root.lift()
    root.attributes("-topmost", True)
    root.after(200, lambda: root.attributes("-topmost", False))
    root.focus_force()
    root.mainloop()


if __name__ == "__main__":
    main()
