"""Vocabulario núcleo — Fase 1 (20-30 símbolos, ver
docs/arquitectura-vocabulario-nucleo-generativo.md).

Combina el vocabulario ya validado con YP (voz/gestos, 92-100% de
confianza en consenso unánime) con conceptos núcleo adicionales de uso
frecuente, siguiendo las categorías del árbol motivo-causa-deseo de
comunicacion-explicativa.md.

Emojis como ícono provisional (Fase 1) — evita depender de una conexión a
internet en vivo durante la sesión con YP (fetch de ARASAAC queda como
mejora futura offline-cacheada, no como dependencia de tiempo real).

IMPORTANTE: "si" y "no" están marcados `seleccionable=False` — el
hallazgo de hoy (reportes/hallazgo_generador_llm_20260709.md) mostró que
el LLM descarta "no" de forma silenciosa y sistemática al generar
oraciones. Se reservan para su rol ya validado de CONFIRMACIÓN (escaneo y
predecir.py), no como contenido del tablero.
"""

from __future__ import annotations

VOCABULARIO_NUCLEO = [
    # Ya validados con YP (voz y/o gesto) — reutilizados sin entrenamiento nuevo
    {"palabra": "agua", "emoji": "💧", "categoria": "necesidad", "seleccionable": True},
    {"palabra": "si", "emoji": "✅", "categoria": "respuesta", "seleccionable": False},
    {"palabra": "no", "emoji": "❌", "categoria": "respuesta", "seleccionable": False},
    {"palabra": "dolor", "emoji": "🤕", "categoria": "salud", "seleccionable": True},
    {"palabra": "bano", "emoji": "🚻", "categoria": "necesidad", "seleccionable": True},
    {"palabra": "ayuda", "emoji": "🆘", "categoria": "urgencia", "seleccionable": True},
    {"palabra": "comer", "emoji": "🍽️", "categoria": "necesidad", "seleccionable": True},
    {"palabra": "mama", "emoji": "👩", "categoria": "persona", "seleccionable": True},
    {"palabra": "cansada", "emoji": "😴", "categoria": "estado", "seleccionable": True},
    {"palabra": "frio", "emoji": "🥶", "categoria": "estado", "seleccionable": True},
    {"palabra": "salir", "emoji": "🚪", "categoria": "accion", "seleccionable": True},

    # Núcleo adicional — Fase 1, seleccionados vía tablero + escaneo,
    # no requieren reconocimiento de voz individual
    {"palabra": "yo", "emoji": "🙋‍♀️", "categoria": "pronombre", "seleccionable": True},
    {"palabra": "tu", "emoji": "👉", "categoria": "pronombre", "seleccionable": True},
    {"palabra": "querer", "emoji": "💭", "categoria": "verbo_nucleo", "seleccionable": True},
    {"palabra": "ir", "emoji": "🚶‍♀️", "categoria": "verbo_nucleo", "seleccionable": True},
    {"palabra": "mas", "emoji": "➕", "categoria": "verbo_nucleo", "seleccionable": True},
    {"palabra": "terminar", "emoji": "🏁", "categoria": "verbo_nucleo", "seleccionable": True},
    {"palabra": "bien", "emoji": "🙂", "categoria": "estado", "seleccionable": True},
    {"palabra": "mal", "emoji": "🙁", "categoria": "estado", "seleccionable": True},
    {"palabra": "papa", "emoji": "👨", "categoria": "persona", "seleccionable": True},
    {"palabra": "casa", "emoji": "🏠", "categoria": "lugar", "seleccionable": True},
    {"palabra": "television", "emoji": "📺", "categoria": "objeto", "seleccionable": True},
    {"palabra": "feliz", "emoji": "😄", "categoria": "emocion", "seleccionable": True},
    {"palabra": "triste", "emoji": "😢", "categoria": "emocion", "seleccionable": True},
    {"palabra": "gracias", "emoji": "🙏", "categoria": "social", "seleccionable": True},

    # Ampliación 2026-07-10 — vocabulario de tema (fringe), personalizado
    # a la vida diaria de YP en Tubará (animales que menciona en familia,
    # frutas comunes) en vez de un set genérico. No requiere entrenamiento
    # de voz/gesto nuevo, igual que el resto de Capa 1.
    {"palabra": "gato", "emoji": "🐈", "categoria": "animal", "seleccionable": True},
    {"palabra": "perro", "emoji": "🐕", "categoria": "animal", "seleccionable": True},
    {"palabra": "gallina", "emoji": "🐔", "categoria": "animal", "seleccionable": True},
    {"palabra": "culebra", "emoji": "🐍", "categoria": "animal", "seleccionable": True},
    {"palabra": "ave", "emoji": "🐦", "categoria": "animal", "seleccionable": True},
    {"palabra": "tortuga", "emoji": "🐢", "categoria": "animal", "seleccionable": True},
    {"palabra": "manzana", "emoji": "🍎", "categoria": "fruta", "seleccionable": True},
    {"palabra": "banano", "emoji": "🍌", "categoria": "fruta", "seleccionable": True},
]


def simbolos_seleccionables() -> list[dict]:
    """Símbolos que aparecen en el tablero de escaneo (excluye sí/no)."""
    return [s for s in VOCABULARIO_NUCLEO if s["seleccionable"]]
