# Guion oral de la presentación IPRE-DICOM

Corresponde a la presentación de 62 diapositivas `presentacion_ipre_dicom_estandar_academico.pdf`.

Tiempo orientativo: 30 a 40 minutos, incluyendo una demostración breve. Ajustar después de ensayar. Los textos entre comillas se pueden decir en voz alta. Las indicaciones entre corchetes son acciones para la expositora, no se leen.

No es necesario leer tablas o nombres de archivos completos. Señala el elemento al que te refieres y explica su función.

## Bloque 1. Problema, alcance y recorrido

### 1. IPRE-DICOM

“Buenos días. Voy a presentar el avance de IPRE-DICOM, un prototipo para recibir imágenes médicas, revisar características técnicas y ejecutar modelos de clasificación a través de una API. Explicaré qué construimos, cómo funciona y qué resultados obtuvimos. El sistema se ejecuta localmente y el experimento de entrenamiento utiliza PneumoniaMNIST. Es un avance de investigación, no una herramienta validada para diagnóstico clínico.”

### 2. Problema y pregunta de investigación

“El problema inicial es que las imágenes no llegan todas en el mismo formato ni con las mismas características. Antes de analizarlas necesitamos abrirlas, preparar sus píxeles y revisar posibles identificadores. La pregunta de ingeniería es cómo integrar esas operaciones en un servicio reutilizable. La pregunta experimental es si podemos entrenar un clasificador, evaluarlo y utilizarlo desde ese servicio.”

### 3. Objetivo inicial y alcance alcanzado

“El objetivo inicial era amplio: calidad, ruido, rotación, vista frontal o lateral y privacidad, entre otras tareas. Esta tabla distingue lo implementado de lo pendiente. Tenemos lectura multiformato, indicadores, revisión de metadata y un clasificador de normal o neumonía entrenado en este trabajo. Frontal o lateral tiene preparación de datos y código, pero no un entrenamiento demostrado. Edad y similitud siguen pendientes.”

### 4. Qué es la API y qué recibe un usuario

“Una API permite que un programa solicite una operación a otro. Aquí, un cliente envía una imagen y recibe una respuesta estructurada. JSON es el formato de texto que organiza esos resultados en campos. Es importante distinguir la API del modelo: el modelo aprende durante un entrenamiento separado. Después, la API utiliza lo aprendido para responder a nuevas solicitudes.”

### 5. Dos preguntas, dos rutas de análisis

“Tenemos dos rutas principales porque responden preguntas distintas. La ruta general analiza características técnicas, privacidad y modelos previos de ruido o rotación. La ruta MedMNIST ejecuta el clasificador normal o neumonía. Además, una tercera operación permite consultar una muestra del dataset. Mostrar una imagen y su etiqueta conocida no es lo mismo que pedir una predicción.”

### 6. Recorrido del proyecto: hitos y dependencias

[Señalar las etapas de arriba hacia abajo.]

“El recorrido comenzó definiendo las tareas y revisando la infraestructura disponible. Después construimos el servicio modular, incorporamos datos y preparamos ejemplos controlados. Finalmente ejecutamos un entrenamiento inicial, corregimos problemas y evaluamos el modelo guardado. Este orden permite conectar el problema con los resultados. Calfuco se inspeccionó, pero el sistema todavía no está desplegado allí.”

### 7. Etapas 1 y 2: necesidad e infraestructura

“Al revisar Calfuco encontramos recursos que podrían servir para entrenamientos posteriores. Sin embargo, aparecieron restricciones de permisos y un entorno que requería preparación. Por eso el avance experimental se realizó en el computador local. La existencia de GPU en Calfuco no significa que las hayamos utilizado: los resultados que presento corresponden a la ejecución local documentada.”

### 8. Etapas 3 y 4: implementar y preparar datos

“La implementación separó las tareas en lectores, indicadores, privacidad y modelos. Incorporamos PneumoniaMNIST para disponer de imágenes con etiquetas y particiones conocidas. Para probar el análisis técnico también preparamos una imagen original y dos variantes: una girada y otra con ruido. Esas variantes permiten observar respuestas ante cambios controlados, pero no son pacientes independientes.”

### 9. Etapas 5 y 6: entrenar, corregir y evaluar

