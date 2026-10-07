"""Presentación autocontenida. Solo Calibri, texto negro; fuentes al pie."""
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'output/pdf/presentacion_ipre_dicom_investigacion_visual.pdf'
FONT=Path('/Applications/Microsoft PowerPoint.app/Contents/Resources/DFonts')
pdfmetrics.registerFont(TTFont('Calibri',str(FONT/'Calibri.ttf')))
pdfmetrics.registerFont(TTFont('CalibriBold',str(FONT/'Calibrib.ttf')))
W,H=960,540
slides=[]

def add(title, paragraphs=None, table=None, diagram=None, source='', takeaway=''):
    slides.append(dict(title=title,paragraphs=paragraphs or [],table=table,diagram=diagram,source=source,takeaway=takeaway))

add('IPRE-DICOM: desarrollo y evaluación de una API',[
 'Prototipo local para recibir imágenes médicas, describir su calidad técnica y servir modelos de clasificación.',
 'Informe de avance de investigación · Pía Ayala · Septiembre de 2026',
 'Recorrido: necesidad inicial, construcción del sistema, experimento reproducible, resultados y trabajo pendiente.'
],source='Evidencia: repositorio local y ejecución documentada en esta sesión.')
add('Problema y pregunta de investigación',[
 'Las imágenes médicas llegan en formatos y tamaños diferentes. Antes de analizarlas se necesita abrirlas correctamente, revisar posibles identificadores y conocer qué modelo puede procesarlas.',
 'Pregunta de ingeniería: ¿cómo reunir lectura, indicadores técnicos y predicciones en un servicio reutilizable desde un navegador u otro programa?',
 'Pregunta experimental: ¿puede el servicio cargar un modelo entrenado con un dataset conocido y reproducir sus predicciones?'
],takeaway='El avance estudia la integración de software y una primera clasificación experimental.')
add('Objetivo inicial y alcance alcanzado',table=[
 ['Necesidad original','Estado actual y evidencia'],
 ['Formatos, ruido y rotación','Lectura multiformato, métricas y checkpoints previos ejecutados.'],
 ['Frontal o lateral','Generador de etiquetas IU y entrenador preparados; sin modelo entrenado.'],
 ['Anonimato','Auditoría y seudonimización de metadata DICOM; sin OCR de píxeles.'],
 ['Clasificador demostrable','PneumoniaMNIST: normal/neumonía, una época completa y test.'],
 ['Edad, similitud y clustering','Ideas iniciales; aún no implementadas ni evaluadas.']
],source='README.md; api/; scripts/; modelos presentes en models/.')
add('Qué es la API y qué recibe un usuario',[
 'Una API es una interfaz que permite pedir una operación a un programa. En este proyecto, un cliente envía una imagen por HTTP y recibe una respuesta estructurada.',
 'El cliente puede ser el visor web, Swagger (/docs), un script Python o una aplicación externa. Todos pueden llamar al mismo servicio FastAPI.',
 'Ejemplo: enviar una radiografía a POST /predict devuelve dimensiones, indicadores de calidad, revisión de privacidad y predicciones disponibles.',
 'La API usa pesos guardados para predecir. El entrenamiento ocurre por separado, en scripts que producen esos archivos de pesos.'
],source='api/main.py; scripts/train.py; scripts/train_medmnist.py')
add('Dos preguntas, dos rutas de análisis',table=[
 ['Ruta','Pregunta','Respuesta'],
 ['POST /predict','¿Qué características técnicas y alertas tiene la imagen?','Métricas, privacidad, ruido/rotación e informe de reglas.'],
 ['POST\n/predict/medmnist/{flag}','¿Qué clase del experimento PneumoniaMNIST predice el modelo?','Probabilidad normal y probabilidad neumonía.'],
 ['GET muestra MedMNIST','¿Qué imagen y etiqueta contiene el dataset?','PNG de la muestra y etiqueta conocida.']
],takeaway='Clasificar neumonía demuestra el ciclo de aprendizaje e integración; no valida ruido o rotación.',source='api/main.py. flag=pneumoniamnist. Muestra: /datasets/medmnist/{flag}/sample.')
add('Recorrido del proyecto: hitos y dependencias',diagram='roadmap',source='Reconstrucción del trabajo a partir de la conversación, archivos y resultados locales.',takeaway='El despliegue en Calfuco sigue pendiente. Los resultados actuales provienen del computador local.')
add('Etapas 1 y 2: necesidad e infraestructura',table=[
 ['Etapa','Acción y motivo','Resultado'],
 ['1. Definir alcance','Separar calidad, orientación, privacidad y clasificación: necesitan etiquetas y evaluaciones distintas.','Conjunto de servicios y tareas identificados.'],
 ['2. Inspeccionar Calfuco','Revisar GPU, RAM, discos, Python y permisos mediante SSH.','RTX 3090 24 GB, dos 2080 Ti y 125 GB RAM reportados.'],
 ['Decisión de ejecución','El acceso a workspace y Docker falló; Python del servidor era 3.6.9.','Continuar el prototipo local; conservar plan de despliegue.']
],source='Salidas SSH compartidas por la usuaria; CHEATSHEET_CALFUCO.md. No equivalen a un despliegue.')
add('Etapas 3 y 4: implementar y preparar datos',table=[
 ['Etapa','Qué se construyó','Por qué fue necesario'],
 ['3. Servicio modular','FastAPI, visor, lectores, métricas, auditoría e inferencia.','Unificar operaciones tras una interfaz HTTP.'],
 ['4. Dataset conocido','Descarga de PneumoniaMNIST, catálogo y explorador de muestras.','Contar con imágenes, etiquetas y particiones reproducibles.'],
 ['Demo controlada','Original del test, copia rotada, copia ruidosa y volumen NPY.','Observar respuestas y fallos en condiciones conocidas.']
],source='api/; scripts/prepare_demo.py; data/medmnist/pneumoniamnist.npz; demo_assets/.')
add('Etapas 5 y 6: entrenar, corregir y evaluar',table=[
 ['Paso observado','Problema o resultado','Decisión aplicada'],
 ['Primera ejecución','Memoria compartida bloqueada al usar procesos auxiliares.','DataLoader con num_workers=0.'],
 ['Entrada 28 × 28','DenseNet121 reducía el mapa espacial hasta tamaño inválido.','Redimensionar a 64 × 64; conservar fuente 28 × 28.'],
 ['Corrida de 5 épocas','Completó época 1; se interrumpió durante época 2.','Evaluar el checkpoint guardado de la época 1.'],
 ['Integración binaria','La salida positiva aparecía rotulada como normal.','Devolver normal=1−p y neumonía=p; añadir prueba.']
],source='Traza de ejecución; scripts/train_medmnist.py; api/medmnist_models.py; tests/.')
add('Arquitectura actual del sistema',diagram='architecture',source='api/main.py; api/static/index.html; api/medmnist_models.py; scripts/train_medmnist.py')
add('Responsabilidad de cada módulo',table=[
 ['Módulo','Responsabilidad','Producto que entrega'],
 ['main.py + visor HTML','Recibir solicitudes y coordinar servicios.','HTTP, interfaz y JSON.'],
 ['image_io.py + lector DICOM','Interpretar archivo y seleccionar representación 2D.','Imagen normalizada y metadata resumida.'],
 ['quality.py / privacy.py','Calcular indicadores y buscar campos identificadores.','Medidas y alertas.'],
 ['medmnist_models.py','Cargar pesos y ejecutar el clasificador del experimento.','Probabilidades por clase.'],
 ['agent_workflow.py','Convertir hallazgos en recomendaciones mediante reglas.','Informe técnico.'],
 ['scripts/train*.py','Ajustar y evaluar modelos fuera del servidor HTTP.','Checkpoint y métricas.']
],source='Archivos bajo api/ y scripts/.')
add('Herramientas del servicio y su función',table=[
 ['Herramienta','Qué es','Uso concreto'],
 ['Python','Lenguaje del backend.','Implementa lectura, modelos, endpoints y pruebas.'],
 ['FastAPI / Uvicorn','Framework web / servidor HTTP.','Define rutas y recibe solicitudes locales.'],
 ['HTML, CSS, JavaScript','Tecnologías del navegador.','Selección de archivo, envío y visualización de resultados.'],
 ['Pillow / NumPy','Imágenes y arreglos numéricos.','Escala de grises, tamaños y operaciones sobre píxeles.'],
 ['pydicom','Biblioteca para DICOM.','Lee metadata y píxeles; exporta copia seudonimizada.']
],source='requirements.txt; api/main.py; api/image_io.py; api/static/index.html')
add('Herramientas de aprendizaje y experimentación',table=[
 ['Herramienta','Papel real','Estado'],
 ['PyTorch','Tensores, gradientes y optimización de pesos.','Entrenamiento e inferencia ejecutados.'],
 ['MONAI','Biblioteca que aporta DenseNet121 y transformaciones.','Arquitectura usada; MONAI no es un modelo por sí mismo.'],
 ['MedMNIST','Datasets con muestras, etiquetas y splits.','PneumoniaMNIST instalado y utilizado.'],
 ['scikit-learn','Funciones para calcular métricas y separar grupos.','Evaluación y pruebas.'],
 ['W&B','Registro de experimentos, parámetros y artefactos.','Integración y prueba offline; corrida real con W&B desactivado.'],
 ['LangGraph','Orquestación del informe mediante un grafo.','Un nodo determinista; sin LLM ni aprendizaje.']
],source='scripts/train*.py; api/agent_workflow.py; requirements*.txt')
add('Funcionamiento paso a paso de POST /predict',[
 '1. El cliente adjunta el archivo en el campo file. La API rechaza entradas vacías y archivos mayores de 64 MiB.',
 '2. El lector interpreta el formato y obtiene una imagen 2D. Conserva información como dimensiones, modalidad o forma del volumen.',
 '3. Calcula indicadores en la imagen resultante y revisa privacidad. Prepara además una copia de 224 × 224 para los modelos previos.',
 '4. Para raster o DICOM CR/DX ejecuta los clasificadores disponibles. Otras entradas reciben métricas sin esos clasificadores.',
 '5. El informe reúne hallazgos y recomendaciones. La respuesta JSON regresa al navegador o al programa solicitante.'
],source='api/main.py: predict. La regla raster no comprueba que el contenido sea una radiografía.')
add('Lectura y visualización: capacidades y límites',table=[
 ['Entrada','Tratamiento actual','Límite relevante'],
 ['DICOM (.dcm/.dicom)','PixelData, slope/intercept, ventana e inversión MONOCHROME1.','Primer frame; no visor volumétrico.'],
 ['PNG/JPEG/TIFF/BMP/WebP','Lectura raster y escala de grises.','Vista previa nativa del navegador según formato.'],
 ['NIfTI (.nii/.nii.gz)','Lectura y selección de cortes centrales hasta 2D.','La interfaz no ofrece navegación 3D.'],
 ['NumPy (.npy)','Arreglos sin objetos serializados; selección 2D.','Fuera del dominio de clasificadores de tórax.'],
 ['MedMNIST (.npz)','Archivo de dataset consultado mediante rutas dedicadas.','No se sube como radiografía individual.']
],source='api/image_io.py; api/main.py; api/static/index.html')
add('Qué significan las medidas de calidad',table=[
 ['Indicador','Cálculo implementado','Interpretación permitida'],
 ['Brillo','Promedio de intensidad entre 0 y 1.','Compara claridad global.'],
 ['Contraste','Desviación estándar de intensidad.','Describe dispersión de tonos.'],
 ['Ruido estimado','Mediana del cambio frente a un suavizado local.','Compara variaciones de alta frecuencia.'],
 ['Nitidez estimada','Promedio de varianzas de diferencias en dos ejes.','Describe variaciones de bordes.']
],takeaway='Se calculan con fórmulas y no necesitan entrenamiento. No hay umbral clínico validado.',source='api/quality.py. Un valor de ruido 0 no prueba ausencia de ruido.')
add('Privacidad e informe de recomendaciones',[
 'La auditoría DICOM busca campos identificadores como PatientName. La respuesta informa nombres y conteos de campos, evitando devolver sus valores.',
 'POST /anonymize/dicom genera una copia: vacía identificadores conocidos, elimina campos privados y remapea UIDs con una clave estable.',
 'Los píxeles permanecen intactos. El sistema exige revisión cuando puede haber texto incrustado; no implementa OCR ni borrado automático de ese texto.',
 'LangGraph organiza reglas: ante una probabilidad de ruido/rotación ≥ 0,5 o una alerta de privacidad, recomienda revisión. No usa un modelo de lenguaje.'
],source='api/privacy.py; api/anonymize.py; api/agent_workflow.py')
add('Dataset del experimento: PneumoniaMNIST',[
 'PneumoniaMNIST contiene radiografías en escala de grises con dos etiquetas: 0=normal y 1=neumonía. Se utilizó el archivo oficial de resolución 28 × 28 disponible localmente.',
 'Una muestra es una imagen con su etiqueta conocida. El modelo aprende a relacionar patrones de píxeles con esa etiqueta.',
 'La clasificación de neumonía permite verificar un ciclo completo: datos, entrenamiento, checkpoint, evaluación e inferencia HTTP.',
 'Sus etiquetas no describen ruido, rotación, privacidad ni edad. Esas tareas necesitan sus propios datos y criterios de evaluación.'
],source='data/medmnist/pneumoniamnist.npz; medmnist.INFO; MD5 verificado: 28209eda62fecd6e6a2d98b1501bb15f')
add('Particiones reales y distribución de clases',table=[
 ['Partición','Total','Normal','Neumonía','Función'],
 ['Train: 80,4%','4.708','1.214','3.494','Ajustar pesos.'],
 ['Validación: 8,9%','524','135','389','Evaluar al final de la época.'],
 ['Test: 10,7%','624','234','390','Evaluar el checkpoint congelado.'],
 ['Total','5.856','1.583','4.273','Archivo instalado.']
],takeaway='Las clases están desbalanceadas: accuracy necesita compararse con una referencia sencilla.',source='Conteos calculados directamente del archivo NPZ. Se conservaron los splits oficiales.')
add('Separación de datos y prevención de fuga',[
 'En train se actualizan los pesos. Validación permite decidir qué checkpoint guardar. Test se reserva para medir el modelo ya elegido.',
 'Para PneumoniaMNIST se mantuvieron las particiones oficiales. El archivo utilizado no permite demostrar aquí una auditoría propia de separación por paciente.',
 'El entrenador general admite source_id: todas las variantes de una imagen o estudio deben quedar juntas, evitando una original en train y su copia ruidosa en validación.',
 'La muestra test #0 también se usó en la demo. Si se toman decisiones de diseño a partir del test, una etapa futura necesitará otro conjunto externo reservado.'
],source='scripts/train.py: split_rows; scripts/train_medmnist.py; scripts/prepare_demo.py')
add('Qué contiene el modelo y qué se guarda',[
 'DenseNet121 es una red de capas que transforma píxeles en características numéricas. Sus filtros aprenden patrones de imagen a partir de ejemplos etiquetados.',
 'Las conexiones densas permiten reutilizar características de capas anteriores. La última parte combina esas características para producir la salida de clasificación.',
 'Los pesos son los números que el entrenamiento ajusta. Un checkpoint es un archivo que conserva esos pesos y datos necesarios para reconstruir el modelo.',
 'En este experimento la red produce un número, llamado logit. La función sigmoid lo transforma a un valor entre 0 y 1 asociado con neumonía. El umbral 0,5 convierte ese valor en una clase.'
],source='MONAI DenseNet121 instanciada en scripts/train_medmnist.py; formato del checkpoint en models/.')
add('Cómo aprende DenseNet121',diagram='learning',source='scripts/train_medmnist.py: ciclo de entrenamiento.',takeaway='Una época recorre todo train. Durante inferencia se usan pesos fijos y no se propaga el error.')
add('Configuración exacta de la corrida inicial',table=[
 ['Parámetro','Valor observado o configurado'],
 ['Modelo','MONAI DenseNet121, 2D, un canal de entrada y una salida; sin pesos preentrenados solicitados.'],
 ['Entrada','28 × 28 redimensionada a 64 × 64; intensidades normalizadas a aproximadamente [−1, 1].'],
 ['Optimización','BCEWithLogitsLoss, Adam, learning rate inicial 0,0001, batch de 64.'],
 ['Plan','5 épocas; CosineAnnealingLR configurado para ese horizonte; semilla 42.'],
 ['Ejecución real','CPU local, num_workers=0; una época completa y detención durante la segunda.'],
 ['Modelo evaluado','Checkpoint guardado al terminar la época 1. No se evaluaron los pesos parciales de época 2.']
],source='Comando y trazas de la sesión; scripts/train_medmnist.py; checkpoint y JSON de métricas.')
add('Cómo interpretar las métricas del experimento',table=[
 ['Métrica','Significado para este estudio'],
 ['Accuracy','Fracción de imágenes cuya clase coincide con la etiqueta, usando umbral 0,5.'],
 ['F1 macro','Media del F1 de normal y neumonía. F1 combina precisión y sensibilidad por clase.'],
 ['ROC-AUC','Mide cómo ordena positivos frente a negativos al variar el umbral. 0,5 es referencia aleatoria.'],
 ['Loss','Error usado para ajustar pesos. No es un porcentaje de imágenes incorrectas.'],
 ['Probabilidad individual','Salida del modelo para una muestra; no equivale a accuracy global ni certeza clínica.']
],takeaway='La correlación no se calculó: el experimento evalúa clasificación binaria.',source='scripts/train_medmnist.py: compute_multilabel_metrics; sklearn.metrics.')
add('Resultados medidos del checkpoint de época 1',table=[
 ['Medición','Validación (524)','Test (624)','Lectura'],
 ['ROC-AUC','0,9912','0,9478','Descenso de 0,0434 en test.'],
 ['F1 macro','0,9398','0,8337','Descenso de 0,1061 en test.'],
 ['Accuracy','No conservada en el registro','85,42%','533 aciertos y 91 errores.'],
 ['Loss de train','0,2315 al finalizar época 1','No corresponde','Único punto de entrenamiento documentado.']
],takeaway='Un punto por época no permite dibujar una curva de aprendizaje ni demostrar convergencia.',source='models/medmnist_pneumoniamnist_28_metrics.json; traza original; evaluación reproducida del checkpoint.')
add('Matriz de confusión: qué errores cometió',table=[
 ['Etiqueta verdadera','Predijo normal','Predijo neumonía','Total'],
 ['Normal','157 aciertos','77 falsas alarmas','234'],
 ['Neumonía','14 casos omitidos','376 aciertos','390'],
 ['Total de predicciones','171','453','624']
],takeaway='Detectó 96,41% de las neumonías y reconoció 67,09% de los normales. Los errores no se distribuyen igual.',source='Reevaluación del checkpoint congelado en test, umbral 0,5. Filas: realidad; columnas: predicción.')
add('Comparación cuantitativa con una referencia',table=[
 ['Método sobre el mismo test','Accuracy','F1 macro','ROC-AUC'],
 ['Siempre predecir neumonía','62,50%','0,3846','0,5000'],
 ['DenseNet121, época 1','85,42%','0,8337','0,9478'],
 ['Diferencia','+22,92 puntos porcentuales','+0,4491','+0,4478']
],takeaway='La referencia acierta por frecuencia de clase. DenseNet mejora esa referencia, pero aún faltan otras redes y semillas.',source='Referencia calculada: 390 positivos de 624; predicción constante. Modelo: JSON de métricas guardado.')
add('Comparación de componentes y modelos del proyecto',table=[
 ['Componente','Datos / salida','Qué evidencia existe'],
 ['Métricas de calidad','Píxeles / medidas numéricas.','Demo reproducible; sin ajuste de pesos.'],
 ['DenseNet ruido y rotación','Checkpoints previos / dos clases por tarea.','Cargan y responden; procedencia de entrenamiento no documentada.'],
 ['DenseNet PneumoniaMNIST','Splits oficiales / normal-neumonía.','Una época, checkpoint y test medido.'],
 ['Clasificador de vista','Manifiesto IU / frontal-lateral.','Preparación implementada; sin entrenamiento.'],
 ['ResNet, ViT, CLIP, DINO, kNN','Alternativas propuestas al inicio.','Sin comparación experimental en este repositorio.']
],source='models/; scripts/; evidencia de ejecución. Ningún ranking de redes puede deducirse de una sola arquitectura.')
add('Experimento técnico de ruido y rotación',table=[
 ['Caso','Ruido por fórmula','P(ruido)','P(rotación)'],
 ['Original de MedMNIST','0,0000','0,9465','0,4261'],
 ['Misma muestra rotada 25°','0,0000','0,9492','0,4278'],
 ['Misma muestra con ruido añadido','0,0588','0,9943','0,4699'],
 ['Volumen NPY de demostración','0,0000','No ejecutado','No ejecutado']
],source='demo_assets/demo_results.json; scripts/prepare_demo.py; POST /predict.',takeaway='Estas variantes de una sola fuente son una prueba funcional, no un conjunto independiente de evaluación.')
add('Análisis crítico de los hallazgos',[
 'La fórmula de ruido aumentó de 0 a 0,0588 con ruido añadido. Esto muestra sensibilidad a esa transformación; no establece un límite de calidad clínica.',
 'El clasificador de ruido asignó 0,9465 a la original. Es una alerta inesperada, pero la imagen no tiene una etiqueta de calidad adjudicada que permita llamarla falso positivo confirmado.',
 'El clasificador de rotación no cruzó 0,5 para la copia girada 25°. Falló en ese ejemplo sintético; no alcanza para estimar sensibilidad global.',
 'DenseNet de neumonía superó la referencia constante. La caída entre validación y test muestra por qué un resultado de validación alto no debe presentarse como rendimiento final.'
],source='Tablas anteriores; no se mezclan tareas de calidad con clasificación de neumonía.')
add('Del checkpoint a una predicción HTTP',[
 'Al iniciar Uvicorn, el registro busca archivos medmnist_*.pt. Lee el dataset, el tamaño de entrada y los pesos para reconstruir DenseNet121.',
 'POST /predict/medmnist/pneumoniamnist recibe un PNG/JPEG, lo convierte a grises, ajusta tamaño, normaliza y calcula una salida.',
 'Sigmoid convierte esa salida en p(neumonía). La API devuelve también p(normal)=1−p(neumonía). No modifica los pesos.',
 'En la prueba test #0, la etiqueta real era 1. El endpoint devolvió HTTP 200, p(neumonía)=0,98005 y p(normal)=0,01995.'
],source='api/medmnist_models.py; scripts/run_demo.py; demo_assets/demo_results.json')
add('Qué puede mostrar hoy la demostración',table=[
 ['Pantalla o acción','Qué muestra','Qué permite comprobar'],
 ['GET /health','CPU y modelos cargados.','Servidor activo y checkpoint disponible.'],
 ['Visor /, botón Analizar','Métricas, alertas y modelos previos.','Ruta técnica POST /predict.'],
 ['Explorador MedMNIST','Muestra test #0, imagen y etiqueta.','Dataset disponible. No ejecuta clasificación.'],
 ['/docs: ruta de predicción MedMNIST','Subir PNG de demo y ejecutar.','Nueva predicción del checkpoint entrenado.'],
 ['python scripts/run_demo.py','Tabla y reporte JSON.','Repetición automatizada de la demo.']
],source='api/static/index.html; api/main.py; scripts/run_demo.py')
add('Guion reproducible de demostración',[
 '1. Desde la carpeta ipre-dicom, activar el entorno: source .venv/bin/activate',
 '2. Iniciar el servicio: MEDMNIST_ROOT=data/medmnist python -m uvicorn api.main:app --host 127.0.0.1 --port 8000',
 '3. Abrir http://127.0.0.1:8000 y analizar los archivos de demo_assets: original, rotada, ruidosa y volumen NPY.',
 '4. Abrir http://127.0.0.1:8000/docs. En la ruta MedMNIST usar flag=pneumoniamnist y subir 01_original_medmnist.png.',
 '5. Contrastar una probabilidad individual con la tabla agregada de las 624 imágenes de test. Explicar que miden aspectos distintos.'
],source='DEMO_PRESENTACION.md; scripts/run_demo.py. Reiniciar la API cuando cambie el checkpoint.')
add('Verificación y amenazas a la validez',[
 'Las 27 pruebas automatizadas verifican contratos HTTP, lectores, reglas, métricas y etiquetas. Pruebas de software aprobadas no miden rendimiento clínico.',
 'El entrenamiento conserva una sola época y una semilla. No hay curvas completas, intervalos de confianza, evaluación externa ni comparación con ResNet.',
 'Hay una diferencia de interpolación por resolver: entrenamiento usa Resize de torchvision; la API usa resize de Pillow sin fijar el mismo filtro. La prueba HTTP verifica integración, no equivalencia numérica completa.',
 'La predicción técnica acepta cualquier raster y la previsualización del navegador es limitada. Falta control semántico de modalidad, visor volumétrico y OCR.'
],source='tests/; scripts/train_medmnist.py; api/medmnist_models.py; api/static/index.html')
add('Roadmap siguiente y criterio de término',table=[
 ['Hito pendiente','Trabajo concreto','Evidencia esperada'],
 ['1. Consistencia del pipeline','Unificar interpolación y registrar configuración/épocas de forma incremental.','Prueba de igualdad entre preprocesamientos e historial completo.'],
 ['2. Experimento comparativo','Entrenar DenseNet y ResNet con protocolo equivalente y varias semillas.','Curvas, métricas por clase y tabla con variabilidad.'],
 ['3. Calidad y vista','Obtener etiquetas revisadas e incorporar IU frontal/lateral.','Evaluación independiente por tarea.'],
 ['4. Calfuco','Resolver carpeta, entorno y acceso autorizado a GPU.','Servicio ejecutado allí y prueba HTTP vía túnel SSH.']
],source='Trabajo propuesto a partir de las limitaciones verificadas. Aún no ejecutado.')
add('Conclusiones del avance',[
 'Se construyó una API modular que integra lectura de archivos, indicadores técnicos, revisión de metadata y modelos. Un cliente externo puede reutilizar esas operaciones por HTTP.',
 'El ciclo experimental quedó demostrado con PneumoniaMNIST: entrenamiento local, checkpoint de época 1, evaluación sobre 624 muestras y predicción desde la API.',
 'El checkpoint alcanzó accuracy 85,42%, F1 macro 0,8337 y ROC-AUC 0,9478. Superó la referencia constante, aunque la evidencia sigue siendo inicial.',
 'Las pruebas también revelaron límites concretos: clasificadores previos poco documentados, alertas de calidad por revisar, preprocesamiento no idéntico y despliegue remoto pendiente.'
],source='Resultados y límites descritos en las secciones anteriores.')
add('Trazabilidad: dónde revisar cada afirmación',table=[
 ['Evidencia','Archivo o ubicación'],
 ['Arquitectura y contratos','api/main.py; api/static/index.html; README.md'],
 ['Algoritmos del análisis','api/image_io.py; quality.py; privacy.py; anonymize.py; agent_workflow.py'],
 ['Entrenamiento','scripts/train_medmnist.py; trazas de la sesión'],
 ['Checkpoint y resultados','models/medmnist_pneumoniamnist_28.pt y archivo *_metrics.json'],
 ['Demostración','scripts/prepare_demo.py; scripts/run_demo.py; demo_assets/demo_results.json'],
 ['Pruebas y plan remoto','tests/; DEMO_PRESENTACION.md; CHEATSHEET_CALFUCO.md']
],takeaway='Los conteos se obtuvieron del NPZ y los resultados del checkpoint local; no son cifras tomadas de otros estudios.')

