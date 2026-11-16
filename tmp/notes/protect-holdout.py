from pathlib import Path
p=Path('index.html');s=p.read_text(encoding='utf8')
old="const candidates = shuffle(bank.filter(item => conceptKey(item) === key && !queued.has(item.id)));"
new="const candidates = shuffle(bank.filter(item => conceptKey(item) === key && !queued.has(item.id) && !readinessReserve.has(familyKey(item))));"
assert old in s;s=s.replace(old,new,1)
p.write_text(s,encoding='utf8')