“La primera ejecución reveló problemas concretos. Ajustamos la carga de datos para evitar procesos auxiliares incompatibles con el entorno. También redimensionamos las imágenes porque la arquitectura no procesaba correctamente la entrada de 28 por 28. Completamos una época y detuvimos la segunda. En la integración corregimos además la correspondencia entre la salida positiva y la etiqueta neumonía.”

**Transición:** “Con ese recorrido en mente, ahora voy a mostrar cómo se organiza el programa y qué hace cada parte.”

## Bloque 2. Arquitectura y módulos

### 10. UML de componentes

[Señalar cliente, API, servicios y registro de modelos.]

“Este diagrama representa responsabilidades. El cliente puede ser el visor, Swagger o un script. La API recibe su solicitud y utiliza los servicios de lectura, análisis y modelos. El entrenador es un programa separado: produce el archivo de pesos que después carga la API. No se ejecuta un entrenamiento cada vez que alguien sube una imagen.”

### 11. UML de secuencia: análisis técnico

[Recorrer el diagrama de arriba hacia abajo.]

“Aquí se muestra el orden de una solicitud. El cliente envía el archivo. La API solicita su lectura, obtiene una representación de la imagen y calcula indicadores y privacidad. Cuando la entrada corresponde a los formatos habilitados, ejecuta los modelos disponibles. Finalmente reúne las respuestas y devuelve un informe. Las flechas discontinuas representan los resultados que regresan entre componentes.”

### 12. UML de secuencia: modelo de neumonía

“Esta secuencia corresponde a la clasificación experimental. Primero se prepara la imagen: escala de grises, tamaño y normalización. Luego DenseNet121 aplica los pesos que ya estaban cargados. La respuesta contiene los valores asociados a normal y neumonía. Durante esta operación los parámetros no cambian. Ese uso de un modelo ya entrenado se llama inferencia.”

### 13. Responsabilidad de cada módulo

“Esta tabla es el mapa general de los archivos. Algunos coordinan solicitudes, otros transforman imágenes y otros calculan resultados. Los scripts de entrenamiento están fuera del servidor HTTP. A continuación voy a explicar cada módulo según lo que recibe, cómo trabaja y qué entrega. Esto permite identificar con precisión dónde hay aprendizaje automático y dónde solo hay fórmulas o reglas.”

### 14. main.py: entrada y coordinación del servicio

“main.py es el punto de entrada del backend. Define las rutas y coordina las funciones. Por ejemplo, en el análisis general comprueba que el archivo no esté vacío ni supere el límite establecido, identifica su formato y llama al lector adecuado. Usa FastAPI para organizar las operaciones. Cuando el servidor arranca, también carga los modelos disponibles y permite consultar su estado.”

### 15. Visor HTML

“El visor es la parte que utiliza una persona desde el navegador. HTML organiza la pantalla, CSS define su apariencia y JavaScript envía las solicitudes. Al pulsar Analizar se llama a la ruta técnica general. El navegador muestra la respuesta, pero no ejecuta las redes neuronales. Además, el explorador MedMNIST muestra ejemplos del dataset: no activa automáticamente el clasificador de neumonía.”

### 16. image_io.py: lectura multiformato

“Este módulo convierte diferentes archivos en una imagen común que los otros componentes puedan procesar. Pillow abre imágenes como PNG o JPEG. NumPy lee arreglos numéricos y NiBabel permite leer NIfTI. Cuando la entrada tiene más de dos dimensiones, se seleccionan cortes centrales hasta obtener una imagen 2D. Por tanto, el análisis actual no representa todo un volumen tridimensional.”

### 17. Lector DICOM

“DICOM requiere una lectura específica porque combina píxeles y atributos del estudio. El lector está dentro de main.py y utiliza pydicom. Obtiene los píxeles y aplica ajustes de intensidad descritos en el archivo, como escala y ventana. También contempla la inversión de tonos. Luego entrega la imagen y un resumen de metadata. Son operaciones de preparación, no decisiones aprendidas por una red.”

### 18. quality.py

“quality.py calcula indicadores mediante fórmulas. El brillo es el promedio de intensidad y el contraste describe su dispersión. Para estimar ruido compara la imagen con una copia suavizada. Para estimar nitidez analiza diferencias entre píxeles vecinos. Utiliza Pillow y NumPy. Estos valores ayudan a describir y comparar imágenes, pero no existe aquí un umbral clínico validado para declararlas buenas o malas.”

### 19. privacy.py

