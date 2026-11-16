import json,re,base64,collections,xml.etree.ElementTree as ET
from pathlib import Path
s=Path('index.html').read_text(encoding='utf8')
old=json.loads(Path('tmp/notes/questions.json').read_text(encoding='utf8'))
new=json.loads(Path('tmp/notes/expanded-questions.json').read_text(encoding='utf8'))
old_prompts={q['question'].strip().casefold() for q in old}
assert not any(q['question'].strip().casefold() in old_prompts for q in new)
assert collections.Counter(q['module'] for q in new)=={i:10 for i in range(1,15)}
for q in new:
 assert 0<=q['answer']<4 and len(set(q['options']))==4
 assert all(q['lesson'][k] for k in ['title','meaning','example','remember'])
images=json.loads(re.search(r'window\.ITE_SOURCE_IMAGES = (\{.*?\});\n</script>',s,re.S).group(1))
for image in images.values():
 decoded=base64.b64decode(image['dataUrl'].split(',',1)[1])
 assert decoded==Path(image['path']).read_bytes()
 assert image['author'] and image['licenseUrl'] and image['source']
 if image['path'].endswith('.svg'):ET.fromstring(decoded)
print('Verified: 140 new prompts, balanced module coverage, valid answer indexes, complete lessons, and six intact offline images with credits.')
