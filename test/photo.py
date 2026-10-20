# Photo backgrounds 390x844: photo_home, photo_level_<theme> x3, photo_win; checks bg loaded, no errors/overflow
import asyncio, os, sys
from playwright.async_api import async_playwright
ROOT = os.environ.get('URL') or 'file://' + os.path.abspath('index.html'); PFX = os.environ.get('PFX', 'photo')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'])
        pg = await (await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)).new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(ROOT); await pg.wait_for_timeout(300)
        await pg.evaluate('localStorage.setItem("mariFilword.v1",JSON.stringify({tut:true,mode:"mid",coins:180,m:{mid:{level:60},easy:{level:5},hard:{level:0}}}))')
        await pg.reload(); await pg.wait_for_timeout(1500)
        bgs = {}
        bgs['main'] = await pg.evaluate('getComputedStyle(document.getElementById("bg")).backgroundImage')
        await pg.screenshot(path=f'shots/{PFX}_home.png')
        want = ['nature', 'food', 'culture']
        lv = await pg.evaluate('''(w)=>{const r={};for(let i=0;i<fw.TOTAL;i++){fw.start(i);const id=document.body.dataset.theme;if(w.includes(id)&&!(id in r))r[id]=i}return r}''', want)
        for th in want:
            await pg.evaluate(f'fw.start({lv[th]})'); await pg.wait_for_timeout(1500)
            for k in range(2): await pg.evaluate(f'fw.trySel(fw.L.words[{k}].path)')
            await pg.wait_for_timeout(700)
            bgs[th] = await pg.evaluate('getComputedStyle(document.getElementById("bg")).backgroundImage')
            await pg.screenshot(path=f'shots/{PFX}_level_{th}.png')
        await pg.evaluate('fw.solveAll()'); await pg.wait_for_timeout(1500); await pg.screenshot(path=f'shots/{PFX}_win.png')
        ov = await pg.evaluate('document.documentElement.scrollWidth>innerWidth')
        for k, v in bgs.items(): print(k, v[-40:])
        bad = [k for k, v in bgs.items() if f'bg/{k}.webp' not in v]
        print('levels', lv, 'errors', errs, 'overflow', ov, 'bad', bad); assert not errs and not ov and not bad
        await b.close()
asyncio.run(main())
