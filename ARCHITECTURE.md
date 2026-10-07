# IPRE-DICOM — Documentación de Arquitectura

Plataforma para clasificar la calidad de radiografías de tórax: detecta si una imagen está **rotada** y/o tiene **ruido** (baja calidad). Consta de una API (FastAPI), una interfaz web y scripts de generación de datos y entrenamiento de modelos.

---

## 1. Visión general

```
┌──────────────┐   sube imagen    ┌───────────────┐   consulta   ┌──────────────┐
│  Navegador    │ ───────────────▶│   API (FastAPI)│ ───────────▶ │  Modelos PyTorch │
│ (static/html) │ ◀───────────────│   api/main.py  │ ◀─────────── │  DenseNet121    │
└──────────────┘  JSON resultados └───────────────┘   predicción └──────────────┘
```

- **Backend**: `api/main.py` — API REST con FastAPI.
- **Frontend**: `api/static/index.html` — página única (HTML+CSS+JS, sin frameworks).
- **Modelos**: PyTorch + MONAI, arquitectura **DenseNet121 2D** (1 canal, 2 clases).
- **Datos**: sintéticos (generados con `scripts/`) o reales (PNG/JPG/DICOM subidos por el usuario).

---

## 2. Estructura del proyecto

```
ipre-dicom/
├── api/
│   ├── main.py              # API FastAPI + lógica de inferencia
│   └── static/
│       └── index.html       # Interfaz web
├── models/                  # Pesos entrenados (.pt)
│   ├── best_rotation.pt     # Clasificador de rotación (existe)
│   └── best_noise.pt        # Clasificador de ruido (pendiente de entrenar)
├── scripts/
│   ├── train.py             # Entrenamiento de modelos
│   ├── make_synthetic_labels.py  # Dataset sintético rotación+ruido (versión original)
│   └── make_noise_dataset.py     # Dataset sintético de ruido (con variantes por imagen)
├── requirements.txt         # Dependencias
├── chexpert_plus.json       # Metadatos del dataset CheXpert Plus (Stanford/AIMI)
└── .venv/                   # Entorno virtual
```

---

## 3. Flujo de uso (inferencia)

1. **Arranque de la API**: al iniciar, `startup()` llama a `load_models()`, que carga en memoria todos los `models/best_*.pt` que existan (`rotation`, `noise`) y crea su pipeline de transforms.
2. **`GET /health`** → `{"status": "ok", "models": ["rotation", ...]}` (qué modelos están cargados).
3. **`GET /`** → devuelve la interfaz web.
4. El usuario **arrastra o selecciona una imagen** en el navegador (PNG, JPG, TIFF, BMP, WebP, GIF o **DICOM**).
5. El navegador hace **`POST /predict`** con la imagen (`multipart/form-data`).
6. El servidor:
   - Detecta si es DICOM (prefijo `DICM` en el byte 128 o extensión `.dcm`).
   - **DICOM**: lee con `pydicom`, aplica `RescaleSlope/Intercept`, aplica windowing (`WindowCenter/Width` si existen, si no min-max) y normaliza a 0–255.
   - **Otros formatos**: abre con PIL, convierte a escala de grises (`L`).
   - Redimensiona a **224×224**, lo convierte a tensor y aplica el transform de cada modelo (add channel, ScaleIntensity, ToTensor).
   - Ejecuta cada modelo cargado y calcula probabilidades con `softmax`.
7. Respuesta JSON:

```json
{
  "filename": "chest.png",
  "dicom": null,
  "results": {
    "rotation": {"clean": 0.93, "rotation": 0.07},
    "noise":    {"clean": 0.31, "noise": 0.69}
  }
}
```

8. La interfaz muestra: barras de probabilidad por tarea, un veredicto ("Imagen limpia ✓" / "Sospecha" / "Problemas") y la metadata DICOM si aplica.

---

## 4. Modelos

| Tarea       | Modelo          | Entrada | Salida      | Estado |
|-------------|-----------------|---------|-------------|--------|
| Rotación    | DenseNet121 2D  | 224×224 gris | limpia / rotada | Entrenado (2 epochs, datos sintéticos mínimos — AUC ≈ 0.5, aleatorio) |
| Ruido       | DenseNet121 2D  | 224×224 gris | limpia / ruidosa | **Pendiente de entrenar** |

