# Release builds: Yandex zip with a mock /sdk.js (LoadingAPI, leaderboard mfscore, rewarded, interstitial, sticky banner, cloud save)
# and the Android www with a mock AndroidBridge. Checks: no test hooks, no JS errors, ads called, leaderboard kind.
import asyncio, os, subprocess, shutil, zipfile, json, time
from playwright.async_api import async_playwright
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
subprocess.run(['python3', 'tools/build_release.py', 'yandex'], check=True, stdout=subprocess.DEVNULL)
subprocess.run(['python3', 'tools/build_release.py', 'android'], check=True, stdout=subprocess.DEVNULL)
Y = '/tmp/fw_yandex'; shutil.rmtree(Y, ignore_errors=True); zipfile.ZipFile('release/mari-filword-yandex.zip').extractall(Y)
assert os.path.exists(Y + '/index.html')
open(Y + '/sdk.js', 'w').write('''window.__y={log:[],data:null};window.YaGames={init:async()=>({
 features:{LoadingAPI:{ready(){__y.log.push('ready')}},GameplayAPI:{start(){__y.log.push('gp+')},stop(){__y.log.push('gp-')}}},
 environment:{i18n:{lang:'ru'}},on(){},
 getPlayer:async()=>({getMode:()=>'lite',getName:()=>'',getData:async()=>__y.data?{save:__y.data}:{},setData:async d=>{__y.data=d.save;__y.log.push('setData')}}),
 isAvailableMethod:async()=>true,
 leaderboards:{setScore:async(n,s)=>{__y.log.push('lb:'+n+':'+s)},getEntries:async n=>({entries:[{rank:1,score:99,player:{publicName:'Тест'}}]})},
 adv:{showRewardedVideo({callbacks:c}){__y.log.push('rewarded');c.onOpen&&c.onOpen();c.onRewarded();c.onClose()},showFullscreenAdv({callbacks:c}){__y.log.push('fullscreen');c.onClose()},
      showBannerAdv(){__y.log.push('banner+');return Promise.resolve()},hideBannerAdv(){__y.log.push('banner-');return Promise.resolve()}}})};''')
srv = subprocess.Popen(['python3', '-m', 'http.server', '8771', '-d', Y], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); time.sleep(1)
BRIDGE = '''window.__a=[];window.AndroidBridge={vibrate(){},share(){},shareImage(){},openUrl(){},
 rewardedAvailable:()=>true,showRewarded(cb){__a.push('rewarded');setTimeout(()=>window[cb](true),50)},
 interstitialAvailable:()=>true,showInterstitial(cb){__a.push('interstitial');setTimeout(()=>window[cb](),50)},
 bannerAvailable:()=>true,showBanner(){__a.push('banner+')},hideBanner(){__a.push('banner-')}};'''
async def play(pg, log):
    # tutorial (first run) → finish it, then rewarded hint and three wins (interstitial on 3rd win)
    await pg.wait_for_timeout(1200)
    assert await pg.evaluate('typeof window.fw') == 'undefined', 'test hooks in release'
    for _ in range(6):
        if await pg.is_visible('#tSkip'): await pg.click('#tSkip'); break
        await pg.wait_for_timeout(300)
    await pg.wait_for_timeout(300); await pg.click('#bAdHint'); await pg.wait_for_timeout(600)
    return await pg.evaluate(log)
async def main():
    fails = []
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'])
        # Yandex
        pg = await (await b.new_context(viewport={'width': 390, 'height': 844})).new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://127.0.0.1:8771/index.html')
        log1 = await play(pg, '__y.log'); await pg.wait_for_timeout(3500); log1 = await pg.evaluate('__y.log')
        await pg.evaluate("document.getElementById('bLb') && 0"); 
        S = await pg.evaluate("JSON.parse(localStorage['mariFilword.v1'])"); S['lastAd'] = 0; S['wins'] = 2
        await pg.evaluate("s=>{localStorage['mariFilword.v1']=JSON.stringify(s)}", S); await pg.reload(); await pg.wait_for_timeout(4500)
        log = log1 + await pg.evaluate('__y.log'); print('yandex log', log)
        for need in ('ready', 'rewarded', 'banner+', 'setData'):
            if need not in log: fails.append('yandex: no ' + need)
        if errs: fails.append(('yandex errs', errs))
        ext = [r for r in await pg.evaluate("performance.getEntriesByType('resource').map(e=>e.name)") if not r.startswith('http://127.0.0.1:8771/')]
        if ext: fails.append(('yandex external requests', ext))
        # Android
        pg = await (await b.new_context(viewport={'width': 390, 'height': 844})).new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.add_init_script(BRIDGE)
        await pg.goto('file://' + ROOT + '/android/app/src/main/assets/www/index.html')
        log = await play(pg, '__a'); print('android log', log)
        for need in ('rewarded', 'banner+'):
            if need not in log: fails.append('android: no ' + need)
        cfg = await pg.evaluate('FW_CONFIG.lbApi')
        if cfg != 'https://pirogovlab.ru/api/mari-filword/': fails.append(('android lbApi', cfg))
        if errs: fails.append(('android errs', errs))
        await b.close()
    srv.terminate()
    print('fails', fails); assert not fails
asyncio.run(main())