“privacy.py busca campos identificadores conocidos, como nombre o identificador del paciente. Informa qué campos están presentes, sin devolver sus valores. También consulta el atributo que declara texto incrustado en la imagen. Pero no inspecciona visualmente los píxeles ni ejecuta OCR. Por eso una comprobación favorable de metadata no permite garantizar que el archivo sea completamente anónimo.”

### 20. anonymize.py

“Este módulo tiene otra responsabilidad: modificar una copia del DICOM. Vacía campos conocidos, elimina tags privados y remapea determinados identificadores usando una clave. No modifica el archivo original que se encuentra en disco ni los píxeles de la copia. La exportación exige condiciones previas. Se presenta como un perfil experimental de seudonimización, no como un proceso completo certificado para compartir información clínica.”

### 21. medmnist_service.py

“Este servicio administra los datos. Recibe el nombre del dataset, la partición, la resolución y el índice de una muestra. Busca el archivo local y extrae la imagen y su etiqueta mediante la biblioteca MedMNIST. El archivo utilizado está en data/medmnist y se llama pneumoniamnist.npz. El catálogo también contempla ChestMNIST, pero eso no significa que hayamos entrenado con ambos.”

### 22. medmnist_models.py

“Este módulo administra el modelo, no el dataset. Lee el checkpoint, reconstruye DenseNet121 con MONAI y carga los pesos usando PyTorch. Prepara una imagen nueva y realiza el cálculo sin actualizar parámetros. La función sigmoid transforma la salida en un valor asociado a neumonía y también se devuelve su complemento para normal. El resultado es experimental, no una certeza clínica.”

### 23. agent_workflow.py

“El informe técnico utiliza reglas explícitas. Por ejemplo, una salida de ruido o rotación sobre el umbral genera una recomendación de revisión. Si aparecen identificadores, recomienda desidentificarlos. LangGraph, cuando está instalado, organiza estas reglas en un único nodo. No hay un modelo de lenguaje razonando sobre la imagen. Recomendar OCR tampoco significa que el programa lo esté ejecutando.”

### 24. train_medmnist.py

“Este es el programa que realmente entrena el clasificador experimental. Carga imágenes y etiquetas, las organiza en lotes y calcula una predicción. Compara esa salida con la respuesta conocida y ajusta los parámetros para reducir el error. Evalúa en validación y guarda un checkpoint cuando mejora el AUC. Al terminar normalmente, evalúa el mejor modelo en test y registra los resultados.”

### 25. train.py

“El entrenador general sirve para preparar tareas de ruido, rotación o vista frontal y lateral a partir de un CSV de rutas y etiquetas. Si hay identificadores de origen, mantiene juntas las variantes de una misma fuente al separar los datos. Tener este código disponible no demuestra el entrenamiento original de los pesos previos. Su procedencia sigue siendo una limitación que debemos documentar.”

### 26. export_wandb_results.py

“Este archivo no entrena modelos. Lee el JSON de resultados que ya existía y lo registra en W&B. Conserva un punto de la primera época y las métricas de test. Después sincronizamos ese registro con la cuenta autenticada. En esta importación se publicaron métricas y configuración, no imágenes médicas ni el checkpoint del modelo. Es una importación posterior, no seguimiento en vivo.”

### 27. Herramientas del servicio

“Esta tabla resume cómo se complementan las herramientas del backend. Python contiene la lógica. FastAPI define las operaciones y Uvicorn mantiene el servidor. Pillow, NumPy y pydicom permiten trabajar con imágenes y sus datos. Ninguna de estas herramientas, por el solo hecho de estar instalada, convierte una operación en inteligencia artificial: depende de la función que implementamos con ella.”

### 28. Herramientas de aprendizaje y experimentación

“En aprendizaje, PyTorch ejecuta el cálculo y la optimización. MONAI aporta la arquitectura DenseNet121 utilizada. MedMNIST aporta los datos y scikit-learn ayuda a evaluar. W&B conserva el registro experimental. LangGraph organiza el informe por reglas. Es importante no intercambiar estos papeles: MONAI no es el dataset, W&B no entrena por nosotros y LangGraph no clasifica estas radiografías.”

### 29. Funcionamiento de POST /predict

“Si juntamos los módulos, esta es la operación completa del análisis técnico: recibir el archivo, leerlo, calcular indicadores, revisar privacidad y ejecutar modelos cuando corresponda. Luego se genera el informe y se devuelve JSON. La regla actual acepta raster para los clasificadores generales sin comprobar que el contenido sea realmente una radiografía de tórax. Ese control semántico está pendiente.”

