import json
p=json.load(open('tmp/notes/pages.json',encoding='utf8'))
sel={(1,11),(2,18),(3,34),(4,16),(6,16),(7,48),(8,41),(9,11),(9,20),(10,18),(11,130),(12,49),(13,79),(14,33)}
for x in p:
 if (x['chapter'],x['page']) in sel: print('\nCH',x['chapter'],'PDF PAGE',x['page'],'\n',x['text'])
