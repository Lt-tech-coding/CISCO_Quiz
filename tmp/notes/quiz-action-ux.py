from pathlib import Path
p=Path('index.html');s=p.read_text(encoding='utf8')
s=s.replace('class="btn danger" id="finish"','class="btn secondary" id="finish"',1)
s=s.replace("    $('next').classList.toggle('secondary', s.mode !== 'exam');", "    $('next').classList.toggle('secondary', s.mode !== 'exam' && !revealed);",1)
needle="    $('finish').textContent = idx === s.questions.length - 1 ? 'Submit & see results' : 'Submit quiz';"
assert needle in s
s=s.replace(needle,needle+"\n    $('finish').classList.toggle('secondary', !(idx === s.questions.length - 1 && (s.mode === 'exam' || revealed)));\n    $('flag').setAttribute('aria-pressed', String(!!s.flags[idx]));",1)
needle="  document.addEventListener('visibilitychange', updateTimer);"
assert needle in s
s=s.replace(needle,needle+"\n  document.addEventListener('click', event => {\n    if (!$('questionMenu').contains(event.target)) $('questionMenu').open = false;\n  });\n  document.addEventListener('keydown', event => {\n    if (event.key === 'Escape' && $('questionMenu').open) {\n      $('questionMenu').open = false;\n      $('questionMenu').querySelector('summary').focus();\n    }\n  });",1)
p.write_text(s,encoding='utf8')
