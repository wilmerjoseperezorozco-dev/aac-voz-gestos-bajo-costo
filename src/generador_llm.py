"""Capa 2 — expansión generativa: convierte una semilla semántica (2-5
símbolos seleccionados en el tablero) en una oración fluida en español,
usando un modelo de lenguaje pequeño y 100% LOCAL (nunca en la nube — la
intención comunicativa de YP es dato sensible, igual que sus audios).

Precedente: KWickChat (Shen et al., 2022) — bolsa de palabras clave +
contexto → oración conversacional completa, ver
docs/arquitectura-vocabulario-nucleo-generativo.md.
"""

from __future__ import annotations

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RUTA_MODELO = RAIZ / "modelos" / "llm" / "qwen2.5-1.5b-instruct-q4_k_m.gguf"

# Raíces léxicas que cubren la conjugación/género esperada de cada concepto
# del vocabulario núcleo -- usado para detectar alucinación (hallazgo
# 2026-07-10, reportes/hallazgo_primera_sesion_tablero_20260710.md: el
# generador introduce en la oración conceptos que NO fueron seleccionados,
# ej. "yo + yo" -> "estoy cansada, quiero descansar"). "yo"/"tu" quedan
# fuera: son pronombres sin huella léxica fija, se reflejan en la
# conjugación del verbo, no se pueden verificar por substring. "querer" e
# "ir" también quedan fuera de la verificación: probado contra los 27
# intentos reales de hoy, ambos aparecen constantemente como conectores
# gramaticales naturales ("quiero", "voy") incluso cuando no fueron
# seleccionados -- marcarlos producía falsos positivos en oraciones
# correctas (ej. "mal + bano" -> "Me siento mal, quiero ir al baño", una
# paráfrasis válida, no una alucinación).
VARIANTES_CONCEPTO: dict[str, list[str]] = {
    "agua": [r"agua"],
    "dolor": [r"dol\w*", r"duel\w*"],
    "bano": [r"bañ\w*"],
    "ayuda": [r"ayud\w*"],
    "comer": [r"com(?:e|es|emos|en|ida|iendo|ió)\w*"],  # evita falso match con "comprar"
    "mama": [r"mam\w*"],
    "cansada": [r"cansad\w*", r"descans\w*"],
    "frio": [r"fr[ií]\w*"],
    "salir": [r"sal\w*"],
    "mas": [r"\bm[aá]s\b"],
    "terminar": [r"termin\w*", r"acab\w*"],
    "bien": [r"\bbien\b"],
    "mal": [r"\bmal\b"],
    "papa": [r"pap[aá]\w*"],
    "casa": [r"casa"],
    "television": [r"televisi[oó]n", r"\btele\b"],
    "feliz": [r"feliz", r"content\w*"],
    "triste": [r"trist\w*"],
    "gracias": [r"gracias"],
    "gato": [r"gat\w*"],
    "perro": [r"perr\w*"],
    "gallina": [r"gallin\w*"],
    "culebra": [r"culebr\w*"],
    "ave": [r"\bave[s]?\b"],
    "tortuga": [r"tortug\w*"],
    "manzana": [r"manzan\w*"],
    "banano": [r"banan\w*", r"pl[aá]tano\w*"],
    "dormir": [r"dorm\w*", r"duerm\w*"],
    "jugar": [r"jug\w*"],
    "ver": [r"\bveo\b", r"\bves\b", r"\bviendo\b", r"\bvi\b"],
    "escuchar": [r"escuch\w*", r"\boigo\b"],
}

PROMPT_SISTEMA = (
    "Eres un asistente que ayuda a una mujer con desconexión motora del "
    "habla a comunicarse (usa SIEMPRE concordancia de género femenino: "
    "'cansada', 'dolorida', no 'cansado', 'dolorido'). Ella selecciona "
    "palabras clave, en orden, en un "
    "tablero. Tu única tarea es generar UNA sola oración corta, natural y "
    "gramaticalmente correcta en español que use TODAS las palabras "
    "seleccionadas (ninguna se descarta) y exprese lo que ELLA quiere decir. "
    "Reglas: "
    "(1) Toda palabra de estado, necesidad, emoción o síntoma (dolor, "
    "cansada, frio, etc.) se refiere a ELLA MISMA, nunca a otra persona "
    "mencionada en la selección. "
    "(2) Las personas mencionadas (mamá, papá) son el OBJETO de la "
    "petición, no quien tiene el síntoma. "
    "(3) No agregues información, nombres ni hechos que no estén en las "
    "palabras dadas. "
    "(4) Responde SOLO con la oración, sin explicaciones ni comillas."
)