def visual(title,kind,source,takeaway=''):
    return dict(title=title,diagram=kind,source=source,takeaway=takeaway,table=None,paragraphs=[])

revised=[]
for s in slides:
    title=s['title']
    if title=='Arquitectura actual del sistema':
        revised.extend([
            visual('UML de componentes: dónde vive cada responsabilidad','components','Estructura actual: api/main.py, api/*.py, scripts/train_medmnist.py y almacenamiento local.'),
            visual('UML de secuencia: análisis técnico de una imagen','sequence_quality','POST /predict. Se representa el camino válido de una radiografía raster; errores de entrada no dibujados.'),
            visual('UML de secuencia: usar el modelo de neumonía','sequence_model','POST /predict/medmnist/pneumoniamnist. El checkpoint se carga al iniciar la API, antes de esta petición.')])
    elif title=='Particiones reales y distribución de clases':
        revised.extend([
            visual('Por qué dividimos las imágenes en tres grupos','splits','Conteos del NPZ local. Se conservaron las particiones oficiales; porcentajes redondeados.'),
            visual('Distribución de clases: qué significa desbalance','classes','Conteos reales de data/medmnist/pneumoniamnist.npz. Barras normalizadas al 100% en cada partición.')])
    elif title=='Matriz de confusión: qué errores cometió':
        revised.append(visual('Cómo leer los 624 resultados del test','confusion','Checkpoint de época 1, umbral 0,5. Recuento reproducido: [[157,77],[14,376]].'))
    elif title=='Comparación cuantitativa con una referencia':
        revised.append(visual('Comparación: ¿el modelo supera una regla trivial?','comparison','Test de 624 imágenes. Referencia constante calculada; métricas del checkpoint reproducidas.'))
    else: revised.append(s)
    if title=='Herramientas de aprendizaje y experimentación':
        revised.extend([
            visual('W&B: dónde se integra en el experimento','wandb_flow','scripts/train.py y scripts/train_medmnist.py. W&B observa el entrenamiento; no forma parte de POST /predict.'),
            dict(title='W&B: qué programamos en los entrenadores',paragraphs=[],diagram=None,table=[
                ['Momento','Código integrado','Qué queda registrado'],
                ['Inicio','wandb.init(config=...)','Modelo, semilla, épocas, lote, learning rate y dispositivo.'],
                ['Fin de cada época','run.log(...)','Loss de train y métricas de validación.'],
                ['Test de MedMNIST','run.summary[...]','ROC-AUC, F1 macro y accuracy finales.'],
                ['Cierre','wandb.Artifact + log_artifact','Mejor checkpoint con alias best/latest, seguido de run.finish().']
            ],source='scripts/train.py:82–173; scripts/train_medmnist.py:93–174. Registro habilitado solo si el modo no es disabled.',takeaway='El artefacto se registra al final: una interrupción puede impedir ese paso.'),
            visual('W&B: implementación, prueba y uso efectivo','wandb_status','Comandos de la sesión: smoke test offline y entrenamiento real con --wandb-mode disabled.')])
    if title=='Dataset del experimento: PneumoniaMNIST':
        revised.append(visual('Una muestra: imagen más respuesta conocida','samples','Imágenes originales del NPZ local: primer ejemplo normal y primer ejemplo de neumonía del test.'))
    if title=='Cómo aprende DenseNet121':
        revised.append(visual('Entrenamiento e inferencia: dos momentos diferentes','train_serve','Scripts de entrenamiento y registro de modelos de la API. Flujo conceptual del sistema actual.'))
    if title=='Resultados medidos del checkpoint de época 1':
        revised.append(visual('Qué se completó realmente durante la corrida','epoch_timeline','Traza de ejecución: época 1 completa; Ctrl+C durante época 2; evaluación posterior del checkpoint guardado.'))
    if title=='Experimento técnico de ruido y rotación':
        revised.append(visual('Prueba controlada: misma imagen, tres condiciones','demo_images','scripts/prepare_demo.py y demo_assets/. Las variantes son de la misma fuente, no tres pacientes distintos.'))
