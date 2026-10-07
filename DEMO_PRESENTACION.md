# Guion de demostración — IPRE-DICOM

Guion sugerido para una presentación de 7–10 minutos. La demo utiliza una muestra
pública de PneumoniaMNIST y no requiere imágenes clínicas identificables.

## 1. Preparación previa

Desde la raíz del proyecto:

```bash
source .venv/bin/activate

python scripts/prepare_demo.py \
  --root data/medmnist \
  --output demo_assets \
  --download

python scripts/run_demo.py

python -m unittest discover -s tests -q

MEDMNIST_ROOT="$PWD/data/medmnist" \
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

Abra antes de presentar estas pestañas:

1. <http://127.0.0.1:8000>
2. <http://127.0.0.1:8000/docs>
3. <http://127.0.0.1:8000/health>
4. El proyecto W&B, si existe una ejecución que pueda enseñarse.

Mantenga abierta una terminal en la raíz del proyecto y cierre aplicaciones que
puedan mostrar datos personales o notificaciones.

`scripts/run_demo.py` ejecuta los cuatro casos contra la API, imprime una tabla y
guarda la respuesta completa en `demo_assets/demo_results.json`. Esto permite mostrar
evidencia incluso si el navegador falla durante la presentación.

## 2. Relato de apertura — 45 segundos

> “El objetivo es construir una API modular para recibir imágenes médicas en distintos
> formatos, visualizarlas y ejecutar controles técnicos. Actualmente el prototipo abre
> DICOM, raster, NIfTI y NumPy; calcula métricas descriptivas; audita privacidad DICOM;
> ejecuta modelos de ruido y rotación; y está preparado para frontal/lateral y modelos
> MedMNIST. Es una herramienta de investigación, no de diagnóstico.”

## 3. Mostrar que el servicio está operativo — 45 segundos

Abra `/health` y señale:

- `status: ok`;
- `device`: CPU, MPS o CUDA;
- `models`: checkpoints generales cargados;
- `medmnist_models`: checkpoints MedMNIST cargados;
- `langgraph_installed`: disponibilidad del flujo agente.

Frase útil:

> “El estado separa claramente que la API esté viva de que haya modelos entrenados y
> cargados. Esto permite operar parcialmente aunque todavía falte un checkpoint.”

## 4. Flujo principal en el visor — 3 minutos

### Caso A: imagen original

En `/`, cargue:

```text
demo_assets/01_original_medmnist.png
```

Muestre:

- dimensiones y tipo de entrada;
- brillo, contraste, ruido y nitidez;
- probabilidades de los checkpoints cargados;
- advertencia de que un raster requiere revisión OCR para descartar texto incrustado;
- informe técnico estructurado.

No interprete `noise_estimate` como umbral clínico. Diga que es un descriptor útil
para comparar imágenes y que aún requiere calibración/validación.

### Caso B: rotación controlada

Cargue:

```text
demo_assets/02_rotada_25_grados.png
```

Compare visualmente con la original. Si el modelo no predice correctamente, no oculte
el resultado:

> “Esta diferencia muestra precisamente por qué necesitamos datos representativos,
> revisión de etiquetas, métricas de validación y seguimiento de experimentos. La API
> ya ejecuta el flujo; el rendimiento del modelo es una etapa separada.”

### Caso C: ruido controlado

Cargue:

```text
demo_assets/03_ruidosa.png
```

Compare `noise_estimate` con el caso original y muestre la salida del modelo de ruido.
Distinga siempre indicador determinista de predicción aprendida.

## 5. Mostrar formatos y diseño de API — 1 minuto

Abra `/docs`, expanda `GET /formats` y ejecute **Try it out**. Explique:

- raster y DICOM pueden activar modelos de tórax;
- NIfTI/NumPy pueden visualizarse y medirse, pero no activan esos modelos;
- `.npz` representa un dataset MedMNIST completo, no una imagen individual;
- cada endpoint tiene un contrato JSON reproducible.

Puede cargar `demo_assets/04_volumen_demo.npy` para mostrar el corte central. Aclare
que es un volumen artificial para probar el formato, no un estudio CT/MR.

## 6. MedMNIST — 1 minuto

En el explorador MedMNIST del visor seleccione:

- dataset: `pneumoniamnist`;
- split: `test`;
- tamaño: `128`;
- índice: `0`.

Explique que MedMNIST permite probar clasificación con splits oficiales y tamaños
normalizados. No contiene DICOM originales, por lo que privacidad/metadata se valida
por un flujo separado.

## 7. Privacidad DICOM — 45 segundos

Si no dispone de un DICOM autorizado, muestre el endpoint en Swagger sin subir datos.
Explique:

- la auditoría enumera campos sensibles presentes, pero no devuelve sus valores;
- la exportación elimina tags privados y remapea UIDs con HMAC;
- no exporta si `BurnedInAnnotation` no confirma `NO`;
- todavía no implementa OCR ni redacción de píxeles;
- por eso se denomina perfil experimental.

## 8. W&B y metodología — 45 segundos

Muestre, si está disponible:

- configuración del experimento;
- pérdida por época;
- ROC-AUC, F1 y accuracy/balanced accuracy;
- mejor checkpoint como artefacto;
- separación por `source_id` para evitar fuga entre train y validación.

Si W&B está offline, explique que las ejecuciones se guardan localmente y pueden
sincronizarse posteriormente.

## 9. Cierre — 30 segundos

> “El avance actual es una plataforma ejecutable y testeada que separa lectura de
> formatos, calidad técnica, privacidad, inferencia y experimentación. El siguiente
> hito es entrenar frontal/lateral con IU Chest X-Ray, validar los modelos sobre datos
> separados por paciente/estudio y añadir revisión humana de casos inciertos.”

## 10. Plan B si falla Internet o la GPU

- La API funciona en CPU.
- Los assets ya preparados no requieren Internet durante la presentación.
- W&B puede mostrarse con capturas o en modo offline.
- `/predict`, `/health`, `/formats` y Swagger funcionan sin descargar datasets.
- No actualice dependencias ni entrene un modelo durante la presentación.

## 11. Comandos de respaldo

Estado:

```bash
curl -s http://127.0.0.1:8000/health | python -m json.tool
```

Analizar la imagen original:

```bash
curl -s -X POST \
  -F 'file=@demo_assets/01_original_medmnist.png' \
  http://127.0.0.1:8000/predict \
  | python -m json.tool
```

Analizar la ruidosa:

```bash
curl -s -X POST \
  -F 'file=@demo_assets/03_ruidosa.png' \
  http://127.0.0.1:8000/predict \
  | python -m json.tool
```

## 12. Resultados que conviene mostrar como avances

- API FastAPI y visor ejecutables.
- Soporte de cuatro familias de formatos.
- Modelos de ruido y rotación cargados de extremo a extremo.
- Integración MedMNIST y entrenador multietiqueta.
- Pipeline IU frontal/lateral listo para entrenar.
- Auditoría y seudonimización DICOM experimental.
- Integración W&B y LangGraph acotado.
- Suite automatizada de 26 pruebas.
- Manual operativo completo y cheat sheet de Calfuco.
