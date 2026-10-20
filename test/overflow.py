# No horizontal scroll in any popup at 320/360/390 px: win (incl. hard 10x10 with many bonuses), tutorial steps, how-to, bonus/translation toasts.
import asyncio, os
from playwright.async_api import async_playwright
ROOT = 'file://' + os.path.abspath('index.html')
CHECK = '''(sel)=>[...document.querySelectorAll(sel)].filter(e=>e.offsetParent!==null||getComputedStyle(e).position==='fixed')
  .flatMap(e=>[e,...e.querySelectorAll('*')]).filter(e=>e.scrollWidth>e.clientWidth+1 && getComputedStyle(e).overflowX!=='hidden' || e.getBoundingClientRect().right>innerWidth+1)
  .map(e=>(e.id||e.className)+':'+e.scrollWidth+'/'+e.clientWidth+'/'+Math.round(e.getBoundingClientRect().right))'''
POP = '.modal.on .card, .tut.on .tcard, .tr .tc, #toast'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'])
        fails = []
        for w in (320, 360, 390):
            ctx = await b.new_context(viewport={'width': w, 'height': 740}); pg = await ctx.new_page()
            async def chk(tag):
                r = await pg.evaluate(f'({CHECK})("{POP}")'); doc = await pg.evaluate('document.documentElement.scrollWidth>innerWidth')
                if r or doc: fails.append((w, tag, r, doc))
            await pg.goto(ROOT); await pg.wait_for_timeout(600)
            for i in range(4):                                   # tutorial steps
                await chk(f'tutorial{i}')
                if i == 0: await pg.evaluate('fw.trySel(fw.L.words[0].path)'); await pg.wait_for_timeout(700)
                else: await pg.click('#tNext'); await pg.wait_for_timeout(300)
            await pg.click('#bBack'); await pg.click('#bHow'); await pg.wait_for_timeout(500); await chk('howto'); await pg.click('#tSkip')
            # hard 10x10 with many bonus words, then win
            await pg.evaluate('fw.setMode("hard"); fw.start(fw.MODES.hard.themed + 2)')
            assert await pg.evaluate('fw.L.n') == 10
            await pg.evaluate('''(()=>{const B=Object.keys(fw.BONUS).filter(x=>x.length>=8).slice(0,25);fw.M.bonus[fw.L&&fw.MODES.hard.themed+2]=B})()''')
            await pg.evaluate('fw.trySel([0,1,2])'); await pg.wait_for_timeout(100); await chk('toast')
            await pg.evaluate('fw.solveAll()'); await pg.wait_for_timeout(1200); await chk('win_hard_10x10')
            await pg.screenshot(path=f'shots/overflow_win_hard_{w}.png')
            await ctx.close()
        print('fails', fails); assert not fails
        await b.close()
asyncio.run(main())
