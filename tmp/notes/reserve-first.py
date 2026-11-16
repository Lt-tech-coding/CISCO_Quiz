from pathlib import Path
p=Path('index.html');s=p.read_text(encoding='utf8')
needle="    const selected = [];\n    while (selected.length < count) {"
replacement="    byModule.forEach(questions => questions.sort((a, b) => Number(readinessReserve.has(familyKey(a))) - Number(readinessReserve.has(familyKey(b)))));\n    const selected = [];\n    while (selected.length < count) {"
assert needle in s;s=s.replace(needle,replacement,1)
p.write_text(s,encoding='utf8')
