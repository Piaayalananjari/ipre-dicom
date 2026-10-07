# IPRE-DICOM

Manual de instalación, operación y experimentación de una API para visualizar y
analizar técnicamente imágenes médicas.

El proyecto permite:

- cargar imágenes DICOM, NIfTI, NumPy y formatos raster;
- visualizar imágenes desde una interfaz web;
- calcular indicadores descriptivos de brillo, contraste, ruido y nitidez;
- ejecutar clasificadores de ruido, rotación y vista frontal/lateral;
- auditar metadata DICOM potencialmente identificadora sin devolver sus valores;
- producir una copia DICOM seudonimizada mediante un perfil experimental;
- explorar y entrenar modelos con ChestMNIST y PneumoniaMNIST;
- registrar experimentos y artefactos en Weights & Biases (W&B);
- organizar hallazgos con un flujo determinista opcional de LangGraph.

> **Advertencia:** este es un prototipo de investigación. No realiza diagnóstico
> médico, no determina por sí solo si una imagen es clínicamente aceptable y no
> certifica anonimización. No debe exponerse a Internet ni utilizarse con datos
> clínicos reales sin controles institucionales adicionales.

## 1. Arquitectura general

```text
Imagen subida
     |
     +-- lector: DICOM / raster / NIfTI / NumPy
     +-- indicadores deterministas de calidad
     +-- auditoría de privacidad
     +-- modelos MONAI disponibles
     |      +-- ruido: clean / noise
     |      +-- rotación: clean / rotation
     |      +-- vista: frontal / lateral
     +-- informe técnico determinista (opcionalmente LangGraph)
     +-- respuesta JSON + interfaz web
```

Los modelos usan `MONAI DenseNet121`; FastAPI sirve la API y el visor. Los
checkpoints se descubren al iniciar el servidor desde `models/`.

## 2. Requisitos

- Python 3.10 o 3.11; se recomienda Python 3.11.
- Al menos 8 GB de RAM para la API.
- GPU NVIDIA opcional para entrenar; la API funciona también en CPU.
- Espacio fuera del repositorio para datasets y experimentos.

El Python 3.6 del sistema de Calfuco es demasiado antiguo. No instale dependencias
sobre `/usr/bin/python3`; utilice un entorno aislado con Python moderno.

## 3. Instalación

### 3.1. Dependencias base

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Verificación:

```bash
python --version
python -c 'import torch; print(torch.__version__); print(torch.cuda.is_available())'
python -c 'import monai, fastapi, pydicom, medmnist; print("dependencias OK")'
```

### 3.2. Dependencias opcionales

```bash
# Flujo LangGraph
pip install -r requirements-agent.txt

# W&B, JupyterLab y herramientas de experimentación
pip install -r requirements-experiment.txt

# PixelData DICOM comprimido: JPEG, JPEG-LS y JPEG 2000
pip install -r requirements-dicom.txt
```

Cada archivo opcional incluye las dependencias base.

## 4. Configuración

| Variable | Obligatoria | Uso |
|---|---:|---|
| `MEDMNIST_ROOT` | No | Carpeta MedMNIST. Por defecto: `data/medmnist`. |
| `DICOM_PSEUDONYM_SECRET` | Para anonimizar | Secreto estable de al menos 16 caracteres para remapear UIDs. |
| `CUDA_VISIBLE_DEVICES` | No | GPU visibles para el proceso. |
| `WANDB_DIR` | No | Carpeta de ejecuciones y artefactos W&B. |

Ejemplo:

```bash
export MEDMNIST_ROOT="$PWD/data/medmnist"
export DICOM_PSEUDONYM_SECRET='reemplace-por-un-secreto-largo-y-privado'
```

No guarde secretos ni credenciales de W&B en Git.

## 5. Iniciar y detener la API

### Desarrollo local

```bash
source .venv/bin/activate
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

- Visor: <http://127.0.0.1:8000>
- Swagger: <http://127.0.0.1:8000/docs>
- OpenAPI: <http://127.0.0.1:8000/openapi.json>
- ReDoc: <http://127.0.0.1:8000/redoc>

Para detener el servidor use `Ctrl+C`.

### Ejecución estable

```bash
MEDMNIST_ROOT="$PWD/data/medmnist" \
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Los modelos se cargan al arrancar. Reinicie la API después de crear o reemplazar un
checkpoint.

### GPU específica en Calfuco

La RTX 3090 observada corresponde a la GPU física 1:

