"""Vocabulario núcleo — Fase 2: léxico universal completo organizado por
categorías (ver docs/arquitectura-vocabulario-nucleo-generativo.md).

Base académica de la ampliación (2026-07-16): Soto & Cooper (2021), "An
early Spanish vocabulary for children who use AAC" (Augmentative and
Alternative Communication, doi:10.1080/07434618.2021.1881822) — la lista
de 218 palabras del Apéndice A, derivada del traslape entre la base de
datos Piñeiro-Manzano (producción espontánea de 200 niños
hispanohablantes) y los Inventarios MacArthur-Bates en español (IDHC).
Es, hasta donde se pudo verificar, la única lista de léxico inicial en
español para AAC validada por pares.

Curaduría aplicada sobre la lista original:
  - Se conservan INTACTOS los 35 símbolos ya practicados por YP en
    sesiones reales (mismo emoji, misma palabra) — la continuidad del
    aprendizaje pesa más que la pureza de la lista.
  - Se excluyen ítems específicos de primera infancia (biberón, cuna,
    carriola, etc.): la usuaria es una mujer adulta; se respeta la
    dignidad de edad aunque el nivel de comunicación simbólica sea
    inicial (práctica estándar en AAC de adultos).
  - Se excluyen palabras función que el generador (Capa 2) aporta por
    sí solo: artículos, preposiciones, conjunciones y la mayoría de
    pronombres/demostrativos — en un tablero con expansión generativa,
    seleccionarlas sería esfuerzo motor sin ganancia semántica.
  - Emoji como ícono provisional (sin dependencia de internet en vivo);
    migración a pictogramas ARASAAC cacheados queda como mejora futura.

"si"/"no" siguen con `seleccionable=False`: reservados para su rol
validado de CONFIRMACIÓN (ver reportes/hallazgo_generador_llm_20260709.md).
"""

from __future__ import annotations

# El orden de CATEGORIAS define el orden de las páginas en el tablero.
# "Básicos" replica los símbolos ya dominados/practicados por YP.
CATEGORIAS = [
    "Básicos",
    "Personas",
    "Acciones",
    "Comida",
    "Animales",
    "Cuerpo",
    "Casa y cosas",
    "Lugares",
    "Describir",
    "Preguntas y saludos",
]

