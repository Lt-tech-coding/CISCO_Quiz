from pathlib import Path
s=Path('index.html').read_text(encoding='utf8');a=s.index('<footer>');b=s.index('</footer>',a)+9;print(s[a:b])
