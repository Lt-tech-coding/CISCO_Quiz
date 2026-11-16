from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf8')
needle='  function conceptLabel(q) {'
reserve='''  // Keep a stable share of each module fresh for unassisted readiness checks.
  function reserveReadinessFamilies() {
    const modules = new Map();
    bank.forEach(q => {
      if (!modules.has(Number(q.module))) modules.set(Number(q.module), new Set());
      modules.get(Number(q.module)).add(familyKey(q));
    });
    function hash(text) {
      let value = 2166136261;
      for (const character of text) value = Math.imul(value ^ character.charCodeAt(0), 16777619);
      return value >>> 0;
    }
    const reserved = new Set();
    modules.forEach(families => {
      if (families.size < 4) return;
      const sorted = [...families].sort((a, b) => hash(a) - hash(b) || a.localeCompare(b));
      sorted.slice(0, Math.ceil(sorted.length * .4)).forEach(family => reserved.add(family));
    });
    return reserved;
  }
  const readinessReserve = reserveReadinessFamilies();

'''
assert needle in s
s=s.replace(needle,reserve+needle,1)
old="    const pool = bank.filter(q => readiness || $('module').value === 'all' || q.module === Number($('module').value));"
new="""    const pool = bank.filter(q => readiness || !readinessReserve.has(familyKey(q)))
      .filter(q => readiness || $('module').value === 'all' || q.module === Number($('module').value));"""
assert old in s
s=s.replace(old,new,1)
start=s.index("    $('timeEstimate').textContent = $('count').value === 'all'")
end=s.index('\n  }',start)
s=s[:start]+'''    const available = bank.filter(q => !readinessReserve.has(familyKey(q)) &&
      ($('module').value === 'all' || Number(q.module) === Number($('module').value))).length;
    const amount = $('count').value === 'all' ? available : Math.min(Number($('count').value), available);
    $('timeEstimate').textContent = amount + ' marks · ' + Number((amount * 1.2).toFixed(1)) +
      ' minutes · 1 mark per question' + ($('count').value === 'all' ? '. This is a long session.' : '');
    $('readinessStart').title = $('count').value === 'all' ? 'Choose 20, 50 or 100 marks' :
      'Mixed readiness test: ' + Number($('count').value) * 1.2 + ' minutes';
    const focus = Object.entries(learning.concepts).filter(([key]) => ['weak', 'due'].includes(conceptState(key)))
      .sort(([a], [b]) => Number(conceptState(b) === 'weak') - Number(conceptState(a) === 'weak')).slice(0, 8);
    $('focusList').replaceChildren();
    if (!focus.length) {
      const item = document.createElement('p');
      item.textContent = seen ? 'No urgent review items. Keep practising to strengthen recall.' : 'Start a session to discover your focus areas.';
      $('focusList').append(item);
    }
    focus.forEach(([key, record]) => {
      const item = document.createElement('p');
      item.textContent = record.label + ' — ' + (conceptState(key) === 'weak' ? 'Needs work' : 'Review due');
      $('focusList').append(item);
    });''' + s[end:]
needle='<p id="readinessProgress"></p></div>'
assert needle in s
s=s.replace(needle,'<p id="readinessProgress"></p><details class="focus-areas"><summary>Your focus areas</summary><div id="focusList"></div></details></div>',1)
s=s.replace('Readiness tests mix all 14 modules and reveal answers after submission.','Readiness tests mix all 14 modules and reveal answers after submission. Some questions are kept fresh for these checks.',1)
s=s.replace("    $('status').textContent = `${Object.keys(s.answers).length} answered", "    $('status').textContent = `${Object.values(s.answers).filter(answered).length} answered",1)
needle="  $('check').onclick = () => {\n    if (!canContinue()) return;"
assert needle in s
s=s.replace(needle,needle+"\n    if (session.mode === 'exam') return;",1)
# Readiness uses its explicitly stated 85% preparation target.
needle="    $('score').textContent = score + '%';"
s=s.replace(needle,"""    if (s.mode === 'exam') $('pass').innerHTML = score >= 85
      ? '<strong class="good">85% practice target reached</strong>'
      : '<strong class="bad">Below the 85% practice target</strong>';
"""+needle,1)
s=s.replace("      row.className = correct / total < .7 ? 'bad' : 'muted';", "      row.className = correct / total < (session.mode === 'exam' ? .85 : .7) ? 'bad' : 'muted';",1)
s=s.replace('</style>','.focus-areas{margin-top:12px;font-size:12px}.focus-areas summary{cursor:pointer;font-weight:700;color:var(--accent)}.focus-areas p{margin:7px 0;border:0;padding:0}\n</style>',1)
p.write_text(s,encoding='utf8')
print('Reserved fresh readiness questions, added named focus areas, and aligned estimates with actual session marks.')