```bash
CUDA_VISIBLE_DEVICES=1 \
MEDMNIST_ROOT=/mnt/workspace/pfayala/medmnist \
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Dentro de PyTorch aparecerá como `cuda:0`; es normal porque es la única GPU visible.

## 6. Uso del visor web

1. Inicie la API y abra <http://127.0.0.1:8000>.
2. Seleccione o arrastre una imagen compatible.
3. Presione **Analizar**.
4. Revise las predicciones, indicadores técnicos, metadata DICOM resumida,
   advertencias de privacidad e informe técnico.
5. Use el explorador MedMNIST para consultar muestras locales por dataset, split,
   tamaño e índice.

El visor consume los mismos endpoints descritos a continuación; no aplica lógica
clínica adicional en el navegador.

## 7. Formatos admitidos

| Familia | Extensiones | Tratamiento |
|---|---|---|
| DICOM | `.dcm`, `.dicom` | Lee PixelData, ventana, pendiente/intercepto y `MONOCHROME1`; usa el primer frame. |
| Raster | `.png`, `.jpg`, `.jpeg`, `.tif`, `.tiff`, `.bmp`, `.webp` | Convierte a escala de grises; usa la primera página. |
| NIfTI-1 | `.nii`, `.nii.gz` | Selecciona cortes centrales hasta obtener 2D. |
| NumPy | `.npy` | Admite arreglos 2D–4D, sin objetos serializados. |
| MedMNIST | `.npz` | Dataset completo; se usa por `/datasets/medmnist`. |

Límite: **64 MiB por archivo**.

Que un archivo pueda abrirse no significa que un modelo sea válido para esa
modalidad. Los modelos de tórax se ejecutan solamente sobre raster o DICOM `CR/DX`.
NIfTI, NumPy y otras modalidades DICOM reciben indicadores y auditoría, pero no
predicciones de los clasificadores de radiografía.

## 8. Referencia completa de la API

Los archivos se envían como `multipart/form-data` en el campo `file`.

### 8.1. `GET /`

Devuelve el visor HTML.

```bash
curl http://127.0.0.1:8000/
```

### 8.2. `GET /health`

Informa dispositivo, modelos cargados, catálogo MedMNIST y LangGraph:

```bash
curl -s http://127.0.0.1:8000/health | python -m json.tool
```

```json
{
  "status": "ok",
  "models": ["rotation", "noise"],
  "device": "cuda",
  "medmnist": [
    {
      "id": "chestmnist",
      "class_name": "ChestMNIST",
      "task": "multi-label, 14 hallazgos de radiografia de torax",
      "sizes": [28, 64, 128, 224],
      "installed_sizes": []
    },
    {
      "id": "pneumoniamnist",
      "class_name": "PneumoniaMNIST",
      "task": "clasificacion binaria normal/neumonia pediatrica",
      "sizes": [28, 64, 128, 224],
      "installed_sizes": [28]
    }
  ],
  "medmnist_models": [],
  "agent": {"engine": "deterministic", "langgraph_installed": true}
}
```

`status: ok` solo confirma que el proceso responde. Revise `models` y
`medmnist_models` para saber qué checkpoints están activos.

### 8.3. `GET /formats`

```bash
curl -s http://127.0.0.1:8000/formats | python -m json.tool
```

Devuelve familias, extensiones, dimensionalidad y `max_upload_mib`.

### 8.4. `POST /predict`

Endpoint principal de análisis.

```bash
# PNG/JPEG
curl -s -X POST -F 'file=@radiografia.png' \
  http://127.0.0.1:8000/predict | python -m json.tool

# DICOM
curl -s -X POST -F 'file=@estudio.dcm;type=application/dicom' \
  http://127.0.0.1:8000/predict | python -m json.tool

# NIfTI comprimido
curl -s -X POST -F 'file=@volumen.nii.gz;type=application/gzip' \
  http://127.0.0.1:8000/predict | python -m json.tool
