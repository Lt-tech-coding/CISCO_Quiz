from pathlib import Path
p=Path('index.html'); s=p.read_text(encoding='utf8')
# Replace the existing green-tinted dark palette, rather than layering another theme on top.
colors={'#101c1d':'#070b14','#e9f3ef':'#edf2ff','#a8bdb5':'#a5b1cb','#334b46':'#2b3853','#70d8b5':'#89acff','#9ce9ce':'#b2caff','#1c302c':'#111b2e','#101c1b':'#070b14','#172824':'#0b1220','#3d9b7c':'#527ee3','#081f19':'#080e1b','#26463a':'#1c2c4b','#a3ebce':'#c0d4ff','#d4e8df':'#dce6ff','#2a4a3e':'#203254','#8ee6c4':'#a8c4ff','#142520':'#0b1323','#476259':'#354564','#102a20':'#0a1225','#2a403a':'#1e2b44','#e1f0e9':'#e1eaff','#456057':'#344566','#39584c':'#2c3d5f','#163e35':'#132340','#285c4d':'#30456a','#172923':'#0d1627','#3c5a4c':'#344563','#26483a':'#1d3158','#224c38':'#12382e','#263d34':'#142139','#3a5247':'#2b3956'}
for old,new in colors.items(): s=s.replace(old,new)
s=s.replace('<div id="options"></div>','<div id="answerResult" class="answer-result hidden" role="status" aria-live="polite"></div><div id="options"></div>',1)
# Explicit feedback on every option; do not rely on color alone.
old="""      if (s.mode === 'practice' && s.checked[idx]) {
        if (correctIndices(q).includes(i)) label.classList.add('correct');else if (Array.isArray(s.answers[idx]) ? s.answers[idx].includes(i) : i === s.answers[idx]) label.classList.add('wrong');
      }"""
new="""      const chosen = Array.isArray(s.answers[idx]) ? s.answers[idx].includes(i) : s.answers[idx] === i;
      const revealed = s.mode === 'practice' && !!s.checked[idx];
      if (chosen || revealed && correctIndices(q).includes(i)) {
        const badge = document.createElement('span');
        badge.className = 'answer-badge';
        if (revealed && correctIndices(q).includes(i)) {
          label.classList.add('correct');
          badge.textContent = chosen ? '✓ Correct · Your answer' : '✓ Correct answer';
        } else if (revealed && chosen) {
          label.classList.add('wrong');
          badge.textContent = '✗ Your answer · Incorrect';
        } else {
          badge.textContent = 'Your answer';
        }
        label.append(badge);
      }"""
assert old in s;s=s.replace(old,new,1)
needle="    $('feedback').classList.add('hidden');"
repl="""    const revealed = s.mode === 'practice' && !!s.checked[idx];
    $('options').classList.toggle('answers-revealed', revealed);
    const result = $('answerResult');
    result.classList.toggle('hidden', !revealed);
    result.classList.remove('good', 'bad');
    if (revealed) {
      const ok = isCorrect(q, s.answers[idx]);
      result.classList.add(ok ? 'good' : 'bad');
      result.textContent = (ok ? '✓ Correct! ' : '✗ Incorrect. ') + 'Correct answer' + (correctIndices(q).length > 1 ? 's: ' : ': ') + correctIndices(q).map(i => String.fromCharCode(65 + i) + '. ' + q.options[i]).join('; ');
    }
    $('feedback').classList.add('hidden');"""
assert needle in s;s=s.replace(needle,repl,1)
# Diagrams are shown only after checking or while reviewing, so they cannot spoil a question.
needle="        paragraph('Concept explained:', q.explanation || 'Review the function of the correct answer.');"
s=s.replace(needle,needle+"\n        appendLessonImage(detail, q);",1)
s=s.replace('      appendStudyNotes(div, q);','      appendLessonImage(div, q);\n      appendStudyNotes(div, q);',1)
css='''
/* Selection is blue; checked answers have explicit labels and distinct status colors. */
.option{flex-wrap:wrap;align-items:center}.option>span:first-of-type{flex:1;min-width:150px}.answer-badge{font-size:11px;font-weight:800;border:1px solid currentColor;border-radius:6px;padding:3px 7px;margin-left:auto;white-space:nowrap}.option.correct .answer-badge{color:var(--good)}.option.wrong .answer-badge{color:var(--bad)}.answer-result{padding:11px 14px;margin-bottom:12px;border:1px solid currentColor;border-radius:10px;font-weight:750;font-size:14px}.option input:disabled{opacity:1}.option.correct{border-width:2px}.option.wrong{border-width:2px}.answers-revealed .option:not(.correct):not(.wrong){opacity:.7;cursor:default}
html:not([data-theme="light"]) .answers-revealed .option.correct{background:#11382c;border-color:#68d7a8}
html:not([data-theme="light"]) .answers-revealed .option.wrong{background:#42212a;border-color:#f09297}
.lesson-image{margin:18px 0;border:1px solid var(--line);border-radius:13px;overflow:hidden;background:#0c1526;color:#eaf1ff}.lesson-image svg{display:block;width:100%;height:auto;max-height:260px}.lesson-image figcaption{border-top:1px solid #2b3853;padding:10px 15px;color:#b8c8e2;font-size:12px}.lesson-image text{font-family:"Segoe UI",Arial,sans-serif}.lesson-image .diagram-node{fill:#182c48;stroke:#5475a2;stroke-width:1.5}.lesson-image .diagram-wire{stroke:#89acff;stroke-width:4;fill:none}.lesson-image .diagram-label{fill:#edf2ff;font-size:15px;font-weight:700}.lesson-image .diagram-small{fill:#b0c4df;font-size:12px}
@media(max-width:560px){.answer-badge{font-size:10px;padding:2px 5px}.answer-result{font-size:13px}.option>span:first-of-type{min-width:120px}.lesson-image svg{min-height:130px}}
'''
s=s.replace('</style>',css+'\n</style>',1)
p.write_text(s,encoding='utf8')
