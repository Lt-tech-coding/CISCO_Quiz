from pathlib import Path
import json
import re

path = Path('index.html')
s = path.read_text(encoding='utf8')
pattern = r'window\.ITE_QUESTIONS\.push\(\.\.\.(\[.*?\])\);'
match = re.search(pattern, s, re.S)
questions = json.loads(match.group(1))
changes = Path('tmp/notes/distractors.tsv').read_text(encoding='utf8').splitlines()
assert len(changes) == len(questions) == 140
for row in changes:
    number, *wrong = row.split('|')
    q = questions[int(number)-1]
    answer = q['options'][q['answer']]
    q['options'] = wrong
    q['options'].insert(q['answer'], answer)
    assert len(set(q['options'])) == 4, q['id']

refs = {
    50: ('Cisco: IPv4 addressing and subnetting', 'https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/ip-addressing/ip-addressing/m_config-ipv4-addr-0.html'),
    51: ('Cisco: IPv4 addressing and subnetting', 'https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/ip-addressing/ip-addressing/m_config-ipv4-addr-0.html'),
    52: ('Cisco: IPv4 addressing and subnetting', 'https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/ip-addressing/ip-addressing/m_config-ipv4-addr-0.html'),
    53: ('Cisco: IPv4 addressing and subnetting', 'https://www.cisco.com/c/en/us/td/docs/routers/ios-xe/ip-addressing/ip-addressing/m_config-ipv4-addr-0.html'),
    54: ('Microsoft: nslookup', 'https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/nslookup'),
    57: ('Microsoft: ipconfig', 'https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/ipconfig'),
    88: ('Oracle: Virtual networking', 'https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/networkingdetails.html'),
    89: ('Oracle: Virtual networking', 'https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/networkingdetails.html'),
    90: ('Oracle: Virtual networking', 'https://docs.oracle.com/en/virtualization/virtualbox/7.2/user/networkingdetails.html'),
    105: ('Microsoft: chkdsk', 'https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/chkdsk'),
    106: ('Microsoft: Repair a Windows image', 'https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/repair-a-windows-image'),
}
for number, (title, url) in refs.items():
    questions[number-1]['references'] = [dict(title=title, url=url)]
s = s[:match.start(1)] + json.dumps(questions, ensure_ascii=False, indent=2).replace('</', '<\\/') + s[match.end(1):]
needle = '    appendStudyNotes(parent, q);'
assert needle in s
s = s.replace(needle, needle + '''
    if (q.references) {
      const references = document.createElement('p');
      references.className = 'small muted';
      references.append(document.createTextNode('Learn more: '));
      q.references.forEach(reference => {
        const link = document.createElement('a');
        link.href = reference.url;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.textContent = reference.title;
        references.append(link);
      });
      parent.append(references);
    }
''', 1)
path.write_text(s, encoding='utf8')
Path('tmp/notes/expanded-questions.json').write_text(json.dumps(questions, ensure_ascii=False, indent=2), encoding='utf8')
print('Refined 140 sets of alternatives and added primary-source links for the relevant technical items.')
