# No visible scrollbars (offsetWidth-clientWidth==0 on every scrollable element) at 1280x800 and 390x844; wheel scroll still works
import asyncio, os
from playwright.async_api import async_playwright
ROOT = os.environ.get('URL') or 'file://' + os.path.abspath('index.html'); SHOT = os.environ.get('SHOT')
JS = '''()=>[document.documentElement,document.body,...document.querySelectorAll('*')].filter(e=>{const s=getComputedStyle(e);return /auto|scroll/.test(s.overflowY+s.overflowX)||e===document.documentElement}).filter(e=>e.offsetParent!==null||e===document.documentElement||e===document.body).map(e=>[e.id||e.className||e.tagName,e.offsetWidth-e.clientWidth-(parseFloat(getComputedStyle(e).borderLeftWidth)+parseFloat(getComputedStyle(e).borderRightWidth)),e.scrollHeight>e.clientHeight]).filter(x=>x[1]>0)'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'], ignore_default_args=['--hide-scrollbars'])
        fails = []
        for vw, vh, mob in [(1280, 800, False), (390, 844, True)]:
            pg = await (await b.new_context(viewport={'width': vw, 'height': vh}, is_mobile=mob, has_touch=mob)).new_page()
            await pg.goto(ROOT); await pg.evaluate('localStorage.setItem("mariFilword.v1",JSON.stringify({tut:true,mode:"mid",m:{mid:{level:60}}}))'); await pg.reload(); await pg.wait_for_timeout(1200)
            if SHOT and not mob: await pg.screenshot(path=SHOT)
            r = await pg.evaluate(JS); fails += [(vw, 'home', r)] if r else []
            if not mob:
                await pg.mouse.move(640, 600); await pg.mouse.wheel(0, 600); await pg.wait_for_timeout(400)
                st = await pg.evaluate('Math.max(document.getElementById("scrHome").scrollTop,scrollY)'); print('wheel scrollTop', st)
                if st <= 0: fails.append('wheel')
            await pg.evaluate('fw.start(48)'); await pg.wait_for_timeout(500); r = await pg.evaluate(JS); fails += [(vw, 'level', r)] if r else []
            await pg.evaluate('fw.solveAll()'); await pg.wait_for_timeout(1200); r = await pg.evaluate(JS); fails += [(vw, 'win', r)] if r else []
            await pg.evaluate('document.getElementById("win").classList.remove("on");fw.lbShow()'); await pg.wait_for_timeout(600); r = await pg.evaluate(JS); fails += [(vw, 'lb', r)] if r else []
        print('fails', fails); assert not fails
        await b.close()
asyncio.run(main())
