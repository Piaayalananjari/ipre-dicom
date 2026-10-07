"""Descripciones contrastadas con el código, para la sección de módulos."""
MODULES = [
('main.py: entrada y coordinación del servicio',
 'Recibe solicitudes HTTP y decide qué funciones ejecutar. FastAPI define las rutas y Uvicorn ejecuta el servidor.',
 ('Entrada y procedimiento',[
 'Recibe el archivo como bytes. En /predict comprueba que no esté vacío y no supere 64 MiB.',
 'Identifica el formato, llama al lector y reúne indicadores, privacidad y modelos aplicables.',
 'Al arrancar carga los checkpoints. /health informa el dispositivo y los modelos disponibles.']),
 ('Recursos y resultado',[
 'Usa FastAPI, PyTorch, MONAI y los servicios de api/. Selecciona CUDA, MPS o CPU según disponibilidad.',
 'Devuelve JSON o un error HTTP explicativo. Las rutas de muestras y exportación devuelven archivos.',
 'No ajusta pesos. /predict y /predict/medmnist/{flag} ejecutan análisis diferentes.']),
 'Ejemplo: una imagen NPY recibe indicadores, pero no pasa por los clasificadores generales de tórax.',
 'api/main.py: startup, predict, predict_medmnist, health.'),
('Visor HTML: interacción desde el navegador',
 'api/static/index.html es el cliente visual. Permite seleccionar una imagen y consultar la API sin escribir una solicitud HTTP manualmente.',
 ('Qué hace y cómo',[
 'JavaScript recoge el archivo y lo adjunta a FormData bajo el campo file.',
 'El botón Analizar usa fetch para enviar POST /predict y presenta sus resultados.',
 'El explorador solicita una muestra MedMNIST y muestra la imagen y su etiqueta conocida.']),
 ('Recursos y límites',[
 'HTML estructura la pantalla, CSS define su aspecto y JavaScript gestiona las peticiones.',
 'La vista previa depende de los formatos que pueda mostrar el navegador. No es un visor 3D.',
 'El explorador no clasifica la muestra. La ruta de clasificación MedMNIST se prueba desde /docs o un script.']),
 'El navegador muestra resultados. Los modelos se ejecutan en el backend, no dentro del HTML.',
 'api/static/index.html: FormData, fetch(/predict), petición a /datasets/medmnist/{flag}/sample.'),
('image_io.py: lectura multiformato y conversión a 2D',
 'Convierte archivos raster, NIfTI o NumPy en una representación común: una imagen 2D en escala de grises y metadata técnica.',
 ('Qué hace y cómo',[
 'Pillow abre PNG, JPEG y otros raster. Selecciona el primer frame y convierte a grises.',
 'NumPy carga .npy con allow_pickle=False. NiBabel lee NIfTI y gzip descomprime .nii.gz.',
 'En arreglos de más de dos dimensiones toma cortes centrales sucesivos hasta obtener 2D.']),
 ('Normalización y salida',[
 'Para arreglos, sustituye valores no finitos y ajusta intensidades con percentiles 1 y 99.',
 'Entrega LoadedImage: imagen Pillow, familia del formato y metadata como forma y cortes elegidos.',
 'No interpreta anatomía. .npz se reserva para el servicio de datasets, no para una imagen individual.']),
 'Un volumen se reduce a un corte para este análisis. No se analiza automáticamente todo su contenido 3D.',
 'api/image_io.py: LoadedImage, load_raster, load_numpy, load_nifti, array_to_grayscale.'),
('Lector DICOM: píxeles y metadata clínica',
 'La lectura DICOM está implementada dentro de main.py. pydicom interpreta el archivo y permite acceder a PixelData y sus atributos.',
 ('Procesamiento de píxeles',[
 'Detecta la marca DICM o la extensión .dcm/.dicom y abre los bytes con pydicom.',
 'read_dicom_array obtiene pixel_array, toma el primer frame y aplica RescaleSlope e Intercept.',
 'Aplica la ventana disponible o el rango mínimo/máximo. Invierte MONOCHROME1 y convierte a 8 bits.']),
 ('Recursos y salida',[
 'pydicom decodifica el objeto. NumPy transforma intensidades y Pillow crea la imagen.',
 'Entrega imagen y metadata resumida: modalidad, filas, columnas y posición de vista.',
 'La API deriva el dataset DICOM a privacy.py. Si PixelData no se decodifica, devuelve un error HTTP.']),
 'La lectura DICOM no es un modelo de IA. Prepara los datos que después consumen los otros módulos.',
 'api/main.py: is_dicom, read_dicom_array y rama DICOM de predict.'),
('quality.py: indicadores calculados sin aprendizaje',
 'Describe numéricamente la imagen 2D que entrega el lector. No carga archivos .pt ni necesita ejemplos etiquetados.',
 ('Cómo calcula los indicadores',[
 'Convierte a grises y divide las intensidades por 255 para trabajar entre 0 y 1.',
 'Brillo: media de intensidad. Contraste: desviación estándar de los píxeles.',
 'Ruido: mediana de la diferencia absoluta frente a una copia suavizada con BoxBlur(1).']),
 ('Recursos y producto',[
 'Nitidez: promedio de las varianzas de diferencias entre píxeles en ambos ejes.',
 'Usa Pillow para grises y suavizado, y NumPy para las operaciones numéricas.',
 'Devuelve dimensiones y medidas redondeadas. No produce por sí solo una etiqueta buena/mala.']),
 'noise_estimate es una fórmula descriptiva. P(ruido) es la salida de otro componente: un clasificador con pesos.',
 'api/quality.py: image_quality_metrics.'),
('privacy.py: auditoría de identificadores',
 'Revisa una lista definida de campos DICOM y una declaración de texto incrustado. No elimina datos ni examina visualmente los píxeles.',
 ('Reglas aplicadas',[
 'Busca campos no vacíos: PatientName, PatientID, fecha de nacimiento e institución.',
 'Si BurnedInAnnotation no declara NO, solicita revisión de texto en píxeles.',
 'En raster no evalúa metadata DICOM. La revisión de píxeles queda pendiente.']),
 ('Recursos y resultado',[
 'Aplica reglas Python al dataset abierto por pydicom, sin red neuronal.',
 'Devuelve nombres y conteo de campos y avisos. Omite los valores sensibles.',
 'El campo anonymous depende de estas reglas limitadas. No garantiza anonimato.']),
 'Ausencia de campos conocidos y BurnedInAnnotation=NO no equivalen a una inspección real de los píxeles.',
 'api/privacy.py: SENSITIVE_DICOM_KEYWORDS, audit_dicom_privacy, non_dicom_privacy_audit.'),
('anonymize.py: copia DICOM seudonimizada',
 'Modifica una copia del dataset para retirar identificadores conocidos. La ruta /anonymize/dicom permite descargar esa copia.',
 ('Condiciones y pasos',[
 'Exige DICOM_PSEUDONYM_SECRET de al menos 16 caracteres y BurnedInAnnotation igual a NO.',
 'Hace una copia profunda, elimina tags privados y vacía los campos identificadores listados.',
 'Sustituye UIDs seleccionados mediante HMAC-SHA256 y actualiza el UID del archivo.']),
 ('Recursos y producto',[
 'Usa pydicom, copy, hashlib y hmac. La misma clave permite un remapeo consistente de un UID.',
 'Devuelve la copia y un resumen de las operaciones. main.py la serializa como archivo DICOM.',
 'Los píxeles no cambian. No hay OCR, redacción visual ni validación institucional del perfil.']),
 'Es un perfil experimental de seudonimización, no una certificación de desidentificación completa.',
 'api/anonymize.py: anonymize_dicom, pseudonymous_uid; api/main.py: anonymize_dicom_endpoint.'),
('medmnist_service.py: acceso al dataset',
 'Administra el catálogo, la descarga explícita y la extracción de muestras. El dataset aporta imágenes y etiquetas, no pesos de un modelo.',
 ('Entrada y procedimiento',[
 'Recibe identificador del dataset, partición train/val/test, resolución e índice de muestra.',
 'Valida esos parámetros y usa la clase correspondiente de la biblioteca medmnist.',
 'sample_png toma una imagen y su etiqueta, y convierte la imagen a PNG mediante Pillow.']),
 ('Archivos y salida',[
 'Lee MEDMNIST_ROOT o data/medmnist. Descarga solo ante una petición explícita.',
 'Devuelve PNG, etiqueta y conteo. La API envía la etiqueta y el conteo en cabeceras HTTP.',
 'Admite ChestMNIST y PneumoniaMNIST. Solo usamos el segundo en el experimento.']),
 'Archivo utilizado: data/medmnist/pneumoniamnist.npz. Ver una muestra no ejecuta una clasificación.',
 'api/medmnist_service.py: dataset_root, list_datasets, load_dataset, sample_png.'),
('medmnist_models.py: inferencia con el modelo guardado',
 'Reconstruye la red entrenada y aplica sus pesos a una imagen nueva. Es el componente que predice normal o neumonía en el experimento actual.',
 ('Carga y cálculo',[
 'Busca models/medmnist_*.pt. Lee dataset, tamaño, número de salidas y state_dict, que contiene los pesos.',
 'Crea DenseNet121 de MONAI, carga los pesos y activa model.eval().',
 'Convierte a grises, redimensiona y normaliza. Ejecuta PyTorch con no_grad(), sin ajustar parámetros.']),
 ('Recursos y producto',[
 'Pillow y NumPy preparan la imagen. MONAI define la red y PyTorch realiza el cálculo.',
 'Sigmoid transforma la salida en p(neumonía). Para dos clases devuelve también p(normal)=1-p.',
 'Entrega etiquetas, probabilidades, tamaño de entrada y advertencia de uso experimental.']),
 'El checkpoint actual usa entrada 64 × 64. Falta unificar el filtro de redimensionado con el entrenamiento.',
 'api/medmnist_models.py: MedMNISTModelRegistry.load, predict y binary_predictions.'),
('agent_workflow.py: informe mediante reglas explícitas',
 'Recibe los resultados ya calculados y redacta recomendaciones predefinidas. No interpreta la imagen mediante un modelo de lenguaje.',
 ('Reglas de decisión',[
 'Si la probabilidad de ruido o rotación alcanza 0,5, añade un hallazgo y recomienda revisión manual.',
 'Si hay identificadores en metadata, recomienda desidentificarlos antes de compartir.',
 'Si los píxeles necesitan revisión, recomienda OCR. El módulo no ejecuta ese OCR.']),
 ('Orquestación y salida',[
 'Con LangGraph instalado ejecuta START, un nodo technical_report y END.',
 'Sin LangGraph llama directamente a la misma función build_report. El criterio no cambia.',
 'Devuelve status, findings y recommended_actions. No usa un LLM, búsqueda web ni entrenamiento.']),
 'Aquí “agente” designa un flujo determinista de un nodo. No existe un agente autónomo de diagnóstico.',
 'api/agent_workflow.py: build_report, AnalysisState, run_report_workflow.'),
('train_medmnist.py: aprendizaje y evaluación',
 'Es un programa separado de la API. Recibe el dataset etiquetado y una configuración, y ajusta una DenseNet121 para la tarea elegida.',
 ('Cómo aprende',[
 'Carga splits oficiales con MedMNIST. torchvision redimensiona, convierte a tensor y normaliza.',
 'DataLoader organiza lotes. BCEWithLogitsLoss mide error y Adam actualiza pesos mediante gradientes.',
 'Evalúa validación sin gradientes y guarda un checkpoint cuando mejora el ROC-AUC.']),
 ('Recursos y producto',[
 'PyTorch y MONAI realizan aprendizaje. scikit-learn calcula AUC, F1 y accuracy por etiqueta.',
 'Al finalizar, evalúa el mejor checkpoint en test y escribe métricas e historial. W&B es opcional.',
 'Produce .pt con pesos y metadata, y JSON de resultados. La API carga el .pt al arrancar.']),
 'La corrida real se interrumpió en época 2. Se evaluó después el checkpoint de época 1 y se conservaron sus resultados.',
 'scripts/train_medmnist.py: main, evaluate, compute_multilabel_metrics.'),
('train.py: entrenador general de ruido, giro o vista',
 'Prepara entrenamiento binario para una tarea seleccionada: noise, rotation o view. Su entrada es un CSV de rutas y etiquetas.',
 ('Cómo está implementado',[
 'Lee path, la etiqueta de la tarea y, si existe, source_id para agrupar originales y variantes.',
 'Divide train/validación por grupos. Sin grupos usa división estratificada y advierte riesgo de fuga.',
 'MONAI carga imágenes y prepara tensores. DenseNet121 usa dos salidas, CrossEntropyLoss y Adam.']),
 ('Recursos y alcance',[
 'scikit-learn mide accuracy, balanced accuracy, F1 y AUC. Guarda best_{task}.pt si mejora AUC.',
 'Puede registrar parámetros y métricas en W&B cuando se habilita ese modo.',
 'Tener el entrenador no demuestra que los checkpoints previos provengan de una corrida documentada aquí.']),
 'Los modelos previos de ruido/rotación se probaron en inferencia. Frontal/lateral todavía no tiene entrenamiento demostrado.',
 'scripts/train.py: split_rows, build_dataset, main.'),
('export_wandb_results.py: publicación de resultados existentes',
 'Importa a W&B las métricas guardadas del experimento. No abre imágenes, no entrena una red y no recalcula el rendimiento.',
 ('Entrada y procedimiento',[
 'Lee models/medmnist_pneumoniamnist_28_metrics.json.',
 'wandb.init crea un registro offline marcado como importación posterior. run.log guarda el punto de época 1.',
 'run.summary conserva las métricas de test y log_artifact adjunta el JSON como artefacto de evaluación.']),
 ('Recursos y resultado',[
 'Usa json, pathlib y el SDK de W&B. Escribe el registro local en output/wandb.',
 'wandb sync transmite ese registro a la cuenta autenticada. La sincronización del run oliy37yu está confirmada.',
 'Esta importación publica métricas y configuración. No incluye imágenes ni el checkpoint del modelo.']),
 'El panel documenta una época ya evaluada. No representa cinco épocas completas ni seguimiento en vivo de la corrida original.',
 'scripts/export_wandb_results.py y registro sincronizado oliy37yu.'),
]

position=next(i for i,s in enumerate(slides) if s['title']=='Responsabilidad de cada módulo')+1
detail=[]
for title,definition,left,right,takeaway,source in MODULES:
    s=make(title,('Responsabilidad',definition),left,right,takeaway,source)
    s['module_detail']=True
    detail.append(s)
slides[position:position]=detail
