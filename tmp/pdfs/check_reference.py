from pathlib import Path
from PIL import Image,ImageOps,ImageDraw
import pdfplumber
root=Path(__file__).resolve().parents[2]
with pdfplumber.open(root/'output/pdf/presentacion_ipre_dicom_estandar_academico.pdf') as pdf:
    fonts=set();colors=set();outside=[]
    for i,p in enumerate(pdf.pages,1):
        for c in p.chars:
            fonts.add(c['fontname']);colors.add(str(c.get('non_stroking_color')))
            if c['x0']<0 or c['x1']>p.width or c['top']<0 or c['bottom']>p.height:outside.append((i,c['text']))
        print(i,p.extract_text().splitlines()[0])
    print('FONTS',fonts,'TEXT COLORS',colors,'OUTSIDE',outside)
files=sorted((root/'tmp/pdfs').glob('estandar-*.png'))
for start in range(0,len(files),4):
    sheet=Image.new('RGB',(2200,1278),'#cccccc')
    for j,path in enumerate(files[start:start+4]):
        im=Image.open(path).convert('RGB');im.thumbnail((1100,619))
        x=(j%2)*1100;y=(j//2)*639
        sheet.paste(im,(x,y+20));ImageDraw.Draw(sheet).text((x+10,y+3),f'Diapositiva {start+j+1}',fill='black')
    sheet.save(root/f'tmp/pdfs/review-{start//4+1:02}.png')