# Par de ejemplo como TURNOS reales de conversación (no texto embebido en
# el prompt de sistema) — con modelos pequeños esto ancla el patrón mucho
# mejor que un ejemplo narrado, y evita que el ejemplo "se filtre" a
# respuestas de entradas no relacionadas (fallo observado y documentado
# en reportes/hallazgo_generador_llm_20260709.md).
EJEMPLO_USUARIO = "Palabras seleccionadas: dolor + cabeza + mama."
EJEMPLO_ASISTENTE = "Me duele la cabeza, quiero que venga mamá."


def _detectar_alucinacion(simbolos: list[str], oracion: str) -> bool:
    """True si la oración generada menciona un concepto del vocabulario
    núcleo que NO fue seleccionado -- señal de que el modelo inventó
    contenido en vez de expandir fielmente la selección. No detecta
    alucinaciones con vocabulario totalmente ajeno al núcleo (ej. "cabeza"),
    solo las que reutilizan otro símbolo del tablero -- el caso observado
    con más frecuencia en la sesión 2026-07-10."""
    texto = oracion.lower()
    seleccionados = set(simbolos)
    for concepto, variantes in VARIANTES_CONCEPTO.items():
        if concepto in seleccionados:
            continue
        if any(re.search(patron, texto) for patron in variantes):
            return True
    return False


def _respaldo_plantilla(simbolos: list[str]) -> str:
    """Concatenación simple y segura de los símbolos seleccionados, usada
    cuando el generador produce contenido no seleccionado. Sacrifica
    fluidez por exactitud garantizada -- la confirmación de YP sigue
    siendo obligatoria de todas formas, pero esta oración nunca inventa
    una necesidad distinta a la que ella seleccionó."""
    return " ".join(simbolos).capitalize() + "."


class GeneradorOraciones:
    def __init__(self, ruta_modelo: Path = RUTA_MODELO):
        if not ruta_modelo.exists():
            raise FileNotFoundError(
                f"No se encontró el modelo en {ruta_modelo}. "
                "Descárgalo desde https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF")
        from llama_cpp import Llama  # import perezoso: carga pesada solo si se usa
        self.modelo = Llama(model_path=str(ruta_modelo), n_ctx=512, verbose=False)

    def generar(self, simbolos: list[str], contexto: str = "") -> str:
        """simbolos: palabras seleccionadas en orden (2-5). contexto:
        detalle opcional (hora del día, quién está presente, etc.)."""
        semilla = " + ".join(simbolos)
        prompt_usuario = f"Palabras seleccionadas: {semilla}."
        if contexto:
            prompt_usuario += f" Contexto: {contexto}."

        mensajes = [
            {"role": "system", "content": PROMPT_SISTEMA},
            {"role": "user", "content": EJEMPLO_USUARIO},
            {"role": "assistant", "content": EJEMPLO_ASISTENTE},
            {"role": "user", "content": prompt_usuario},
        ]
        respuesta = self.modelo.create_chat_completion(
            messages=mensajes, max_tokens=60, temperature=0.4, top_p=0.9)
        texto = respuesta["choices"][0]["message"]["content"].strip()
        oracion = texto.strip('"').strip("«»")

        if _detectar_alucinacion(simbolos, oracion):
            print(f"  ⚠️  Alucinación detectada (concepto no seleccionado en "
                  f"la oración) — usando respaldo seguro en vez de: «{oracion}»")
            return _respaldo_plantilla(simbolos)
        return oracion


if __name__ == "__main__":
    import sys
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("Cargando modelo local (puede tardar unos segundos)...")
    generador = GeneradorOraciones()

    pruebas = [
        (["dolor", "cabeza", "mama"], ""),
        (["agua", "querer"], ""),
        (["cansada", "salir", "no"], "de noche"),
        (["yo", "querer", "television"], ""),
        (["bano", "ayuda"], ""),
    ]
    print("\n--- Pruebas de generación ---")
    for simbolos, contexto in pruebas:
        oracion = generador.generar(simbolos, contexto)
        ctx = f" (contexto: {contexto})" if contexto else ""
        print(f"  {' + '.join(simbolos)}{ctx}")
        print(f"    -> {oracion}\n")
