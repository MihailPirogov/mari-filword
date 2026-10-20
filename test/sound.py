# Sounds: events play tones (mock AudioContext counts oscillators); muted by the 🔊 toggle, during ads (Platform.audio) and when hidden
import asyncio, os
from playwright.async_api import async_playwright
ROOT = 'file://' + os.path.abspath('index.html')
MOCK = '''window.__tones=0;window.__hidden=false;Object.defineProperty(document,'hidden',{get:()=>window.__hidden});
class FakeCtx{constructor(){this.state='running';this.currentTime=0;this.destination={}}resume(){this.state='running'}suspend(){this.state='suspended'}
 createOscillator(){__tones++;return{type:'',frequency:{setValueAtTime(){},exponentialRampToValueAtTime(){}},connect(){},start(){},stop(){}}}
 createGain(){return{gain:{setValueAtTime(){},exponentialRampToValueAtTime(){}},connect(){}}}}
window.AudioContext=FakeCtx;'''
async def main():
    fails = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'])
        pg = await b.new_page(viewport={'width': 390, 'height': 844}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.add_init_script(MOCK)
        await pg.goto(ROOT); await pg.evaluate('localStorage.setItem("mariFilword.v1",JSON.stringify({tut:true,mode:"mid",m:{mid:{level:5}}}))'); await pg.reload(); await pg.wait_for_timeout(600)
        await pg.evaluate('fw.start(5)'); await pg.wait_for_timeout(500)
        async def count(js):
            n0 = await pg.evaluate('__tones'); await pg.evaluate(js); await pg.wait_for_timeout(1300); return await pg.evaluate('__tones') - n0
        # real swipe → letter tones + word tones
        path = await pg.evaluate('fw.L.words[0].path')
        bx = [await (await pg.query_selector(f'.cell[data-i="{i}"]')).bounding_box() for i in path]
        n0 = await pg.evaluate('__tones')
        await pg.mouse.move(bx[0]['x'] + 10, bx[0]['y'] + 10); await pg.mouse.down()
        for q in bx[1:]: await pg.mouse.move(q['x'] + q['width'] / 2, q['y'] + q['height'] / 2, steps=3)
        await pg.mouse.up(); await pg.wait_for_timeout(600)
        sw = await pg.evaluate('__tones') - n0
        res = {'swipe': sw, 'wrong': await count("fw.trySel([0,1])"), 'click': await count("document.getElementById('bHint').click()")}
        res['ad_muted'] = await count("Platform.audio.suspend('ad');fw.snd('win')"); await pg.evaluate("Platform.audio.resume('ad')")
        res['after_ad'] = await count("fw.snd('word')")
        res['hidden'] = await count("__hidden=true;document.dispatchEvent(new Event('visibilitychange'));fw.snd('win')")
        await pg.evaluate("__hidden=false;document.dispatchEvent(new Event('visibilitychange'))")
        res['visible'] = await count("fw.snd('word')")
        await pg.evaluate("document.getElementById('bBack').click()"); await pg.wait_for_timeout(400)
        await pg.click('#bSnd'); await pg.wait_for_timeout(200)
        res['toggle_icon'] = await pg.inner_text('#bSnd'); res['toggled'] = await count("fw.snd('win')")
        await pg.reload(); await pg.wait_for_timeout(500); res['persist'] = await pg.inner_text('#bSnd'); res['after_reload'] = await count("fw.snd('win')")
        await pg.click('#bSnd'); res['on_again'] = await count("fw.snd('win')")
        win = await count("fw.start(6);fw.solveAll()")
        res['win'] = win
        print(res, errs)
        ok = (res['swipe'] >= len(path) + 3 and res['wrong'] >= 1 and res['click'] >= 1 and res['ad_muted'] == 0 and res['after_ad'] >= 3
              and res['hidden'] == 0 and res['visible'] >= 3 and res['toggle_icon'] == '🔇' and res['toggled'] == 0 and res['persist'] == '🔇'
              and res['after_reload'] == 0 and res['on_again'] >= 5 and res['win'] >= 5 and not errs)
        await b.close()
    print('sound OK' if ok else 'sound FAIL'); assert ok
asyncio.run(main())
