import json,re
p=json.load(open('tmp/notes/pages.json',encoding='utf8'))
sel={(2,15),(2,16),(2,17),(3,33),(4,12),(4,14),(4,19),(8,14),(8,40),(8,43),(9,12),(11,150),(12,7),(13,46)}
for x in p:
 if (x['chapter'],x['page']) in sel: print('\nCH',x['chapter'],'PAGE',x['page'],'\n',x['text'])