slides=revised

def lines(text,width,size=19,font='Calibri'):
    result=[]
    for paragraph in text.split('\n'):
        line=''
        words=[]
        for word in paragraph.split():
            while pdfmetrics.stringWidth(word,font,size)>width:
                k=len(word)-1
                while pdfmetrics.stringWidth(word[:k],font,size)>width:k-=1
                words.append(word[:k]);word=word[k:]
            words.append(word)
        for word in words:
            t=(line+' '+word).strip()
            if pdfmetrics.stringWidth(t,font,size)>width and line:
                result.append(line);line=word
            else:line=t
        result.append(line)
    return result

def text(c,s,x,y,w,size=19,bold=False):
    font='CalibriBold' if bold else 'Calibri'
    c.setFillColorRGB(0,0,0);c.setFont(font,size)
    for line in lines(s,w,size,font):
        c.drawString(x,y,line);y-=size*1.24
    return y

def box(c,s,x,y,w,h):
    c.setStrokeColorRGB(0,0,0);c.setLineWidth(.8);c.rect(x,y,w,h)
    ls=lines(s,w-20,16)
    text(c,s,x+10,y+h/2+len(ls)*10-15,w-20,16)

def arrow(c,x,y,xx,yy):
    c.setLineWidth(1);c.line(x,y,xx,yy)
    if yy==y:
        d=1 if xx>x else -1;c.line(xx,yy,xx-7*d,yy+4);c.line(xx,yy,xx-7*d,yy-4)
    else:
        d=1 if yy>y else -1;c.line(xx,yy,xx-4,yy-7*d);c.line(xx,yy,xx+4,yy-7*d)

