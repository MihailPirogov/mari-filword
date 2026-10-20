# «Удалить меня из таблицы»: hidden without nickname, removes the player on the server (php -S, FW_DATA=/tmp/fwdel)
import asyncio, os, json, subprocess, shutil, time
shutil.rmtree('/tmp/fwdel', ignore_errors=True); os.makedirs('/tmp/fwdel')
srv = subprocess.Popen(['php', '-S', '127.0.0.1:8766', '-t', 'server'], env={**os.environ, 'FW_DATA': '/tmp/fwdel'}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'])
        pg = await b.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + os.path.abspath('index.html') + '?lbapi=http://127.0.0.1:8766/leaderboard.php')
        await pg.evaluate('localStorage.setItem("mariFilword.v1",JSON.stringify({tut:true}))'); await pg.reload(); await pg.wait_for_timeout(500)
        await pg.evaluate('fw.lbShow()'); await pg.wait_for_timeout(400)
        print('del hidden before nick', await pg.evaluate('lbDel.hidden'))
        await pg.fill('#lbName', 'Удалямый'); await pg.click('#lbNick button'); await pg.wait_for_timeout(1200)
        print('players', open('/tmp/fwdel/players.json').read()[:80])
        print('del hidden after nick', await pg.evaluate('lbDel.hidden'))
        await pg.click('#lbDel'); await pg.wait_for_timeout(1200)
        print('msg', await pg.inner_text('#lbErr'), 'players', open('/tmp/fwdel/players.json').read(), 'name', await pg.evaluate('fw.S.lb.name'), errs)
        ok = open('/tmp/fwdel/players.json').read() == '[]' and not errs and await pg.evaluate('fw.S.lb.name') == ''
        await b.close(); srv.terminate(); print('delete OK' if ok else 'delete FAIL'); assert ok
asyncio.run(main())
