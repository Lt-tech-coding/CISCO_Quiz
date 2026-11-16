from pathlib import Path
import re
s=Path('index.html').read_text(encoding='utf8');a=s.index('<body>');b=s.index('<script>',a)
html=s[a:b]
html=re.sub(r'data:image/[^\"]+','[embedded image]',html)
html=re.sub(r'><','>\n<',html)
print(html)