def draw_diagram(c,kind):
    if kind in VISUALS:
        return VISUALS[kind](c)
    if kind=='architecture':
        box(c,'Cliente\nVisor, Swagger o script',44,350,215,77)
        box(c,'FastAPI + Uvicorn\napi/main.py',337,350,263,77)
        arrow(c,259,389,337,389);text(c,'HTTP',276,404,58,13)
        box(c,'JSON / imagen / DICOM\nRespuesta al cliente',678,350,238,77)
        arrow(c,600,389,678,389)
        box(c,'/predict\nLectores, calidad, privacidad\nModelos ruido/rotación\nInforme por reglas',44,157,255,139)
        box(c,'/predict/medmnist\nRegistro de DenseNet121\nNormal / neumonía',353,181,247,91)
        box(c,'/datasets/medmnist\nCatálogo y muestras NPZ\n/anonymize/dicom\nCopia de metadata',661,157,255,139)
        c.line(171,320,788,320);arrow(c,469,350,469,320)
        for x,y in [(171,296),(476,272),(788,296)]:arrow(c,x,320,x,y)
        box(c,'Entrenamiento separado\nscripts/train_medmnist.py',44,49,255,65)
        box(c,'models/*.pt\nPesos guardados en disco',353,49,247,65)
        box(c,'data/medmnist/*.npz\nDataset local',661,49,255,65)
        arrow(c,299,81,353,81);arrow(c,476,114,476,181)
        arrow(c,788,114,788,157)
    elif kind=='roadmap':
        entries=[('1. Necesidad','Calidad, orientación, privacidad y formatos.'),('2. Infraestructura','Inspección SSH; decisión de ejecución local.'),('3. Implementación','API, lectores, métricas, modelos e interfaz.'),('4. Datos y demo','MedMNIST y transformaciones controladas.'),('5. Aprendizaje','Errores corregidos y checkpoint de época 1.'),('6. Evaluación','Test, integración HTTP y análisis de límites.')]
        for i,(a,b) in enumerate(entries):
            y=413-i*49;text(c,a,49,y,195,19,True);text(c,b,264,y,650,18)
            if i<5:arrow(c,220,y-6,220,y-33)
    else:
        for i,(a,b) in enumerate([
            ('1. Datos','Leer un lote de 64 imágenes de train con sus etiquetas.'),
            ('2. Predicción','La red calcula un valor de salida a partir de los píxeles.'),
            ('3. Error','BCEWithLogitsLoss compara salida y etiqueta conocida.'),
            ('4. Aprendizaje','Backpropagation calcula gradientes; Adam ajusta pesos.'),
            ('5. Validación','Sin actualizar pesos, calcular métricas en validation.'),
            ('6. Checkpoint','Guardar pesos cuando mejora el ROC-AUC de validación.')]):
            y=413-i*49;text(c,a,49,y,195,19,True);text(c,b,264,y,650,18)
            if i<5:arrow(c,220,y-6,220,y-33)