### 30. Lectura y visualización: capacidades y límites

“El backend admite varias familias de archivos, pero leer un formato no significa ofrecer todas sus funciones de visualización. DICOM multiframe se reduce al primer frame y los volúmenes a cortes 2D. El navegador tiene además sus propias limitaciones de vista previa. Finalmente, un NPZ representa un dataset empaquetado, por eso se consulta con rutas dedicadas y no se sube como imagen individual.”

### 31. Medidas de calidad

“Esta tabla permite interpretar los valores del análisis técnico. Brillo, contraste, ruido y nitidez son descriptores de los píxeles. Por ejemplo, un cambio del indicador de ruido puede ayudar a comparar una imagen con su versión alterada. No debe confundirse con la probabilidad que devuelve el modelo de ruido. Tampoco un valor cero demuestra ausencia de ruido.”

### 32. Privacidad e informe

“La revisión de privacidad y el informe acompañan al análisis, pero tienen límites explícitos. Se pueden detectar campos conocidos y generar una copia con metadata seudonimizada. Sin embargo, los píxeles permanecen intactos. Si contienen un nombre impreso, este sistema no lo borra automáticamente. Por eso la revisión humana y una desidentificación formal siguen siendo necesarias antes de compartir datos clínicos.”

**Transición:** “Hasta aquí expliqué el sistema. Ahora voy a separar esa implementación del experimento de aprendizaje que efectivamente realizamos.”

## Bloque 3. Datos, entrenamiento y evaluación

### 33. Dataset del experimento

“El dataset utilizado fue PneumoniaMNIST, dentro de la colección MedMNIST. Contiene 5.856 imágenes con etiquetas normal o neumonía. Trabajamos con el archivo de 28 por 28 píxeles y conservamos sus particiones oficiales. Estas etiquetas permiten entrenar esa clasificación concreta. No permiten concluir que el modelo haya aprendido ruido, rotación, edad o privacidad, porque son tareas distintas.”

### 34. Una muestra y su etiqueta

[Señalar primero la imagen y después la etiqueta.]

“Cada ejemplo tiene dos partes: los píxeles que observa el modelo y la etiqueta que usamos como respuesta conocida. En entrenamiento la etiqueta permite calcular el error. En evaluación permite comprobar si la predicción coincide. Las etiquetas que aparecen aquí provienen del dataset. No estoy realizando una interpretación médica de estas imágenes durante la presentación.”

### 35. Tres grupos de imágenes

“Dividimos las funciones de los datos en aprender, revisar y examinar. Las 4.708 imágenes de entrenamiento permiten ajustar parámetros. Las 524 de validación permiten revisar el modelo y seleccionar el checkpoint. Las 624 de test se utilizan para evaluar el modelo elegido. En validación y test no se actualizan sus pesos. Los porcentajes corresponden a las particiones oficiales que mantuvimos.”

### 36. Distribución de clases

“Las clases no están equilibradas. En test hay 234 imágenes normales y 390 con etiqueta neumonía. Eso significa que un sistema que responda siempre neumonía acertaría el 62,5%, aunque no analizara la imagen. Por esta razón necesitamos comparar contra esa referencia y observar los errores por clase. Un porcentaje de aciertos aislado puede resultar engañoso.”

### 37. Prevención de fuga de información

“Una evaluación puede parecer demasiado buena si información de las imágenes de prueba influye en el entrenamiento. Por ejemplo, no conviene entrenar con una imagen y evaluar con una copia de esa misma imagen que solo está girada. El entrenador general permite agrupar variantes por origen. En PneumoniaMNIST mantuvimos los splits oficiales, pero no hicimos una auditoría propia de separación por paciente.”

### 38. Modelo y checkpoint

“DenseNet121 es la arquitectura de red utilizada. Sus capas transforman los píxeles en características numéricas y una salida final. Los pesos son los números internos que cambian durante el aprendizaje. Un checkpoint guarda esos números y la configuración necesaria para reconstruir el modelo. Así podemos cerrar el entrenamiento y usar después el modelo desde la API, sin comenzar nuevamente.”

### 39. Cómo aprende DenseNet121

[Recorrer los pasos del esquema.]

“El proceso se repite por lotes. Primero entran las imágenes y se calcula una salida. Después una función de pérdida compara esa salida con las etiquetas. La retropropagación calcula cómo influyen los parámetros en el error y Adam los actualiza. Al recorrer todo entrenamiento completamos una época. Luego evaluamos en validación, sin actualizar pesos, para decidir si guardamos un nuevo checkpoint.”

