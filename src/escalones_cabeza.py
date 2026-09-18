"""Tarea de escalones con la cabeza: ¿la persona gira hacia el lado que se ilumina?

Uso:
    py -3.12 src/escalones_cabeza.py
    py -3.12 src/escalones_cabeza.py --sin-monitor        # pantalla completa
    py -3.12 src/escalones_cabeza.py --alias CTRL1 --nota "texto"
    py -3.12 src/escalones_cabeza.py --hold 6 --sin-sonido

Tres círculos grandes (izquierda, centro, derecha); uno se ilumina a la vez
y se mantiene ~5 s, con un tono corto al cambiar. La persona gira la cabeza
hacia el círculo iluminado y lo sostiene. Es una elección discreta ("girar y
sostener"), más cercana a un gesto que a un seguimiento continuo, y no
necesita calibración: se compara la postura (yaw) de la cabeza en los tramos
"izquierda" contra los de "derecha" con una prueba de permutación exacta.

Con 4 tramos por lado, la separación completa por azar tiene p = 2/70 (0.029).
Orden fijo de la secuencia, para que las sesiones sean comparables.

Requiere modelos/face_landmarker.task. Los datos (biometría) van a
data_mirada/, fuera de GitHub. ESC aborta; nada se guarda al abortar.
"""

from __future__ import annotations

import sys
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "src"))

import monitor_operador as mon  # noqa: E402
import persecucion_mirada as pm  # noqa: E402
from mirada_modelo import SECUENCIA_ESCALONES, analizar_escalones  # noqa: E402

if sys.stdout is not None and sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FRACCION_X = {"I": 0.15, "C": 0.50, "D": 0.85}     # posición horizontal de cada círculo


def posicion(lado: str, pantalla: tuple[int, int]) -> tuple[float, float]:
    return FRACCION_X[lado] * pantalla[0], pantalla[1] / 2