def note(c,s,y=100):
    text(c,s,49,y,855,18)

def shade(c,x,y,w,h,g=.9):
    c.setFillGray(g);c.rect(x,y,w,h,fill=1,stroke=0);c.setFillGray(0)

def component(c,label,x,y,w,h):
    box(c,label,x,y,w,h)
    c.rect(x+w-23,y+h-18,13,10)
    c.rect(x+w-27,y+h-16,7,3);c.rect(x+w-27,y+h-11,7,3)

def components(c):
    text(c,'Cada rectángulo es un componente; las flechas indican quién utiliza a quién.',49,438,860,17)
    component(c,'Cliente\nVisor / Swagger / script',49,301,236,83)
    component(c,'API FastAPI\nRutas HTTP',368,301,221,83)
    arrow(c,285,342,368,342);text(c,'HTTP',304,355,64,14)
    component(c,'Servicios\nLectura, calidad, privacidad\nInforme de reglas',677,272,235,112)
    arrow(c,589,343,677,343)
    component(c,'Registro de modelos\nDenseNet121 + pesos',368,140,221,92)
    arrow(c,479,301,479,232);text(c,'usa',490,263,85,14)
    component(c,'Entrenador\nScript Python separado',49,140,236,92)
    arrow(c,285,185,368,185);text(c,'genera .pt',287,200,85,14)
    component(c,'Datos\nNPZ en disco\nImagen subida en memoria',677,140,235,92)
    arrow(c,792,272,792,232)
    note(c,'La API corre localmente. Calfuco aún no aloja este sistema. El entrenamiento produce archivos que la API carga después.',91)

