import json,re
pages=json.load(open('tmp/notes/pages.json',encoding='utf8'))
for ch in [7,8,9,10,11]:
 print('\nCHAPTER',ch)
 for x in pages:
  if x['chapter']!=ch: continue
  ls=[l.strip() for l in x['text'].splitlines() if l.strip() and not re.search('©|Cisco|Networking Academy|All rights|Public',l)]
  if len(ls)>2: print(x['page'],' / '.join(ls[:2])[:125])