```

Respuesta representativa:

```json
{
  "filename": "radiografia.png",
  "input": {
    "extension": ".png",
    "content_type": "image/png",
    "format": "raster",
    "metadata": {"pil_format": "PNG", "original_mode": "L", "frames": 1}
  },
  "dicom": null,
  "privacy": {
    "metadata_identifiers_present": [],
    "metadata_identifier_count": 0,
    "burned_in_annotation": "NOT_APPLICABLE",
    "pixel_text_review_required": true,
    "anonymous": false,
    "warning": "Una imagen raster no contiene metadata DICOM evaluable..."
  },
  "quality_metrics": {
    "width": 224,
    "height": 224,
    "brightness_mean": 0.4521,
    "contrast_std": 0.2214,
    "noise_estimate": 0.0118,
    "sharpness_estimate": 0.003142,
    "interpretation": "Indicadores descriptivos; no constituyen una evaluacion clinica."
  },
  "model_applicability": {
    "chest_xray_models_executed": true,
    "reason": "Entrada raster o radiografia DICOM CR/DX."
  },
  "results": {
    "rotation": {"clean": 0.92, "rotation": 0.08},
    "noise": {"clean": 0.73, "noise": 0.27},
    "view": {"frontal": 0.88, "lateral": 0.12}
  },
  "agent_report": {
    "status": "review",
    "findings": [],
    "recommended_actions": ["Revisar texto incrustado en los pixeles mediante OCR."],
    "disclaimer": "Informe de apoyo tecnico; no es diagnostico medico.",
    "engine": "langgraph-deterministic-workflow",
    "langgraph_ready": true
  }
}
```

Interpretación:

- `quality_metrics` son descriptores, no umbrales clínicos;
- `privacy` enumera nombres de campos sensibles, nunca sus valores;
- `results` contiene solo modelos cargados;
- cada par de probabilidades suma aproximadamente 1;
- `view` es una categoría válida y no una falla de calidad;
- `agent_report` resume ruido, rotación y privacidad;
- `engine` indica función directa o grafo LangGraph.

Guardar la respuesta:

```bash
curl -s -X POST -F 'file=@radiografia.png' \
  http://127.0.0.1:8000/predict > resultado.json
```

### 8.5. `POST /anonymize/dicom`

Genera un DICOM seudonimizado experimentalmente:

```bash
export DICOM_PSEUDONYM_SECRET='reemplace-por-un-secreto-largo-y-privado'

curl -X POST \
  -F 'file=@estudio.dcm;type=application/dicom' \
  -o estudio-anonimizado.dcm \
  -D cabeceras-anonimizacion.txt \
  http://127.0.0.1:8000/anonymize/dicom
```

El endpoint elimina tags privados, vacía identificadores directos, remapea UIDs
mediante HMAC, marca `PatientIdentityRemoved=YES` y no modifica PixelData. Remapea
`StudyInstanceUID`, `SeriesInstanceUID`, `SOPInstanceUID` y `FrameOfReferenceUID`.

Cabeceras de respuesta:

- `Content-Type: application/dicom`;
- `X-Anonymization-Profile: research-basic-v1`;
- `X-Pixel-Data-Modified: false`.

Se rechaza la exportación si `BurnedInAnnotation` no es exactamente `NO`. Aun con
`NO`, se requiere validación institucional, OCR cuando corresponda y revisión contra
DICOM PS3.15.

### 8.6. `GET /datasets/medmnist`

```bash
curl -s http://127.0.0.1:8000/datasets/medmnist | python -m json.tool
```

Devuelve datasets habilitados, tamaños posibles e instalados. Están integrados:

- `chestmnist`: 14 etiquetas de hallazgos de tórax;
- `pneumoniamnist`: normal/neumonía pediátrica.

Tamaños: `28`, `64`, `128`, `224`.

### 8.7. `POST /datasets/medmnist/{id}/download`

La descarga siempre es explícita; nunca ocurre al arrancar:

```bash
export MEDMNIST_ROOT=/ruta/con/espacio/medmnist
curl -X POST \
  'http://127.0.0.1:8000/datasets/medmnist/pneumoniamnist/download?size=128'
```

| Parámetro | Valores | Predeterminado |
|---|---|---:|
| `id` | `chestmnist`, `pneumoniamnist` | obligatorio |
| `size` | `28`, `64`, `128`, `224` | `28` |

```json
{"dataset": "pneumoniamnist", "size": 128, "train_samples": 4708, "status": "ready"}
```

El conteo puede cambiar entre versiones; use la respuesta real como fuente de verdad.

### 8.8. `GET /datasets/medmnist/{id}/sample`

```bash
curl -D sample-headers.txt -o sample.png \
  'http://127.0.0.1:8000/datasets/medmnist/pneumoniamnist/sample?split=test&size=128&index=0'
