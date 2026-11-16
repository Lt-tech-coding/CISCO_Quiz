from pypdf import PdfReader
from pathlib import Path
base=Path(r'C:\Users\south\OneDrive\Documents\Rosebank College\Year 3\Semester 6\ISST7322\notes')
for i in range(1,7):
 p=base/f'ISST LEARNING UNIT {i}.pdf'
 r=PdfReader(p)
 print('\nUNIT',i,'PAGES',len(r.pages))
 for n in range(min(3,len(r.pages))):
  print('PAGE',n+1,(r.pages[n].extract_text() or '')[:5000])
