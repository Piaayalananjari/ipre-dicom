from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import landscape
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "pdf" / "presentacion_ipre_dicom_tecnica.pdf"
W, H = landscape((720, 405))

NAVY = HexColor("#102A43")
BLUE = HexColor("#1677A8")
CYAN = HexColor("#27B3C2")
PALE = HexColor("#EAF6F8")
INK = HexColor("#243B53")
MUTED = HexColor("#627D98")
CORAL = HexColor("#E76F51")


def wrap(text, font, size, width, c):
    words, lines, current = text.split(), [], ""
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
        self.c.setTitle("IPRE-DICOM - Avance de proyecto")
        self.c.setAuthor("Pía Ayala")
        self.c.setSubject("API experimental para análisis técnico de imágenes médicas")
        self.page = 0

    def footer(self):
        self.c.setFont("Helvetica", 7)
        self.c.setFillColor(MUTED)
        self.c.drawRightString(W - 24, 14, f"IPRE-DICOM   {self.page}/20")

    def title(self, title):
        self.page += 1
        self.c.setFillColor(NAVY)
        self.c.setFont("Helvetica-Bold", 23)
        self.c.drawString(36, H - 45, title)
        self.c.setStrokeColor(CYAN)
        self.c.setLineWidth(2)
        self.c.line(36, H - 55, W - 36, H - 55)

    def text(self, text, x, y, width, size=14, leading=None, color=INK, bold=False):
        font = "Helvetica-Bold" if bold else "Helvetica"
        leading = leading or size * 1.28
        self.c.setFillColor(color)
        self.c.setFont(font, size)
        for line in wrap(text, font, size, width, self.c):
            self.c.drawString(x, y, line)
            y -= leading
        return y

    def bullets(self, items, x, y, width, size=13, leading=20):
        for item in items:
            self.c.setFillColor(CYAN)
            self.c.circle(x + 3, y + 4, 2.2, fill=1, stroke=0)
            y = self.text(item, x + 14, y, width - 14, size=size, leading=leading)
            y -= 5
        return y

    def box(self, x, y, w, h, fill=PALE):
        self.c.setFillColor(fill)
        self.c.roundRect(x, y, w, h, 8, fill=1, stroke=0)

    def end(self):
        self.footer()
        self.c.showPage()

    def save(self):
        self.c.save()


d = Deck(OUT)

# 1
d.page = 1
d.c.setFillColor(NAVY)
d.c.setFont("Helvetica-Bold", 35)
d.c.drawString(52, 292, "IPRE-DICOM")
d.c.setStrokeColor(CYAN); d.c.setLineWidth(3); d.c.line(52, 325, 150, 325)
d.text("API experimental para análisis técnico de imágenes médicas", 52, 255, 590, 20)
d.text("Pía Ayala · Avance de proyecto · septiembre de 2026", 52, 208, 550, 12, color=MUTED)
d.box(52, 92, 530, 58)
d.text("Formatos médicos, control técnico, privacidad e inferencia reproducible", 72, 124, 490, 15, bold=True)
d.footer(); d.c.showPage()

# 2
d.title("Problema y objetivo")
d.text("PROBLEMA", 45, 310, 270, 14, color=BLUE, bold=True)
d.text("Las imágenes provienen de fuentes, formatos y tamaños distintos. Antes de entrenar se necesita un flujo uniforme, trazable y seguro.", 45, 282, 280, 14)
d.text("PREGUNTA", 45, 178, 270, 14, color=BLUE, bold=True)
d.text("¿Cómo recibir una imagen, inspeccionarla y ejecutar modelos sin mezclar lectura, privacidad e inferencia?", 45, 150, 280, 14)
d.box(370, 105, 300, 205)
d.text("OBJETIVO DEL PROTOTIPO", 394, 278, 250, 14, color=NAVY, bold=True)
d.text("Construir una API modular que abra imágenes médicas, calcule indicadores técnicos, audite metadata DICOM y ejecute clasificadores disponibles.", 394, 243, 248, 15)
d.text("Alcance: investigación y apoyo técnico, sin diagnóstico clínico.", 394, 142, 245, 13, color=CORAL, bold=True)
d.end()

