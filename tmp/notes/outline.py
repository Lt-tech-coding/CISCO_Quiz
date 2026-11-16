import json,re
p=json.load(open('tmp/notes/pages.json',encoding='utf8'))
for ch in range(1,15):
 pages=[x for x in p if x['chapter']==ch]
 print('\nCHAPTER',ch, 'PAGES',len(pages))
 for x in pages:
  lines=x['text'].splitlines()
  clean=[l.strip() for l in lines if l.strip() and not re.search('©|Cisco|Networking Academy|All rights|Public',l)]
  print(x['page'], ' / '.join(clean[:2])[:150])