VOCABULARIO_NUCLEO = [
    # ------------- respuestas reservadas (no seleccionables) -------------
    {"palabra": "si", "emoji": "✅", "categoria": "respuesta", "seleccionable": False},
    {"palabra": "no", "emoji": "❌", "categoria": "respuesta", "seleccionable": False},

    # ------------- Básicos: los 24 ya practicados por YP -------------
    {"palabra": "yo", "emoji": "🙋‍♀️", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "tu", "emoji": "👉", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "querer", "emoji": "💭", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "ir", "emoji": "🚶‍♀️", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "mas", "emoji": "➕", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "terminar", "emoji": "🏁", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "ayuda", "emoji": "🆘", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "agua", "emoji": "💧", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "bano", "emoji": "🚻", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "comer", "emoji": "🍽️", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "dormir", "emoji": "🛌", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "dolor", "emoji": "🤕", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "cansada", "emoji": "😴", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "frio", "emoji": "🥶", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "bien", "emoji": "🙂", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "mal", "emoji": "🙁", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "feliz", "emoji": "😄", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "triste", "emoji": "😢", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "gracias", "emoji": "🙏", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "salir", "emoji": "🚪", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "jugar", "emoji": "⚽", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "ver", "emoji": "👀", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "escuchar", "emoji": "👂", "categoria": "Básicos", "seleccionable": True},
    {"palabra": "television", "emoji": "📺", "categoria": "Básicos", "seleccionable": True},

    # ------------- Personas -------------
    {"palabra": "mama", "emoji": "👩", "categoria": "Personas", "seleccionable": True},
    {"palabra": "papa", "emoji": "👨", "categoria": "Personas", "seleccionable": True},
    {"palabra": "abuela", "emoji": "👵", "categoria": "Personas", "seleccionable": True},
    {"palabra": "abuelo", "emoji": "👴", "categoria": "Personas", "seleccionable": True},
    {"palabra": "hermano", "emoji": "👦", "categoria": "Personas", "seleccionable": True},
    {"palabra": "hermana", "emoji": "👧", "categoria": "Personas", "seleccionable": True},
    {"palabra": "amigo", "emoji": "🧑‍🤝‍🧑", "categoria": "Personas", "seleccionable": True},
    {"palabra": "tia", "emoji": "👩‍🦱", "categoria": "Personas", "seleccionable": True},

    # ------------- Acciones -------------
    {"palabra": "abrir", "emoji": "🔓", "categoria": "Acciones", "seleccionable": True},
    {"palabra": "cerrar", "emoji": "🔒", "categoria": "Acciones", "seleccionable": True},
    {"palabra": "dar", "emoji": "🤲", "categoria": "Acciones", "seleccionable": True},
    {"palabra": "beber", "emoji": "🚰", "categoria": "Acciones", "seleccionable": True},
    {"palabra": "hablar", "emoji": "🗣️", "categoria": "Acciones", "seleccionable": True},
    {"palabra": "cantar", "emoji": "🎤", "categoria": "Acciones", "seleccionable": True},
    {"palabra": "bailar", "emoji": "💃", "categoria": "Acciones", "seleccionable": True},
    {"palabra": "caminar", "emoji": "🚶", "categoria": "Acciones", "seleccionable": True},
    {"palabra": "correr", "emoji": "🏃", "categoria": "Acciones", "seleccionable": True},
    {"palabra": "llorar", "emoji": "😭", "categoria": "Acciones", "seleccionable": True},
    {"palabra": "buscar", "emoji": "🔍", "categoria": "Acciones", "seleccionable": True},
    {"palabra": "esperar", "emoji": "⏳", "categoria": "Acciones", "seleccionable": True},
    {"palabra": "comprar", "emoji": "🛒", "categoria": "Acciones", "seleccionable": True},
    {"palabra": "cocinar", "emoji": "👨‍🍳", "categoria": "Acciones", "seleccionable": True},
    {"palabra": "parar", "emoji": "🛑", "categoria": "Acciones", "seleccionable": True},
    {"palabra": "venir", "emoji": "🫴", "categoria": "Acciones", "seleccionable": True},
    {"palabra": "sentar", "emoji": "💺", "categoria": "Acciones", "seleccionable": True},
    {"palabra": "gustar", "emoji": "❤️", "categoria": "Acciones", "seleccionable": True},

    # ------------- Comida -------------
    {"palabra": "manzana", "emoji": "🍎", "categoria": "Comida", "seleccionable": True},
    {"palabra": "banano", "emoji": "🍌", "categoria": "Comida", "seleccionable": True},
    {"palabra": "leche", "emoji": "🥛", "categoria": "Comida", "seleccionable": True},
    {"palabra": "jugo", "emoji": "🧃", "categoria": "Comida", "seleccionable": True},
    {"palabra": "galleta", "emoji": "🍪", "categoria": "Comida", "seleccionable": True},
    {"palabra": "helado", "emoji": "🍦", "categoria": "Comida", "seleccionable": True},
    {"palabra": "chocolate", "emoji": "🍫", "categoria": "Comida", "seleccionable": True},
    {"palabra": "comida", "emoji": "🍲", "categoria": "Comida", "seleccionable": True},
    {"palabra": "naranja", "emoji": "🍊", "categoria": "Comida", "seleccionable": True},
    {"palabra": "dulce", "emoji": "🍬", "categoria": "Comida", "seleccionable": True},

    # ------------- Animales -------------
    {"palabra": "gato", "emoji": "🐈", "categoria": "Animales", "seleccionable": True},
    {"palabra": "perro", "emoji": "🐕", "categoria": "Animales", "seleccionable": True},
    {"palabra": "gallina", "emoji": "🐔", "categoria": "Animales", "seleccionable": True},
    {"palabra": "culebra", "emoji": "🐍", "categoria": "Animales", "seleccionable": True},
    {"palabra": "ave", "emoji": "🐦", "categoria": "Animales", "seleccionable": True},
    {"palabra": "tortuga", "emoji": "🐢", "categoria": "Animales", "seleccionable": True},
    {"palabra": "caballo", "emoji": "🐴", "categoria": "Animales", "seleccionable": True},
    {"palabra": "vaca", "emoji": "🐄", "categoria": "Animales", "seleccionable": True},
    {"palabra": "pollo", "emoji": "🐤", "categoria": "Animales", "seleccionable": True},
    {"palabra": "pescado", "emoji": "🐟", "categoria": "Animales", "seleccionable": True},
    {"palabra": "raton", "emoji": "🐭", "categoria": "Animales", "seleccionable": True},
    {"palabra": "mariposa", "emoji": "🦋", "categoria": "Animales", "seleccionable": True},
    {"palabra": "conejo", "emoji": "🐰", "categoria": "Animales", "seleccionable": True},

    # ------------- Cuerpo -------------
    {"palabra": "cabeza", "emoji": "🧠", "categoria": "Cuerpo", "seleccionable": True},
    {"palabra": "boca", "emoji": "👄", "categoria": "Cuerpo", "seleccionable": True},
    {"palabra": "mano", "emoji": "✋", "categoria": "Cuerpo", "seleccionable": True},
    {"palabra": "nariz", "emoji": "👃", "categoria": "Cuerpo", "seleccionable": True},
    {"palabra": "ojo", "emoji": "👁️", "categoria": "Cuerpo", "seleccionable": True},
    {"palabra": "oreja", "emoji": "🦻", "categoria": "Cuerpo", "seleccionable": True},
    {"palabra": "pie", "emoji": "🦶", "categoria": "Cuerpo", "seleccionable": True},

    # ------------- Casa y cosas -------------
    {"palabra": "casa", "emoji": "🏠", "categoria": "Casa y cosas", "seleccionable": True},
    {"palabra": "silla", "emoji": "🪑", "categoria": "Casa y cosas", "seleccionable": True},
    {"palabra": "luz", "emoji": "💡", "categoria": "Casa y cosas", "seleccionable": True},
    {"palabra": "telefono", "emoji": "📱", "categoria": "Casa y cosas", "seleccionable": True},
    {"palabra": "cuchara", "emoji": "🥄", "categoria": "Casa y cosas", "seleccionable": True},
    {"palabra": "vaso", "emoji": "🥤", "categoria": "Casa y cosas", "seleccionable": True},
    {"palabra": "cama", "emoji": "🛏️", "categoria": "Casa y cosas", "seleccionable": True},
    {"palabra": "reloj", "emoji": "⌚", "categoria": "Casa y cosas", "seleccionable": True},
    {"palabra": "zapato", "emoji": "👟", "categoria": "Casa y cosas", "seleccionable": True},
    {"palabra": "sombrero", "emoji": "👒", "categoria": "Casa y cosas", "seleccionable": True},
    {"palabra": "espejo", "emoji": "🪞", "categoria": "Casa y cosas", "seleccionable": True},

    # ------------- Lugares (y transporte / naturaleza) -------------
    {"palabra": "calle", "emoji": "🛣️", "categoria": "Lugares", "seleccionable": True},
    {"palabra": "cocina", "emoji": "🍳", "categoria": "Lugares", "seleccionable": True},
    {"palabra": "parque", "emoji": "🌳", "categoria": "Lugares", "seleccionable": True},
    {"palabra": "playa", "emoji": "🏖️", "categoria": "Lugares", "seleccionable": True},
    {"palabra": "carro", "emoji": "🚗", "categoria": "Lugares", "seleccionable": True},
    {"palabra": "moto", "emoji": "🏍️", "categoria": "Lugares", "seleccionable": True},
    {"palabra": "avion", "emoji": "✈️", "categoria": "Lugares", "seleccionable": True},
    {"palabra": "tren", "emoji": "🚂", "categoria": "Lugares", "seleccionable": True},
    {"palabra": "sol", "emoji": "☀️", "categoria": "Lugares", "seleccionable": True},
    {"palabra": "estrella", "emoji": "⭐", "categoria": "Lugares", "seleccionable": True},
    {"palabra": "flor", "emoji": "🌸", "categoria": "Lugares", "seleccionable": True},

    # ------------- Describir -------------
    {"palabra": "grande", "emoji": "🔼", "categoria": "Describir", "seleccionable": True},
    {"palabra": "pequeno", "emoji": "🔽", "categoria": "Describir", "seleccionable": True},
    {"palabra": "limpio", "emoji": "🧼", "categoria": "Describir", "seleccionable": True},
    {"palabra": "lindo", "emoji": "🌟", "categoria": "Describir", "seleccionable": True},
    {"palabra": "caliente", "emoji": "🔥", "categoria": "Describir", "seleccionable": True},
    {"palabra": "rojo", "emoji": "🔴", "categoria": "Describir", "seleccionable": True},
    {"palabra": "azul", "emoji": "🔵", "categoria": "Describir", "seleccionable": True},
    {"palabra": "amarillo", "emoji": "🟡", "categoria": "Describir", "seleccionable": True},
    {"palabra": "verde", "emoji": "🟢", "categoria": "Describir", "seleccionable": True},
    {"palabra": "blanco", "emoji": "⚪", "categoria": "Describir", "seleccionable": True},
    {"palabra": "arriba", "emoji": "⬆️", "categoria": "Describir", "seleccionable": True},
    {"palabra": "abajo", "emoji": "⬇️", "categoria": "Describir", "seleccionable": True},

    # ------------- Preguntas y saludos -------------
    {"palabra": "donde", "emoji": "❔", "categoria": "Preguntas y saludos", "seleccionable": True},
    {"palabra": "quien", "emoji": "🧐", "categoria": "Preguntas y saludos", "seleccionable": True},
    {"palabra": "que", "emoji": "❓", "categoria": "Preguntas y saludos", "seleccionable": True},
    {"palabra": "aqui", "emoji": "📍", "categoria": "Preguntas y saludos", "seleccionable": True},
    {"palabra": "otra_vez", "emoji": "🔁", "categoria": "Preguntas y saludos", "seleccionable": True},
    {"palabra": "hola", "emoji": "🤗", "categoria": "Preguntas y saludos", "seleccionable": True},
    {"palabra": "adios", "emoji": "👋", "categoria": "Preguntas y saludos", "seleccionable": True},
    {"palabra": "uno", "emoji": "1️⃣", "categoria": "Preguntas y saludos", "seleccionable": True},
    {"palabra": "dos", "emoji": "2️⃣", "categoria": "Preguntas y saludos", "seleccionable": True},
    {"palabra": "tres", "emoji": "3️⃣", "categoria": "Preguntas y saludos", "seleccionable": True},
    {"palabra": "cuatro", "emoji": "4️⃣", "categoria": "Preguntas y saludos", "seleccionable": True},
    {"palabra": "cinco", "emoji": "5️⃣", "categoria": "Preguntas y saludos", "seleccionable": True},
]


def simbolos_seleccionables() -> list[dict]:
    """Todos los símbolos que pueden aparecer en el tablero (excluye sí/no)."""
    return [s for s in VOCABULARIO_NUCLEO if s["seleccionable"]]


def simbolos_por_categoria(categoria: str) -> list[dict]:
    """Símbolos seleccionables de una categoría, en su orden de definición."""
    return [s for s in simbolos_seleccionables() if s["categoria"] == categoria]
