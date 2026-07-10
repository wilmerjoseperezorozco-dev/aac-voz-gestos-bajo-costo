"""Vocabulario núcleo — Fase 1 (20-30 símbolos, ver
docs/arquitectura-vocabulario-nucleo-generativo.md).

Combina el vocabulario ya validado con YP (voz/gestos, 92-100% de
confianza en consenso unánime) con conceptos núcleo adicionales de uso
frecuente, siguiendo las categorías del árbol motivo-causa-deseo de
comunicacion-explicativa.md. Los íconos se resuelven contra ARASAAC
(https://arasaac.org) por palabra clave en español.
"""

from __future__ import annotations

VOCABULARIO_NUCLEO = [
    # Ya validados con YP (voz y/o gesto) — reutilizados sin entrenamiento nuevo
    {"palabra": "agua", "categoria": "necesidad", "ya_validado": True},
    {"palabra": "si", "categoria": "respuesta", "ya_validado": True},
    {"palabra": "no", "categoria": "respuesta", "ya_validado": True},
    {"palabra": "dolor", "categoria": "salud", "ya_validado": True},
    {"palabra": "bano", "categoria": "necesidad", "ya_validado": True},
    {"palabra": "ayuda", "categoria": "urgencia", "ya_validado": True},
    {"palabra": "comer", "categoria": "necesidad", "ya_validado": True},
    {"palabra": "mama", "categoria": "persona", "ya_validado": True},
    {"palabra": "cansada", "categoria": "estado", "ya_validado": True},
    {"palabra": "frio", "categoria": "estado", "ya_validado": True},
    {"palabra": "salir", "categoria": "accion", "ya_validado": True},

    # Núcleo adicional — Fase 1, seleccionados vía tablero + escaneo,
    # no requieren reconocimiento de voz individual
    {"palabra": "yo", "categoria": "pronombre", "ya_validado": False},
    {"palabra": "tu", "categoria": "pronombre", "ya_validado": False},
    {"palabra": "querer", "categoria": "verbo_nucleo", "ya_validado": False},
    {"palabra": "ir", "categoria": "verbo_nucleo", "ya_validado": False},
    {"palabra": "mas", "categoria": "verbo_nucleo", "ya_validado": False},
    {"palabra": "terminar", "categoria": "verbo_nucleo", "ya_validado": False},
    {"palabra": "bien", "categoria": "estado", "ya_validado": False},
    {"palabra": "mal", "categoria": "estado", "ya_validado": False},
    {"palabra": "papa", "categoria": "persona", "ya_validado": False},
    {"palabra": "casa", "categoria": "lugar", "ya_validado": False},
    {"palabra": "television", "categoria": "objeto", "ya_validado": False},
    {"palabra": "feliz", "categoria": "emocion", "ya_validado": False},
    {"palabra": "triste", "categoria": "emocion", "ya_validado": False},
    {"palabra": "gracias", "categoria": "social", "ya_validado": False},
]
