from pathlib import Path
import json,re
pages={(x['chapter'],x['page']):x for x in json.loads(Path('tmp/notes/pages.json').read_text(encoding='utf8'))}
questions=json.loads(Path('tmp/notes/questions.json').read_text(encoding='utf8'))
# Topic matches use PDF page positions, which can differ from printed slide numbers.
refs='''1:11 1:8 1:12 1:22 1:19 2:15 3:39 3:31 1:7 3:11 3:33 1:31 3:9 1:32 4:12 4:29 4:25 14:23 6:16 5:30 5:31 5:45 5:62 11:149 11:150 6:12 - 7:48 7:21 7:32 8:15 8:40 8:19 9:12 9:20 9:11 10:20 10:24 10:18 11:26 11:130 11:67 12:7 12:46 12:49 13:22 13:79 13:35 14:27 14:11 14:33 1:8 7:42 5:41 1:31 3:31 1:8 1:12 2:17 3:39 4:8 3:14 3:33 1:32 3:10 3:8 4:12 4:12 4:8 4:29 14:23 6:12 5:31 6:12 5:45 5:24 6:16 11:149 6:12 - 11:150 7:21 7:48 7:32 7:25 7:42 8:17 8:40 8:19 8:35 6:25 9:12 9:20 9:11 9:10 9:20 10:18 10:20 10:24 10:18 10:15 11:26 11:130 11:67 - 11:165 12:46 12:49 12:7 12:8 13:37 13:22 13:79 13:35 13:73 13:34 14:27 14:11 14:33 14:23 14:48 1:8 2:15 4:8 4:12 6:12 6:15 13:37 8:40 9:11 10:13 11:86 12:32 13:23 14:23'''.split()
assert len(refs)==135,len(refs)
notes={}; mapping={}; signature_map={}
def signature(q):
 return str(q['module'])+'|'+ '|'.join(sorted(q['options'][i] for i in q.get('answers',[q.get('answer')]) ))
for q,ref in zip(questions[:135],refs):
 signature_map[signature(q)]=ref
for q in questions:
 ref=signature_map.get(signature(q),'-')
 if ref=='-': continue
 ch,page=map(int,ref.split(':')); raw=pages[ch,page]['text']
 lines=[x.strip() for x in raw.splitlines() if x.strip() and not re.search(r'©|All rights reserved|Cisco Confidential',x)]
 # Do not turn image-only tables or video demonstration titles into explanations.
 title=' — '.join(lines[:2]); body=' '.join(lines[2:])
 body=re.sub(r'\s+',' ',body).replace('','•')
 if len(body)<160 or 'Video Demonstration' in title or title.startswith('Lab'): continue
 # Older authentication slides do not explain MFA; do not imply that they do.
 if q['id'] and ref=='13:79': continue
 key=f'{ch}-{page}'
 notes[key]={'chapter':ch,'page':page,'file':f'ITE7_Chp{ch}.pdf','title':title,'text':body}
 mapping[q['id']]=key
path=Path('index.html'); s=path.read_text(encoding='utf8')
marker='<script>\n(() => {\n  \'use strict\';'
assert marker in s
payload='<script>\n// Related excerpts from the supplied IT Essentials 7 chapter notes.\nwindow.ITE_STUDY_NOTES = '+json.dumps(notes,ensure_ascii=False).replace('</','<\\/')+';\nwindow.ITE_QUESTION_NOTES = '+json.dumps(mapping)+';\n</script>\n'
s=s.replace(marker,payload+marker,1)
# Lookup by ID also works for previously saved sessions.
helper='''  function appendStudyNotes(parent, q) {
    const key = window.ITE_QUESTION_NOTES[q.id];
    const note = window.ITE_STUDY_NOTES[key];
    if (!note) return;
    const details = document.createElement('details');
    details.className = 'study-notes';
    const summary = document.createElement('summary');
    summary.textContent = 'Read your notes: ' + note.title;
    details.append(summary);
    const reference = document.createElement('p');
    reference.className = 'small muted';
    reference.textContent = 'Related background • IT Essentials 7 • ' + note.file + ' • PDF page ' + note.page;
    details.append(reference);
    const excerpt = document.createElement('blockquote');
    excerpt.textContent = note.text;
    details.append(excerpt);
    parent.append(details);
  }
'''
s=s.replace('  function render() {',helper+'  function render() {',1)
start=s.index("        paragraph('What you need to understand:'")
end=s.index('        fb.append(detail);',start)
s=s[:start]+'''        paragraph('Concept explained:', q.explanation || 'Review the function of the correct answer.');
        appendStudyNotes(detail, q);
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
          detail.append(alternatives);
        }
'''+s[end:]
old="      const tip = document.createElement('p');\n      tip.textContent = 'Important exam point: ' + (q.studyTip || 'Understand why the correct option meets the condition.');\n      div.append(tip);"
assert old in s
s=s.replace(old,'      appendStudyNotes(div, q);',1)
css='''.study-notes,.answer-alternatives{margin-top:14px;border:1px solid var(--line);border-radius:10px;padding:13px 15px}.study-notes summary,.answer-alternatives summary{cursor:pointer;font-weight:700;line-height:1.5}.study-notes summary:focus-visible,.answer-alternatives summary:focus-visible{outline:3px solid #f1aa46;outline-offset:4px}.study-notes blockquote{margin:12px 0 0;padding-left:14px;border-left:3px solid var(--accent);font-size:14px;line-height:1.8;white-space:pre-line}.study-notes>p{margin-top:10px}.answer-alternatives p{font-size:14px}\n'''
s=s.replace('/* Dark is the default;',css+'/* Dark is the default;',1)
s=s.replace('Detailed explanations help concepts stick.','Explanations and excerpts from your chapter notes.',1)
path.write_text(s,encoding='utf8')
print('Questions with relevant text excerpts:',len(mapping),'of',len(questions))
print('Distinct PDF pages used:',len(notes))
Path('tmp/notes/coverage.json').write_text(json.dumps({'covered':len(mapping),'pages':len(notes),'uncovered_core':[q['question'] for q in questions[:135] if q['id'] not in mapping]},indent=2),encoding='utf8')
