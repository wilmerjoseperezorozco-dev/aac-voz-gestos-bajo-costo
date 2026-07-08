# Propuesta de expansión — Sistema multimodal de comunicación asistida

**Para presentar en la universidad.** Este documento posiciona el MVP frente al
estado del arte profesional y define la ruta hacia un sistema multimodal
(voz + imágenes + movimiento) sobre hardware económico.

## 1. Dónde está el MVP frente a los sistemas profesionales

| Sistema | Enfoque | Limitación que nuestro MVP ataca |
|---|---|---|
| Google Project Relate | ASR personalizado para habla disártrica (app Android) | Requiere grabar **500+ frases** para crear el modelo; inglés y pocos idiomas; requiere cuenta y nube |
| Voiceitt | Reconocimiento de habla atípica, comercial | Suscripción paga; requiere internet |
| Tobii Dynavox y similares | Dispositivos generadores de habla (SGD) | Costo típico **>US$6.000** (reportado por makers de AAC open source) |
| **Nuestro MVP** | Clasificador personal k-NN+DTW, offline | **10 muestras por palabra**, $0 de hardware adicional, español, datos 100% locales |

Argumento central para la sustentación: la literatura confirma que los ASR
comerciales fallan con habla disártrica y que la personalización es la vía
(Project Relate, Euphonia, patente WO2025259567A1 de reconocimiento
disártrico personalizado). Nuestro aporte no es competir con Google: es
demostrar que la **versión mínima personalizada funciona con recursos de un
hogar colombiano** y validarlo con protocolo documentado.

## 2. Ruta multimodal — "lectura completa" de la persona

YP reconoce sonidos e imágenes y tiene movilidad parcial. Cada canal es
una fuente de señal; el sistema profesional combina las tres:

```
  VOZ (listo, 77.5% LOOCV)      → k-NN + DTW sobre MFCC
  IMAGEN/TABLERO (fase 2)       → cámara + selección visual confirmatoria
  MOVIMIENTO/GESTO (fase 3)     → visión artificial o sensor inercial
                ↓
  FUSIÓN: la palabra final = voto ponderado de los canales disponibles
```

### Canal 2 — Imágenes (Raspberry Pi + pantalla + cámara)

Precedente directo: el proyecto open source **Talker** (Hackaday) construyó
un generador de habla por toque de iconos sobre Raspberry Pi, como
alternativa de bajo costo a dispositivos de US$6.000. Nuestra versión
añade la cámara para dos usos: (a) que YP señale/mire tarjetas físicas y
el sistema las reconozca, y (b) dataset de imágenes propio para entrenar
reconocimiento de sus gestos faciales de sí/no.

**Kit unificado recomendado (todo oficial Raspberry Pi, se consigue en
Colombia vía distribuidores como Vistronica/Sigma):**

| Componente | Precio ref. |
|---|---|
| Raspberry Pi 5 (4 GB) | ~US$60 |
| Pantalla táctil oficial 7" | ~US$60-75 |
| Camera Module 3 | ~US$25 |
| MicroSD 64 GB + fuente + carcasa | ~US$25 |
| **Total** | **~US$170-185 (≈ $700-800 mil COP)** |

