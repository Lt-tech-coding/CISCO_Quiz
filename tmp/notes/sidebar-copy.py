from pathlib import Path
s=Path('index.html').read_text(encoding='utf8');a=s.index('<aside');b=s.index('<div class="side-card invoice-card">',a);print(s[a:b])