# 3
d.title("Flujo de una imagen dentro de la API")
labels = ["Archivo\nsubido", "Lector según\nformato", "Imagen 2D\nnormalizada", "Análisis\ny modelos", "JSON e\ninterfaz web"]
xs = [34, 171, 308, 445, 582]
for i, (x, label) in enumerate(zip(xs, labels)):
    d.box(x, 225, 105, 70)
    lines = label.split("\n")
    for j, line in enumerate(lines):
        d.text(line, x + 12, 268 - j * 19, 83, 11, bold=True)
    if i < 4:
        d.c.setStrokeColor(CYAN); d.c.setLineWidth(2); d.c.line(x + 107, 260, xs[i+1] - 4, 260)
        d.c.line(xs[i+1] - 10, 265, xs[i+1] - 4, 260); d.c.line(xs[i+1] - 10, 255, xs[i+1] - 4, 260)
d.text("1", 55, 165, 40, 24, color=BLUE, bold=True); d.text("FastAPI recibe el archivo mediante /predict.", 55, 132, 170, 12)
d.text("2", 280, 165, 40, 24, color=BLUE, bold=True); d.text("Cada módulo entrega resultados independientes.", 280, 132, 180, 12)
d.text("3", 515, 165, 40, 24, color=BLUE, bold=True); d.text("La interfaz presenta el mismo contrato JSON.", 515, 132, 160, 12)
d.end()

# 4
d.title("Capacidades implementadas")
d.text("ENTRADA Y ANÁLISIS", 45, 310, 280, 14, color=NAVY, bold=True)
d.bullets(["DICOM, raster, NIfTI y NumPy", "Brillo, contraste, ruido y nitidez", "Corte central para volúmenes"], 45, 282, 280)
d.text("MODELOS", 45, 173, 280, 14, color=NAVY, bold=True)
d.bullets(["DenseNet121 de MONAI", "Ruido y rotación probados localmente", "Frontal/lateral preparado"], 45, 145, 280, size=11.5, leading=17)
d.text("DATOS Y EXPERIMENTACIÓN", 375, 310, 295, 14, color=NAVY, bold=True)
d.bullets(["ChestMNIST y PneumoniaMNIST", "Manifiesto para IU Chest X-Ray", "Splits por paciente o estudio", "Métricas y artefactos en W&B"], 375, 282, 290)
d.text("SEGURIDAD", 375, 130, 280, 14, color=NAVY, bold=True)
d.bullets(["Auditoría DICOM", "Seudonimización experimental", "LangGraph determinista opcional"], 375, 102, 285, size=12, leading=17)
d.end()

# 5
d.title("Demostración con cambios controlados")
imgs = ["01_original_medmnist.png", "02_rotada_25_grados.png", "03_ruidosa.png"]
captions = [("Original", "Muestra pública de PneumoniaMNIST"), ("Rotada", "Alteración controlada de 25 grados"), ("Ruidosa", "Ruido gaussiano reproducible")]
for i, (img, cap) in enumerate(zip(imgs, captions)):
    x = 48 + i * 220
    d.c.drawImage(ImageReader(str(ROOT / "demo_assets" / img)), x, 125, 175, 175, preserveAspectRatio=True, anchor="c")
    d.text(cap[0], x, 98, 175, 14, bold=True)
    d.text(cap[1], x, 77, 175, 9, color=MUTED)
d.text("La demo compara indicadores deterministas y predicciones aprendidas sin usar datos identificables.", 85, 42, 560, 11, color=MUTED)
d.end()

# 6
d.title("Modelos y etiquetas")
rows = [
    ("Tarea", "Clase 0", "Clase 1", "Estado"),
    ("Ruido", "clean", "noise", "Checkpoint disponible"),
    ("Rotación", "clean", "rotation", "Checkpoint disponible"),
    ("Vista", "frontal", "lateral", "Falta entrenar"),
    ("PneumoniaMNIST", "normal", "pneumonia", "Pipeline listo"),
    ("ChestMNIST", "14 hallazgos", "multietiqueta", "Pipeline listo"),
]
colx = [45, 200, 325, 465]
for ri, row in enumerate(rows):
    y = 305 - ri * 38
    if ri == 0:
        d.c.setFillColor(NAVY); d.c.rect(38, y - 10, 635, 31, fill=1, stroke=0)
    elif ri % 2 == 0:
        d.c.setFillColor(PALE); d.c.rect(38, y - 10, 635, 31, fill=1, stroke=0)
    for x, cell in zip(colx, row):
        d.text(cell, x, y, 180, 11, color=white if ri == 0 else INK, bold=ri == 0)
d.box(75, 45, 570, 42)
d.text("La API funciona de extremo a extremo. Cada modelo aún requiere validación externa.", 95, 69, 530, 13, bold=True)
d.end()