```

| Parámetro | Valores | Predeterminado |
|---|---|---:|
| `split` | `train`, `val`, `test` | `train` |
| `size` | `28`, `64`, `128`, `224` | `28` |
| `index` | `0` hasta el último índice | `0` |

Devuelve `image/png`. Las cabeceras `X-MedMNIST-Labels` y
`X-MedMNIST-Samples` contienen etiquetas y cantidad de muestras.

### 8.9. `POST /predict/medmnist/{id}`

Ejecuta un checkpoint MedMNIST sobre una imagen raster:

```bash
curl -s -X POST -F 'file=@radiografia.png' \
  http://127.0.0.1:8000/predict/medmnist/pneumoniamnist \
  | python -m json.tool
```

```json
{
  "dataset": "pneumoniamnist",
  "input_size": 128,
  "predictions": [
    {"label": "normal", "probability": 0.18234},
    {"label": "pneumonia", "probability": 0.81766}
  ],
  "warning": "Clasificacion experimental; no es diagnostico medico."
}
```

Solo acepta raster. Sin checkpoint cargado responde `404`; entrene el modelo, copie
el `.pt` a `models/` y reinicie la API.

## 9. Códigos de error

| Código | Situación habitual |
|---:|---|
| `400` | Archivo vacío/inválido, DICOM ilegible, parámetros MedMNIST incorrectos o PixelData no decodificable. |
| `404` | No existe checkpoint MedMNIST para el dataset. |
| `413` | `/predict` recibió más de 64 MiB. |
| `422` | DICOM no anonimizable con seguridad o falta el campo `file`. |
| `503` | Falta `DICOM_PSEUDONYM_SECRET`. |

Formato normal de error: `{"detail": "Descripcion del problema"}`.

## 10. Modelos y checkpoints

```text
models/
├── best_noise.pt
├── best_rotation.pt
├── best_view.pt
├── medmnist_pneumoniamnist_128.pt
└── medmnist_chestmnist_128.pt
```

Los archivos ausentes se omiten sin impedir el arranque. Compruebe `/health`.

| Tarea | Etiqueta 0 | Etiqueta 1 | Archivo |
|---|---|---|---|
| `noise` | `clean` | `noise` | `best_noise.pt` |
| `rotation` | `clean` | `rotation` | `best_rotation.pt` |
| `view` | `frontal` | `lateral` | `best_view.pt` |

## 11. Datos sintéticos de ruido y rotación

Generador combinado, a partir de PNG limpios:

```bash
python scripts/make_synthetic_labels.py \
  --input /ruta/png-limpios \
  --output /ruta/dataset-sintetico \
  --n-rotated 1000 --n-noisy 1000 --size 224
```

Produce `clean/`, `rotated/`, `noisy/` y `labels.csv` con
`path,source_id,rotation_label,noise_label`.

Generador orientado a ruido:

```bash
python scripts/make_noise_dataset.py \
  --input /ruta/png-limpios \
  --output /ruta/dataset-ruido \
  --variants 20 --size 224
```

Los datos sintéticos validan el flujo; no reemplazan etiquetas reales ni validación
externa.

## 12. Entrenar ruido, rotación o vista

```bash
CUDA_VISIBLE_DEVICES=1 python scripts/train.py \
  --csv /ruta/labels.csv \
  --task noise \
  --group-column source_id \
  --epochs 15 --batch-size 32 --lr 0.0001 \
  --output models
```

`--task` admite `noise`, `rotation` o `view`. El CSV requiere `path`,
`<task>_label` y, preferentemente, `source_id` o un ID de paciente seudonimizado.

El entrenamiento separa grupos completos: variantes y vistas de una misma fuente no
cruzan entre train y validación. Sin columna de grupo usa separación por fila y muestra
una advertencia de fuga. El mejor ROC-AUC se guarda en `best_<task>.pt`.

## 13. Frontal/lateral con IU Chest X-Ray

```bash
python scripts/build_iu_manifest.py \
  --projections /mnt/data/iu-x-ray/indiana_projections.csv \
  --images /mnt/data/iu-x-ray/images/images_normalized \
  --output /mnt/workspace/pfayala/manifests/iu-view.csv
```

El script detecta columnas comunes, normaliza `PA/AP` como frontal y
`lateral/LAT/LL/RL` como lateral, omite valores desconocidos, informa faltantes y
conserva el estudio como `source_id`.

```bash
CUDA_VISIBLE_DEVICES=1 python scripts/train.py \
  --csv /mnt/workspace/pfayala/manifests/iu-view.csv \
  --task view --group-column source_id \
  --epochs 15 --batch-size 32 \
  --wandb-mode online --run-name iu-view-densenet
