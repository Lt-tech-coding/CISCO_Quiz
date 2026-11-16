from pathlib import Path
p=Path('index.html');s=p.read_text(encoding='utf8')
s=s.replace('} else if (/ram|working memory|sodimm|so-dimm/.test(text)) {',r'} else if (/\bram\b|working memory|sodimm|so-dimm/.test(text)) {',1)
needle="    $('check').classList.toggle('hidden', s.mode === 'exam');"
assert needle in s
s=s.replace(needle,needle+"\n    $('check').textContent = revealed ? 'Answer checked' : 'Check answer';",1)
p.write_text(s,encoding='utf8')