### 40. Entrenamiento e inferencia

“La parte superior muestra el aprendizaje: datos etiquetados, ajuste de parámetros y archivo guardado. La inferior muestra la inferencia: una imagen nueva pasa por la API y recibe una predicción usando pesos fijos. El archivo del modelo conecta ambos momentos. Por eso subir cien imágenes a la API no equivale a entrenarla con cien ejemplos nuevos.”

### 41. Configuración de la corrida

“La corrida utilizó DenseNet121 sin solicitar pesos preentrenados, lotes de 64 y Adam con tasa inicial de aprendizaje de 0,0001. La entrada de 28 por 28 se redimensionó a 64 por 64. Configuramos cinco épocas, pero la ejecución local completó una y se detuvo durante la segunda. Todas las métricas que presentaré corresponden al checkpoint guardado de la primera.”

### 42. Interpretación de métricas

“Accuracy es la proporción total de aciertos. F1 combina precisión y sensibilidad, y su versión macro da el mismo peso a cada clase. ROC-AUC evalúa la capacidad de ordenar positivos por encima de negativos. Loss es el error utilizado al entrenar, no un porcentaje de fallos. No calculamos correlación. Tampoco una probabilidad individual es equivalente al rendimiento global del modelo.”

### 43. Resultados medidos

“En test obtuvimos accuracy de 85,42%, F1 macro de 0,8337 y ROC-AUC de 0,9478. Accuracy corresponde a 533 respuestas correctas de 624. Los resultados de validación fueron superiores a los de test. Esto muestra por qué no debemos comunicar solo la mejor cifra de validación. La diferencia exige análisis adicional, pero por sí sola no demuestra una causa específica.”

### 44. Qué se completó realmente

“Este esquema separa el plan de la ejecución. Se planificaron cinco épocas, pero solo tenemos una época completa documentada. La segunda se interrumpió y no utilizamos sus pesos parciales para esta evaluación. Por eso no presento una curva de cinco puntos ni afirmo que el modelo haya convergido. El resultado sirve como experimento inicial e integración funcional.”

## Bloque 4. Registro experimental y hallazgos

### 45. W&B en el experimento

“W&B es una bitácora. El entrenamiento lo ejecuta PyTorch, mientras W&B puede recibir configuración, métricas y artefactos. Un artefacto es un archivo asociado al experimento, por ejemplo un modelo o un JSON de resultados. Este registro ayuda a comparar ejecuciones. W&B no interviene cuando la API clasifica una imagen y no es necesario abrirlo para que la API funcione.”

### 46. Código de W&B en los entrenadores

“En los entrenadores incorporamos cuatro momentos de registro: crear la ejecución, registrar cada época, guardar las métricas finales y adjuntar el checkpoint. Esas operaciones solo se activan si habilitamos W&B. Como el artefacto del modelo se adjunta al final, una interrupción puede impedir ese último paso. Por eso es importante distinguir las capacidades del código de la evidencia de una ejecución concreta.”

### 47. Evidencia disponible en W&B

“En nuestra corrida original W&B estaba desactivado. Después importamos las métricas que habíamos conservado y sincronizamos el registro con la cuenta. Lo que existe online es esa importación posterior: un punto de la primera época, configuración y resultados de test. No se subieron imágenes ni el modelo en esta importación. Tampoco se reconstruyeron datos de épocas que no completamos.”

### 48. Consulta del experimento publicado

[Opcional: abrir el enlace de la diapositiva. Si ya se está haciendo la demo al final, dejarlo para ese momento.]

“Este enlace permite consultar el registro real. En la configuración se identifica el dataset y el tamaño de entrada. El historial conserva un punto y el resumen contiene las métricas de test. El artefacto adjunto es un JSON de resultados. La utilidad aquí es hacer visible la evidencia que respalda las cifras de la presentación, sin confundirla con un entrenamiento nuevo.”

### 49. Matriz de confusión

[Señalar filas como etiquetas reales y columnas como predicciones.]

“Esta matriz explica dónde se equivoca el modelo. Reconoció 157 imágenes normales y 376 con etiqueta neumonía. Clasificó 77 normales como neumonía y 14 neumonías como normales. Por tanto, el rendimiento no es igual en ambas clases: detectó alrededor del 96,4% de las neumonías, pero reconoció solo el 67,1% de los normales. La accuracy global no muestra por sí sola esa diferencia.”

