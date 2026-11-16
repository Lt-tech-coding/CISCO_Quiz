from pathlib import Path
import base64
import json
import re

rows = Path('tmp/notes/new-questions.tsv').read_text(encoding='utf8').splitlines()
questions = []
for i, row in enumerate(rows):
    module, topic, prompt, correct, w1, w2, w3, why, meaning, example, remember = row.split('|')
    options = [w1, w2, w3]
    answer = (i * 3 + 1) % 4
    options.insert(answer, correct)
    question = dict(id=f'ite8-expanded-{i+1:03d}', module=int(module), question=prompt,
                    options=options, answer=answer, explanation=why,
                    lesson=dict(title=topic, meaning=meaning, example=example, remember=remember))
    questions.append(question)
assert len(questions) == 140
assert len({q['question'] for q in questions}) == 140
credits = json.loads(Path('assets/diagrams/credits.json').read_text(encoding='utf8'))
captions = {
    'pc-parts': ('Classic desktop PC components', 'Number key: 1 monitor; 2 motherboard; 3 CPU; 4 RAM; 5 expansion slots; 6 power supply; 7 optical drive; 8 storage; 9 mouse; 10 keyboard. This is a classic layout, not a model-specific assembly guide.'),
    'motherboard': ('Older motherboard architecture', 'This historical block diagram shows connections in a late-2000s design. Current systems may integrate these functions differently; check the exact board manual for component placement.'),
    'raid-0': ('RAID 0: striping', 'Follow blocks A1, A2, A3 and A4 across the disks. The blocks are distributed, not mirrored. RAID 0 has no drive-failure redundancy.'),
    'raid-1': ('RAID 1: mirroring', 'Compare the blocks on Disk 0 and Disk 1: both hold the same data. A mirror provides redundancy; keep independent backups too.'),
    'dhcp': ('DHCP address-allocation exchange', 'Read the exchange from top to bottom: Discover → Offer → Request → Acknowledge. The selected server commits the configuration. The lower section also shows release of the lease.'),
    'laser': ('Inside a laser printer', 'This cutaway shows the paper path and imaging mechanism. Use the explanation to distinguish toner-image development from the later heat-and-pressure fusing stage.'),
}
for key, item in credits.items():
    path = Path(item['path'])
    mime = {'.svg': 'image/svg+xml', '.png': 'image/png', '.jpg': 'image/jpeg'}[path.suffix]
    item['dataUrl'] = f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode()
    item['title'], item['caption'] = captions[key]

path = Path('index.html')
s = path.read_text(encoding='utf8')
marker = "<script>\n(() => {\n  'use strict';"
assert marker in s
payload = '<script>\n// Additional original practice questions, not reproduced exam items.\nwindow.ITE_QUESTIONS.push(...' + json.dumps(questions, ensure_ascii=False, indent=2).replace('</', '<\\/') + ');\n// Source images are embedded so the single-file quiz still works offline.\nwindow.ITE_SOURCE_IMAGES = ' + json.dumps(credits, ensure_ascii=False).replace('</', '<\\/') + ';\n</script>\n'
s = s.replace(marker, payload + marker, 1)
s = s.replace('<div class="grid"><div><label class="field-label" for="mode">', '<div class="grid"><div class="bank-field"><label class="field-label" for="bankSource">Question bank</label><select id="bankSource"><option value="core">275 core questions (recommended)</option><option value="new">140 newly added questions</option><option value="all">All 1,140 versions, including repeats</option></select><span class="field-help">Use core questions to cover more concepts with less repetition.</span></div><div><label class="field-label" for="mode">', 1)
old = "    let pool = bank.filter(q => $('module').value === 'all' || q.module === $('module').value * 1).map(q => ({"
new = """    const source = $('bankSource').value;
    let pool = bank.filter(q => source === 'all' || (source === 'new' ? q.id.startsWith('ite8-expanded-') : !q.id.startsWith('ite8-variant-')))
      .filter(q => $('module').value === 'all' || q.module === $('module').value * 1).map(q => ({"""
