from pathlib import Path
import re

path = Path('index.html')
s = path.read_text(encoding='utf8')
replacements = {
    '<label class="field-label" for="bankSource">Question bank</label>': '<label class="field-label" for="bankSource">Practice set</label>',
    '275 core questions (recommended)': 'Core practice · 275 questions',
    '140 newly added questions': 'Extra practice · 140 questions',
    'All 1,140 versions, including repeats': 'Extended practice · 1,140 versions',
    'Use core questions to cover more concepts with less repetition.': 'Choose core practice for focused revision, or extended practice for more repetition.',
    'Your progress is saved in this browser. Works offline.': 'Your progress is saved on this device.',
    'Explanations and excerpts from your chapter notes.': 'Clear explanations, examples and study notes.',
    "'Read your notes: '": "'Explore study notes: '",
    'Unofficial study tool · Not affiliated with Cisco or CompTIA · This practice quiz does not confer certification.': 'Independent IT Essentials practice · Not affiliated with Cisco.',
    '"A browser error occurred: " + e.message': '"Something went wrong. Refresh the page and try again."',
    ", document.createTextNode(' · Image unchanged')": '',
}
for old, new in replacements.items():
    assert old in s, old
    s = s.replace(old, new, 1)
s, count = re.subn(r'<div class="disclaimer">.*?</div>', '', s, count=1, flags=re.S)
assert count == 1
path.write_text(s, encoding='utf8')
print('Removed behind-the-scenes interface copy; study explanations and source credits retained.')
