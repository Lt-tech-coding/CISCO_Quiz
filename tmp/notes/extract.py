import zipfile,json,re
from pathlib import Path
from pypdf import PdfReader
from io import BytesIO
pages=[]
with zipfile.ZipFile(r'C:\Users\south\Downloads\Archive.zip') as z:
 for chapter in range(1,15):
  name=f'ITE7_Chp{chapter}.pdf'
  reader=PdfReader(BytesIO(z.read(name)))
  for i,p in enumerate(reader.pages):
   pages.append({'chapter':chapter,'page':i+1,'text':p.extract_text() or ''})
  print(chapter,len(reader.pages),pages[-len(reader.pages)]['text'][:160].replace('\n',' '))
Path('tmp/notes/pages.json').write_text(json.dumps(pages,ensure_ascii=False),encoding='utf-8')