# 7
d.title("Privacidad DICOM")
d.text("AUDITORÍA", 55, 305, 270, 15, color=NAVY, bold=True)
d.bullets(["Detecta campos sensibles", "No devuelve sus valores", "Revisa BurnedInAnnotation", "Solicita revisión OCR"], 55, 273, 275)
d.text("EXPORTACIÓN EXPERIMENTAL", 385, 305, 280, 15, color=NAVY, bold=True)
d.bullets(["Elimina tags privados", "Vacía identificadores conocidos", "Remapea UIDs con HMAC", "Conserva PixelData"], 385, 273, 275)
d.box(70, 57, 580, 62, fill=HexColor("#FCECE7"))
d.text("Límite actual: no hay OCR ni redacción de píxeles. Se requiere validación institucional.", 92, 91, 535, 13, color=CORAL, bold=True)
d.end()

# 8
d.title("Validación y reproducibilidad")
d.text("26", 60, 285, 160, 38, color=BLUE, bold=True)
d.text("pruebas automatizadas aprobadas", 60, 245, 250, 15)
d.text("4", 60, 167, 160, 32, color=CYAN, bold=True)
d.text("familias de formatos principales", 60, 132, 250, 15)
d.text("LA SUITE COMPRUEBA", 365, 305, 290, 15, color=NAVY, bold=True)
d.bullets(["Lectura y normalización", "Privacidad DICOM", "Servicios MedMNIST", "Separación por fuente", "Endpoints HTTP"], 365, 273, 280)
d.text("W&B registra configuración, pérdida, ROC-AUC, F1 y el mejor checkpoint.", 365, 110, 275, 13)
d.end()

# 9
d.title("Estado actual del proyecto")
d.text("VALIDADO EN ENTORNO LOCAL", 45, 310, 300, 15, color=BLUE, bold=True)
d.bullets(["API y visor ejecutables en el Mac", "Soporte multiformato", "Ruido y rotación integrados", "MedMNIST, W&B y LangGraph", "Auditoría DICOM", "Manual, demo y pruebas"], 45, 277, 300, size=11.5, leading=17)
d.text("TRABAJO PENDIENTE", 380, 310, 285, 15, color=CORAL, bold=True)
d.bullets(["Entrenar vista con IU", "Validar por paciente", "Calibrar probabilidades", "Añadir OCR", "Incorporar autenticación", "Evaluar búsqueda por similitud"], 380, 277, 285, size=12, leading=17)
d.end()

# 10
d.title("Próximo experimento")
d.text("DATASET", 50, 305, 260, 14, color=BLUE, bold=True)
d.text("IU Chest X-Ray para clasificar vista frontal o lateral.", 50, 275, 270, 14)
d.text("DISEÑO", 50, 185, 260, 14, color=BLUE, bold=True)
d.text("Separación por source_id para mantener cada estudio en una sola partición.", 50, 155, 270, 14)
d.text("EVALUACIÓN", 390, 305, 260, 14, color=BLUE, bold=True)
d.text("ROC-AUC, F1, balanced accuracy y matriz de confusión.", 390, 275, 260, 14)
d.text("ENTREGA", 390, 185, 260, 14, color=BLUE, bold=True)
d.text("best_view.pt integrado automáticamente en /predict.", 390, 155, 260, 14)
d.box(80, 53, 560, 48)
d.text("Objetivo inmediato: validar el flujo con datos reales y revisión humana de errores.", 102, 80, 520, 14, bold=True)
d.end()

# 11
d.title("Arquitectura por capas")
layers = [
    ("PRESENTACIÓN", "Visor web y documentación Swagger"),
    ("APLICACIÓN", "Endpoints FastAPI y validación de carga"),
    ("DOMINIO", "Formatos, calidad, privacidad y flujo agente"),
    ("MODELOS Y DATOS", "MONAI, checkpoints, MedMNIST e IU"),
]
for i, (heading, body) in enumerate(layers):
    x = 42 + i * 166
    d.box(x, 170, 150, 135)
    d.text(heading, x + 14, 278, 122, 11, color=BLUE, bold=True)
    d.text(body, x + 14, 242, 120, 13)
d.box(90, 72, 540, 48)
d.text("La separación permite reemplazar un modelo o agregar un formato sin reescribir toda la API.", 112, 99, 500, 13, bold=True)
d.end()

