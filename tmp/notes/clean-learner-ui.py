from pathlib import Path
import re

p=Path('index.html');s=p.read_text(encoding='utf8')
# Remove redundant explanations of the interface while keeping task-critical information.
s=s.replace('<p>Set your session length, then choose practice or a test.</p>','',1)
s=s.replace('<span class="field-help">This topic applies to practice. Readiness tests cover all modules.</span>','',1)
s=s.replace('Work on weak concepts with explanations after each answer.','Learn with feedback after each answer.',1)
s=s.replace('Mix all 14 modules. Answers stay hidden until you submit.','All 14 modules. See your answers after submission.',1)
s=s.replace('Targeted practice','Practice')
# Keep the requested InvoiceLite promotion, but remove generic feature descriptions.
sidebar_start=s.index('<aside class="sidebar"')
cards_start=s.index('<div class="side-card">',sidebar_start)
promotion_start=s.index('<div class="side-card invoice-card">',cards_start)
s=s[:cards_start]+s[promotion_start:]
old="'You have ' + families.size + ' unseen question families left. Choose a shorter readiness test, or continue targeted practice.'"
new="'Only ' + families.size + ' new questions are available. Choose a shorter test or continue practising.'"
assert old in s;s=s.replace(old,new,1)
old="'A fresh mixed test needs unseen questions in all 14 modules. Continue targeted practice; repeated questions will not be counted as a fresh readiness test.'"
new="'There are not enough new questions across all modules for another readiness test. Continue practising.'"
assert old in s;s=s.replace(old,new,1)
s=s.replace("'Readiness target met: two fresh tests at 85%+. Keep reviewing weak modules.'", "'Goal reached: two tests at 85% or higher.'",1)
s=s.replace("'Readiness goal: 85%+ in two fresh mixed tests. This is a practice target.'", "'Your goal: score 85% or higher in two readiness tests.'",1)
s=s.replace(" + ' concepts practised'", " + ' topics practised'",1)
s=s.replace("' minutes · 1 mark per question' + ($('count').value === 'all' ? '. This is a long session.' : '')", "' minutes'",1)
old="    reference.textContent = 'Related background • IT Essentials 7 • ' + note.file + ' • PDF page ' + note.page;"
new="    reference.textContent = 'IT Essentials 7 · Chapter ' + note.chapter + ' · Page ' + note.page;"
assert old in s;s=s.replace(old,new,1)
# Credits remain accessible without taking attention away from the lesson.
s=s.replace('    caption.append(credit);', '''    const credits = document.createElement('details');
    const creditLabel = document.createElement('summary');
    creditLabel.textContent = 'Image credits';
    credits.className = 'image-credits';
    credits.append(creditLabel, credit);
    caption.append(credits);''',1)
old="    guidance.textContent = 'These module scores show this session only. Practice will revisit weak concepts.';\n    parent.append(guidance);"
assert old in s;s=s.replace(old,'',1)
s=s.replace("'Readiness test: answers appear after submission. The timer keeps running on Home.' : 'Check each answer to learn. The timer keeps running on Home.'", "'Answers are shown after submission. Your timer continues when you leave.' : 'Your timer continues when you leave.'",1)
s=s.replace('Check each answer to learn. The timer keeps running on Home.','Your timer continues when you leave.',1)
s=s.replace('</style>','.image-credits{margin-top:10px}.image-credits summary{cursor:pointer;font-size:11px;color:var(--muted)}\n</style>',1)
p.write_text(s,encoding='utf8')
print('Cleaned visible interface copy and kept study content, navigation, timing and accessible image credits.')