def sequence(c,names,messages):
    xs=[105+i*(750/(len(names)-1)) for i in range(len(names))]
    for x,name in zip(xs,names):
        box(c,name,x-72,397,144,46)
        c.setDash(4,4);c.line(x,397,x,368-(len(messages)-1)*32-22);c.setDash()
    for i,(a,b,label,ret) in enumerate(messages):
        y=368-i*32
        if ret:c.setDash(4,3)
        arrow(c,xs[a],y,xs[b],y)
        c.setDash()
        left=min(xs[a],xs[b]);width=abs(xs[b]-xs[a])
        text(c,label,left+8,y+8,width-12,13)
    note(c,'Lectura: el tiempo avanza de arriba abajo. Flecha continua = solicitud; flecha discontinua = respuesta.',86)

def seq_quality(c):
    sequence(c,['Cliente','API','Servicios','Modelos'],[
        (0,1,'1. POST /predict + archivo',False),
        (1,2,'2. Leer imagen y metadata',False),
        (2,1,'3. Imagen 2D disponible',True),
        (1,2,'4. Métricas y privacidad',False),
        (2,1,'5. Medidas y alertas',True),
        (1,3,'6. Predecir ruido / rotación [entrada aplicable]',False),
        (3,1,'7. Probabilidades',True),
        (1,0,'8. JSON con informe de reglas',True)])