### 50. Comparación con una regla trivial

“La referencia responde siempre neumonía y acierta el 62,5% por la distribución del test. DenseNet alcanza el 85,42%, una mejora de 22,92 puntos porcentuales. Esto demuestra que supera esa regla sencilla en este conjunto. No demuestra que sea la mejor arquitectura, porque todavía no ejecutamos una comparación equivalente con otras redes.”

### 51. Tabla comparativa de rendimiento

“La comparación completa incluye accuracy, F1 macro y ROC-AUC sobre el mismo test. El modelo supera la referencia en las tres medidas. Usar el mismo conjunto evita que la diferencia se deba simplemente a evaluar imágenes distintas. Aun así, esta tabla compara una red con una regla constante, no DenseNet con ResNet ni un conjunto de modelos entrenados.”

### 52. Comparación de componentes y modelos

“Esta tabla distingue el nivel de evidencia de cada componente. Para PneumoniaMNIST tenemos una corrida inicial y resultados de test. Para ruido y rotación tenemos pesos previos que cargan y responden, pero no su entrenamiento original documentado. Para frontal o lateral hay preparación. ResNet, CLIP, DINO y otras alternativas fueron propuestas, pero todavía no tienen resultados comparativos en este proyecto.”

### 53. Prueba técnica de ruido y rotación

“Aquí cambiamos de tarea: ya no evaluamos neumonía. Analizamos la misma fuente original, girada y con ruido añadido. La fórmula de ruido aumentó con la perturbación. Sin embargo, el clasificador de rotación no superó el umbral en la copia girada 25 grados. Son observaciones de una prueba controlada, no métricas de rendimiento sobre una población de imágenes.”

### 54. Misma imagen, tres condiciones

[Señalar original, giro y ruido.]

“Las imágenes permiten entender visualmente la prueba anterior. Sabemos qué transformación aplicamos y podemos contrastarla con la respuesta del programa. No son tres pacientes distintos y no deben contarse como evidencia independiente. Este ensayo sirve para descubrir fallos concretos y orientar pruebas posteriores con más ejemplos y etiquetas revisadas.”

### 55. Análisis crítico

“Los hallazgos combinan avances y límites. La fórmula respondió al ruido añadido. El modelo de rotación falló en el ejemplo sintético. La alerta de ruido sobre la original resulta inesperada, pero no tenemos una etiqueta de calidad adjudicada para llamarla falso positivo confirmado. Por separado, el clasificador de neumonía superó su referencia. Cada conclusión debe mantenerse dentro de la tarea y los datos que la respaldan.”

### 56. Del checkpoint a HTTP

“Además de medir el modelo, comprobamos su integración con el servicio. La API reconstruyó la red y respondió correctamente a una solicitud sobre la muestra cero del test. La ejecución documentada devolvió aproximadamente 0,98 para neumonía. Esa es la salida para una imagen, no una precisión del 98% del sistema. La preparación exacta de la entrada puede influir en ese valor.”

**Transición:** “Ahora voy a mostrar el flujo funcionando. Separaré el análisis técnico de la clasificación experimental para que se vea qué hace cada ruta.”

## Bloque 5. Demostración, limitaciones y cierre

### 57. Qué muestra la demostración

“La demostración comprobará varias partes. Primero veremos que el servidor está activo y que cargó los modelos. Después analizaremos imágenes en el visor. Luego mostraremos una muestra del dataset y ejecutaremos el clasificador desde Swagger, que es la interfaz para probar las rutas de la API. Finalmente podremos contrastar el resultado individual con las métricas del experimento en W&B.”

### 58. Guion reproducible de demostración

[Cambiar al navegador. Seguir el libreto de demo incluido más abajo. Mantener el servidor iniciado antes de comenzar a exponer.]

“La API está funcionando en mi computador. No voy a entrenar durante la demo: utilizaré los archivos de modelo ya guardados. Los comandos de esta diapositiva permiten repetir el proceso. Si falla la interfaz, también contamos con un script que ejecuta las peticiones internamente y produce un reporte.”

### 59. Verificación y amenazas a la validez

[Volver a la presentación.]