# 12
d.title("Contratos principales de la API")
rows = [
    ("Endpoint", "Entrada", "Salida"),
    ("GET /health", "Sin archivo", "Dispositivo, modelos y datasets"),
    ("GET /formats", "Sin archivo", "Formatos y límite de carga"),
    ("POST /predict", "DICOM, raster, NIfTI o NPY", "Métricas, privacidad, modelos e informe"),
    ("POST /anonymize/dicom", "DICOM", "DICOM seudonimizado"),
    ("/datasets/medmnist/...", "Dataset, split, tamaño e índice", "Catálogo, descarga o muestra"),
    ("/predict/medmnist/...", "Raster y checkpoint", "Probabilidad por etiqueta"),
]
colx = [45, 250, 455]
widths = [190, 190, 225]
for ri, row in enumerate(rows):
    y = 310 - ri * 35
    if ri == 0:
        d.c.setFillColor(NAVY); d.c.rect(38, y - 9, 640, 29, fill=1, stroke=0)
    elif ri % 2 == 0:
        d.c.setFillColor(PALE); d.c.rect(38, y - 9, 640, 29, fill=1, stroke=0)
    for x, w, cell in zip(colx, widths, row):
        d.text(cell, x, y, w, 9.5, color=white if ri == 0 else INK, bold=ri == 0)
d.text("FastAPI publica OpenAPI, Swagger y validación automática de parámetros.", 132, 54, 470, 11, color=MUTED)
d.end()

# 13
d.title("Preprocesamiento según formato")
d.text("DICOM", 55, 305, 270, 15, color=NAVY, bold=True)
d.bullets(["Decodificación de PixelData", "Pendiente e intercepto", "Ventana o rango observado", "Inversión MONOCHROME1", "Primer frame multiframe"], 55, 273, 275, size=12, leading=18)
d.text("OTROS FORMATOS", 385, 305, 280, 15, color=NAVY, bold=True)
d.bullets(["Raster en escala de grises", "Corte central para NIfTI y NPY", "Percentiles 1 y 99", "Redimensión a 224 x 224", "Normalización MONAI"], 385, 273, 275, size=12, leading=18)
d.box(95, 52, 530, 45, fill=HexColor("#FCECE7"))
d.text("Abrir un formato no implica que un clasificador sea válido para esa modalidad.", 118, 78, 490, 12, color=CORAL, bold=True)
d.end()

# 14
d.title("Modelado con MONAI DenseNet121")
d.text("ENTRADA", 45, 305, 250, 14, color=BLUE, bold=True)
d.text("Imagen 2D, un canal, intensidad normalizada.", 45, 277, 270, 13)
d.text("RED", 45, 205, 250, 14, color=BLUE, bold=True)
d.text("DenseNet121 reutiliza características mediante conexiones densas.", 45, 177, 270, 13)
d.text("SALIDA", 45, 105, 250, 14, color=BLUE, bold=True)
d.text("Dos logits para ruido, rotación o vista.", 45, 77, 270, 13)
d.text("INFERENCIA", 380, 305, 280, 14, color=NAVY, bold=True)
d.bullets(["Carga best_<task>.pt al iniciar", "Transforma una imagen en tensor", "Softmax produce probabilidades", "Asigna nombres y devuelve JSON"], 380, 270, 285, size=13, leading=19)
d.text("MedMNIST usa una salida por etiqueta y sigmoid.", 380, 115, 270, 11, color=MUTED)
d.end()

# 15
d.title("Pipeline de entrenamiento")
labels = ["CSV, etiquetas\ny grupo", "Split por\nsource_id", "DenseNet121 y\nCrossEntropy", "Métricas de\nvalidación", "Mejor\ncheckpoint"]
xs = [35, 171, 307, 443, 579]
for i, (x, label) in enumerate(zip(xs, labels)):
    d.box(x, 226, 106, 70)
    for j, line in enumerate(label.split("\n")):
        d.text(line, x + 11, 267 - j * 19, 84, 10.5, bold=True)
    if i < 4:
        d.c.setStrokeColor(CYAN); d.c.setLineWidth(2); d.c.line(x + 108, 260, xs[i+1] - 4, 260)
        d.c.line(xs[i+1] - 10, 265, xs[i+1] - 4, 260); d.c.line(xs[i+1] - 10, 255, xs[i+1] - 4, 260)
d.text("PREVENCIÓN DE FUGA", 70, 165, 250, 14, color=NAVY, bold=True)
d.text("La imagen original y sus variantes permanecen en una sola partición.", 70, 132, 255, 13)
d.text("SELECCIÓN", 390, 165, 250, 14, color=NAVY, bold=True)
d.text("Se conserva el checkpoint con mayor ROC-AUC de validación.", 390, 132, 255, 13)
d.end()

