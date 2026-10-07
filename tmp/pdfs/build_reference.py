"""PDF de investigación, adaptado al patrón expositivo de la referencia Beamer."""
from pathlib import Path
BASE=Path(__file__).with_name('build_academic.py')
exec(compile(BASE.read_text().split('OUT.parent.mkdir')[0],str(BASE),'exec'))
OUT=ROOT/'output/pdf/presentacion_ipre_dicom_estandar_academico.pdf'
URL='https://wandb.ai/pfayala-pontificia-universidad-cat-lica-de-chile/ipre-dicom-medmnist/runs/oliy37yu'

# Se mantienen cifras, imágenes y diagramas del informe, con nueva jerarquía.
for s in slides:
    if s['title']=='Resultados medidos del checkpoint de época 1':
        s['table'][4]=['Loss de train','No corresponde','No corresponde','0,2315 en train al terminar época 1.']
    if s['title']=='Herramientas de aprendizaje y experimentación':
        s['table'][5][2]='Integración y registro offline; métricas reales importadas y sincronizadas.'
    if s['diagram']=='wandb_status':
        s.update(title='W&B: evidencia disponible y alcance del registro',diagram=None,table=[
            ['Etapa','Qué ocurrió','Qué demuestra'],
            ['Entrenamiento original','W&B desactivado. Una época completa y detención en la segunda.','El modelo y las métricas existen localmente.'],
            ['Importación posterior','export_wandb_results.py leyó el JSON de métricas y creó un registro offline.','Resultados reales, sin repetir el entrenamiento.'],
            ['Sincronización web','Run oliy37yu sincronizado el 28 de septiembre de 2026.','Experimento disponible en la cuenta autenticada.'],
            ['Contenido publicado','Configuración, un punto de época 1, resumen de test y artefacto JSON.','Sin imágenes médicas ni checkpoint en esta importación.']
        ],source='scripts/export_wandb_results.py; salida confirmada de wandb sync: done.',takeaway='La importación conserva resultados existentes. No reconstruye épocas ni curvas que no se registraron.')

def make(title,definition,left,right,conclusion,source):
    return dict(title=title,definition=definition,columns=[left,right],takeaway=conclusion,source=source,diagram=None,table=None,paragraphs=[])

