from pathlib import Path
import re
s=Path('index.html').read_text(encoding='utf8')
print('Em dashes:',s.count(chr(0x2014)))
for m in list(re.finditer(chr(0x2014),s))[:12]:
 print(ascii(s[max(0,m.start()-65):m.start()+90]))
