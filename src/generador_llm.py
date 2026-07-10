"""Capa 2 — expansión generativa: convierte una semilla semántica (2-5
símbolos seleccionados en el tablero) en una oración fluida en español,
usando un modelo de lenguaje pequeño y 100% LOCAL (nunca en la nube — la
intención comunicativa de YP es dato sensible, igual que sus audios).

Precedente: KWickChat (Shen et al., 2022) — bolsa de palabras clave +
contexto → oración conversacional completa, ver
docs/arquitectura-vocabulario-nucleo-generativo.md.
"""

from __future__ import annotations

from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RUTA_MODELO = RAIZ / "modelos" / "llm" / "qwen2.5-1.5b-instruct-q4_k_m.gguf"

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
        return texto.strip('"').strip("«»")


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