- Arquitectura: `DenseNet121(spatial_dims=2, in_channels=1, out_channels=2)` de MONAI.
- La API solo expone los modelos cuyo `.pt` exista en `models/`; si falta uno, esa tarea no aparece en los resultados.

---

## 4.1. Cómo funcionan los modelos (PyTorch + MONAI + DenseNet121)

### PyTorch

Motor numérico del sistema: tensores, autograd (derivadas automáticas para backpropagation), el bucle de entrenamiento (`optimizer.step()`) y la inferencia (`model(x)`, `torch.softmax`). Nunca se escribe el entrenamiento a mano: se monta un modelo, una pérdida y un optimizador, y PyTorch calcula los gradientes automáticamente.

### MONAI

Capa sobre PyTorch especializada en imágenes médicas:

- Redes listas (`monai.networks.nets.DenseNet121`).
- Transforms con diccionarios (`LoadImaged`, `ScaleIntensityd`, `RandRotated`, …) que respetan la estructura `{"img": ..., "label": ...}`.
- DataLoaders orientados a datos médicos.

En este proyecto: MONAI aporta el modelo y el pipeline de preprocesado; PyTorch hace el resto.

### DenseNet121

CNN (red convolucional) de 121 capas. Idea clave: **conexiones densas** — cada bloque recibe los feature maps de *todos* los bloques anteriores, no solo del anterior. Ventajas:

- Reutiliza features → menos parámetros (más eficiente).
- Gradiente fluye mejor → más fácil de entrenar.

Internamente: bloques convolucionales (BatchNorm + ReLU + Conv) apilados, terminando en un clasificador final (fully connected).

### Qué significan los parámetros

```python
DenseNet121(spatial_dims=2, in_channels=1, out_channels=2)
```

| Parámetro | Valor | Significado |
|---|---|---|
| `spatial_dims=2` | 2D | imágenes 2D (224×224), no volúmenes 3D |
| `in_channels=1` | 1 canal | escala de grises (radiografía), no RGB (3) |
| `out_channels=2` | 2 clases | binario: limpia vs. rotada (o limpia vs. ruidosa) |

### Flujo de una imagen por el modelo

1. **Input**: tensor `[1, 1, 224, 224]` = (batch, canal, alto, ancho)
2. **Convoluciones densas**: extraen features jerárquicos — bordes → texturas → formas (costillas, diafragma…)
3. **Pooling**: reduce la resolución espacial
4. **Última capa**: produce 2 números (logits), uno por clase
5. **Softmax**: convierte logits en probabilidades que suman 1 → `{"clean": 0.93, "rotation": 0.07}`

---

## 4.2. Cómo aprende el modelo (ciclo de entrenamiento)

El aprendizaje es un bucle de ensayo-error (`scripts/train.py`):

```python
for batch in train_loader:
    x, y = batch["img"].to(device), batch["label"].to(device)
    optimizer.zero_grad()          # 1. limpia gradientes de la iteración anterior
    logits = model(x)              # 2. forward: el modelo "adivina"
    loss = loss_fn(logits, y)      # 3. ¿qué tan mal adivinó?
    loss.backward()                # 4. backward: calcula gradientes
    optimizer.step()               # 5. actualiza pesos en contra del error
```

**Paso a paso:**

- **Forward (2)**: la imagen atraviesa las 121 capas y salen 2 logits (números crudos). Ejemplo: `[0.2, 0.5]` para "limpia" y "ruidosa".
- **Loss (3)**: `CrossEntropyLoss` compara con la verdad (`y=1` si es ruidosa). Cuanto peor la adivinanza, mayor el número.
- **Backward (4)**: autograd. Cada operación del forward quedó registrada en un grafo. `loss.backward()` recorre ese grafo al revés (regla de la cadena) y calcula, para cada peso (~7M), *"si este peso subiera un poco, ¿cuánto cambiaría la pérdida?"*. Ese número es el gradiente.
- **Step (5)**: Adam mueve cada peso en dirección **contraria** a su gradiente:

```
peso_nuevo = peso_viejo - learning_rate × gradiente
```

Con lr `1e-4` (pasos cautelosos). Adam además adapta el tamaño del paso por peso (pesos que varían mucho → pasos más pequeños), acelerando la convergencia.

**Época vs. batch**: el dataset se parte en batches de 32. Una **época** = ver todos los batches una vez. Con 15 épocas, el modelo ve cada imagen 15 veces. `CosineAnnealingLR` reduce el learning rate progresivamente para "afinar" al final.