```

Reinicie la API después de crear `models/best_view.pt`.

## 14. MedMNIST

MedMNIST tiene imágenes normalizadas y etiquetas, no DICOM originales. Es útil para
clasificación, no para estudiar metadata DICOM.

```bash
export MEDMNIST_ROOT=/mnt/workspace/pfayala/medmnist
mkdir -p "$MEDMNIST_ROOT"

CUDA_VISIBLE_DEVICES=1 python scripts/train_medmnist.py \
  --dataset pneumoniamnist \
  --size 128 --root "$MEDMNIST_ROOT" --download \
  --epochs 10 --batch-size 64 \
  --wandb-mode offline
```

Para 14 etiquetas use `--dataset chestmnist`. El entrenador usa
`BCEWithLogitsLoss`, ROC-AUC macro, F1 macro y exactitud por etiqueta; selecciona por
AUC de validación y evalúa el split oficial de test.

Archivos: `models/medmnist_<dataset>_<size>.pt`.

## 15. Weights & Biases

```bash
pip install -r requirements-experiment.txt
wandb login
```

Modo conectado:

```bash
CUDA_VISIBLE_DEVICES=1 python scripts/train.py \
  --csv /ruta/labels.csv --task noise --epochs 15 \
  --wandb-mode online --wandb-project ipre-dicom \
  --run-name noise-densenet-baseline
```

Modo offline y sincronización posterior:

```bash
mkdir -p /mnt/workspace/pfayala/wandb
WANDB_DIR=/mnt/workspace/pfayala/wandb \
CUDA_VISIBLE_DEVICES=1 python scripts/train.py \
  --csv /ruta/labels.csv --task noise --wandb-mode offline

wandb sync /mnt/workspace/pfayala/wandb/wandb/offline-run-*
```

Se registran hiperparámetros, métricas y el mejor checkpoint. No se suben
automáticamente imágenes ni metadata DICOM.

## 16. LangGraph y agentes

El informe es primero una función determinista. Con LangGraph se ejecuta como un nodo
de un grafo acotado; sin él usa un fallback idéntico. Actualmente:

- no llama a un LLM ni diagnostica;
- no recibe valores DICOM identificadores;
- no modifica archivos;
- no decide aceptación clínica.

Un futuro agente con LangChain/LLM debería explicar resultados ya calculados,
conservar el JSON determinista como fuente de verdad y nunca enviar PHI a servicios
externos.

## 17. Operación en Calfuco

### Almacenamiento

- `/mnt/data`: HDD para datasets originales;
- `/mnt/workspace`: SSD para entornos, manifests, cachés y entrenamiento;
- `/`: sistema/home; no guardar datasets grandes.

El administrador debe otorgar permisos para `/mnt/workspace/pfayala`. Un
`Permission denied` no se resuelve desde la cuenta sin privilegios.

### Sesión persistente

```bash
ssh pfayala@146.155.13.94
nvidia-smi
source /mnt/workspace/pfayala/ipre-env/bin/activate
cd ~/ipre-dicom
tmux new -s ipre
```

Separarse: `Ctrl+B`, después `D`. Volver: `tmux attach -t ipre`.

### API mediante túnel SSH

En Calfuco:

```bash
MEDMNIST_ROOT=/mnt/workspace/pfayala/medmnist \
CUDA_VISIBLE_DEVICES=1 \
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

En el Mac:

```bash
ssh -N -L 8000:127.0.0.1:8000 pfayala@146.155.13.94
```

Abra <http://127.0.0.1:8000>. La API no tiene autenticación: no use
`--host 0.0.0.0` en un servidor compartido ni abra el puerto públicamente.

### Jupyter por túnel

```bash
# Calfuco
jupyter lab --no-browser --ip=127.0.0.1 --port=8888

# Mac, en otra terminal
ssh -N -L 8888:127.0.0.1:8888 pfayala@146.155.13.94
```

Abra la URL local con el token mostrado. Más detalles:
[CHEATSHEET_CALFUCO.md](CHEATSHEET_CALFUCO.md).

## 18. Pruebas

```bash
PYTHONPYCACHEPREFIX=/tmp/ipre-pycache \
python -m unittest discover -s tests -v
```

Cubren formatos, privacidad/seudonimización DICOM, MedMNIST, métricas, separación de
grupos, manifiesto IU, flujo agente y endpoints HTTP. No requieren GPU ni checkpoints
reales.

## 19. Solución de problemas

### `/health` muestra `models: []`

```bash
ls -lh models/
curl -s http://127.0.0.1:8000/health | python -m json.tool
```

