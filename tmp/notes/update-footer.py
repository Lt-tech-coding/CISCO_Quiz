from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf8')
start=s.index('<footer>')
end=s.index('</footer>',start)+len('</footer>')
footer='''<footer class="site-footer">
  <div class="footer-inner">
    <div class="footer-top">
      <div class="footer-brand">ITE<span>8</span> Practice Lab</div>
      <p class="footer-copyright">© 2026 <a href="https://stealthxmedia.com" target="_blank" rel="noopener noreferrer">stealthxmedia.com</a></p>
    </div>
    <div class="footer-bottom">
      <p>Independent study tool. Not affiliated with Cisco.</p>
      <a class="footer-invoice" href="https://invoicelite.app/download" target="_blank" rel="noopener noreferrer">Make your next move with InvoiceLite <span aria-hidden="true">↗</span></a>
    </div>
  </div>
</footer>'''
s=s[:start]+footer+s[end:]
css='''
/* A quiet, responsive footer that works with both themes. */
.site-footer{padding:0 28px;background:var(--panel);text-align:left;border-top:1px solid var(--line);color:var(--muted)}
.footer-inner{max-width:1184px;margin:0 auto;padding:27px 0 24px}
.footer-top,.footer-bottom{display:flex;align-items:center;justify-content:space-between;gap:16px}
.footer-top{padding-bottom:18px;border-bottom:1px solid var(--line)}
.footer-brand{color:var(--ink);font-size:16px;font-weight:800;letter-spacing:-.03em}.footer-brand span{color:var(--accent)}
.footer-copyright{font-size:12px;margin:0}.footer-copyright a{font-weight:700;color:var(--ink);text-underline-offset:4px}
.footer-bottom{padding-top:17px;font-size:12px}.footer-bottom p{margin:0;line-height:1.6}.footer-invoice{display:inline-flex;align-items:center;gap:8px;color:var(--muted);text-underline-offset:4px}.footer-invoice span{color:var(--accent)}
@media(max-width:560px){.site-footer{padding:0 20px}.footer-inner{padding:23px 0}.footer-top,.footer-bottom{align-items:flex-start;flex-direction:column;gap:11px}.footer-top{padding-bottom:16px}.footer-bottom{padding-top:16px}}
'''
s=s.replace('</style>',css+'\n</style>',1)
p.write_text(s,encoding='utf8')
assert s.count('href="https://stealthxmedia.com"')==1
assert '<footer class="site-footer">' in s
print('Updated footer with linked stealthxmedia.com copyright and responsive layout.')
