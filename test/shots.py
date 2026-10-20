# Headless smoke test + mobile screenshots 390x844: /workspace/pwvenv/bin/python test/shots.py
import asyncio, os, shutil
from playwright.async_api import async_playwright
ROOT = 'file://' + os.path.abspath('index.html'); OUT = 'shots'
async def main():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e) + ' ' + (e.stack or '')[:300]))
        shot = lambda n: pg.screenshot(path=f'{OUT}/{n}.png')
        await pg.goto(ROOT + '?adsim=1'); await pg.wait_for_timeout(1300)
        assert await pg.evaluate('fw.tut') == 0, 'tutorial did not auto-start'
        await shot('01_tutorial_swipe_finger')
        async def swipe(path, hold=None):
            boxes = [await (await pg.query_selector(f'.cell[data-i="{i}"]')).bounding_box() for i in path]
            c = lambda bx: (bx['x'] + bx['width'] / 2, bx['y'] + bx['height'] / 2)
            await pg.mouse.move(*c(boxes[0])); await pg.mouse.down()
            for bx in boxes[1:]: await pg.mouse.move(*c(bx), steps=5)
            if hold: await shot(hold)
            await pg.mouse.up()
        await pg.evaluate('document.getElementById("finger").style.opacity=0')
        await swipe(await pg.evaluate('fw.L.words[0].path'), '02_swiping_snake_line')
        await pg.wait_for_timeout(1100)
        assert await pg.evaluate('fw.M.found[0].length') == 1, 'swipe did not find word'
        assert await pg.evaluate('fw.tut') == 1
        await shot('03_tutorial_translation')
        await pg.click('#tNext'); await pg.wait_for_timeout(400); await shot('04_tutorial_all_cells')
        await pg.click('#tNext'); await pg.wait_for_timeout(400); await shot('05_tutorial_hint')
        await pg.click('#tNext'); await pg.wait_for_timeout(300)
        assert await pg.evaluate('fw.tut') == -1 and await pg.evaluate('fw.S.tut')
        await pg.click('#bHint'); await pg.wait_for_timeout(500); await shot('06_hint_used')
        await swipe(await pg.evaluate('fw.L.words[1].path')); await pg.wait_for_timeout(900)
        await shot('07_two_words_found')
        await pg.evaluate('fw.solveAll()'); await pg.wait_for_timeout(1500); await shot('08_win')
        assert 'Еш' in await pg.evaluate('document.getElementById("winTheme").textContent')
        await pg.click('#bNext'); await pg.wait_for_timeout(600)
        assert await pg.evaluate('document.getElementById("tr").textContent.trim()') == '', 'stale translation from previous level'
        await shot('09_level2_clean')
        for g, name in [(17, '10_animals_6x6'), (70, '11_plants_8x8'), (116, '12_numbers_7x7'), (104, '13_colors_7x7')]:
            await pg.evaluate(f'fw.start({g})'); await pg.wait_for_timeout(400)
            ws = await pg.evaluate('fw.L.words.length')
            for k in range(min(4, ws)): await swipe(await pg.evaluate(f'fw.L.words[{k}].path'))
            await pg.wait_for_timeout(900); await shot(name)
        bad = await pg.evaluate('''(()=>{const r=[];for(let g=0;g<fw.TOTAL+20;g++){fw.start(g);const L=fw.L; if(!L||L.cells.some(x=>!x))r.push(g);} return r;})()''')
        assert not bad, ('bad levels', bad)
        total = await pg.evaluate('fw.TOTAL')
        await pg.evaluate('fw.M.level=40;localStorage.setItem("mariFilword.v1",JSON.stringify(fw.S))')
        await pg.reload(); await pg.wait_for_timeout(700)
        assert await pg.evaluate('fw.M.level') == 40 and await pg.evaluate('fw.tut') == -1, 'progress/tutorial flag not persisted'
        await shot('14_home')
        await pg.evaluate('document.getElementById("scrHome").scrollTop=9999'); await pg.wait_for_timeout(200); await shot('14b_home_themes_scrolled')
        await pg.evaluate('document.getElementById("scrHome").scrollTop=0')
        await pg.evaluate('document.querySelector(".themes").scrollIntoView(false)'); 
        await pg.click('#bHow'); await pg.wait_for_timeout(900)
        assert await pg.evaluate('fw.tut') == 0, 'replay «Как играть» failed'
        await shot('15_howto_replay')
        # migration: old v1 save (single progress) → «Средний»
        await pg.evaluate('localStorage.setItem("mariFilword.v1",JSON.stringify({level:37,coins:120,found:{"37":[0]},tut:true}))')
        await pg.reload(); await pg.wait_for_timeout(600)
        assert await pg.evaluate('fw.S.mode') == 'mid' and await pg.evaluate('fw.S.m.mid.level') == 37 and await pg.evaluate('fw.S.m.easy.level') == 0, 'migration'
        await pg.evaluate('fw.S.m.easy.level=23;fw.S.m.hard.level=3;localStorage.setItem("mariFilword.v1",JSON.stringify(fw.S))')
        await pg.reload(); await pg.wait_for_timeout(600)
        await shot('20_difficulty_select_mid')
        names = await pg.evaluate('[...document.querySelectorAll(".th .tn")].map(e=>e.children[0].textContent+"|"+e.children[1].textContent)')
        assert len(names) == 15 and names[0] == 'Еш|Семья' and names[-1] == 'Тӱрлӧ мут|Всё подряд', names
        assert await pg.evaluate('document.querySelector(".md.on b").textContent') == 'Кокла'
        for m, g, name in [('easy', 23, '21_level_easy'), ('mid', 37, '22_level_mid'), ('hard', 3, '23_level_hard')]:
            await pg.click(f'.md[data-m="{m}"]'); await pg.wait_for_timeout(300)
            if m == 'easy': await shot('20_difficulty_select_easy')
            if m == 'hard': await shot('20_difficulty_select_hard')
            await pg.click('#bPlay'); await pg.wait_for_timeout(400)
            assert await pg.evaluate('fw.M.level') == g
            assert await pg.evaluate('document.getElementById("gTheme").textContent') and await pg.evaluate('document.getElementById("gRu").textContent')
            n = await pg.evaluate('fw.L.words.length')
            for k in range(min(3, n)): await pg.evaluate(f'fw.trySel(fw.L.words[{k}].path)')
            await pg.wait_for_timeout(900)
            path = await pg.evaluate('fw.L.words[3].path')
            boxes = [await (await pg.query_selector(f'.cell[data-i="{i}"]')).bounding_box() for i in path]
            await pg.mouse.move(boxes[0]['x'] + 10, boxes[0]['y'] + 10); await pg.mouse.down()
            for bx in boxes[1:-1]: await pg.mouse.move(bx['x'] + bx['width'] / 2, bx['y'] + bx['height'] / 2, steps=4)
            await shot(name); await pg.mouse.up(); await pg.wait_for_timeout(300)
            await pg.click('#bBack'); await pg.wait_for_timeout(300)
        print('OK themed levels =', total, 'errors:', errs)
        await b.close()
asyncio.run(main())
