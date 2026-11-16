import urllib.request,hashlib
from pathlib import Path
from urllib.parse import quote
name='RAID_1.svg'; h=hashlib.md5(name.encode()).hexdigest(); url=f'https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{quote(name)}'
req=urllib.request.Request(url,headers={'User-Agent':'ITEPracticeLab/1.0 (educational local study project)'})
with urllib.request.urlopen(req,timeout=20) as r: data=r.read()
Path('assets/diagrams/raid-1.svg').write_bytes(data)
print(len(data),url)