El código actual corre sin cambios en la Pi (numpy/scipy puro, sin GPU).
La misma Pi conecta a **bocinas** por jack/Bluetooth (la "proyección por
bocinas" que buscas: la voz de YP amplificada en la sala de su casa) y
sirve la interfaz como **PWA en el celular** de la familia por WiFi local.

### Canal 3 — Movimiento (validación planificada)

Tres opciones evaluadas, en orden recomendado:

1. **MediaPipe + webcam (costo $0, validar PRIMERO).** Estimación de pose y
   manos con la cámara que ya existe. Validado clínicamente en la
   literatura: MediaPipe Hands alcanza precisión útil para aplicaciones
   clínicas de seguimiento de mano, y MediaPipe Pose es un modelo de bajo
   costo computacional (corre en la Pi). Si un gesto repetible de YP
   (levantar mano, giro de cabeza) se detecta consistentemente, tenemos el
   canal de movimiento sin comprar nada.
2. **Kinect (v2 de segunda mano, ~US$30-60 + adaptador).** Cámara de
   profundidad con esqueleto 3D; amplia literatura en rehabilitación
   (evaluación de marcha, Parkinson) con costo <US$500 y ventaja de
   funcionar sin controles físicos — ideal para usuarios con compromiso
   motor/cognitivo. Nota: Microsoft descontinuó Azure Kinect (sucesor:
   Orbbec Femto Bolt); para MVP conviene Kinect v2 usado + libfreenect2.
3. **Arduino + sensor inercial MPU-6050 (~$30-50 mil COP).** Pulsera/diadema
   casera que capta movimientos gruesos (sacudida, inclinación) incluso
   fuera del campo visual de la cámara. Es el "accesorio casero" más
   barato y robusto; se clasifica con el mismo enfoque k-NN+DTW ya validado
   (las señales del acelerómetro son series temporales, igual que los MFCC).

**Criterio de validación del canal de movimiento** (mismo rigor del
protocolo de voz): 3 gestos seleccionados, 10 repeticiones cada uno, LOOCV
≥80% y confirmación en vivo ≥70% en 30 intentos.

## 3. Arquitectura objetivo (versión universidad)

```
   [Micrófono]──voz──┐
   [Cámara Pi]──gesto/imagen──┤→ [Raspberry Pi 5: fusión + modelo] → [Pantalla 7": palabra + imagen]
   [Arduino IMU]──movimiento──┘                                   → [Bocinas: voz sintetizada]
                                                                  → [Celular (PWA): historial para la familia]
```

## 4. Estado de validación (honesto, para la diapositiva de resultados)

| Componente | Estado | Evidencia |
|---|---|---|
| Pipeline técnico de voz | ✅ Validado | 91.7% LOOCV sintético + 77.5% LOOCV con voz real de YP (80 muestras) |
| Depuración de datos | ✅ Documentada | 30 muestras descartadas con motivo en `registros/descartes.csv` |
| Validación en vivo | 🔄 En curso | 17 intentos iniciales; se requiere sesión estructurada de 30+ intentos confirmados |
| Hallazgo clínicamente relevante | ✅ Documentado | El «no» de YP es inconsistente entre emisiones → se sustituirá por vocalización alternativa consistente (práctica estándar AAC) |
| Canal de imágenes | ⏳ Planificado | Kit Raspberry Pi definido (~US$180) |
| Canal de movimiento | ⏳ Planificado | Ruta: MediaPipe ($0) → Kinect v2 usado → Arduino IMU |

## 5. Referencias (para la bibliografía de la propuesta)

- Revisión de tecnología asistida por voz en disartria: [PMC12537997](https://pmc.ncbi.nlm.nih.gov/articles/PMC12537997/)
- ASR personalizado en ELA (uso real de Project Relate, 500+ frases): [PMC12379579](https://pmc.ncbi.nlm.nih.gov/articles/PMC12379579/)
- Desarrollo de tecnología de voz CON usuarios disártricos: [PubMed 38537126](https://pubmed.ncbi.nlm.nih.gov/38537126/)
- Patente de reconocimiento disártrico personalizado (2025): [WO2025259567A1](https://patents.google.com/patent/WO2025259567A1/en)
- ASR disártrico independiente del hablante (arXiv 2025): [arxiv 2501.14994](https://arxiv.org/pdf/2501.14994)
- AAC open source sobre Raspberry Pi (Talker): [hackaday.io/project/20459](https://hackaday.io/project/20459-talker)
- Hardware abierto para tecnología asistiva: [opensource.com](https://opensource.com/life/15/5/building-better-assistive-technology-open-hardware)
- Validación clínica de MediaPipe Hands: [ScienceDirect S1746809424005664](https://www.sciencedirect.com/science/article/pii/S1746809424005664)
- Kinect vs. captura óptica de referencia (marcha): [MDPI Sensors 20(18):5104](https://www.mdpi.com/1424-8220/20/18/5104)
- Kinect en rehabilitación (<US$500, apto para usuarios con compromiso cognitivo): [ClinicalTrials NCT02631850](https://cdn.clinicaltrials.gov/large-docs/50/NCT02631850/Prot_SAP_ICF_000.pdf)
