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
_VARIANTES_MANUALES: dict[str, list[str]] = {
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
    "casa": [r"\bcasa\b", r"\bcasita\b"],  # \b evita falso match con "casada"
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
    "jugar": [r"\bjug(?:ar|amos|ando|aba|u[eé])\b", r"\bjuega\w*", r"\bjuego\b"],  # no confundir con "jugo"
    "ver": [r"\bveo\b", r"\bves\b", r"\bviendo\b", r"\bvi\b"],
    "escuchar": [r"escuch\w*", r"\boigo\b"],
    # Verbos nuevos con conjugación irregular, raíz corta o riesgo de
    # colisión léxica -- el patrón automático no los cubre bien:
    "beber": [r"\bbeb\w*", r"\btomar\b", r"\btomo\b", r"\btoma\w*"],
    "venir": [r"\bven\w*", r"\bviene\w*", r"\bvengo\b"],
    # sentar restringido: "me siento mal" es del verbo SENTIR, no sentarse
    # (ambigüedad real del español) -- solo formas inequívocas de sentarse:
    "sentar": [r"\bsentar\w*", r"\bsentad[oa]s?\b", r"\bsi[eé]ntate\b"],
    "gustar": [r"\bgust\w*", r"\bencant\w*"],
    "cerrar": [r"\bcerr\w*", r"\bcierr\w*"],
    "esperar": [r"\besper\w*"],
    # parar restringido: la preposición "para" es omnipresente -- solo
    # formas inequívocas del verbo parar/detener:
    "parar": [r"\bparar\b", r"\bparad[oa]s?\b", r"\bp[aá]rate\b", r"\bpare\b", r"\bdet[eé]n\w*"],
    "abrir": [r"\babr(?:ir|e|o|es|imos|en|iendo|[ií]|i[oó])\b", r"\babiert\w*"],  # no confundir con "abrazo"
    "cantar": [r"\bcant(?:ar|a|o|as|amos|an|ando|aba|[eé]|[oó])\b"],  # no confundir con "cantidad"
    "comprar": [r"\bcompr(?:ar|a|o|as|amos|an|ando|aba|[eé]|[oó])\b"],  # no confundir con "comprende"
    "cocinar": [r"\bcocin(?:ar|o|as|amos|an|ando|aba|[eé]|[oó])\b"],  # no confundir con "cocina" (lugar)
    "cabeza": [r"\bcabez\w*"],
    "comida": [r"\bcomidas?\b"],  # femenino solo: "comido" es participio de comer
    "otra_vez": [r"\botra vez\b", r"\bde nuevo\b", r"\brepet\w*", r"\brepit\w*"],
    # Parientes con género: separados a mano para que "abuela" no marque
    # falsa alucinación cuando lo seleccionado fue "abuelo" (y viceversa):
    "abuela": [r"\babuel(?:a|as|ita|itas)\b"],
    "abuelo": [r"\babuel(?:o|os|ito|itos)\b"],
    "hermano": [r"\bherman(?:o|os|ito|itos)\b"],
    "hermana": [r"\bherman(?:a|as|ita|itas)\b"],
    "caliente": [r"\bcalient\w*", r"\bcalor\b"],
    "uno": [r"\buno\b"],  # exacto: "una"/"unos" son artículos omnipresentes
}

# Palabras exentas de verificación: pronombres sin huella léxica fija
# ("yo"/"tu" viven en la conjugación del verbo), conectores gramaticales
# naturales que el generador usa legítimamente sin selección explícita
# ("querer"->"quiero", "ir"->"voy", validado contra los 27 intentos del
# 2026-07-10), y palabras función demasiado frecuentes en cualquier
# oración española para servir de señal ("que", "aqui").
_EXENTAS_VERIFICACION = {"yo", "tu", "querer", "ir", "que", "aqui", "donde"}
# "donde" exenta: en el español costeño "ir donde mamá" es construcción
# legítima que el generador puede producir sin que "donde" esté
# seleccionado -- marcarla daría falsos positivos.

_VOCALES_FLEXIBLES = {"a": "[aá]", "e": "[eé]", "i": "[ií]", "o": "[oó]",
                      "u": "[uúü]", "n": "[nñ]"}


def _patron_flexible(texto: str) -> str:
    """Convierte una palabra sin tildes en un patrón tolerante a acentos y
    eñes (el vocabulario se guarda sin tildes, pero el LLM escribe
    'avión', 'pequeño', 'ratón')."""
    return "".join(_VOCALES_FLEXIBLES.get(c, re.escape(c)) for c in texto)


def _variantes_automaticas(palabra: str, categoria: str) -> list[str]:
    """Patrón conservador para palabras sin definición manual: verbos por
    raíz (sin la terminación -ar/-er/-ir), sustantivos/adjetivos por
    palabra completa con género/plural opcionales. Prefiere no detectar
    antes que producir falsos positivos -- la confirmación de YP sigue
    siendo la salvaguarda final."""
    if categoria == "Acciones" and palabra[-2:] in ("ar", "er", "ir") and len(palabra) > 4:
        return [r"\b" + _patron_flexible(palabra[:-2]) + r"\w*"]
    if palabra[-1] in ("o", "a"):
        return [r"\b" + _patron_flexible(palabra[:-1]) + r"(?:o|a|os|as|itos?|itas?)\b"]
    return [r"\b" + _patron_flexible(palabra) + r"(?:es|s)?\b"]


def _construir_variantes() -> dict[str, list[str]]:
    """Una sola fuente de verdad: cada símbolo seleccionable del
    vocabulario núcleo queda cubierto por la verificación anti-alucinación
    automáticamente, sin mantener una lista paralela a mano."""
    from vocabulario_nucleo import simbolos_seleccionables
    variantes: dict[str, list[str]] = {}
    for simbolo in simbolos_seleccionables():
        palabra = simbolo["palabra"]
        if palabra in _EXENTAS_VERIFICACION:
            continue
        if palabra in _VARIANTES_MANUALES:
            variantes[palabra] = _VARIANTES_MANUALES[palabra]
        else:
            variantes[palabra] = _variantes_automaticas(palabra, simbolo["categoria"])
    return variantes


VARIANTES_CONCEPTO: dict[str, list[str]] = _construir_variantes()

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