“La demo comprueba integración, pero no resuelve todas las preguntas experimentales. Las pruebas automatizadas verifican comportamiento del software, no calidad clínica. Solo tenemos una época completa y una semilla. Además, encontramos una diferencia entre el filtro de redimensionado del entrenamiento y el de la API. Debemos unificarlos y comprobar equivalencia antes de afirmar que ambos recorridos son numéricamente idénticos.”

### 60. Roadmap siguiente

“El siguiente paso es cerrar esas diferencias de preprocesamiento y registrar un historial completo. Después podremos comparar arquitecturas bajo el mismo protocolo y varias semillas. Para calidad y vista necesitamos etiquetas adecuadas y evaluación independiente. Finalmente, el despliegue en Calfuco exige resolver permisos y entorno. Cada hito debe terminar en una evidencia verificable, no solo en código preparado.”

### 61. Conclusiones

“El avance produjo una API modular y un ciclo inicial de aprendizaje integrado. Entrenamos un clasificador con PneumoniaMNIST, conservamos su checkpoint, lo evaluamos sobre 624 imágenes y lo utilizamos desde una ruta HTTP. La accuracy fue 85,42%, superior a la referencia constante. También identificamos límites concretos. La contribución actual es un prototipo experimental comprobable, con una ruta clara para ampliar y validar sus capacidades.”

### 62. Trazabilidad y cierre

“Esta última diapositiva indica dónde revisar el código, los datos del experimento y los resultados. Las cifras presentadas corresponden al checkpoint local evaluado, no a resultados de otros estudios. Como cierre, distingo tres cosas: lo implementado en software, lo medido experimentalmente y lo que sigue pendiente. Muchas gracias. Quedo atenta a sus preguntas.”

## Libreto de la demo en vivo

Usar entre las diapositivas 58 y 59. Duración orientativa: 4 a 6 minutos. Evitar leer JSON completo y esperar a que termine cada petición.

### A. Estado del servicio

