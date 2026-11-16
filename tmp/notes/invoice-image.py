from pathlib import Path
import base64
p=Path('index.html');s=p.read_text(encoding='utf8')
old='<div class="invoice-top"><span class="invoice-icon" aria-hidden="true">↗</span><span class="invoice-label">A little something extra</span></div>'
assert old in s
image='data:image/png;base64,'+base64.b64encode(Path('assets/App_Icon.png').read_bytes()).decode()
new='<a class="invoice-art" href="https://invoicelite.app/download" target="_blank" rel="noopener noreferrer" aria-label="Discover InvoiceLite"><img src="'+image+'" alt="InvoiceLite — Streamlined Billing" width="1024" height="1024" loading="lazy"></a><div class="invoice-top"><span class="invoice-label">A little something extra</span></div>'
s=s.replace(old,new,1)
s=s.replace('</style>','.invoice-art{display:block;max-width:180px;margin:0 auto 18px;position:relative;z-index:1}.invoice-art img{display:block;width:100%;height:auto;border-radius:14px;border:1px solid var(--line)}\n</style>',1)
p.write_text(s,encoding='utf8')
assert 'InvoiceLite — Streamlined Billing' in s and old not in s
print('InvoiceLite promotion now uses the supplied image, embedded for offline viewing.')
