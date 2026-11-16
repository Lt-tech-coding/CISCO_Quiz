from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf8')
for field in ['bankSource', 'mode', 'shuffle']:
    pattern = r'<div(?: class="bank-field")?><label class="field-label" for="' + field + r'">.*?</div>'
    s, count = re.subn(pattern, '', s, count=1, flags=re.S)
    assert count == 1, field
old = """    const source = $('bankSource').value;
    let pool = bank.filter(q => source === 'all' || (source === 'new' ? q.id.startsWith('ite8-expanded-') : !q.id.startsWith('ite8-variant-')))
      .filter(q => $('module').value === 'all' || q.module === $('module').value * 1).map(q => ({"""
new = """    let pool = bank.filter(q => $('module').value === 'all' || q.module === $('module').value * 1).map(q => ({"""
assert old in s
s=s.replace(old,new,1)
start=s.index("    if ($('shuffle').value === 'yes') {")
end=s.index("    const count = $('count').value;",start)
block=s[start:end]
block=block.replace("    if ($('shuffle').value === 'yes') {\n",'',1)
# Remove the enclosing conditional, preserving the existing option/answer remapping.
assert block.endswith('    }\n')
block=block[:-6]
block='\n'.join(line[2:] if line.startswith('      ') else line for line in block.split('\n'))
s=s[:start]+block+s[end:]
s=s.replace("      mode: $('mode').value,", "      mode: 'practice',",1)
old='<span id="counter" class="pill"></span><span id="status" class="small muted"></span>'
new='<span id="counter" class="pill"></span><div class="quiz-top-actions"><span id="status" class="small muted"></span><button class="btn secondary" id="home" type="button" aria-label="Save quiz and return home">Home</button></div>'
assert old in s
s=s.replace(old,new,1)
s=s.replace('<p class="small muted">In exam mode, answers are revealed after submission. Unanswered questions count as incorrect.</p>','<p class="small muted">Check each answer to learn as you go. Unanswered questions count as incorrect when you finish.</p>',1)
needle="  $('start').onclick = start;"
assert needle in s
s=s.replace(needle,needle+"""
  $('home').onclick = () => {
    save();
    show('setup');
    $('resume').classList.remove('hidden');
    window.scrollTo(0, 0);
  };""",1)
s=s.replace('</style>','.quiz-top-actions{display:flex;align-items:center;gap:12px;flex-wrap:wrap;justify-content:flex-end}\n</style>',1)
p.write_text(s,encoding='utf8')
print('Removed bank, study-mode and order selectors. Full bank and shuffling enabled; Home saves and returns to setup.')
