# ?design=new screenshots 390x844: new_home, new_level, new_win, new_leaderboard (+ no overflow, no JS errors)
import asyncio, os
from playwright.async_api import async_playwright
ROOT = 'file://' + os.path.abspath('index.html')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'])
        pg = await (await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, is_mobile=True, has_touch=True)).new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(ROOT); await pg.wait_for_timeout(300)
        await pg.evaluate('localStorage.setItem("mariFilword.v1",JSON.stringify({tut:true,mode:"mid",coins:180,m:{mid:{level:41},easy:{level:5},hard:{level:0}},lb:{total:1240,week:310,name:"Михаил",pid:"a".repeat(32),key:"b".repeat(32)}}))')
        await pg.reload(); await pg.wait_for_timeout(700)
        assert await pg.evaluate('!!document.querySelector(".road")')
        await pg.screenshot(path='shots/new_home.png')
        await pg.evaluate('document.getElementById("scrHome").scrollTop=700'); await pg.wait_for_timeout(200); await pg.screenshot(path='shots/new_home_map.png')
        await pg.evaluate('fw.start(41)'); await pg.wait_for_timeout(400)
        for k in range(3): await pg.evaluate(f'fw.trySel(fw.L.words[{k}].path)')
        await pg.wait_for_timeout(800)
        path = await pg.evaluate('fw.L.words[3].path')
        boxes = [await (await pg.query_selector(f'.cell[data-i="{i}"]')).bounding_box() for i in path]
        await pg.mouse.move(boxes[0]['x'] + 12, boxes[0]['y'] + 12); await pg.mouse.down()
        for bx in boxes[1:-1]: await pg.mouse.move(bx['x'] + bx['width'] / 2, bx['y'] + bx['height'] / 2, steps=4)
        await pg.screenshot(path='shots/new_level.png'); await pg.mouse.up()
        await pg.evaluate('fw.solveAll()'); await pg.wait_for_timeout(1500); await pg.screenshot(path='shots/new_win.png')
        await pg.evaluate('document.getElementById("win").classList.remove("on");document.getElementById("bBack").click()'); await pg.wait_for_timeout(300)
        await pg.evaluate('fw.lbShow()'); await pg.wait_for_timeout(500); await pg.screenshot(path='shots/new_leaderboard.png')
        ov = await pg.evaluate('document.documentElement.scrollWidth>innerWidth')
        print('errors', errs, 'overflow', ov); assert not errs and not ov
        await b.close()
asyncio.run(main())
