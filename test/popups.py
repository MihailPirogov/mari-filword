# Every popup fits the viewport: ribbon fully visible, «Дальше»/close visible, only inner lists scroll
import asyncio, os
from playwright.async_api import async_playwright
ROOT = os.environ.get('URL') or 'file://' + os.path.abspath('index.html'); SHOT = os.environ.get('SHOT')
CHK = '''(sel)=>{const m=document.querySelector(sel);const c=m.querySelector('.card,.tcard');const vh=innerHeight,vw=innerWidth;const bad=[];
 const els=[c,...c.querySelectorAll('h2,button,.stars')].filter(e=>e.offsetParent);
 for(const e of els){const r=e.getBoundingClientRect();if(r.top<0||r.bottom>vh+0.5||r.left<0||r.right>vw+0.5)bad.push((e.id||e.tagName)+' '+[r.top,r.bottom,r.left,r.right].map(Math.round))}
 // nothing clipped by the card: card must not hide overflow
 const s=getComputedStyle(c);if(/hidden|auto|scroll/.test(s.overflowY))bad.push('card overflow '+s.overflowY);
 return bad}'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'], ignore_default_args=['--hide-scrollbars'])
        fails = []
        for vw, vh in [(320, 568), (360, 640), (390, 844), (788, 910), (1280, 800)]:
            pg = await (await b.new_context(viewport={'width': vw, 'height': vh})).new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(ROOT); await pg.evaluate('localStorage.setItem("mariFilword.v1",JSON.stringify({tut:true,mode:"hard",m:{hard:{level:300}},lb:{total:500,week:50,name:"Тест",pid:"a".repeat(32),key:"b".repeat(32)}}))'); await pg.reload(); await pg.wait_for_timeout(800)
            await pg.evaluate('fw.start(300)'); await pg.wait_for_timeout(300)
            await pg.evaluate('fw.solveAll()'); await pg.wait_for_timeout(1500)
            n = await pg.evaluate('document.querySelectorAll("#winWords>div").length')
            r = await pg.evaluate(CHK, '#win'); fails += [(vw, vh, 'win', r)] if r else []
            if SHOT and (vw, vh) == (788, 910): await pg.screenshot(path=SHOT)
            await pg.screenshot(path=f'shots/popup_win_{vw}x{vh}.png')
            await pg.evaluate('document.getElementById("win").classList.remove("on");fw.lbShow()'); await pg.wait_for_timeout(700)
            r = await pg.evaluate(CHK, '#lbm'); fails += [(vw, vh, 'lb', r)] if r else []
            await pg.screenshot(path=f'shots/popup_lb_{vw}x{vh}.png')
            if errs: fails.append((vw, vh, errs))
            print(vw, vh, 'words', n, 'ok' if not fails else fails[-1])
        print('fails', fails); assert not fails
        await b.close()
asyncio.run(main())