def seq_model(c):
    sequence(c,['Cliente','API','Preprocesado','DenseNet121'],[
        (0,1,'1. POST ruta MedMNIST + PNG',False),
        (1,2,'2. Convertir y normalizar',False),
        (2,1,'3. Tensor de 64 × 64',True),
        (1,3,'4. Inferencia con pesos fijos',False),
        (3,1,'5. p(neumonía)',True),
        (1,0,'6. JSON: p y 1−p; HTTP 200',True)])
    text(c,'El modelo ya está cargado. Esta petición no entrena ni actualiza pesos.',135,148,680,17,True)

def splits(c):
    text(c,'5.856 imágenes etiquetadas: se asigna una función distinta a cada grupo.',49,431,864,21,True)
    x=55
    for count,label,g in [(4708,'Train',.78),(524,'Validación',.9),(624,'Test',.98)]:
        w=850*count/5856;shade(c,x,354,w,35,g);c.rect(x,354,w,35)
        text(c,f'{100*count/5856:.1f}%'.replace('.',','),x+12,366,w-18,14,True);x+=w
    for x,head,count,pct,desc in [
        (55,'APRENDER','4.708','80,4%','Train: las imágenes y sus etiquetas permiten corregir los pesos.'),
        (352,'REVISAR','524','8,9%','Validación: comprobar el modelo al final de la época, sin modificarlo.'),
        (649,'EXAMINAR','624','10,7%','Test: medir el checkpoint elegido con imágenes separadas.')]:
        text(c,head,x,314,255,20,True);text(c,f'{count} imágenes · {pct}',x,280,255,19)
        text(c,desc,x,238,247,19)
    note(c,'“Ajustar pesos” significa cambiar los números internos del modelo para reducir errores. En validación y test esos números permanecen fijos.',130)

def classes(c):
    text(c,'Gris = normal; blanco = neumonía. Cada barra representa el 100% de su grupo.',49,432,855,18)
    for y,label,n,p in [(335,'Train',1214,3494),(253,'Validación',135,389),(171,'Test',234,390)]:
        text(c,label,49,y+13,155,21,True)
        x,w=235,620;ratio=n/(n+p)
        shade(c,x,y,w*ratio,45,.8);c.rect(x,y,w*ratio,45);c.rect(x+w*ratio,y,w*(1-ratio),45)
        text(c,f'{n:,}'.replace(',','.'),x+12,y+16,120,17,True)
        text(c,f'{p:,}'.replace(',','.'),x+w*ratio+12,y+16,160,17,True)
        text(c,f'{100*ratio:.1f}% normal; {100*(1-ratio):.1f}% neumonía',235,y-23,640,16)
    note(c,'En test hay más neumonías: responder siempre “neumonía” ya acierta 390/624 = 62,5%. Por eso necesitamos una comparación y métricas por clase.',99)

def confusion(c):
    text(c,'La fila indica la etiqueta conocida; la columna indica la respuesta del modelo.',49,431,860,18)
    text(c,'Predijo normal',279,387,230,20,True);text(c,'Predijo neumonía',538,387,259,20,True)
    for y,label in [(297,'Real: normal'),(191,'Real: neumonía')]:text(c,label,49,y,212,20,True)
    for x,y,num,desc,diag in [(269,258,157,'Normales reconocidos',True),(528,258,77,'Falsas alarmas',False),(269,150,14,'Neumonías omitidas',False),(528,150,376,'Neumonías detectadas',True)]:
        if diag:shade(c,x,y,249,97,.9)
        c.rect(x,y,249,97);text(c,str(num),x+16,y+56,216,30,True);text(c,desc,x+16,y+25,220,17)
    note(c,'533 aciertos (157 + 376) y 91 errores (77 + 14). Detecta 96,4% de neumonías, pero reconoce solo 67,1% de normales.',100)

def comparison(c):
    text(c,'Accuracy = porcentaje de respuestas correctas sobre las mismas 624 imágenes.',49,430,860,19)
    x,w=260,520
    for y,label,value in [(316,'Siempre neumonía',62.5),(222,'DenseNet, época 1',85.4167)]:
        text(c,label,49,y+15,203,20,True);shade(c,x,y,w*value/100,43,.82);c.rect(x,y,w*value/100,43)
        text(c,f'{value:.2f}%',x+w*value/100+13,y+13,125,23,True)
    for v in [0,25,50,75,100]:
        xx=x+w*v/100;c.line(xx,194,xx,200);text(c,str(v),xx-10,177,58,14)
    text(c,'Escala de accuracy (%)',380,151,300,16)
    note(c,'La red mejora la referencia en 22,92 puntos porcentuales. Aún no se comparó contra ResNet ni se repitió con otras semillas.',105)

def wandb_flow(c):
    text(c,'W&B actúa como una bitácora: recibe registros del entrenamiento.',49,431,860,20)
    box(c,'Script de entrenamiento\nDatos + modelo + optimizador',55,280,302,100)
    box(c,'W&B SDK\nRegistro del experimento',470,280,385,100)
    arrow(c,357,327,470,327);text(c,'métricas',369,342,99,15)
    box(c,'Checkpoint .pt\nPesos en disco',55,141,302,83);arrow(c,205,280,205,224)
    box(c,'offline\nRegistro local',470,141,174,83)
    box(c,'online\nCuenta / panel web',680,141,175,83)
    c.line(557,252,767,252);arrow(c,662,280,662,252);arrow(c,557,252,557,224);arrow(c,767,252,767,224)
    note(c,'Entrenar lo hace PyTorch. W&B registra parámetros, métricas y el archivo del modelo para consultar y comparar experimentos.',100)