def dibujar_escalones(pantalla, activo: str | None, cara_ok: bool, paso: str):
    ancho, alto = pantalla
    lienzo = np.zeros((alto, ancho, 3), np.uint8)
    radio = int(0.12 * alto)
    for lado in ("I", "C", "D"):
        cx, cy = (int(v) for v in posicion(lado, pantalla))
        if lado == activo:
            cv2.circle(lienzo, (cx, cy), radio, (0, 200, 0), -1)
            cv2.circle(lienzo, (cx, cy), radio, (255, 255, 255), 4)
            cv2.circle(lienzo, (cx, cy), radio // 4, (0, 0, 255), -1)
        else:
            cv2.circle(lienzo, (cx, cy), radio, (70, 70, 70), 3)
    cv2.putText(lienzo, paso, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (140, 140, 140), 1)
    cv2.circle(lienzo, (25, alto - 25), 7, (0, 200, 0) if cara_ok else (0, 0, 255), -1)
    return lienzo


def tono() -> None:
    try:
        import winsound
        winsound.Beep(660, 110)
    except Exception:            # sin sonido disponible: la prueba sigue igual
        pass


def main() -> None:
    args = sys.argv[1:]
    rapido = "--rapido" in args
    sin_espera = "--sin-espera" in args
    con_sonido = "--sin-sonido" not in args
    con_monitor = "--sin-monitor" not in args
    alias = (args[args.index("--alias") + 1] if "--alias" in args
             else pm.CONFIG["participante"]["alias"])
    nota = args[args.index("--nota") + 1] if "--nota" in args else ""
    hold = 1.5 if rapido else 5.0
    if "--hold" in args:
        hold = float(args[args.index("--hold") + 1])
    analiza_desde = 0.5 if rapido else min(2.0, hold * 0.4)
    ventana = "--ventana" in args or (con_monitor and mon.num_monitores() <= 1)
    pantalla = (800, 450) if ventana else pm.tamano_pantalla()

    cara = pm.crear_detector()
    cap = cv2.VideoCapture(pm.CONFIG["camara"]["indice"], cv2.CAP_DSHOW)
    if not cap.isOpened():
        raise SystemExit("No se pudo abrir la cámara")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    hilo = pm.HiloCamara(cap, cara, pm.extraer_cabeza, 6, con_monitor)
    hilo.start()

    if ventana:
        cv2.namedWindow(pm.VENTANA, cv2.WINDOW_AUTOSIZE)
        cv2.moveWindow(pm.VENTANA, 0, 0)
    else:
        cv2.namedWindow(pm.VENTANA, cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(pm.VENTANA, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    if con_monitor:
        mon.crear_ventana(*mon.posicion_ventana(pantalla[0], ventana))

    total = hold * len(SECUENCIA_ESCALONES)
    print("=" * 60)
    print(f"  ESCALONES CON LA CABEZA — {alias} — {len(SECUENCIA_ESCALONES)} pasos de "
          f"{hold:.0f} s ({total:.0f} s)")
    print("  Un círculo se ilumina; la persona gira la cabeza hacia él y lo sostiene.")
    print("  ESC aborta (no se guarda nada).")
    print("=" * 60)

    try:
        if not sin_espera:
            pm.esperar_espacio(
                hilo, pantalla,
                f"{alias}  |  punto verde = cara detectada  |  ESPACIO para empezar")
        hilo.iniciar_fase(
            lambda t: posicion(SECUENCIA_ESCALONES[min(int(t // hold),
                                                       len(SECUENCIA_ESCALONES) - 1)],
                               pantalla), 0.0)
        inicio, anterior = time.monotonic(), -1
        while True:
            t = time.monotonic() - inicio
            if t >= total:
                break
            paso = int(t // hold)
            if paso != anterior:
                anterior = paso
                if con_sonido:
                    tono()
            cv2.imshow(pm.VENTANA, dibujar_escalones(
                pantalla, SECUENCIA_ESCALONES[paso], hilo.cara_ok,
                f"{paso + 1}/{len(SECUENCIA_ESCALONES)}"))
            pm.mostrar_monitor(hilo)
            if cv2.waitKey(15) == 27:
                raise KeyboardInterrupt
        datos, total_frames = hilo.resultado()
    except KeyboardInterrupt:
        print("\nAbortado.")
        return
    finally:
        estadisticas = hilo.estadisticas()
        hilo.parar = True
        hilo.join(timeout=2)
        cap.release()
        cv2.destroyAllWindows()

    if len(datos) < 30:
        print(f"\n❌ Solo {len(datos)} frames válidos (de {total_frames}). "
              "Mejor luz y la cara centrada frente a la cámara.")
        return
    escalones = [(i * hold, lado) for i, lado in enumerate(SECUENCIA_ESCALONES)]
    r = analizar_escalones(datos[:, 0], datos[:, 3], escalones, hold, analiza_desde)

    print("\n" + "=" * 60)
    print(f"  RESULTADO — {alias} — escalones")
    print("=" * 60)
    print(f"  Tramos analizados: {r['n_izq']} izquierda, {r['n_der']} derecha, "
          f"{r['n_centro']} centro (se descartan los primeros {analiza_desde:.1f} s de cada uno)")
    print(f"  Yaw medio: izquierda {r['media_izq']:+.1f}°   centro {r['media_centro']:+.1f}°   "
          f"derecha {r['media_der']:+.1f}°   (izq - der = {r['diferencia']:+.1f}°)")
    print(f"  Separa izquierda de derecha por completo: "
          f"{'SÍ' if r['separacion_completa'] else 'no'}   |   "
          f"p (permutación exacta) = {r['p_permutacion']:.3f}   |   d = {r['d_cohen']:.1f}")
    print(f"  Estabilidad dentro de cada tramo (desv. media del yaw): "
          f"{r['estabilidad_media']:.1f}°")
    print("  Entorno: "
          f"{estadisticas['fps']:.0f} fps | cara {estadisticas['tasa_cara']:.0%} | "
          f"brillo {estadisticas['brillo']:.0f} | "
          f"{estadisticas['pct_frames_con_aviso']:.0f}% de frames con aviso")
    if r["separacion_completa"] and r["p_permutacion"] <= 0.05:
        print("  Lectura: la cabeza se ubica distinto según el lado iluminado "
              "(respuesta clara y sostenida).")
    else:
        print("  Lectura: no se distingue de forma fiable el lado. Con 4 y 4 tramos "
              "el p mínimo posible es 0.029; con menos respuesta no se alcanza.")

    if rapido:
        print("\n  (--rapido: prueba corta, no se guarda nada)")
        return
    pm.DIR_DATOS.mkdir(exist_ok=True)
    sello = datetime.now().strftime("%Y%m%d_%H%M%S")
    np.savez_compressed(
        pm.DIR_DATOS / f"escalones_{sello}.npz", datos=datos, alias=alias,
        secuencia=np.array(SECUENCIA_ESCALONES), hold_s=hold,
        analiza_desde_s=analiza_desde, pantalla=np.array(pantalla))
    pm.DIR_REGISTROS.mkdir(exist_ok=True)
    pm.agregar_csv(pm.DIR_REGISTROS / "sesiones_escalones.csv", {
        "fecha_hora": datetime.now().isoformat(timespec="seconds"),
        "alias": alias, "nota": nota, "hold_s": hold, **r,
        **{k: estadisticas[k] for k in ("fps", "tasa_cara", "brillo",
                                        "ancho_cara_pct", "pct_frames_con_aviso")}})
    print(f"\n  Guardado en data_mirada/escalones_{sello}.npz")


if __name__ == "__main__":
    main()