assert old in s
s = s.replace(old, new, 1)
s = s.replace('    const lesson = window.ITE_LESSONS[lessonKey];', '    const lesson = q.lesson || window.ITE_LESSONS[lessonKey];', 1)
start = s.index('  // Original SVG teaching diagrams')
end = s.index('  function appendStudyNotes', start)
helper = '''  // Downloaded source diagrams, with embedded image bytes and visible attribution.
  function appendLessonImage(parent, q) {
    const images = window.ITE_SOURCE_IMAGES || {};
    const text = (q.question + ' ' + correctIndices(q).map(i => q.options[i]).join(' ')).toLowerCase();
    let key = null;
    if (/raid 0|stripes data without redundancy|striping without redundancy/.test(text)) key = 'raid-0';
    else if (/raid 1|disk mirroring|mirrored pairs/.test(text)) key = 'raid-1';
    else if (/dhcp|169\\.254/.test(text)) key = 'dhcp';
    else if (/laser|fuser|toner/.test(text)) key = 'laser';
    else if (/chipset/.test(text) && Number(q.module) <= 3) key = 'motherboard';
    else if (Number(q.module) === 1 || Number(q.module) === 2) key = 'pc-parts';
    const image = images[key];
    if (!image) return;

    const figure = document.createElement('figure');
    figure.className = 'lesson-image source-image';
    const heading = document.createElement('h4');
    heading.textContent = image.title;
    figure.append(heading);
    const picture = document.createElement('img');
    picture.src = image.dataUrl;
    picture.alt = image.title + '. ' + image.caption;
    picture.loading = 'lazy';
    figure.append(picture);
    const caption = document.createElement('figcaption');
    const description = document.createElement('p');
    description.textContent = image.caption;
    caption.append(description);
    const credit = document.createElement('p');
    credit.className = 'image-credit';
    credit.append(document.createTextNode('Image: ' + image.author + ' · '));
    const source = document.createElement('a');
    source.href = image.source;
    source.target = '_blank';
    source.rel = 'noopener noreferrer';
    source.textContent = 'Original source';
    const license = document.createElement('a');
    license.href = image.licenseUrl;
    license.target = '_blank';
    license.rel = 'noopener noreferrer';
    license.textContent = image.license;
    credit.append(source, document.createTextNode(' · '), license, document.createTextNode(' · Image unchanged'));
    caption.append(credit);
    figure.append(caption);

    const enlarge = document.createElement('details');
    enlarge.className = 'image-zoom';
    const summary = document.createElement('summary');
    summary.textContent = 'Enlarge diagram';
    const fullSize = document.createElement('img');
    fullSize.src = image.dataUrl;
    fullSize.alt = picture.alt;
    fullSize.loading = 'lazy';
    enlarge.append(summary, fullSize);
    figure.append(enlarge);
    parent.append(figure);
  }

'''
s = s[:start] + helper + s[end:]
s = s.replace('1,000 practice question versions based on 135 original core questions.', '275 core practice questions, including 140 newly added questions across all 14 modules. An optional expanded bank includes 865 reworded variants (1,140 versions in total).', 1)
s = s.replace('All 135 core questions', 'All 275 core questions')
css = '''
.bank-field{grid-column:1/-1}.source-image{background:var(--panel);color:var(--ink)}.source-image h4{padding:16px 18px;margin:0;font-size:15px}.source-image>img{display:block;width:100%;max-height:470px;object-fit:contain;background:white;padding:14px}.source-image figcaption{border-color:var(--line);color:var(--muted)}.source-image figcaption p{margin:5px 0;line-height:1.6}.image-credit{font-size:11px!important}.image-credit a{color:var(--accent)}.image-zoom{padding:12px 16px;border-top:1px solid var(--line)}.image-zoom summary{cursor:pointer;font-weight:700;font-size:13px}.image-zoom img{display:block;min-width:600px;max-width:100%;background:white;margin-top:12px;padding:12px}.image-zoom[open]{overflow:auto}.image-zoom summary:focus-visible{outline:3px solid #f1aa46;outline-offset:3px}
'''
s = s.replace('</style>', css + '\n</style>', 1)
path.write_text(s, encoding='utf8')
Path('tmp/notes/expanded-questions.json').write_text(json.dumps(questions, ensure_ascii=False, indent=2), encoding='utf8')
print('Added 140 original questions and 6 offline source images. Default core bank: 275; expanded total: 1,140.')