def wandb_status(c):
    for x,head,body in [
        (49,'1. Implementado','wandb.init, run.log, resumen final y registro del checkpoint en ambos entrenadores.'),
        (349,'2. Probado offline','Prueba pequeña con valores de ejemplo. Comprueba el registro, no el rendimiento del clasificador.'),
        (649,'3. Corrida real','PneumoniaMNIST se ejecutó con --wandb-mode disabled. Sus métricas quedaron en archivos locales.')]:
        text(c,head,x,423,265,23,True);text(c,body,x,372,260,21)
    text(c,'Qué se puede mostrar hoy',49,205,835,23,True)
    text(c,'Código de integración y métricas locales. No existe un panel W&B de la corrida real ni una curva de varias épocas registrada allí.',49,166,850,20)
    text(c,'Siguiente ejecución: elegir offline para registrar localmente u online con una cuenta autenticada. Si se interrumpe, el artefacto final puede no registrarse.',49,102,850,17)

def samples(c):
    import numpy as np
    from PIL import Image
    with np.load(ROOT/'data/medmnist/pneumoniamnist.npz') as data:
        for j,(label,name) in enumerate([(0,'Normal'),(1,'Neumonía')]):
            index=int(np.flatnonzero(data['test_labels'].reshape(-1)==label)[0]);arr=data['test_images'][index]
            x=80+j*300;c.drawImage(ImageReader(Image.fromarray(arr)),x,202,220,220)
            text(c,f'Etiqueta {label}: {name}',x,174,256,21,True)
            text(c,f'Test, índice {index} · fuente 28 × 28',x,145,266,16)
    text(c,'Imagen',723,380,184,22,True);text(c,'Los píxeles son la entrada del modelo.',723,346,180,18)
    text(c,'Etiqueta',723,268,184,22,True);text(c,'La respuesta conocida sirve para aprender o evaluar.',723,234,180,18)
    note(c,'Las imágenes se amplían solo para mostrarlas. La etiqueta proviene del dataset, no de una interpretación visual realizada aquí.',91)

def train_serve(c):
    text(c,'ENTRENAMIENTO: aprende a partir de imágenes etiquetadas',49,434,865,21,True)
    for x,s in [(49,'Train + etiquetas'),(354,'Ajustar DenseNet'),(659,'Guardar pesos .pt')]:box(c,s,x,329,252,61)
    arrow(c,301,360,354,360);arrow(c,606,360,659,360)
    arrow(c,785,329,785,230);text(c,'La API carga este archivo al arrancar',445,278,380,17)
    text(c,'INFERENCIA: aplica los pesos ya aprendidos',49,247,610,21,True)
    for x,s in [(49,'Nueva imagen'),(354,'API + pesos fijos'),(659,'Probabilidades')]:box(c,s,x,146,252,61)
    arrow(c,301,177,354,177);arrow(c,606,177,659,177)
    c.line(785,230,480,230);arrow(c,480,230,480,207)
    note(c,'Enviar una imagen a la API no enseña al modelo. Para aprender de nuevas imágenes hay que ejecutar otro entrenamiento.',98)

def epoch_timeline(c):
    text(c,'Plan: 5 épocas. Evidencia disponible: una época completa.',49,431,860,23,True)
    for i in range(5):
        x=55+i*175
        if i==0:shade(c,x,298,155,81,.78)
        c.rect(x,298,155,81);text(c,f'Época {i+1}',x+16,342,133,21,True)
        text(c,['Completa','Interrumpida','No ejecutada','No ejecutada','No ejecutada'][i],x,271,162,17)
    arrow(c,132,298,132,183);box(c,'Checkpoint de época 1\nEs el modelo evaluado en test',49,117,374,66)
    text(c,'Solo conocemos un punto:',488,221,390,22,True)
    text(c,'Loss train = 0,2315\nROC-AUC validación = 0,9912\nF1 macro validación = 0,9398',488,181,391,20)
    note(c,'Un solo punto no permite evaluar convergencia ni sobreajuste. No se conserva qué fracción de la segunda época alcanzó a ejecutarse.',76)

def demo_images(c):
    for i,(filename,label,desc) in enumerate([
        ('01_original_medmnist.png','Original','Referencia de la demo'),
        ('02_rotada_25_grados.png','Rotada 25°','Giro artificial conocido'),
        ('03_ruidosa.png','Ruido añadido','Perturbación gaussiana')]):
        x=58+i*300;c.drawImage(str(ROOT/'demo_assets'/filename),x,202,240,240)
        text(c,label,x,169,256,23,True);text(c,desc,x,137,262,18)
    note(c,'Se comparan respuestas antes y después de modificar una misma fuente. Este ensayo descubre fallos puntuales; no mide rendimiento poblacional.',87)

VISUALS={'components':components,'sequence_quality':seq_quality,'sequence_model':seq_model,'splits':splits,'classes':classes,'confusion':confusion,'comparison':comparison,'wandb_flow':wandb_flow,'wandb_status':wandb_status,'samples':samples,'train_serve':train_serve,'epoch_timeline':epoch_timeline,'demo_images':demo_images}

OUT.parent.mkdir(parents=True,exist_ok=True)
c=canvas.Canvas(str(OUT),pagesize=(W,H),initialFontName='Calibri')
c.setTitle('IPRE-DICOM: recorrido, arquitectura y evaluación experimental')
c.setAuthor('Pía Ayala')
for index,s in enumerate(slides,1):
    text(c,s['title'],44,494,872,29,True)
    c.setStrokeColorRGB(0,0,0);c.setLineWidth(.7);c.line(44,472,916,472)
    if s['diagram']:draw_diagram(c,s['diagram'])
    elif s['table']:
        rows=s['table'];n=len(rows[0]);widths={2:[235,637],3:[216,333,323],4:[350,155,155,212],5:[193,113,125,134,307]}[n]
        y=441
        for ri,row in enumerate(rows):
            size=16.5 if n<=3 else 16
            heights=[len(lines(t,widths[j]-18,size,'CalibriBold' if ri==0 else 'Calibri'))*size*1.24 for j,t in enumerate(row)]
            h=max(heights)+17
            x=44
            for j,t in enumerate(row):
                text(c,t,x+7,y,widths[j]-18,size,ri==0);x+=widths[j]
            c.setLineWidth(.4);c.line(44,y-h+21,916,y-h+21);y-=h
        assert y>70,(index,y)
    else:
        y=433
        for p in s['paragraphs']:
            y=text(c,p,49,y,859,20)-18
        assert y>78,(index,y)
    if s['takeaway']:text(c,s['takeaway'],49,85,857,16,True)
    text(c,s['source'],44,34,815,10.5)
    text(c,f'{index} / {len(slides)}',862,21,70,11)
    c.showPage()
c.save()
print(OUT)
print(f'{len(slides)} diapositivas')