Revise los nombres exactos y reinicie la API.

### PyTorch no detecta CUDA

```bash
nvidia-smi
echo "$CUDA_VISIBLE_DEVICES"
python -c 'import torch; print(torch.__version__); print(torch.version.cuda); print(torch.cuda.is_available())'
```

No cambie drivers ni CUDA del sistema sin el administrador.

### DICOM comprimido no se decodifica

Instale `requirements-dicom.txt` y reinicie. Algunos Transfer Syntax pueden requerir
codecs adicionales o conversión aprobada.

### MedMNIST corrupto o incompleto

Mueva solamente el `.npz` indicado por el error y vuelva a descargarlo; no borre
otros tamaños válidos.

### Inferencia MedMNIST responde `404`

Entrene el dataset, confirme el `.pt` en `models/` y reinicie.

### Anonimización responde `503`

Configure `DICOM_PSEUDONYM_SECRET` en el mismo entorno que inicia Uvicorn.

### Anonimización responde `422`

Normalmente `BurnedInAnnotation` no es `NO` o no existe. El prototipo no hace OCR ni
redacción de píxeles y por seguridad no exporta.

### No se puede crear `/mnt/workspace/pfayala`

El administrador debe crearla y asignar propietario/grupo. No use `sudo`, no cambie
permisos ajenos y no mueva datasets al home si `/` está casi lleno.

### Docker devuelve permiso denegado

La cuenta no accede al socket Docker. El proyecto funciona con `venv`; si Docker es
obligatorio, debe habilitarlo el administrador.

## 20. Seguridad, privacidad y límites

- No suba imágenes identificables a una instancia pública.
- No registre pacientes, IDs, rutas sensibles o imágenes clínicas en W&B.
- Use túneles SSH para Calfuco.
- Mantenga `DICOM_PSEUDONYM_SECRET` estable y privado.
- Un raster puede contener texto aunque no tenga metadata DICOM.
- `BurnedInAnnotation=NO` no sustituye una inspección OCR.
- Los indicadores no tienen umbrales clínicos validados.
- Las probabilidades dependen del dataset y población de entrenamiento.
- Valide externamente antes de cualquier uso más allá de investigación.
- No mezcle pacientes/estudios entre train, validación y test.

## 21. Estructura del proyecto

```text
api/
├── main.py                 # API, formatos y endpoints
├── image_io.py             # raster, NIfTI y NumPy
├── quality.py              # indicadores deterministas
├── privacy.py              # auditoría sin revelar valores
├── anonymize.py            # seudonimización experimental
├── medmnist_service.py     # catálogo, descarga y muestras
├── medmnist_models.py      # inferencia de checkpoints
├── agent_workflow.py       # informe/LangGraph
└── static/index.html       # visor web
scripts/
├── make_synthetic_labels.py
├── make_noise_dataset.py
├── build_iu_manifest.py
├── train.py
└── train_medmnist.py
models/                     # checkpoints
tests/                      # pruebas unitarias y HTTP
ARCHITECTURE.md
CHEATSHEET_CALFUCO.md
```

## 22. Flujo recomendado

1. Obtener espacio personal en `/mnt/workspace`.
2. Crear el entorno Python 3.11.
3. Ejecutar las pruebas.
4. Iniciar la API y probar datos no sensibles.
5. Guardar originales en `/mnt/data` y datos activos en `/mnt/workspace`.
6. Construir manifests con `source_id` de paciente/estudio.
7. Entrenar una línea base pequeña y registrar métricas en W&B.
8. Revisar errores y etiquetas manualmente.
9. Copiar el mejor checkpoint a `models/` y reiniciar.
10. Validar endpoint y visor mediante túnel SSH.
11. Antes de datos reales, acordar gobernanza, anonimización, retención y accesos.

Este orden separa exploración, entrenamiento, inferencia, privacidad y operación.

## 23. Demostración para una presentación

Para preparar imágenes públicas reproducibles y seguir un relato de 7–10 minutos:

```bash
python scripts/prepare_demo.py \
  --root data/medmnist \
  --output demo_assets \
  --download
```

Use el guion [DEMO_PRESENTACION.md](DEMO_PRESENTACION.md), que incluye orden de
pestañas, casos original/rotado/ruidoso, comandos de respaldo y plan sin Internet.

Para ejecutar todos los casos y guardar sus respuestas reales:

```bash
python scripts/run_demo.py
```

El resultado detallado queda en `demo_assets/demo_results.json`.