explanations={
'Problema y pregunta de investigación': (
 'Pregunta central','¿Cómo integrar lectura multiformato, revisión técnica y modelos de clasificación en una API que otro programa pueda utilizar?',
 ('Necesidad de ingeniería',['Interpretar archivos con tamaños y representaciones diferentes.','Separar lectura, análisis y modelos para poder probar cada componente.']),
 ('Pregunta experimental',['Entrenar un clasificador con imágenes etiquetadas y un protocolo explícito.','Comprobar su rendimiento en test y servir el checkpoint mediante HTTP.']),
 'El estudio presenta un prototipo de investigación. La utilidad clínica requiere una evaluación independiente.'),
'Qué es la API y qué recibe un usuario':(
 'Concepto','Una API expone operaciones de un programa. El cliente envía una solicitud HTTP y recibe datos estructurados, normalmente JSON.',
 ('Interacción del usuario',['El visor, Swagger o un script adjuntan una imagen.','POST /predict devuelve indicadores, privacidad y predicciones disponibles.']),
 ('Papel del aprendizaje',['Un script separado ajusta los pesos del modelo con imágenes etiquetadas.','La API carga esos pesos y predice. Una solicitud no vuelve a entrenar el modelo.']),
 'El navegador es un cliente del servicio. Otra aplicación puede consumir la misma API.'),
'Privacidad e informe de recomendaciones':(
 'Alcance','El sistema revisa metadata DICOM y genera un informe por reglas. La revisión de privacidad no garantiza anonimato completo.',
 ('Metadata DICOM',['La auditoría informa nombres y conteos de campos identificadores, sin devolver sus valores.','La copia seudonimizada vacía campos, retira tags privados y remapea UIDs con una clave.']),
 ('Píxeles e informe',['Los píxeles permanecen intactos. No hay OCR ni borrado de texto incrustado.','LangGraph organiza un nodo determinista de recomendaciones. No hay LLM ni agente autónomo.']),
 'Una alerta exige revisión humana. No se puede declarar que una imagen carece de información identificadora.'),
'Dataset del experimento: PneumoniaMNIST':(
 'Unidad de observación','Cada muestra contiene una radiografía en escala de grises y una etiqueta conocida: 0 = normal, 1 = neumonía.',
 ('Datos utilizados',['Archivo oficial local de 28 × 28 píxeles.','5.856 imágenes, distribuidas en entrenamiento, validación y test.','La etiqueta permite comparar una predicción con la respuesta conocida.']),
 ('Adecuación al proyecto',['Permite demostrar entrenamiento, evaluación e inferencia HTTP.','No contiene etiquetas de ruido, rotación, privacidad o edad.','Redimensionar a 64 × 64 no agrega detalle anatómico.']),
 'Este experimento valida un recorrido técnico con un dataset conocido, no todas las tareas iniciales.'),
'Separación de datos y prevención de fuga':(
 'Fuga de información','Ocurre cuando información de evaluación influye en el aprendizaje o la selección del modelo y hace que el resultado parezca mejor de lo que generaliza.',
 ('Protocolo utilizado',['Train actualiza pesos. Validación decide el checkpoint. Test evalúa el modelo elegido.','Se conservaron los splits oficiales de PneumoniaMNIST. No se realizó una auditoría propia por paciente del NPZ.']),
 ('Control y riesgo pendiente',['El entrenador general admite source_id para agrupar una imagen y sus variantes.','Test #0 también forma parte de la demo. Si sus resultados guían ajustes, se necesitará un nuevo test externo reservado.']),
 'Las copias de una misma imagen deben permanecer en la misma partición.'),
'Qué contiene el modelo y qué se guarda':(
 'Modelo','DenseNet121 transforma píxeles en características y produce una salida numérica. Los pesos son los parámetros internos que aprende a ajustar.',
 ('Representación y aprendizaje',['Las capas aprenden filtros a partir de ejemplos etiquetados.','Las conexiones densas reutilizan características anteriores.','La última salida, llamada logit, no está restringida al intervalo de 0 a 1.']),
 ('Salida y checkpoint',['Sigmoid convierte el logit en p(neumonía).','Con umbral 0,5 se obtiene la clase predicha.','El checkpoint guarda pesos y metadata para reconstruir la red sin entrenarla otra vez.']),
 'MONAI aporta la implementación de la arquitectura. DenseNet121 es el modelo concreto utilizado.'),
'Análisis crítico de los hallazgos':(
 'Criterio de interpretación','Un resultado funcional comprueba que el programa responde. Un resultado predictivo necesita etiquetas y un conjunto de evaluación apropiado.',
 ('Calidad técnica',['El ruido calculado aumentó a 0,0588 con la perturbación añadida.','La alerta de ruido en la original no puede llamarse falso positivo confirmado: no hay etiqueta de calidad adjudicada.']),
 ('Clasificación y límites',['El modelo de rotación falló en la copia girada 25°. Un caso no permite estimar sensibilidad global.','DenseNet de neumonía superó la referencia. El descenso entre validación y test exige cautela.']),
 'Las evidencias de calidad y neumonía corresponden a tareas distintas y no deben mezclarse.'),
'Del checkpoint a una predicción HTTP':(
 'Carga del modelo','Al iniciar el servidor, el registro lee models/medmnist_*.pt y reconstruye DenseNet121 con los pesos y la configuración guardados.',
 ('Solicitud y cálculo',['La ruta MedMNIST recibe PNG/JPEG, convierte a grises, redimensiona y normaliza.','El modelo calcula p(neumonía). La respuesta incluye p(normal) = 1 − p(neumonía).']),
 ('Evidencia de integración',['Test #0 tiene etiqueta 1, neumonía.','La petición devolvió HTTP 200 y p(neumonía) = 0,98005.','Una predicción individual no equivale a la accuracy de todo el test.']),
 'La prueba confirma carga e inferencia HTTP. La equivalencia exacta del preprocesamiento sigue pendiente.'),
'Verificación y amenazas a la validez':(
 'Dos niveles de evidencia','Las 27 pruebas de software verifican contratos y comportamiento del código. No constituyen una validación clínica del clasificador.',
 ('Limitaciones experimentales',['Una época completa y una semilla. Sin convergencia demostrada.','Sin intervalos de confianza, test externo ni comparación entre arquitecturas.','Procedencia de los modelos previos de calidad sin documentar.']),
 ('Limitaciones del sistema',['Entrenamiento y API usan filtros de redimensionado no idénticos.','La ruta técnica acepta raster sin verificar contenido torácico.','Vista previa limitada, sin navegación 3D ni OCR.']),
 'Los resultados sustentan un avance de ingeniería y aprendizaje inicial, con tareas de validación abiertas.'),
}

