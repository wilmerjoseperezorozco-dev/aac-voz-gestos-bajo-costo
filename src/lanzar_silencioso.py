"""Lanzador para presentaciones/demos: abre el centro de comunicación sin
ninguna ventana de consola (pensado para usarse con pythonw.exe).

Diferencia clave frente a llamar centro_comunicacion.py directo con
pythonw: si algo falla, pythonw normalmente lo esconde en silencio (la
ventana simplemente no aparece, sin ninguna pista de por qué). Este
lanzador atrapa cualquier error y lo escribe en
`logs/error_presentacion.log`, para poder diagnosticarlo después de una
demo en vivo en vez de quedarse sin ninguna explicación.

Uso (con pythonw, sin consola):
    pythonw.exe src/lanzar_silencioso.py
"""

from __future__ import annotations

import sys
import traceback
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

LOG = RAIZ / "logs" / "error_presentacion.log"


def main() -> None:
    try:
        import centro_comunicacion
        centro_comunicacion.main()
    except Exception:
        LOG.parent.mkdir(exist_ok=True)
        with LOG.open("a", encoding="utf-8") as f:
            f.write(f"\n=== {datetime.now().isoformat(timespec='seconds')} ===\n")
            f.write(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