**Validación**: cada época se evalúa en el 20% apartado (nunca visto). Si el AUC mejora → se guarda `best_<task>.pt`. Esto evita el **overfitting** (memorizar el dataset en vez de generalizar).

---

## 4.3. Qué features aprende (jerarquía visual)

| Capas | Qué detectan | Analogía médica |
|---|---|---|
| Primeras | Bordes, líneas, contrastes locales | "aquí hay una transición de tono" |
| Medias | Texturas, patrones repetidos | grano del ruido, costillas, contorno pulmonar |
| Profundas | Formas y conceptos globales | "tórax inclinado", "imagen con moteado" |

- El **ruido gaussiano** es un patrón local (píxeles vecinos varían aleatoriamente) → se detecta en capas tempranas-medias.
- La **rotación** es un patrón global (estructura anatómica inclinada) → capas profundas.

Los pesos de las convoluciones empiezan aleatorios; las primeras épocas el modelo usa cualquier señal estadística (brillo, varianza) correlacionada con la etiqueta. Con más épocas, los kernels convergen hacia detectores útiles. Nadie los diseña: emergen del gradiente descendente.

---

## 4.4. Los transforms de MONAI

Pipeline de preprocesado en `api/main.py`:

```python
Compose([
    EnsureChannelFirstd(keys="img", channel_dim="no_channel"),
    ScaleIntensityd(keys="img"),
    ToTensord(keys="img"),
])
```

- **`...d`** = versión *dictionary*: reciben `{"img": ..., "label": ...}` y aplican solo a las keys indicadas.
- **`Compose`** = encadena los transforms en orden, como una tubería.

| Transform | Entrada → Salida | Por qué |
|---|---|---|
| `EnsureChannelFirstd` | `(224, 224)` → `(1, 224, 224)` | PyTorch exige canal primero |
| `ScaleIntensityd` | valores 0–255 → 0–1 | inputs normalizados convergen más rápido |
| `ToTensord` | numpy → `torch.Tensor` | el modelo come tensores |

En `train.py` además hay **augmentation** (solo en entrenamiento):

```python
T.RandRotated(keys="img", range_x=0.05, prob=0.5),
T.RandGaussianNoised(keys="img", prob=0.3, std=0.02),
```

Pequeñas rotaciones/ruido aleatorios por época hacen que el modelo aprenda características invariantes en vez de memorizar imágenes exactas.

**Importante**: en inferencia (`/predict`) solo se usan los 3 transforms deterministas (sin augmentation) — el modelo ve la imagen estandarizada igual que en validación.

---

## 4.5. Pipeline completo de una predicción

```
subes chest.png
  → PIL la abre, escala de grises, 224×224
  → numpy array (224, 224) con valores 0–255
  → EnsureChannelFirstd → (1, 224, 224)
  → ScaleIntensityd → valores 0–1
  → ToTensord → tensor float
  → unsqueeze(0) → (1, 1, 224, 224)   [batch de 1]
  → model(x) con torch.no_grad()      [sin grafo: 0 gradientes = más rápido]
  → salen 2 logits
  → softmax → 2 probabilidades que suman 1
  → {"clean": 0.31, "noise": 0.69}
```

`torch.no_grad()`: en inferencia no se necesitan gradientes, así que PyTorch no construye el grafo computacional — ahorra memoria y tiempo.

### Por qué el modelo de rotación actual predice al azar

Se entrenó con **12 imágenes** (4 limpias, 4 rotadas, 4 ruidosas) durante 2 épocas. Con tan poca variedad no hay señal que aprender: memorizar 12 imágenes no generaliza a fotos reales → ~50%. Es lo que se corrige con el dataset de ruido (1200+ imágenes, 15 épocas).

---

## 5. Flujo de entrenamiento

### 5.1 Generar dataset sintético

**Rotación** (`scripts/make_synthetic_labels.py`):
- Genera imágenes rotadas (ángulos groseros 90/180/270° o inclinaciones de −45° a 45°).

**Ruido** (`scripts/make_noise_dataset.py`):
- Por cada imagen base: genera N variantes ruidosas (sigma 8–45, blur opcional, brillo/contraste aleatorios) y N/2 variantes limpias (solo brillo/contraste).
- Escribe `labels_noise.csv` con columnas `path, noise_label`.

### 5.2 Entrenar