for s in slides:
    if s['title'] in explanations:
        label,definition,left,right,take=explanations[s['title']]
        s.update(definition=(label,definition),columns=[left,right],takeaway=take,paragraphs=[])

# W&B se explica después de los resultados a los que da trazabilidad.
wb=[s for s in slides if s['title'].startswith('W&B:')]
slides=[s for s in slides if not s['title'].startswith('W&B:')]
i=next(i for i,s in enumerate(slides) if s['diagram']=='epoch_timeline')+1
wb.append(make('W&B: cómo consultar el experimento publicado',
 ('Registro confirmado','Proyecto ipre-dicom-medmnist. Run oliy37yu: importación posterior de las métricas guardadas del checkpoint de época 1.'),
 ('Qué encontrará la audiencia',['Configuración: dataset, arquitectura, tamaños y número de muestras.','Historial: loss 0,2315, AUC de validación 0,9912 y F1 macro 0,9398 en época 1.']),
 ('Qué significa cada evidencia',['Resumen de test: accuracy 85,42%, F1 macro 0,8337, ROC-AUC 0,9478.','Artefacto de evaluación: JSON de métricas. Un punto no describe una curva de aprendizaje.']),
 'Abrir experimento en W&B (enlace clicable)',
 'Sincronización confirmada el 28-09-2026. La visualización puede requerir acceso a la cuenta o al proyecto.'))
slides[i:i]=wb
# Recuperar la tabla cuantitativa completa junto al gráfico de accuracy.
i=next(i for i,s in enumerate(slides) if s['diagram']=='comparison')+1
slides.insert(i,dict(title='Comparación de rendimiento en el mismo test',diagram=None,paragraphs=[],table=[
 ['Método','Accuracy','F1 macro','ROC-AUC'],
 ['Siempre predecir neumonía','62,50%','0,3846','0,5000'],
 ['DenseNet121, época 1','85,42%','0,8337','0,9478'],
 ['Mejora absoluta','22,92 puntos porcentuales','0,4491','0,4478']],
 source='624 imágenes. Referencia constante calculada y checkpoint local reevaluado.',
 takeaway='La red supera una regla basada en frecuencia. Esta tabla no compara DenseNet con ResNet u otras redes.'))

exec(compile((ROOT/'tmp/pdfs/module_details.py').read_text(),str(ROOT/'tmp/pdfs/module_details.py'),'exec'))

def fill(c,x,y,w,h,color):
    c.setFillColorRGB(*color);c.rect(x,y,w,h,stroke=0,fill=1);c.setFillColorRGB(0,0,0)

def panel(c,label,body,x,top,w,size=20):
    n=len(lines(body,w-22,size));h=37+n*size*1.24+14
    fill(c,x,top-h,w,h,(.955,.968,.972))
    fill(c,x,top-34,w,34,(.77,.88,.90))
    text(c,label,x+10,top-24,w-20,23)
    text(c,body,x+11,top-59,w-22,size)
    return top-h

def bullets(c,items,x,top,w,size=20,gap=12):
    y=top
    for item in items:
        p=c.beginPath();p.moveTo(x,y+6);p.lineTo(x+9,y+1);p.lineTo(x,y-4);p.close()
        c.setFillColorRGB(0,0,0);c.drawPath(p,fill=1,stroke=0)
        y=text(c,item,x+20,y,w-20,size)-gap
    return y

