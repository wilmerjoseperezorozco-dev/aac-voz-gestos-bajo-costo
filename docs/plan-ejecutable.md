# Plan ejecutable — de MVP a publicación

> Visión de expansión multimodal (móvil, bocinas, Raspberry Pi + pantalla +
> cámara, Kinect/Arduino) y comparativa con sistemas profesionales:
> ver [propuesta-expansion.md](propuesta-expansion.md).

## Fase 0 — Ya completada (2026-07-06)

- [x] Pipeline completo funcionando en la PC: grabación → MFCC+DTW → k-NN →
      voz sintetizada, verificado con 91.7% LOOCV en datos sintéticos.
- [x] Protocolo de validación documentado.
- [x] Primer entrenamiento con voz real de YP: 77.5% LOOCV (80 muestras),
      con depuración documentada de 30 muestras (registros/descartes.csv).
- [x] Hallazgo: el «no» de YP es inconsistente → sustituir por vocalización
      alternativa que ella repita igual (práctica estándar AAC).

## Fase 1 — Validación con YP (semanas 1-2)

- [ ] Consentimiento informado firmado.
- [ ] 3+ sesiones de grabación (80 muestras totales, `src/grabar.py`).
- [ ] Entrenar y archivar reportes de `entrenar.py` por sesión (evolución).
- [ ] 30+ intentos en vivo con confirmación s/n (`src/predecir.py`).
- [ ] Test de línea base con 3-5 oyentes externos (protocolo §4).
- **Entregable:** carpeta `reportes/` con evidencia fechada para la sustentación.

## Fase 2 — Presentación universitaria (semana 3)

- [ ] Presentación: problema → enfoque personalizado → demo → métricas → costo.
- [ ] Ensayar demo en vivo + plan B (`demo_sintetico.py`) + video grabado.
- [ ] Una diapositiva de limitaciones (n=1, vocabulario cerrado) — da seriedad.

## Fase 3 — Soluciones audaces a explorar (semanas 4-8)

Ordenadas por relación impacto/esfuerzo:

1. **Transferencia con modelos preentrenados (Wav2Vec2/Whisper encoder).**
   Usar los embeddings de un modelo grande como características en lugar de
   MFCC y mantener el k-NN. Con las mismas 80 muestras suele duplicar la
   robustez al ruido. Torch ya está instalado en esta PC. *Esfuerzo: bajo.*
2. **Ampliación progresiva de vocabulario (8 → 25 → 50 palabras)** con
   selección guiada por la familia: las palabras que YP más necesita.
3. **Tablero híbrido imagen+voz:** como ella reconoce imágenes, mostrar las
   4 predicciones más probables como tarjetas grandes y que confirme
   señalando/tocando. Convierte errores del modelo en interacción útil.
4. **App PWA en el celular** (grabación y predicción en el navegador,
   modelo servido localmente) — libera a la familia de la PC.
5. **Predicción de frases:** n-gramas sobre el historial de uso
   ("dolor" → sugerir "cabeza/estómago"). El CSV de predicciones ya
   registra la secuencia temporal necesaria.
6. **Micrófono de contacto casero (laringófono DIY, ~$20.000 COP):** piezo +
   preamplificador simple pegado al cuello; capta vibración laríngea e ignora
   el ruido ambiente. El accesorio "casero" con más impacto científico.

## Fase 4 — Publicación (meses 2-4)

- [ ] **Repositorio público:** subir código + `data_demo/` + reportes
      agregados. NUNCA `data/` (biometría). Licencia MIT o Apache-2.0.
- [ ] **Artículo corto** (paper estudiantil / semillero): formato estudio de
      caso n=1 con línea base humana. Objetivos: RENATA, encuentros de
      semilleros ACOFI, o revista de ingeniería de la universidad.
- [ ] **Video demo de 2 min** (con autorización explícita de YP).
- [ ] Contactar fundaciones de parálisis cerebral / afasia en Barranquilla
      para pilotos con 2-3 participantes más (pasar de n=1 a serie de casos).

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| YP no produce vocalizaciones consistentes | El sistema aprende CUALQUIER patrón repetible (hasta un soplo o vocal sostenida distinta por palabra); reducir vocabulario a 4 palabras si hace falta |
| Ruido en el lugar de grabación | Grabar siempre en el mismo cuarto; explorar laringófono DIY (Fase 3.6) |
| Demo falla en la universidad | `demo_sintetico.py` + video pregrabado |
| Datos sensibles expuestos | `data/` fuera de cualquier repo; alias YP en todo documento |
