from pathlib import Path
import json

lessons = {}
for row in Path('tmp/notes/lessons.tsv').read_text(encoding='utf8').splitlines():
    key, title, meaning, example, remember = row.split('|')
    lessons[key] = dict(title=title, meaning=meaning, example=example, remember=remember)

keys = '''psu esd atx ram cooling standoffs sata thermal disconnect uefi raid1 ssd cmos nvme troubleshoot multimeter video tickets apipa dhcp dns router ethernet ipconfig ping gateway wifi battery dock bluetooth laser inkjet dotmatrix hypervisor iaas snapshot ntfs installmedia gpt taskmanager sfc devicemanager android ls sudo phishing mfa leastprivilege approval listening pii esd sodimm ethernetport ssd thermal disconnect eps raminstall sata airflow secureboot raid0 nvme cmos post troubleshoot testcause cooling multimeter verify subnet dns privateip router frequency apipa ipconfig gateway wifi ping dock swollen bluetooth backlight sodimm laser inkjet dotmatrix spooler printerlink type1 saas snapshot virtualbenefits iaas gpt ntfs cleaninstall bootcompat backup taskmanager sfc devicemanager netstat restorepoint ls sudo android permissions encryption phishing mfa leastprivilege updates ransomware approval listening pii tickets escalate esd installprep cooling troubleshoot privateip dhcp mobilecare printercare virtualbenefits installprep performance mobilecare accountcare tickets'''.split()
assert len(keys) == 135, len(keys)
assert not set(keys) - lessons.keys()
questions = json.loads(Path('tmp/notes/questions.json').read_text(encoding='utf8'))

def signature(q):
    return str(q['module']) + '|' + '|'.join(sorted(q['options'][i] for i in q.get('answers', [q.get('answer')])))

by_signature = {signature(q): key for q, key in zip(questions[:135], keys)}
by_id = {q['id']: key for q, key in zip(questions[:135], keys)}
mapping = {q['id']: by_id.get(q['id'], by_signature[signature(q)]) for q in questions}
path = Path('index.html')
s = path.read_text(encoding='utf8')
marker = "<script>\n(() => {\n  'use strict';"
assert marker in s
payload = '<script>\n// Simple meaning, reasoning, practical example, and takeaway.\nwindow.ITE_LESSONS = ' + json.dumps(lessons, ensure_ascii=False, indent=2).replace('</', '<\\/') + ';\nwindow.ITE_QUESTION_LESSONS = ' + json.dumps(mapping, indent=2) + ';\n</script>\n'
s = s.replace(marker, payload + marker, 1)
helper = '''  function appendExplanation(parent, q) {
    const lessonKey = window.ITE_QUESTION_LESSONS[q.id];
    const lesson = window.ITE_LESSONS[lessonKey];
    const section = document.createElement('section');
    section.className = 'teaching-explanation';
    const title = document.createElement('h3');
    title.textContent = lesson ? lesson.title : 'Understand this answer';
    section.append(title);

    function teachingBlock(label, value, className) {
      const block = document.createElement('div');
      block.className = className || 'teaching-block';
      const heading = document.createElement('h4');
      heading.textContent = label;
      const content = document.createElement('p');
      content.textContent = value;
      block.append(heading, content);
      section.append(block);
    }

    if (lesson) teachingBlock('1. In simple terms', lesson.meaning);
    teachingBlock(lesson ? '2. Why this answer is right' : 'Why this answer is right', q.explanation || correctIndices(q).map(i => q.options[i]).join('; '));
    if (lesson) {
      teachingBlock('3. A practical example', lesson.example);
      teachingBlock('Remember for the exam', lesson.remember, 'exam-takeaway');
    }
    parent.append(section);
    appendLessonImage(parent, q);
    appendStudyNotes(parent, q);

    if (q.distractors) {
      const alternatives = document.createElement('details');
      alternatives.className = 'answer-alternatives';
      const summary = document.createElement('summary');
      summary.textContent = 'Compare the other choices';
      alternatives.append(summary);
      q.options.forEach((opt, i) => {
        if (correctIndices(q).includes(i)) return;
        const p = document.createElement('p');
        p.textContent = opt + ': ' + (q.distractors[opt] || 'This choice does not meet the question conditions.');
        alternatives.append(p);
      });
      parent.append(alternatives);
    }
  }

  function moveToQuestion(offset) {
    const index = session.index + offset;
    if (index < 0 || index >= session.questions.length) return;
    session.index = index;
    save();
    render();
    window.scrollTo(0, 0);
  }

'''
s = s.replace('  function render() {', helper + '  function render() {', 1)
start = s.index('        function paragraph(label, value) {')
end = s.index('        fb.append(detail);', start)
s = s[:start] + '''        appendExplanation(detail, q);
        const continueButton = document.createElement('button');
        continueButton.type = 'button';
        continueButton.className = 'btn explanation-next';
        const lastQuestion = idx === s.questions.length - 1;
        continueButton.textContent = lastQuestion ? 'Finish & score' : 'Next question →';
        continueButton.onclick = lastQuestion ? finish : () => moveToQuestion(1);
        detail.append(continueButton);
''' + s[end:]
start = s.index("      const why = document.createElement('p');", s.index('  function review('))
end = s.index('      area.append(div);', start)
s = s[:start] + '      appendExplanation(div, q);\n' + s[end:]
start = s.index("  $('prev').onclick = () => {")
end = s.index("  $('check').onclick = () => {", start)
s = s[:start] + "  $('prev').onclick = () => moveToQuestion(-1);\n  $('next').onclick = () => moveToQuestion(1);\n" + s[end:]
start = s.index("  $('check').onclick = () => {")
end = s.index("  $('flag').onclick", start)
block = s[start:end]
block = block.replace('    render();', "    render();\n    $('feedback').scrollIntoView({ block: 'start', behavior: 'auto' });")
s = s[:start] + block + s[end:]
s = s.replace('<div id="feedback" class="feedback hidden" aria-live="polite"></div>', '<div id="feedback" class="feedback hidden" aria-live="polite" aria-label="Answer explanation"></div>', 1)
css = '''
/* Core explanations stay open. Only supplementary source excerpts are collapsed. */
.feedback{scroll-margin-top:18px}.teaching-explanation{margin:0}.teaching-explanation h3{font-size:23px;line-height:1.3;margin:0 0 20px;letter-spacing:-.025em}.teaching-block{margin:0 0 21px}.teaching-explanation h4{font-size:14px;color:var(--accent);margin:0 0 7px}.teaching-explanation p{font-size:15px;line-height:1.85;margin:0;max-width:75ch}.exam-takeaway{padding:17px 19px;border-left:4px solid var(--accent);background:var(--panel);border-radius:0 10px 10px 0;margin:22px 0}.exam-takeaway h4{margin-bottom:7px}.explanation-next{margin-top:22px}.review>.teaching-explanation{margin-top:22px}html[data-theme="light"] .teaching-explanation h4{color:#066a59}
'''
s = s.replace('</style>', css + '\n</style>', 1)
path.write_text(s, encoding='utf8')
print(f'Added {len(lessons)} topic lessons mapped to all {len(mapping)} question versions.')