def base(c,title,index):
    # La referencia tiene bandas oscuras y letras blancas. Se aclaran las bandas
    # para mantener la restricción de la usuaria: Calibri y texto siempre negro.
    fill(c,0,481,960,59,(.78,.85,.91))
    text(c,title,20,502,920,28)
    text(c,f'{index} / {len(slides)}',880,12,73,10)

def table(c,s):
    rows=s['table'];n=len(rows[0])
    widths={2:[245,667],3:[222,345,345],4:[345,167,167,233],5:[180,114,129,144,345]}[n]
    size=16.5 if n<4 else 16
    hs=[max(len(lines(t,widths[j]-18,size,'CalibriBold' if ri==0 or j==0 else 'Calibri'))*size*1.24 for j,t in enumerate(row))+15 for ri,row in enumerate(rows)]
    total=sum(hs)
    assert total<(333 if s['takeaway'] else 380),(s['title'],total)
    y=445 if total>260 else 422
    c.setLineWidth(1);c.line(24,y+16,936,y+16)
    for ri,(row,h) in enumerate(zip(rows,hs)):
        x=24
        for j,t in enumerate(row):
            text(c,t,x+7,y,widths[j]-18,size,ri==0 or j==0);x+=widths[j]
        y-=h
        if ri==0:
            c.setLineWidth(.55);c.line(24,y+24,936,y+24)
    c.setLineWidth(1);c.line(24,y+12,936,y+12)

def cover(c):
    fill(c,15,286,930,132,(.78,.85,.91))
    text(c,'IPRE-DICOM',350,379,550,34,True)
    text(c,'API para análisis de imágenes médicas',197,338,730,29)
    text(c,'Arquitectura, metodología y evaluación experimental',176,309,760,24)
    text(c,'Avance de investigación',371,225,560,24)
    text(c,'Pía Ayala · Septiembre de 2026',324,185,540,22)
    text(c,'Prototipo local · Experimento con PneumoniaMNIST',239,131,710,20)

OUT.parent.mkdir(parents=True,exist_ok=True)
c=canvas.Canvas(str(OUT),pagesize=(453.543,255.118),initialFontName='Calibri')
c.setTitle('IPRE-DICOM: arquitectura, metodología y resultados')
c.setAuthor('Pía Ayala')
for index,s in enumerate(slides,1):
    c.saveState();c.scale(453.543/960,255.118/540)
    if index==1:
        cover(c);text(c,f'1 / {len(slides)}',880,12,70,10)
    else:
        base(c,s['title'],index)
        if s.get('columns'):
            module=s.get('module_detail')
            bottom=panel(c,*s['definition'],18,450,924,size=18 if module else 20)
            for j,(heading,items) in enumerate(s['columns']):
                x=26+j*478
                text(c,heading,x,bottom-(28 if module else 34),424,22,True)
                end=bullets(c,items,x+10,bottom-(55 if module else 67),420,18 if module else 19,9 if module else 12)
                assert end>90,(index,s['title'],end)
        elif s['diagram']:
            draw_diagram(c,s['diagram'])
        elif s['table']:
            table(c,s)
        else:
            ps=s['paragraphs']
            if s['title']=='Conclusiones del avance':
                y=437
                for i,p in enumerate(ps,1):
                    text(c,str(i)+'.',26,y,30,23,True)
                    y=text(c,p,64,y,857,21)-21
            elif s['title']=='Guion reproducible de demostración':
                y=438
                for p in ps:y=text(c,p,26,y,904,20)-16
            else:
                bottom=panel(c,'Procedimiento',ps[0],18,452,924)
                y=bullets(c,ps[1:],32,bottom-35,888,20)
                assert y>90,(index,s['title'],y)
        if s['takeaway']:
            fill(c,18,38,924,76,(.955,.968,.972))
            fill(c,18,88,924,26,(.77,.88,.90))
            text(c,'Interpretación',28,95,900,19)
            text(c,s['takeaway'],28,67,900,17)
        text(c,s['source'].replace('–','-'),24,20,825,9.5)
        if s['title']=='W&B: cómo consultar el experimento publicado':
            c.linkURL(URL,(24,42,935,100),relative=1,thickness=0)
    c.restoreState();c.showPage()
c.save()
print(OUT)
print(f'{len(slides)} diapositivas')