# 16
d.title("Datasets y función dentro del proyecto")
rows = [
    ("Fuente", "Tipo", "Uso", "Limitación"),
    ("PneumoniaMNIST", "Binario", "Probar pipeline", "Sin DICOM"),
    ("ChestMNIST", "14 etiquetas", "Multietiqueta", "Resolución reducida"),
    ("IU Chest X-Ray", "Frontal/lateral", "Entrenar view", "Falta descargar"),
    ("CheXpert", "Radiografías", "Escalamiento", "Gran tamaño"),
    ("Sintéticos", "Ruido/rotación", "Validar flujo", "Variabilidad limitada"),
]
colx = [45, 205, 350, 510]
for ri, row in enumerate(rows):
    y = 305 - ri * 42
    if ri == 0:
        d.c.setFillColor(NAVY); d.c.rect(38, y - 10, 640, 32, fill=1, stroke=0)
    elif ri % 2 == 0:
        d.c.setFillColor(PALE); d.c.rect(38, y - 10, 640, 32, fill=1, stroke=0)
    for x, cell in zip(colx, row):
        d.text(cell, x, y, 150, 10.5, color=white if ri == 0 else INK, bold=ri == 0)
d.end()

# 17
d.title("Evaluación y seguimiento con W&B")
d.text("DURANTE EL ENTRENAMIENTO", 55, 305, 290, 14, color=NAVY, bold=True)
d.bullets(["Pérdida por época", "Learning rate", "Accuracy y balanced accuracy", "F1 y ROC-AUC"], 55, 271, 285)
d.text("TRAZABILIDAD", 385, 305, 280, 14, color=NAVY, bold=True)
d.bullets(["Hiperparámetros y semilla", "Arquitectura y dispositivo", "Método de separación", "Mejor checkpoint como artefacto"], 385, 271, 280)
d.box(70, 63, 580, 55)
d.text("W&B opera online u offline. El proyecto no sube automáticamente imágenes clínicas ni metadata DICOM.", 93, 94, 535, 12, bold=True)
d.end()

# 18
d.title("Flujo agente acotado")
d.text("ENTRADAS PERMITIDAS", 55, 305, 275, 15, color=NAVY, bold=True)
d.bullets(["Probabilidades calculadas", "Conteo de campos sensibles", "Necesidad de revisar píxeles"], 55, 270, 280)
d.text("SALIDAS", 385, 305, 275, 15, color=NAVY, bold=True)
d.bullets(["Estado ok o review", "Hallazgos estructurados", "Acciones recomendadas", "Aviso de uso no diagnóstico"], 385, 270, 280)
d.box(72, 62, 576, 52)
d.text("LangGraph organiza herramientas. No reemplaza los modelos ni toma decisiones clínicas.", 98, 91, 530, 13, color=BLUE, bold=True)
d.end()

# 19
d.title("Plan de despliegue en Calfuco")
d.text("RECURSOS OBSERVADOS", 55, 305, 280, 14, color=NAVY, bold=True)
d.bullets(["Tres GPU, incluida una RTX 3090", "/mnt/data para originales", "/mnt/workspace para datos activos", "Python del sistema 3.6.9"], 55, 270, 285, size=11.5, leading=18)
d.text("PASOS TODAVÍA PENDIENTES", 385, 305, 285, 14, color=NAVY, bold=True)
d.bullets(["Obtener permisos personales", "Crear entorno Python moderno", "Copiar proyecto e instalar", "Ejecutar pruebas", "Iniciar API y túnel SSH"], 385, 270, 280, size=11.5, leading=18)
d.box(95, 56, 530, 55, fill=HexColor("#FCECE7"))
d.text("Estado actual: no desplegado. Solo se inspeccionó el servidor y se documentó el procedimiento.", 118, 87, 490, 11.5, color=CORAL, bold=True)
d.end()

# 20
d.page += 1
d.c.setStrokeColor(CYAN); d.c.setLineWidth(3); d.c.line(52, 326, 150, 326)
d.text("Un prototipo local funcional, con modelos aún en etapa de validación", 52, 290, 600, 25, color=NAVY, bold=True)
d.text("La infraestructura ya separa formatos, calidad técnica, privacidad, inferencia y experimentación.", 52, 220, 600, 16)
d.text("Demostración en vivo", 52, 153, 400, 20, color=BLUE, bold=True)
d.text("/health · visor web · original · rotación · ruido · Swagger", 52, 119, 550, 13, color=MUTED)
d.text("Preguntas", 52, 58, 250, 17, bold=True)
d.footer(); d.c.showPage()

d.save()
print(OUT)
