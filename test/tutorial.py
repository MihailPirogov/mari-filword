# Tutorial spotlight: each step's target inside the bright hole, bubble inside viewport and not overlapping the target
import asyncio, os
from playwright.async_api import async_playwright
ROOT = os.environ.get('URL') or 'file://' + os.path.abspath('index.html'); SHOT = os.environ.get('SHOT')
T = ['board', 'tr', 'board', 'bHint']
CHK = '''(id)=>{const t=document.getElementById(id).getBoundingClientRect(),h=document.getElementById('spotHole').getBoundingClientRect(),c=document.getElementById('tcard').getBoundingClientRect();const bad=[];
 if(!(h.left<=t.left&&h.top<=t.top&&h.right>=t.right&&h.bottom>=t.bottom))bad.push('target outside hole');
 if(c.top<0||c.bottom>innerHeight+.5)bad.push('bubble off-screen '+[c.top,c.bottom].map(Math.round));
 if(!(c.bottom<=t.top||c.top>=t.bottom)&&id!=='board')bad.push('bubble covers target');
 if(id==='board'&&c.top<t.bottom&&c.bottom>t.top&&t.height<innerHeight-c.height-16)bad.push('bubble covers board');
 return bad}'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'])
        fails = []
        for vw, vh, mob, tag in [(390, 844, True, 'mobile'), (360, 640, True, 'small'), (1280, 800, False, 'desktop'), (788, 910, False, 'tablet')]:
            pg = await (await b.new_context(viewport={'width': vw, 'height': vh}, is_mobile=mob, has_touch=mob, device_scale_factor=2 if mob else 1)).new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(ROOT); await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(500)
            await pg.evaluate('fw.start(0)'); await pg.wait_for_timeout(1200)
            for k, tid in enumerate(T):
                st = await pg.evaluate('fw.tut')
                if st != k: fails.append((tag, 'step', k, st)); break
                r = await pg.evaluate(CHK, tid)
                if r: fails.append((tag, k, r))
                await pg.screenshot(path=f'shots/tut_{tag}_{k}.png')
                if k == 3 and SHOT and tag == 'mobile': await pg.screenshot(path=SHOT)
                if k == 0: await pg.evaluate('fw.trySel(fw.L.words[0].path)'); await pg.wait_for_timeout(1000)
                else: await pg.click('#tNext'); await pg.wait_for_timeout(500)
            if await pg.evaluate('fw.tut') != -1: fails.append((tag, 'not ended'))
            if errs: fails.append((tag, errs))
            print(tag, 'ok' if not fails else fails[-1])
        print('fails', fails); assert not fails
        await b.close()
asyncio.run(main())
