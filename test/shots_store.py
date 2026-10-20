# Store screenshots → release/store/raw/{mobile,desktop}_N_*.png (mobile 360x640@3 = 1080x1920, desktop 1600x900@1.2 = 1920x1080)
import asyncio, os, json
from playwright.async_api import async_playwright
ROOT = 'file://' + os.path.abspath('index.html') + '?lbapi=' + 'https://lb.mock/'; R = 'release/store/raw'; os.makedirs(R, exist_ok=True)
NAMES = ['Кугу_Ӱдыр', 'Олык', 'Pasha.mhr', 'Эрвий', 'Ӱжара', 'Сакар', 'Йошкар', 'Мичи', 'Тойдемар', 'Пеледыш']
BOARD = {'ok': True, 'period': 'week', 'week': '2026-W43', 'top': [{'r': i + 1, 'n': n, 's': 2480 - i * 190, 'lv': 120 - i * 9, 'me': i == 3} for i, n in enumerate(NAMES)], 'me': None, 'total': 57}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'])
        for kind, vw, vh, dpr in (('mobile', 360, 640, 3), ('desktop', 1600, 900, 1.2)):
            ctx = await b.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=dpr, is_mobile=kind == 'mobile', has_touch=kind == 'mobile')
            await ctx.route('https://lb.mock/**', lambda r: r.fulfill(status=200, content_type='application/json', headers={'Access-Control-Allow-Origin': '*'}, body=json.dumps(BOARD, ensure_ascii=False)))
            pg = await ctx.new_page(); n = 0
            async def snap(name):
                nonlocal n; n += 1; await pg.screenshot(path=f'{R}/{kind}_{n}_{name}.png')
            await pg.goto(ROOT); await pg.evaluate('localStorage.setItem("mariFilword.v1",JSON.stringify({tut:true,mode:"mid",coins:240,m:{mid:{level:44},easy:{level:61},hard:{level:9}},lb:{total:1940,week:1290,name:"Эрвий",pid:"a".repeat(32),key:"b".repeat(32),wk:"2026-W43"}}))')
            await pg.reload(); await pg.wait_for_timeout(1500)
            # 1 level in progress (nature)
            await pg.evaluate('fw.start(48)'); await pg.wait_for_timeout(1500)
            for k in range(3): await pg.evaluate(f'fw.trySel(fw.L.words[{k}].path)')
            await pg.wait_for_timeout(900); await snap('game')
            # 2 home + map
            await pg.evaluate('document.getElementById("bBack").click()'); await pg.wait_for_timeout(1500); await snap('home')
            # 3 hard 7x7 (food theme photo) with swipe in progress
            await pg.evaluate('fw.setMode("hard")'); await pg.reload(); await pg.wait_for_timeout(800)
            await pg.evaluate('fw.start(30)'); await pg.wait_for_timeout(1500)
            for k in range(2): await pg.evaluate(f'fw.trySel(fw.L.words[{k}].path)')
            path = await pg.evaluate('fw.L.words[2].path')
            boxes = [await (await pg.query_selector(f'.cell[data-i="{i}"]')).bounding_box() for i in path]
            await pg.mouse.move(boxes[0]['x'] + 10, boxes[0]['y'] + 10); await pg.mouse.down()
            for bx in boxes[1:-1]: await pg.mouse.move(bx['x'] + bx['width'] / 2, bx['y'] + bx['height'] / 2, steps=3)
            await pg.wait_for_timeout(300); await snap('hard'); await pg.mouse.up()
            # 4 win
            await pg.evaluate('fw.setMode("mid")'); await pg.reload(); await pg.wait_for_timeout(800)
            await pg.evaluate('fw.start(144)'); await pg.wait_for_timeout(1300); await pg.evaluate('fw.solveAll()'); await pg.wait_for_timeout(2600); await snap('win')
            # 5 leaderboard
            await pg.evaluate('document.getElementById("win").classList.remove("on");fw.lbShow()'); await pg.wait_for_timeout(1500); await snap('leaderboard')
            # 6 tutorial
            await pg.evaluate('localStorage.clear()'); await pg.reload(); await pg.wait_for_timeout(1500)
            await pg.evaluate('fw.trySel(fw.L.words[0].path)'); await pg.wait_for_timeout(1200); await snap('tutorial')
            await ctx.close()
        await b.close()
asyncio.run(main())
