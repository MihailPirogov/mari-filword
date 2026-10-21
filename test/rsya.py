# RSYA web ads (js/adapters/rsya.js) with a mock Ya.Context: IDs empty → no loader; IDs set → floorAd after tutorial, fullscreen for
# «🎬 Бесплатно» (hint only after close, sound muted meanwhile) and interstitial on the 3rd win; ad blocker / onError → game keeps working.
import asyncio, os, subprocess, time, re
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT); PORT = 8781
srv = subprocess.Popen(['python3', '-m', 'http.server', str(PORT)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
BASE = f'http://127.0.0.1:{PORT}/'
IDS = "window.FW_CONFIG.rsya = { floorTouch: 'R-A-T-1', floorDesktop: 'R-A-D-1', fullscreenTouch: 'R-A-T-2', fullscreenDesktop: 'R-A-D-2' };"
MOCK = '''window.__rs=[];window.Ya={Context:{AdvManager:{render(o){__rs.push(o.type+':'+o.blockId+':'+o.platform);
 if(o.type==='fullscreen'){ if(window.__fail){setTimeout(()=>o.onError&&o.onError({}),50);return;}
   setTimeout(()=>{o.onRender&&o.onRender(); window.__mutedDuring=window.Sound&&Sound.muted; setTimeout(()=>o.onClose&&o.onClose(),300)},50);} }}}};
(window.yaContextCb||[]).forEach(f=>f()); window.yaContextCb={push:f=>f()};'''
async def page(b, ids, mode, mobile=True):
    ctx = await b.new_context(viewport={'width': 390, 'height': 844} if mobile else {'width': 1280, 'height': 800}, is_mobile=mobile, has_touch=mobile)
    reqs = []
    async def r_index(r):
        s = open('index.html', encoding='utf-8').read().replace('<script src="js/adapters/android.js', '<script src="js/adapters/rsya.js"></script>\n<script src="js/adapters/android.js', 1)
        await r.fulfill(status=200, content_type='text/html', body=s)
    async def r_cfg(r):
        s = open('js/config.js', encoding='utf-8').read(); s = s.replace("if (!window.RELEASE)", (IDS if ids else '') + "\nif (!window.RELEASE)", 1)
        await r.fulfill(status=200, content_type='application/javascript', body=s)
    async def r_ctx(r):
        reqs.append(r.request.url)
        if mode == 'blocked': await r.abort()
        else: await r.fulfill(status=200, content_type='application/javascript', body=MOCK)
    await ctx.route(BASE + 'index.html', r_index); await ctx.route(re.compile(r'.*/js/config\.js.*'), r_cfg); await ctx.route('https://yandex.ru/ads/system/context.js', r_ctx)
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto(BASE + 'index.html'); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(1200)
    if mode == 'fail': await pg.evaluate('window.__fail=true')
    return ctx, pg, errs, reqs
async def main():
    fails = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        # 1. no IDs: loader never requested, ads off, game OK
        ctx, pg, errs, reqs = await page(b, False, 'ok')
        st = await pg.evaluate('[Platform.name, Platform.ads.rewardedAvailable(), Platform.ads.bannerAvailable()]')
        print('no ids', st, reqs, errs)
        if reqs or st[1] or st[2] or errs: fails.append(('no ids', st, reqs, errs))
        await ctx.close()
        # 2. IDs + mock, mobile
        for mobile in (True, False):
            ctx, pg, errs, reqs = await page(b, True, 'ok', mobile)
            plat = 'touch' if mobile else 'desktop'
            await pg.click('#tSkip'); await pg.wait_for_timeout(400)
            floor = await pg.evaluate('__rs.slice()')
            hints0 = await pg.evaluate('(fw.M.hints[0]||[]).length')
            await pg.click('#bAdHint'); await pg.wait_for_timeout(1200)
            hints1 = await pg.evaluate('(fw.M.hints[0]||[]).length'); muted = await pg.evaluate('window.__mutedDuring'); after = await pg.evaluate('Sound.muted')
            await pg.evaluate('fw.S.wins=2;fw.S.lastAd=0'); await pg.evaluate('fw.solveAll()'); await pg.wait_for_timeout(1500); await pg.click('#bNext'); await pg.wait_for_timeout(1200)
            log = await pg.evaluate('__rs'); print(plat, log, 'hint', hints0, '→', hints1, 'muted during', muted, 'after', after, errs)
            exp = [f'floorAd:R-A-{plat[0].upper()}-1:{plat}', f'fullscreen:R-A-{plat[0].upper()}-2:{plat}', f'fullscreen:R-A-{plat[0].upper()}-2:{plat}']
            if log[:3] != exp or floor != exp[:1] or hints1 != hints0 + 1 or not muted or after or errs: fails.append((plat, log, hints0, hints1, muted, after, errs))
            await ctx.close()
        # 3. ad blocker: loader aborted → no ads, 🎬 says unavailable, game works
        ctx, pg, errs, reqs = await page(b, True, 'blocked')
        await pg.click('#tSkip'); await pg.wait_for_timeout(400); await pg.click('#bAdHint'); await pg.wait_for_timeout(600)
        msg = await pg.inner_text('#tr'); av = await pg.evaluate('Platform.ads.rewardedAvailable()')
        await pg.evaluate('fw.solveAll()'); await pg.wait_for_timeout(1500); won = await pg.evaluate("document.getElementById('win').classList.contains('on')")
        print('blocked', av, msg[:40], 'won', won, errs)
        if av or 'недоступна' not in msg or not won or errs: fails.append(('blocked', av, msg, won, errs))
        await ctx.close()
        # 4. onError from the fullscreen block → no hint, sound back, game OK
        ctx, pg, errs, reqs = await page(b, True, 'fail')
        await pg.click('#tSkip'); await pg.wait_for_timeout(400)
        h0 = await pg.evaluate('(fw.M.hints[0]||[]).length'); await pg.click('#bAdHint'); await pg.wait_for_timeout(800)
        h1 = await pg.evaluate('(fw.M.hints[0]||[]).length'); after = await pg.evaluate('Sound.muted')
        print('onError', h0, h1, after, errs)
        if h1 != h0 or after or errs: fails.append(('onError', h0, h1, after, errs))
        await ctx.close(); await b.close()
    srv.terminate()
    print('fails', fails); assert not fails
asyncio.run(main())