```bash
.venv/bin/python scripts/train.py \
  --csv /tmp/ipre_noise/out/labels_noise.csv \
  --task noise \      # rotation | noise | view
  --epochs 15 \
  --batch-size 32
```

Qué hace `train.py`:
1. Lee el CSV y toma la columna `<task>_label`.
2. Split 80/20 estratificado (`train_test_split`).
3. Data augmentation en train: `RandRotate`, `RandGaussianNoise` (MONAI).
4. Modelo `DenseNet121` 2D, pérdida `CrossEntropyLoss`, optimizador `Adam` (lr 1e-4), `CosineAnnealingLR`.
5. Por época: entrena, evalúa en validación (accuracy, F1, AUC).
6. Guarda el mejor modelo por AUC en `models/best_<task>.pt`.

Para `view`, `scripts/build_iu_manifest.py` convierte la tabla de proyecciones de IU
Chest X-Ray en etiquetas frontal/lateral y usa el estudio como `source_id`, evitando
que vistas del mismo estudio crucen entre entrenamiento y validación. La API presenta
esta salida como clasificación de vista, separada de las alertas de calidad.

### 5.3 Entrenar con datos reales (CheXpert Plus)

El proyecto tiene `chexpert_plus.json` (metadatos del dataset Stanford/AIMI via Redivis). Para usarlo se necesitaría descargar las imágenes con el CLI de Redivis y adaptar el CSV. **No implementado aún.**

---

## 6. Endpoints

| Método | Ruta        | Descripción                                       |
|--------|-------------|---------------------------------------------------|
| GET    | `/`         | Interfaz web                                      |
| GET    | `/health`   | Estado de la API y modelos cargados               |
| POST   | `/predict`  | Subir imagen (`file`), devuelve probabilidades por tarea |
| GET    | `/datasets/medmnist` | Catálogo MedMNIST y tamaños locales |
| POST   | `/datasets/medmnist/{id}/download` | Descarga explícita de un dataset/tamaño |
| GET    | `/datasets/medmnist/{id}/sample` | Muestra PNG de un split e índice |
| GET    | `/formats` | Formatos soportados y límite de carga |
| POST   | `/predict/medmnist/{id}` | Inferencia con checkpoint MedMNIST entrenado |
| POST   | `/anonymize/dicom` | Desidentificación experimental; rechaza riesgo de texto incrustado |

### 6.1. Análisis técnico y privacidad

`POST /predict` devuelve además:

- indicadores descriptivos de brillo, contraste, ruido y nitidez;
- auditoría de campos DICOM potencialmente identificadores, sin devolver sus valores;
- advertencia de revisión OCR para texto incrustado en píxeles;
- informe estructurado de acciones recomendadas.

La auditoría no certifica anonimización. Un flujo clínico requiere un perfil formal de
desidentificación DICOM, revisión de UIDs y OCR/pixel redaction.

### 6.2. MedMNIST y agentes

MedMNIST se carga bajo demanda desde `MEDMNIST_ROOT`; nunca se descarga al arrancar la
API. Se integran inicialmente ChestMNIST y PneumoniaMNIST en tamaños 28, 64, 128 y 224.

El informe técnico se modela como una herramienta determinista. Cuando LangGraph está
instalado se ejecuta dentro de un grafo acotado; sin LangGraph usa el mismo código como
fallback. Un LLM no participa en las predicciones y no recibe valores PHI.

---

## 7. Ejecutar

```bash
# 1. Crear entorno (si no existe)
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 2. Arrancar la API
.venv/bin/python -m uvicorn api.main:app --port 8000

# 3. Abrir en el navegador
open http://localhost:8000
```

---

## 8. Dependencias clave

- `torch`, `monai` — deep learning y transforms médicos
- `fastapi`, `uvicorn`, `python-multipart` — API y subida de archivos
- `pydicom` — lectura de archivos DICOM
- `pillow`, `numpy` — procesamiento de imagen
- `scikit-learn`, `pandas` — métricas y datos

---

## 9. Estado actual y pasos siguientes

- [x] API con inferencia multi-tarea
- [x] Interfaz web con subida por drag & drop
- [x] Soporte DICOM (lectura, windowing, metadata)
- [x] Modelo de rotación (entrenado pero inútil: AUC ≈ 0.5)
- [ ] **Entrenar modelo de ruido** (`best_noise.pt`) — interrumpido, pendiente
- [ ] Reentrenar rotación con dataset decente
- [ ] Datos reales (CheXpert Plus) o más imágenes base sintéticas
