from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "pdf" / "presentacion_ipre_dicom_completa.pdf"
W, H = landscape((720, 405))
TOTAL = 39

NAVY = HexColor("#102A43")
BLUE = HexColor("#1677A8")
CYAN = HexColor("#27B3C2")
PALE = HexColor("#EAF6F8")
INK = HexColor("#243B53")
MUTED = HexColor("#627D98")
CORAL = HexColor("#E76F51")
GREEN = HexColor("#218C74")
LIGHT_CORAL = HexColor("#FCECE7")


def wrap(text, font, size, width, c):
    words, lines, current = str(text).split(), [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if c.stringWidth(candidate, font, size) <= width:
            current = candidate
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


class Deck:
    def __init__(self, path):
        self.c = canvas.Canvas(str(path), pagesize=(W, H))
        self.c.setTitle("IPRE-DICOM - Presentación técnica completa")
        self.c.setAuthor("Pía Ayala")
        self.c.setSubject("Arquitectura, entrenamiento, métricas, pruebas y demostración reproducible")
        self.page = 0

    def footer(self):
        self.c.setFillColor(MUTED)
        self.c.setFont("Helvetica", 7)
        self.c.drawRightString(W - 22, 13, f"IPRE-DICOM   {self.page}/{TOTAL}")

    def start(self, title, subtitle=None):
        self.page += 1
        self.c.setFillColor(NAVY)
        self.c.setFont("Helvetica-Bold", 22)
        self.c.drawString(34, H - 42, title)
        self.c.setStrokeColor(CYAN)
        self.c.setLineWidth(2)
        self.c.line(34, H - 52, W - 34, H - 52)
        if subtitle:
            self.text(subtitle, 36, H - 72, W - 72, 9.5, color=MUTED)

    def text(self, text, x, y, width, size=13, color=INK, bold=False, leading=None):
        font = "Helvetica-Bold" if bold else "Helvetica"
        leading = leading or size * 1.28
        self.c.setFillColor(color)
        self.c.setFont(font, size)
        for line in wrap(text, font, size, width, self.c):
            self.c.drawString(x, y, line)
            y -= leading
        return y

    def bullets(self, items, x, y, width, size=12, leading=18, color=INK):
        for item in items:
            self.c.setFillColor(CYAN)
            self.c.circle(x + 3, y + 4, 2.2, fill=1, stroke=0)
            y = self.text(item, x + 14, y, width - 14, size, color=color, leading=leading)
            y -= 4
        return y

    def box(self, x, y, w, h, fill=PALE, radius=7):
        self.c.setFillColor(fill)
        self.c.roundRect(x, y, w, h, radius, fill=1, stroke=0)

    def label(self, text, x, y, color=BLUE):
        self.text(text.upper(), x, y, 280, 12, color=color, bold=True)

    def end(self):
        self.footer()
        self.c.showPage()

    def table(self, rows, col_x, y=307, row_h=34, sizes=None):
        sizes = sizes or [10] * len(col_x)
        for ri, row in enumerate(rows):
            yy = y - ri * row_h
            if ri == 0:
                self.c.setFillColor(NAVY)
                self.c.rect(38, yy - 9, 642, row_h - 2, fill=1, stroke=0)
            elif ri % 2 == 0:
                self.c.setFillColor(PALE)
                self.c.rect(38, yy - 9, 642, row_h - 2, fill=1, stroke=0)
            for index, (x, value) in enumerate(zip(col_x, row)):
                self.text(value, x, yy, (col_x[index + 1] - x - 8) if index + 1 < len(col_x) else 672 - x,
                          sizes[index], color=white if ri == 0 else INK, bold=ri == 0)

    def save(self):
        self.c.save()


d = Deck(OUT)

# 1
d.page = 1
d.c.setStrokeColor(CYAN); d.c.setLineWidth(3); d.c.line(52, 326, 155, 326)
d.text("IPRE-DICOM", 52, 290, 590, 34, color=NAVY, bold=True)
d.text("Arquitectura, entrenamiento y demostración reproducible", 52, 246, 610, 20)
d.text("Pía Ayala · Avance técnico · septiembre de 2026", 52, 199, 550, 12, color=MUTED)
d.box(52, 87, 565, 66)
d.text("Prototipo local para visualizar imágenes médicas, ejecutar controles técnicos y organizar resultados sin afirmar validez clínica.", 74, 124, 520, 14, bold=True)
d.footer(); d.c.showPage()

# 2
d.start("Qué problema intenta resolver")
d.label("Situación", 48, 310)
d.bullets(["Las imágenes llegan en formatos, tamaños y convenciones diferentes.",
           "La calidad técnica, la privacidad y la clasificación requieren procesos distintos.",
           "Un experimento necesita trazabilidad para poder repetirse y compararse."], 48, 280, 290, size=13, leading=19)
d.box(390, 120, 275, 185)
d.label("Objetivo del prototipo", 414, 273)
d.text("Recibir una imagen, abrirla de forma uniforme, calcular indicadores, ejecutar checkpoints disponibles y devolver un informe estructurado mediante una API.", 414, 240, 230, 14)
d.text("Uso previsto: investigación y apoyo técnico.", 414, 146, 225, 12, color=CORAL, bold=True)
d.end()

# 3
d.start("Qué existía y qué se implementó en este trabajo")
d.label("Disponible al comenzar", 48, 307)
d.bullets(["Dos archivos de pesos: best_noise.pt y best_rotation.pt.",
           "No se dispone de logs, dataset de origen ni métricas verificables de esos pesos.",
           "CheXpert estaba almacenado en Calfuco, pero no conectado al código local."], 48, 276, 295, size=12, leading=18)
d.label("Implementado e integrado", 380, 307, GREEN)
d.bullets(["API FastAPI y visor web.", "Lectores DICOM, raster, NIfTI y NumPy.",
           "Métricas, privacidad y anonimización experimental.", "MedMNIST, entrenamiento, W&B y pipeline IU.",
           "Demo reproducible y 26 pruebas automatizadas."], 380, 276, 285, size=12, leading=18)
d.box(85, 53, 550, 46, LIGHT_CORAL)
d.text("Conclusión metodológica: podemos demostrar integración y funcionamiento, pero no rendimiento clínico de los pesos existentes.", 108, 79, 510, 12, color=CORAL, bold=True)
d.end()

# 4
d.start("Estado verificable hoy")
states = [
    ("PROBADO LOCALMENTE", GREEN, ["API y visor", "Formatos y métricas", "Carga de noise/rotation", "PneumoniaMNIST entrenado", "27 pruebas"]),
    ("IMPLEMENTADO, NO EJECUTADO", BLUE, ["Clasificador frontal/lateral", "Comparación con ResNet", "Registro W&B online", "Manifiesto IU"]),
    ("NO REALIZADO", CORAL, ["Despliegue en Calfuco", "Validación clínica", "OCR de píxeles", "Búsqueda vectorial"]),
]
for i, (heading, color, items) in enumerate(states):
    x = 42 + i * 222
    d.box(x, 91, 204, 220, PALE if i < 2 else LIGHT_CORAL)
    d.text(heading, x + 15, 280, 176, 11, color=color, bold=True)
    d.bullets(items, x + 14, 245, 176, size=11.5, leading=17)
d.end()

# 5
d.start("Arquitectura del repositorio")
modules = [
    ("VISOR", "api/static/index.html", "Carga archivos y muestra resultados"),
    ("API", "api/main.py", "Rutas, validación y orquestación"),
    ("SERVICIOS", "image_io.py · quality.py · privacy.py", "Lectura, métricas y auditoría"),
    ("MODELOS", "medmnist_models.py · MONAI", "Carga checkpoints e inferencia"),
    ("FLUJO", "agent_workflow.py", "Hallazgos y acciones acotadas"),
    ("ENTRENAMIENTO", "scripts/train*.py", "Splits, métricas y checkpoints"),
]
for i, (head, file, desc) in enumerate(modules):
    col, row = i % 3, i // 3
    x, y = 42 + col * 222, 218 - row * 137
    d.box(x, y, 204, 112)
    d.text(head, x + 14, y + 85, 175, 11, color=BLUE, bold=True)
    d.text(file, x + 14, y + 61, 175, 9, color=MUTED)
    d.text(desc, x + 14, y + 35, 175, 11)
d.end()

# 6
d.start("Secuencia exacta de POST /predict")
labels = ["1. Recibir\narchivo", "2. Detectar\nformato", "3. Convertir\na imagen 2D", "4. Métricas y\nprivacidad", "5. Modelos\naplicables", "6. Informe\nJSON"]
xs = [26, 141, 256, 371, 486, 601]
for i, (x, label) in enumerate(zip(xs, labels)):
    d.box(x, 218, 94, 82)
    for j, line in enumerate(label.split("\n")):
        d.text(line, x + 10, 267 - j * 20, 74, 10.5, bold=True)
    if i < len(xs) - 1:
        d.c.setStrokeColor(CYAN); d.c.setLineWidth(2)
        d.c.line(x + 96, 258, xs[i + 1] - 5, 258)
        d.c.line(xs[i + 1] - 11, 263, xs[i + 1] - 5, 258)
        d.c.line(xs[i + 1] - 11, 253, xs[i + 1] - 5, 258)
d.label("Decisión de dominio", 60, 164)
d.text("Los modelos generales solo se ejecutan para raster o DICOM CR/DX. NIfTI y NumPy reciben métricas, pero quedan fuera del dominio del clasificador de tórax.", 60, 135, 600, 13)
d.end()

# 7
d.start("Preprocesamiento por formato")
rows = [
    ("Formato", "Operación", "Salida para la API"),
    ("DICOM", "PixelData, slope/intercept, ventana, MONOCHROME1", "Imagen 2D + metadata resumida"),
    ("Raster", "Primera página y escala de grises", "Imagen 2D"),
    ("NIfTI", "Descompresión y cortes centrales", "Imagen 2D + shape/voxel spacing"),
    ("NumPy", "allow_pickle=False, cortes centrales, percentiles", "Imagen 2D + dtype/shape"),
    ("MedMNIST NPZ", "Dataset completo", "Se consulta por endpoints de dataset"),
]
d.table(rows, [48, 180, 455], y=304, row_h=43, sizes=[10, 9.5, 9.5])
d.end()

# 8
d.start("Contratos de la API")
rows = [
    ("Endpoint", "Responsabilidad", "Estado"),
    ("GET /health", "Dispositivo, modelos y datasets", "Probado"),
    ("GET /formats", "Capacidades de entrada", "Probado"),
    ("POST /predict", "Análisis técnico completo", "Probado"),
    ("POST /anonymize/dicom", "Copia DICOM seudonimizada", "Probado con fixtures"),
    ("/datasets/medmnist/...", "Descarga, catálogo y muestra", "Probado con dataset real"),
    ("/predict/medmnist/...", "Inferencia MedMNIST", "Sin checkpoint entrenado"),
]
d.table(rows, [48, 260, 585], y=306, row_h=39, sizes=[9.5, 9.5, 9.5])
d.end()

# 9
d.start("Indicadores técnicos sin modelo")
d.label("Brillo", 50, 310); d.text("Promedio de intensidad normalizada.", 50, 282, 280, 13)
d.label("Contraste", 50, 218); d.text("Desviación estándar de intensidad.", 50, 190, 280, 13)
d.label("Ruido estimado", 380, 310); d.text("Mediana de la diferencia respecto de un suavizado local.", 380, 282, 280, 13)
d.label("Nitidez estimada", 380, 218); d.text("Varianza de gradientes horizontales y verticales.", 380, 190, 280, 13)
d.box(85, 66, 550, 54, LIGHT_CORAL)
d.text("Estos valores permiten comparar entradas. Todavía no tienen umbrales clínicos calibrados.", 110, 97, 510, 13, color=CORAL, bold=True)
d.end()

# 10
d.start("Modelos disponibles en la ejecución local")
rows = [
    ("Tarea", "Checkpoint", "Salida", "Qué sabemos"),
    ("Ruido", "best_noise.pt", "clean / noise", "Carga y responde"),
    ("Rotación", "best_rotation.pt", "clean / rotation", "Carga y responde"),
    ("Vista", "best_view.pt", "frontal / lateral", "No existe aún"),
    ("PneumoniaMNIST", "medmnist_...pt", "normal / pneumonia", "Entrenado: 1 época"),
    ("ChestMNIST", "medmnist_...pt", "14 probabilidades", "No existe aún"),
]
d.table(rows, [48, 160, 325, 520], y=305, row_h=42, sizes=[10, 9.5, 9.5, 9.5])
d.box(88, 47, 545, 43, LIGHT_CORAL)
d.text("No contamos con la procedencia ni métricas originales de los dos checkpoints existentes.", 111, 72, 500, 12, color=CORAL, bold=True)
d.end()

# 11
d.start("Cómo está diseñado el entrenamiento general")
labels = ["CSV con path,\netiqueta y grupo", "Split por\nsource_id", "DenseNet121\n2D", "CrossEntropy +\nAdam + cosine LR", "Validación\npor época", "Guardar mejor\nROC-AUC"]
xs = [26, 141, 256, 371, 486, 601]
for i, (x, label) in enumerate(zip(xs, labels)):
    d.box(x, 214, 94, 86)
    for j, line in enumerate(label.split("\n")):
        d.text(line, x + 9, 266 - j * 19, 76, 9.5, bold=True)
    if i < len(xs) - 1:
        d.c.setStrokeColor(CYAN); d.c.setLineWidth(2); d.c.line(x + 96, 257, xs[i + 1] - 5, 257)
d.label("Métricas implementadas", 65, 160)
d.text("Accuracy, balanced accuracy, F1, ROC-AUC y classification report.", 65, 132, 590, 13)
d.text("Estado: código y pruebas de split listos; no se ejecutó un nuevo entrenamiento completo en esta etapa.", 65, 91, 590, 12, color=CORAL, bold=True)
d.end()

# 12
d.start("Conceptos básicos del conjunto de datos")
d.label("Muestra", 48, 310, BLUE)
d.text("Una imagen individual y su etiqueta. En PneumoniaMNIST la etiqueta 0 significa normal y la etiqueta 1 indica neumonía.", 48, 282, 285, 12.5)
d.label("Conjunto maestro", 48, 190, BLUE)
d.text("Colección completa antes de separar el experimento. El término técnico habitual es dataset; no es una sola imagen de referencia.", 48, 162, 285, 12.5)
d.label("Etiqueta", 385, 310, GREEN)
d.text("Respuesta conocida que el modelo intenta aprender. Durante el entrenamiento se compara la predicción con esta respuesta.", 385, 282, 285, 12.5)
d.label("Clase", 385, 190, GREEN)
d.text("Categoría posible de salida. Para PneumoniaMNIST existen dos clases: normal y neumonía.", 385, 162, 285, 12.5)
d.box(98, 51, 524, 48, PALE)
d.text("La API no aprende al recibir una imagen. Solo aplica un modelo cuyos pesos deberían haberse aprendido antes.", 122, 79, 480, 12, color=NAVY, bold=True)
d.end()

# 13
d.start("Separación oficial de PneumoniaMNIST")
rows = [
    ("Partición", "Muestras", "% del total", "Normal", "Neumonía", "Uso"),
    ("Train", "4.708", "80,4%", "1.214", "3.494", "Ajustar pesos"),
    ("Validation", "524", "8,9%", "135", "389", "Elegir modelo"),
    ("Test", "624", "10,7%", "234", "390", "Medición final"),
    ("Total", "5.856", "100%", "1.583", "4.273", "Dataset maestro"),
]
d.table(rows, [44, 132, 214, 310, 405, 515], y=303, row_h=43, sizes=[9.5, 9.5, 9.5, 9.5, 9.5, 9.5])
d.text("El proyecto usa los splits incluidos por MedMNIST; no vuelve a mezclar estas 5.856 imágenes.", 62, 82, 600, 12.5, color=GREEN, bold=True)
d.text("El desbalance importa: 73,0% del total corresponde a neumonía.", 62, 56, 600, 11.5, color=CORAL)
d.end()

# 14
d.start("Qué ocurre durante una época de entrenamiento")
labels = ["1. Leer un\nbatch", "2. Calcular\nlogits", "3. Comparar\ncon etiquetas", "4. Propagar\nel error", "5. Actualizar\nlos pesos", "6. Validar\nsin aprender"]
xs = [26, 141, 256, 371, 486, 601]
for i, (x, label) in enumerate(zip(xs, labels)):
    d.box(x, 215, 94, 86)
    for j, line in enumerate(label.split("\n")):
        d.text(line, x + 9, 267 - j * 19, 76, 9.5, bold=True)
    if i < len(xs) - 1:
        d.c.setStrokeColor(CYAN); d.c.setLineWidth(2); d.c.line(x + 96, 258, xs[i + 1] - 5, 258)
d.label("Época", 56, 168)
d.text("Una pasada completa por todas las muestras de train. El script propone 10 épocas por defecto.", 56, 140, 610, 12.5)
d.text("La validación se ejecuta al final de cada época. Sus imágenes no actualizan los pesos.", 56, 102, 610, 12.5, color=GREEN, bold=True)
d.text("Estado real: este ciclo está programado, pero todavía no se ejecutó de principio a fin sobre PneumoniaMNIST.", 56, 66, 610, 11.5, color=CORAL)
d.end()

# 15
d.start("Modelo, pérdida y optimización implementados")
d.label("DenseNet121 de MONAI", 48, 307, BLUE)
d.bullets(["Entrada de un canal en escala de grises.", "Salida binaria para PneumoniaMNIST.", "Reutiliza características mediante conexiones densas."], 48, 276, 285, size=12, leading=18)
d.label("BCEWithLogitsLoss", 385, 307, GREEN)
d.bullets(["Compara logits con etiquetas 0/1.", "Penaliza predicciones incorrectas.", "Permite una o varias etiquetas por imagen."], 385, 276, 285, size=12, leading=18)
d.label("Actualización de pesos", 48, 154, BLUE)
d.text("Adam usa learning rate 0,0001. CosineAnnealingLR lo reduce durante las 10 épocas.", 48, 126, 285, 12.5)
d.label("Reproducibilidad", 385, 154, GREEN)
d.text("Semilla 42, configuración registrada y checkpoint con el mejor ROC-AUC de validación.", 385, 126, 285, 12.5)
d.end()

# 16
d.start("Train, validación y test cumplen funciones distintas")
rows = [
    ("Partición", "¿Actualiza pesos?", "Pregunta que responde", "Momento"),
    ("Train", "Sí", "¿Qué patrones minimizan el error?", "Cada batch"),
    ("Validation", "No", "¿Qué época generaliza mejor?", "Cada época"),
    ("Test", "No", "¿Cómo rinde el modelo elegido?", "Una vez al final"),
]
d.table(rows, [48, 155, 280, 555], y=303, row_h=51, sizes=[10, 9.5, 9.5, 9.5])
d.box(88, 67, 545, 54, LIGHT_CORAL)
d.text("Usar test para escoger hiperparámetros contaminaría la evaluación final. El código reserva test hasta cargar el mejor checkpoint.", 111, 98, 500, 11.5, color=CORAL, bold=True)
d.end()

# 17
d.start("Métricas de clasificación y su significado")
rows = [
    ("Métrica", "Qué mide", "Cuándo ayuda"),
    ("Accuracy", "% total de aciertos", "Clases equilibradas"),
    ("Balanced accuracy", "Promedio del recall por clase", "Clases desbalanceadas"),
    ("F1", "Equilibrio entre precisión y recall", "Importan falsos positivos y negativos"),
    ("ROC-AUC", "Ordena positivos sobre negativos", "Comparar discriminación entre modelos"),
    ("Matriz de confusión", "TP, TN, FP y FN", "Entender el tipo de error"),
]
d.table(rows, [48, 175, 410], y=305, row_h=40, sizes=[9.5, 9.5, 9.5])
d.end()

# 18
d.start("Probabilidad, accuracy y correlación no son equivalentes")
d.label("Probabilidad individual", 48, 306, BLUE)
d.text("P(neumonía)=0,80 significa que el modelo asignó 0,80 a esa clase para una imagen. No afirma 80% de aciertos globales.", 48, 277, 285, 12.5)
d.label("Accuracy del conjunto", 385, 306, GREEN)
d.text("Porcentaje de muestras clasificadas correctamente después de fijar un umbral, normalmente 0,5.", 385, 277, 285, 12.5)
d.label("Correlación", 48, 174, CORAL)
d.text("Mide asociación entre variables. Este proyecto no usa correlación como métrica principal porque la tarea es clasificación.", 48, 145, 285, 12.5)
d.label("ROC-AUC", 385, 174, BLUE)
d.text("Resume la discriminación para todos los umbrales. 0,5 equivale al azar y 1,0 a separación perfecta.", 385, 145, 285, 12.5)
d.box(92, 48, 536, 43, PALE)
d.text("Los porcentajes reales solo podrán reportarse después de entrenar y evaluar el checkpoint nuevo.", 117, 73, 490, 12, color=NAVY, bold=True)
d.end()

# 19
d.start("Comparación de modelos considerada")
rows = [
    ("Modelo", "Fortaleza", "Costo", "Uso en este proyecto"),
    ("DenseNet121", "Buen extractor para radiografías", "Medio", "Implementado con MONAI"),
    ("ResNet18/50", "Baseline simple y conocido", "Bajo/medio", "Comparación pendiente"),
    ("ViT", "Contexto global", "Alto; necesita más datos", "No implementado"),
    ("CLIP", "Embeddings texto-imagen", "Alto", "Exploración futura"),
    ("DINO", "Embeddings sin etiquetas", "Alto", "Clustering futuro"),
    ("kNN", "Búsqueda por similitud", "Depende del índice", "No entrenado"),
]
d.table(rows, [43, 145, 365, 475], y=306, row_h=36, sizes=[9, 9, 9, 9])
d.text("La elección actual es DenseNet121 porque MONAI ya ofrece una implementación médica reproducible y compatible con imágenes de un canal.", 57, 50, 610, 10.5, color=GREEN, bold=True)
d.end()

# 20
d.start("Qué se hizo y qué falta para comparar modelos")
d.label("Realizado", 50, 307, GREEN)
d.bullets(["DenseNet121 entrenada una época.", "Splits oficiales de MedMNIST.", "Checkpoint seleccionado por ROC-AUC.", "Evaluación final sobre test.", "Predicción verificada desde la API."], 50, 276, 285, size=11.5, leading=17)
d.label("Pendiente", 390, 307, CORAL)
d.bullets(["Completar más épocas en Calfuco.", "Guardar curvas de múltiples épocas.", "Repetir con varias semillas.", "Entrenar ResNet con el mismo split.", "Comparar AUC, F1, tiempo y memoria."], 390, 276, 280, size=11.5, leading=17)
d.box(95, 50, 530, 46, LIGHT_CORAL)
d.text("La corrida inicial ya entrega resultados observados. La comparación entre arquitecturas sigue pendiente.", 120, 77, 486, 11.5, color=CORAL, bold=True)
d.end()

# 21
d.start("Resultados del entrenamiento real")
rows = [
    ("Medición", "Validación", "Test", "Interpretación"),
    ("ROC-AUC", "0,9912", "0,9478", "Buena discriminación inicial"),
    ("F1", "0,9398", "0,8337", "Baja al generalizar"),
    ("Accuracy", "No calculada", "0,8542", "85,42% de aciertos"),
    ("Loss de train", "0,2315", "No aplica", "Error de la época 1"),
]
d.table(rows, [48, 175, 300, 420], y=303, row_h=45, sizes=[10, 10, 10, 9.5])
d.box(78, 48, 565, 50, PALE)
d.text("DenseNet121, una época, 4.708 train, 524 validación y 624 test. Entrada original 28 x 28 redimensionada a 64 x 64.", 103, 78, 520, 11.5, color=NAVY, bold=True)
d.end()

# 22
d.start("Interpretación de los resultados obtenidos")
d.label("Lo que indican", 50, 307, GREEN)
d.bullets(["ROC-AUC de test 0,9478: el ranking entre clases es prometedor.", "F1 de test 0,8337: precisión y recall todavía tienen errores.", "Accuracy 85,42%: 533 de 624 decisiones serían correctas con umbral 0,5."], 50, 276, 300, size=12, leading=18)
d.label("Lo que no demuestran", 390, 307, CORAL)
d.bullets(["No validan uso clínico.", "Una época no prueba convergencia.", "Una sola semilla no mide variabilidad.", "No existe aún comparación experimental con ResNet."], 390, 276, 270, size=12, leading=18)
d.box(94, 52, 532, 46, LIGHT_CORAL)
d.text("El ROC-AUC bajó 0,0434 entre validación y test. La diferencia justifica evaluar siempre en datos separados.", 119, 79, 487, 11.5, color=CORAL, bold=True)
d.end()

# 12
d.start("Por qué se usa source_id")
d.box(55, 160, 270, 150, LIGHT_CORAL)
d.label("Split incorrecto", 78, 279, CORAL)
d.text("Original en train", 78, 245, 220, 13, bold=True)
d.text("Copia ruidosa de la misma imagen en validación", 78, 210, 220, 13)
d.text("Resultado optimista por fuga", 78, 174, 220, 12, color=CORAL, bold=True)
d.box(395, 160, 270, 150, PALE)
d.label("Split agrupado", 418, 279, GREEN)
d.text("Todas las variantes de una fuente quedan juntas", 418, 245, 220, 13, bold=True)
d.text("Train y validación contienen fuentes diferentes", 418, 207, 220, 13)
d.text("Evaluación más honesta", 418, 174, 220, 12, color=GREEN, bold=True)
d.text("GroupShuffleSplit usa source_id, paciente o estudio como unidad de separación.", 97, 99, 530, 13)
d.end()

# 13
d.start("Integración real de PneumoniaMNIST")
d.label("Dataset instalado", 50, 310, GREEN)
d.bullets(["Archivo: data/medmnist/pneumoniamnist.npz", "Fuente oficial: Zenodo", "MD5 verificado: 28209eda62fecd6e6a2d98b1501bb15f", "Tamaño disponible: 28 x 28"], 50, 279, 315, size=12, leading=18)
d.label("Endpoint probado", 400, 310, BLUE)
d.bullets(["Split: test", "Índice: 0", "Respuesta HTTP: 200", "Muestras del test: 624", "Etiqueta devuelta: [1]", "Contenido: image/png"], 400, 279, 260, size=12, leading=18)
d.box(112, 48, 500, 43)
d.text("El explorador web mostró: “Muestra 0 de 624 · etiquetas [1]”.", 135, 73, 460, 12.5, bold=True)
d.end()

# 14
d.start("Qué significa MedMNIST dentro del proyecto")
d.label("Sí se usa para", 52, 307, GREEN)
d.bullets(["Probar descarga y catálogo de datasets.", "Visualizar muestras de splits oficiales.", "Implementar un entrenador binario y multietiqueta.", "Definir el formato de checkpoints e inferencia."], 52, 276, 290, size=12, leading=18)
d.label("No resuelve", 390, 307, CORAL)
d.bullets(["Lectura de metadata DICOM.", "Anonimización de pacientes.", "Validación del modelo de ruido existente.", "Entrenamiento frontal/lateral."], 390, 276, 270, size=12, leading=18)
d.box(95, 59, 530, 48, LIGHT_CORAL)
d.text("El checkpoint PneumoniaMNIST ya está cargado: /predict/medmnist devuelve probabilidades normal y pneumonia.", 118, 87, 490, 12, color=GREEN, bold=True)
d.end()

# 15
d.start("Casos preparados para la demostración")
images = ["01_original_medmnist.png", "02_rotada_25_grados.png", "03_ruidosa.png"]
captions = [("Original", "PneumoniaMNIST test #0"), ("Rotada", "25 grados"), ("Ruidosa", "Ruido gaussiano sigma 35")]
for i, (name, cap) in enumerate(zip(images, captions)):
    x = 49 + i * 220
    d.c.drawImage(ImageReader(str(ROOT / "demo_assets" / name)), x, 126, 175, 175, preserveAspectRatio=True, anchor="c")
    d.text(cap[0], x, 99, 175, 14, bold=True)
    d.text(cap[1], x, 77, 175, 9.5, color=MUTED)
d.text("Además se generó un volumen NPY artificial para comprobar lectura 3D y exclusión de modelos fuera de dominio.", 92, 42, 545, 11, color=MUTED)
d.end()

# 16
d.start("Resultados reales de POST /predict")
rows = [
    ("Caso", "Ruido estimado", "P(noise)", "P(rotation)", "¿Modelos?"),
    ("Original", "0.0000", "0.9465", "0.4261", "Sí"),
    ("Rotada 25°", "0.0000", "0.9492", "0.4278", "Sí"),
    ("Ruidosa", "0.0588", "0.9943", "0.4699", "Sí"),
    ("Volumen NPY", "0.0000", "-", "-", "No"),
]
d.table(rows, [48, 190, 350, 470, 600], y=302, row_h=46, sizes=[10, 10, 10, 10, 10])
d.box(78, 47, 565, 48, PALE)
d.text("Ejecución local en CPU con los checkpoints presentes en models/.", 104, 75, 520, 12, bold=True)
d.end()

# 17
d.start("Hallazgos de la demostración")
d.label("Funcionó", 48, 310, GREEN)
d.bullets(["Los cuatro archivos recibieron HTTP 200.", "El ruido determinista distinguió la variante ruidosa: 0.0588 frente a 0.0000.", "NPY quedó fuera del dominio de los modelos, como estaba diseñado.", "El informe LangGraph se produjo de manera reproducible."], 48, 280, 300, size=12, leading=18)
d.label("Problemas encontrados", 390, 310, CORAL)
d.bullets(["P(noise) fue 0.9465 incluso en la original: alto falso positivo.", "La rotada quedó bajo el umbral 0.5: el modelo no detectó el caso.", "No se pueden inferir métricas globales con tres imágenes.", "Los pesos requieren procedencia, dataset y validación."], 390, 280, 280, size=12, leading=18)
d.end()

# 18
d.start("Conclusión del experimento local")
d.box(60, 199, 600, 116)
d.text("La infraestructura funciona", 90, 278, 540, 20, color=GREEN, bold=True)
d.text("La API abre los formatos, ejecuta los módulos, aplica reglas de dominio y devuelve resultados estructurados.", 90, 241, 540, 14)
d.box(60, 67, 600, 102, LIGHT_CORAL)
d.text("Los modelos aún no son confiables", 90, 136, 540, 20, color=CORAL, bold=True)
d.text("La demo evidencia falsos positivos de ruido y baja sensibilidad a la rotación. El siguiente trabajo debe centrarse en datos, etiquetas y evaluación.", 90, 101, 540, 14)
d.end()

# 19
d.start("Privacidad y anonimización DICOM")
d.label("Auditoría", 50, 310)
d.bullets(["Busca campos como PatientName, PatientID e InstitutionName.", "Devuelve nombres de campos, nunca sus valores.", "Evalúa BurnedInAnnotation y exige revisión de píxeles."], 50, 279, 300, size=12, leading=18)
d.label("Exportación experimental", 390, 310)
d.bullets(["Elimina tags privados.", "Vacía identificadores directos conocidos.", "Remapea UIDs con HMAC estable.", "No modifica PixelData."], 390, 279, 270, size=12, leading=18)
d.box(95, 58, 530, 48, LIGHT_CORAL)
d.text("Sin OCR ni redacción de píxeles. No equivale a certificación DICOM PS3.15.", 120, 86, 485, 12, color=CORAL, bold=True)
d.end()

# 20
d.start("Flujo agente: qué hace y qué no hace")
d.label("Entrada", 48, 310)
d.bullets(["Probabilidades ya calculadas", "Conteo de identificadores", "Bandera de revisión de píxeles"], 48, 280, 285, size=12, leading=18)
d.label("Salida", 390, 310)
d.bullets(["Estado ok o review", "Hallazgos estructurados", "Acciones recomendadas", "Aviso no diagnóstico"], 390, 280, 270, size=12, leading=18)
d.box(85, 62, 550, 52)
d.text("LangGraph solo orquesta una función determinista. No usa un LLM, no clasifica imágenes y no toma decisiones clínicas.", 110, 92, 510, 12, color=BLUE, bold=True)
d.end()

# 21
d.start("Pruebas automatizadas")
d.text("27", 58, 286, 160, 40, color=BLUE, bold=True)
d.text("pruebas aprobadas", 58, 243, 220, 16)
d.text("0", 58, 164, 160, 34, color=GREEN, bold=True)
d.text("fallos actuales", 58, 127, 220, 16)
d.label("Cobertura principal", 340, 310)
d.bullets(["Formatos y extensiones", "Privacidad y anonimización", "MedMNIST y métricas", "Split agrupado", "Manifiesto IU", "Endpoints HTTP", "Flujo agente"], 340, 279, 310, size=12, leading=17)
d.text("Comando: python -m unittest discover -s tests -v", 78, 61, 560, 11, color=MUTED)
d.end()

# 22
d.start("Entrenamiento MedMNIST ejecutado")
d.label("Configuración", 48, 310)
d.bullets(["PneumoniaMNIST o ChestMNIST", "Tamaños 28, 64, 128 o 224", "DenseNet121 con un canal", "BCEWithLogitsLoss", "Adam y cosine scheduler"], 48, 280, 290, size=12, leading=18)
d.label("Evaluación", 390, 310)
d.bullets(["ROC-AUC macro", "F1 macro", "Exactitud por etiqueta", "Selección por validación", "Evaluación final en test"], 390, 280, 270, size=12, leading=18)
d.box(100, 55, 520, 44, PALE)
d.text("Corrida inicial: 1 época, ROC-AUC test 0,9478, F1 test 0,8337 y accuracy test 0,8542.", 123, 81, 480, 12, color=GREEN, bold=True)
d.end()

# 23
d.start("W&B: qué se preparó")
d.label("Registro por época", 50, 310)
d.bullets(["Pérdida", "Learning rate", "Accuracy y balanced accuracy", "F1 y ROC-AUC"], 50, 280, 285, size=12, leading=18)
d.label("Trazabilidad", 390, 310)
d.bullets(["Hiperparámetros", "Semilla y dispositivo", "Método de split", "Mejor checkpoint como artefacto", "Modo online u offline"], 390, 280, 270, size=12, leading=18)
d.box(86, 57, 548, 47, LIGHT_CORAL)
d.text("La corrida inicial guardó métricas y checkpoint local. W&B sigue probado solo mediante un smoke test offline.", 111, 85, 510, 12, color=CORAL, bold=True)
d.end()

# 24
d.start("Pipeline frontal/lateral con IU Chest X-Ray")
labels = ["indiana_\nprojections.csv", "Normalizar\nPA/AP/LAT", "Buscar\nimágenes", "Manifest con\nsource_id", "Entrenar\ntask=view", "best_view.pt\nen la API"]
xs = [26, 141, 256, 371, 486, 601]
for i, (x, label) in enumerate(zip(xs, labels)):
    d.box(x, 214, 94, 86)
    for j, line in enumerate(label.split("\n")):
        d.text(line, x + 9, 266 - j * 19, 76, 9.5, bold=True)
    if i < len(xs) - 1:
        d.c.setStrokeColor(CYAN); d.c.setLineWidth(2); d.c.line(x + 96, 257, xs[i + 1] - 5, 257)
d.text("La vista lateral es una categoría válida, no una alerta de mala calidad.", 95, 142, 535, 14, color=BLUE, bold=True)
d.text("Estado: generador de manifiesto y entrenamiento listos; dataset y entrenamiento todavía pendientes.", 95, 100, 535, 12, color=CORAL, bold=True)
d.end()

# 25
d.start("Calfuco: recursos inspeccionados, despliegue pendiente")
d.label("Observado por SSH", 48, 310, GREEN)
d.bullets(["RTX 3090 de 24 GB y dos RTX 2080 Ti", "125 GB de RAM", "/mnt/data para datasets", "/mnt/workspace para entrenamiento", "Python del sistema 3.6.9"], 48, 279, 310, size=12, leading=18)
d.label("Bloqueos", 400, 310, CORAL)
d.bullets(["Sin permiso en /mnt/workspace/pfayala", "Sin acceso al daemon Docker", "Falta entorno Python moderno", "Proyecto aún no copiado ni ejecutado"], 400, 279, 260, size=12, leading=18)
d.box(105, 52, 510, 44, LIGHT_CORAL)
d.text("Estado correcto para presentar: plan documentado, no despliegue realizado.", 130, 78, 470, 12, color=CORAL, bold=True)
d.end()

# 26
d.start("Cómo ejecutar la demostración")
d.label("Terminal 1", 45, 310)
d.box(45, 217, 300, 72, HexColor("#F3F6F8"))
d.text("source .venv/bin/activate", 62, 265, 270, 10, bold=True)
d.text("MEDMNIST_ROOT=data/medmnist python -m uvicorn api.main:app --host 127.0.0.1 --port 8000", 62, 242, 265, 9)
d.label("Terminal 2", 390, 310)
d.box(390, 217, 285, 72, HexColor("#F3F6F8"))
d.text("python scripts/run_demo.py", 408, 263, 250, 11, bold=True)
d.text("Guarda demo_assets/demo_results.json", 408, 238, 250, 10)
d.label("Navegador", 45, 171)
d.bullets(["Abrir http://127.0.0.1:8000", "Cargar original, rotada y ruidosa", "En MedMNIST: PneumoniaMNIST / test / 28 / índice 0"], 45, 140, 620, size=12, leading=18)
d.end()

# 27
d.start("Guion de la demo en vivo")
steps = [
    ("1", "Abrir /health", "Mostrar CPU y modelos rotation/noise."),
    ("2", "Explorador MedMNIST", "Mostrar test #0 de 624, etiqueta [1]."),
    ("3", "Imagen original", "Explicar métricas y falso positivo de ruido."),
    ("4", "Imagen rotada", "Mostrar que el modelo no cruza 0.5."),
    ("5", "Imagen ruidosa", "Comparar noise_estimate 0.0588 y P(noise) 0.9943."),
    ("6", "Volumen NPY", "Mostrar lectura y exclusión de modelos."),
]
for i, (num, title, body) in enumerate(steps):
    col, row = i % 2, i // 2
    x, y = 45 + col * 340, 275 - row * 75
    d.text(num, x, y, 30, 20, color=BLUE, bold=True)
    d.text(title, x + 35, y, 270, 13, bold=True)
    d.text(body, x + 35, y - 24, 270, 10.5, color=MUTED)
d.end()

# 28
d.page += 1
d.c.setStrokeColor(CYAN); d.c.setLineWidth(3); d.c.line(52, 326, 155, 326)
d.text("Conclusión", 52, 289, 580, 29, color=NAVY, bold=True)
d.text("Se implementó y probó una plataforma local modular.", 52, 241, 610, 18, color=GREEN, bold=True)
d.text("La demostración confirmó formatos, reglas de dominio, MedMNIST y respuestas estructuradas.", 52, 202, 610, 14)
d.text("El nuevo modelo PneumoniaMNIST alcanzó ROC-AUC 0,9478 y accuracy 85,42% en test tras una época.", 52, 159, 610, 14, color=GREEN, bold=True)
d.text("Siguiente hito: completar más épocas y comparar DenseNet121 con ResNet usando exactamente los mismos splits.", 52, 111, 610, 14)
d.text("Preguntas", 52, 57, 240, 17, bold=True)
d.footer(); d.c.showPage()

d.save()
print(OUT)