[Abrir http://127.0.0.1:8000/health.]

“Aquí aparece el estado del servicio. En la lista puedo comprobar qué modelos están cargados. Esto diferencia que el servidor esté disponible de que tenga un modelo específico listo para responder.”

[Señalar `models` y `medmnist_models`. No afirmar CPU si el dispositivo mostrado es otro.]

### B. Análisis técnico

[Abrir http://127.0.0.1:8000. Cargar `demo_assets/01_original_medmnist.png` y pulsar Analizar.]

“Estoy enviando una imagen a la ruta de análisis técnico. La respuesta incluye medidas calculadas y salidas de los modelos disponibles. Por ejemplo, el indicador numérico de ruido y la probabilidad del modelo de ruido provienen de mecanismos diferentes.”

[Cargar `03_ruidosa.png` y comparar. Opcionalmente mostrar `02_rotada_25_grados.png`.]

“Esta es la misma fuente con ruido añadido. Comparo las respuestas antes y después de la transformación. Si el modelo no detecta correctamente una alteración, lo presento como una limitación observada, no como un fallo que deba ocultarse.”

### C. Dataset

[En el explorador elegir `pneumoniamnist`, `test`, tamaño `28`, índice `0`.]

“Esta operación consulta el dataset instalado en el computador. Muestra una imagen y la etiqueta que ya viene con ella. Todavía no estoy solicitando una predicción. Mantengo la resolución 28 porque es la versión instalada que utilizamos.”

### D. Clasificador normal/neumonía

[Abrir http://127.0.0.1:8000/docs. Expandir POST /predict/medmnist/{flag}. Try it out. Escribir `pneumoniamnist`, adjuntar `01_original_medmnist.png` y pulsar Execute.]

“Ahora ejecuto otra ruta, la del clasificador experimental. El backend prepara la imagen y aplica el checkpoint entrenado. El código 200 indica que la solicitud terminó correctamente. Estos valores representan la salida del modelo para este archivo. No son la accuracy del experimento ni constituyen un diagnóstico.”

[Leer los valores realmente mostrados. No prometer el valor exacto de la prueba anterior: el archivo ampliado de demo no tiene por qué dar idéntica salida al PNG nativo extraído del dataset.]

### E. W&B

[Abrir https://wandb.ai/pfayala-pontificia-universidad-cat-lica-de-chile/ipre-dicom-medmnist/runs/oliy37yu.]

“Este panel permite consultar las métricas del experimento. A diferencia de la petición anterior, el resumen de test agrupa 624 imágenes. El registro se importó después del entrenamiento. Hay un punto de época 1, no una curva completa de cinco épocas.”

### Si falla alguna pantalla

“La interfaz no está respondiendo en este momento. Voy a distinguir ese problema de ejecución de los resultados ya documentados. Disponemos de un script de prueba y de un reporte local para revisar las respuestas.”

[No decir que una prueba en vivo funcionó si no terminó. Si se muestra un reporte previo, identificarlo explícitamente como una ejecución anterior.]

## Respuestas breves a preguntas previsibles

**¿Entrenaste la API?**

“Entrenamos un modelo que la API utiliza. La API coordina solicitudes y operaciones. El entrenamiento es un programa separado.”

**¿Qué clasifica el modelo que entrenaste?**

“Normal y neumonía según las etiquetas de PneumoniaMNIST. No aprendió ruido, edad ni privacidad a partir de esas etiquetas.”

**¿De dónde salieron las etiquetas?**

“Del dataset utilizado. No las generamos nosotros ni las produjo W&B.”

**¿Por qué usaste MONAI?**

“En esta implementación aporta DenseNet121 y herramientas de procesamiento. Es la biblioteca que usamos para construir la red, no una evidencia de que esta arquitectura sea la mejor. Eso requiere comparación.”

**¿El 85,42% significa que puede usarse clínicamente?**

“No. Describe los aciertos en este test concreto. Falta evaluación externa, análisis más amplio y validación adecuada al uso previsto.”

**¿Por qué solo una época?**

“Se configuraron cinco, pero la corrida local se detuvo durante la segunda. Lo que puedo respaldar es el checkpoint de la primera. No atribuyo a esa detención una causa experimental que no quedó documentada.”

**¿Completaste una comparación de modelos?**

“Comparamos DenseNet con una referencia que siempre predice neumonía. Todavía no ejecutamos una comparación controlada entre distintas arquitecturas.”

**¿W&B entrenó o almacenó las imágenes?**

“No en este flujo. Registró configuración y resultados. La importación sincronizada contiene métricas y un JSON, no imágenes médicas ni el checkpoint.”

**¿Qué inteligencia tiene el agente?**

“Actualmente aplica reglas predefinidas dentro de un flujo de un nodo. No usa un modelo de lenguaje ni decide autónomamente qué herramientas ejecutar.”

**¿Está funcionando en Calfuco?**

“No. Se inspeccionaron sus recursos, pero el entrenamiento presentado y la demo corresponden al entorno local.”

## Recordatorio de términos antes de ensayar

- **API:** interfaz para solicitar operaciones a un programa.
- **Endpoint o ruta:** dirección de una operación concreta dentro de la API.
- **Metadata:** datos que describen el archivo o estudio, distintos de los píxeles.
- **Dataset:** colección de ejemplos. Un `Dataset` de pydicom, en cambio, es el objeto que representa un archivo DICOM.
- **Etiqueta:** respuesta conocida asociada a una muestra.
- **Tensor:** arreglo de números con el que opera la red.
- **Pesos:** parámetros numéricos que se ajustan durante el entrenamiento.
- **Checkpoint:** archivo que guarda los parámetros y, según el formato, su configuración.
- **Época:** recorrido completo del conjunto de entrenamiento.
- **Inferencia:** aplicar un modelo con parámetros fijos.
- **OCR:** reconocimiento de texto dentro de una imagen. Se recomienda revisión, pero aquí no se ejecuta OCR.
- **W&B:** se puede nombrar “Weights and Biases” o “la bitácora de experimentos”.

## Frases que conviene evitar

| Evitar | Decir en su lugar |
|---|---|
| “La API aprende cada vez que subimos una imagen”. | “La API aplica un modelo entrenado previamente”. |
| “Entrenamos cinco épocas”. | “Planificamos cinco y completamos una”. |
| “Probamos varios datasets y varias redes”. | “El experimento documentado usa PneumoniaMNIST y DenseNet121”. |
| “Anonimizamos completamente cualquier imagen”. | “Auditamos metadata y generamos una copia seudonimizada bajo condiciones limitadas”. |
| “El agente diagnostica y ejecuta OCR”. | “El flujo aplica reglas y recomienda revisión, sin diagnóstico ni OCR”. |
| “El 98% de esta imagen es la precisión del sistema”. | “Es una salida individual. La accuracy del test se calcula sobre las 624 imágenes”. |
| “La demo demuestra que el modelo funciona para todos los casos”. | “La demo comprueba integración y muestra respuestas en ejemplos concretos”. |
