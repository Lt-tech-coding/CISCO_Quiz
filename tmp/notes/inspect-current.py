from pathlib import Path
import re
s=Path('index.html').read_text(encoding='utf8');a=s.index('<body>');b=s.index('<script>',a)
t=s[a:b];t=re.sub(r'data:image/[^\"]+','[image]',t);print(t.replace('><','>\n<'))
