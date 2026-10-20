# Leaderboard: local mode, server mode via `php -S` (server/leaderboard.php), nickname filter, anti-cheat sanity, rate limit.
import asyncio, os, json, subprocess, time, shutil, urllib.request
from playwright.async_api import async_playwright
ROOT = 'file://' + os.path.abspath('index.html'); API = 'http://127.0.0.1:8765/'
def post(d):
    r = urllib.request.Request(API, json.dumps(d).encode(), {'Content-Type': 'application/json'})
    try: return json.load(urllib.request.urlopen(r))
    except urllib.error.HTTPError as e: return json.load(e)
async def main():
    shutil.rmtree('/tmp/fwdata', ignore_errors=True)
    srv = subprocess.Popen(['php', '-S', '127.0.0.1:8765', 'server/leaderboard.php'], env=dict(os.environ, FW_DATA='/tmp/fwdata'), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(0.8)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'])
            pg = await (await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2)).new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            # local mode
            await pg.goto(ROOT); await pg.wait_for_timeout(400); await pg.evaluate('fw.S.tut=true;document.getElementById("tSkip").click()')
            await pg.evaluate('fw.setMode("hard");fw.start(0);fw.solveAll()'); await pg.wait_for_timeout(1000)
            n = await pg.evaluate('fw.L.words.length'); tot = await pg.evaluate('fw.S.lb.total')
            assert tot == (n * 2 + 20) * 3, ('score', tot, n)
            assert 'очков' in await pg.evaluate('document.getElementById("winScore").textContent')
            await pg.evaluate('document.getElementById("win").classList.remove("on");document.getElementById("bBack").click()')
            await pg.click('#bLb'); await pg.wait_for_timeout(400)
            assert 'не подключена' in await pg.evaluate('document.getElementById("lbNote").textContent')
            print('local mode OK, score', tot)
            # server mode
            await pg.goto(ROOT + '?lbapi=' + API); await pg.wait_for_timeout(400)
            await pg.click('#bLb'); await pg.wait_for_timeout(500)
            await pg.fill('#lbName', 'х у й'); await pg.click('#lbNick button'); await pg.wait_for_timeout(300)
            assert 'нельзя' in await pg.evaluate('document.getElementById("lbErr").textContent')
            await pg.fill('#lbName', 'Михаил'); await pg.click('#lbNick button'); await pg.wait_for_timeout(800)
            t = await pg.evaluate('document.getElementById("lbErr").textContent'); assert 'сохран' in t, t
            # a second player with more points via API
            pid2, key2 = 'b' * 32, 'c' * 32
            assert post({'a': 'name', 'pid': pid2, 'key': key2, 'name': 'Ӱдыр'})['ok']
            assert post({'a': 'submit', 'pid': pid2, 'key': key2, 'total': 500, 'week': 500, 'wk': await pg.evaluate('fw.LB.weekId()'), 'lv': 5})['ok']
            assert post({'a': 'submit', 'pid': pid2, 'key': key2, 'total': 400, 'week': 400, 'wk': '', 'lv': 5})['err'] == 'decrease'
            assert post({'a': 'submit', 'pid': pid2, 'key': key2, 'total': 900000, 'week': 0, 'wk': '', 'lv': 5})['err'] == 'too_fast'
            assert post({'a': 'submit', 'pid': pid2, 'key': 'd' * 32, 'total': 600, 'week': 0, 'wk': '', 'lv': 5})['err'] == 'bad_key'
            assert post({'a': 'name', 'pid': 'e' * 32, 'key': key2, 'name': 'Михаил'})['err'] == 'name_taken'
            await pg.click('.tab[data-p="week"]'); await pg.wait_for_timeout(700)
            rows = await pg.evaluate('[...document.querySelectorAll("#lbList li")].map(l=>l.textContent)')
            me = await pg.evaluate('document.getElementById("lbMe").textContent')
            assert len(rows) == 2 and 'Ӱдыр' in rows[0] and 'Михаил' in rows[1] and 'место: 2' in me, (rows, me)
            await pg.screenshot(path='shots/leaderboard_a.png')
            await pg.click('.tab[data-p="all"]'); await pg.wait_for_timeout(500)
            assert len(await pg.evaluate('[...document.querySelectorAll("#lbList li")].map(l=>l.textContent)')) == 2
            # rate limit: >20 posts / 10 min per player → 429
            codes = [post({'a': 'submit', 'pid': pid2, 'key': key2, 'total': 500, 'week': 0, 'wk': '', 'lv': 5}).get('err') for _ in range(22)]
            assert 'rate' in codes, codes
            print('server mode OK; errors', errs); assert not errs
            await b.close()
    finally: srv.terminate()
asyncio.run(main())
