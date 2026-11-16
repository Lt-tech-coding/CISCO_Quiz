import hashlib
import json
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

items = [
    ('pc-parts', 'Personal_computer,_exploded.svg', 'Gustavb', 'CC BY 2.5', 'https://creativecommons.org/licenses/by/2.5/'),
    ('motherboard', 'Motherboard_diagram.svg', 'Gribeco; Moxfyre; subsequent Commons contributors', 'CC BY-SA 3.0', 'https://creativecommons.org/licenses/by-sa/3.0/'),
    ('raid-0', 'RAID_0.svg', 'Cburnett', 'CC BY-SA 3.0', 'https://creativecommons.org/licenses/by-sa/3.0/'),
    ('raid-1', 'RAID_1.svg', 'Cburnett', 'CC BY-SA 3.0', 'https://creativecommons.org/licenses/by-sa/3.0/'),
    ('dhcp', 'DHCP_-_A_new_Address_Allocating_Sequence_Diagram_-_en.png', 'Michel Bakni', 'CC BY-SA 4.0', 'https://creativecommons.org/licenses/by-sa/4.0/'),
    ('laser', 'Laser_printer_(cutaway_diagram).jpg', 'Welleman', 'Public domain', 'https://commons.wikimedia.org/wiki/File:Laser_printer_(cutaway_diagram).jpg'),
]
manifest = {}
for key, filename, author, license_name, license_url in items:
    digest = hashlib.md5(filename.encode()).hexdigest()
    url = f'https://upload.wikimedia.org/wikipedia/commons/{digest[0]}/{digest[:2]}/{quote(filename)}'
    target = Path('assets/diagrams') / (key + Path(filename).suffix)
    if target.exists():
        data = target.read_bytes()
    else:
        request = Request(url, headers={'User-Agent': 'ITEPracticeLab/1.0 (local educational project)'})
        with urlopen(request, timeout=30) as response:
            data = response.read()
    assert len(data) > 1000, filename
    if filename.endswith('.svg'):
        assert b'<svg' in data
        assert b'<script' not in data.lower()
    target.write_bytes(data)
    manifest[key] = dict(path=target.as_posix(), source='https://commons.wikimedia.org/wiki/File:' + quote(filename), author=author, license=license_name, licenseUrl=license_url, originalUrl=url)
    Path('assets/diagrams/credits.json').write_text(json.dumps(manifest, indent=2), encoding='utf8')
    print(key, len(data))
Path('assets/diagrams/credits.json').write_text(json.dumps(manifest, indent=2), encoding='utf8')
