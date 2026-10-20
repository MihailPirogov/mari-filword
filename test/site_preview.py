# Preview staged pages over the live site (requests for files present in site_stage/out are served locally) + broken-link check
import asyncio, os, sys, mimetypes
from playwright.async_api import async_playwright
O = os.path.abspath('site_stage/out'); BASE = os.environ.get('BASE', 'https://pirogovlab.ru'); LOCAL = BASE == 'https://pirogovlab.ru' and not os.environ.get('LIVE')
PAGES = [('landing', '/mari-filword-igra/'), ('landing_en', '/en/mari-filword-igra/'), ('blog', '/blog/2026-10-20-mari-filword/'), ('home', '/'), ('blogindex', '/blog/')]
async def main():
    bad = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        for vw, vh, tag in ((1280, 900, 'desktop'), (390, 844, 'mobile')):
            ctx = await b.new_context(viewport={'width': vw, 'height': vh})
            async def route(r):
                u = r.request.url; path = u.split('pirogovlab.ru', 1)[1].split('?')[0]
                f = O + path + ('index.html' if path.endswith('/') else '')
                if LOCAL and os.path.isfile(f): await r.fulfill(path=f, content_type=mimetypes.guess_type(f)[0] or 'text/html')
                else: await r.continue_()
            await ctx.route('https://pirogovlab.ru/**', route)
            pg = await ctx.new_page()
            fails = []; pg.on('response', lambda resp: fails.append((resp.status, resp.url)) if resp.status >= 400 else None)
            for name, u in PAGES:
                await pg.goto(BASE + u); await pg.wait_for_timeout(1200)
                if name == 'home':
                    el = await pg.query_selector('a.proj[href="/mari-filword-igra/"]'); await el.scroll_into_view_if_needed(); await pg.wait_for_timeout(500)
                await pg.screenshot(path=f'site_stage/preview/{name}_{tag}.png')
                if tag == 'desktop':
                    links = await pg.evaluate("[...document.querySelectorAll('a[href],img[src]')].map(e=>e.href||e.src).filter(h=>h.startsWith('https://pirogovlab.ru')&&/filword/.test(h))")
                    for h in sorted(set(links)):
                        rr = await ctx.request.get(h.split('#')[0])
                        if rr.status >= 400: bad.append((u, rr.status, h))
            bad += [(tag, *f) for f in fails]
            await ctx.close()
        await b.close()
    print('bad', bad); assert not bad
asyncio.run(main())
