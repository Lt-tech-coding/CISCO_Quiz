from pathlib import Path
p=Path('index.html');s=p.read_text(encoding='utf8')
s=s.replace("/raid 0|stripes data without redundancy|striping without redundancy/.test(text)",r"/\braid 0\b|stripes data without redundancy|striping without redundancy/.test(text)")
s=s.replace("/raid 1|disk mirroring|mirrored pairs/.test(text)",r"/\braid 1\b|disk mirroring/.test(text)")
p.write_text(s,encoding='utf8')
