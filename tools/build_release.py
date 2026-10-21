#!/usr/bin/env python3
"""Release builds of «Мари филворд» (Mari Word Search).
  python3 tools/build_release.py yandex   -> release/build/yandex/ + release/mari-filword-yandex.zip (Yandex SDK, ysdk leaderboard 'mfscore', SDK ads, no external links)
  python3 tools/build_release.py android  -> android/app/src/main/assets/www/ (AndroidBridge ads, common leaderboard https://pirogovlab.ru/api/mari-filword/)
  python3 tools/build_release.py web      -> release/build/web/ (public https://pirogovlab.ru/mari-filword/: indexable, Metrika 108319724, no ads, + privacy/)
All release builds set window.RELEASE=true (test hooks, ?adsim, ?lbapi off)."""
import os, re, sys, shutil, time, zipfile
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(ROOT)
target = sys.argv[1]; V = time.strftime('%Y%m%d%H%M')
out = {'yandex': 'release/build/yandex', 'android': 'android/app/src/main/assets/www', 'web': 'release/build/web'}[target]
shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
for d in ('css', 'js', 'data', 'img'): shutil.copytree(d, f'{out}/{d}', ignore=shutil.ignore_patterns('bg_src'))
if target != 'yandex': os.remove(f'{out}/js/adapters/yandex.js')
if target != 'web': os.remove(f'{out}/js/adapters/rsya.js')   # RSYA web ads: public web build only
if target != 'android' and target != 'web': pass
s = open('index.html', encoding='utf-8').read()
s = re.sub(r'\?v=\d+[a-z]?', '?v=' + V, s)
pre = f'<script>window.RELEASE=true;window.BUILD_V="{V}";</script>\n'
if target == 'yandex': pre = '<script src="/sdk.js"></script>\n' + pre
s = s.replace('<script src="data/words.js', pre + '<script src="data/words.js', 1)
if target == 'yandex': s = s.replace('<script src="js/adapters/android.js', f'<script src="js/adapters/yandex.js?v={V}"></script>\n<script src="js/adapters/android.js', 1)
if target == 'web':
    s = s.replace('<script src="js/adapters/android.js', f'<script src="js/adapters/rsya.js?v={V}"></script>\n<script src="js/adapters/android.js', 1)
    s = s.replace('<meta charset="utf-8">', '<meta charset="utf-8">\n<meta name="description" content="Мари филворд — бесплатная игра: ищи марийские слова змейкой на сетке, узнавай перевод. 1300+ уровней, 14 тем, три сложности.">\n<link rel="canonical" href="https://pirogovlab.ru/mari-filword/">', 1)
    ym = ('<script>(function(m,e,t,r,i,k,a){m[i]=m[i]||function(){(m[i].a=m[i].a||[]).push(arguments)};m[i].l=1*new Date();'
          'for(var j=0;j<document.scripts.length;j++){if(document.scripts[j].src===r){return;}}k=e.createElement(t),a=e.getElementsByTagName(t)[0],k.async=1,k.src=r,a.parentNode.insertBefore(k,a)})'
          '(window,document,"script","https://mc.yandex.ru/metrika/tag.js?id=108319724","ym");ym(108319724,"init",{ssr:true,clickmap:true,referrer:document.referrer,url:location.href,accurateTrackBounce:true,trackLinks:true});</script>\n'
          '<noscript><div><img src="https://mc.yandex.ru/watch/108319724" style="position:absolute;left:-9999px" alt=""></div></noscript>\n</body>')
    s = s.replace('</body>', ym, 1)
    shutil.copytree('site/privacy', out + '/privacy')
open(out + '/index.html', 'w', encoding='utf-8').write(s)
cfg = f'{out}/js/config.js'; c = open(cfg, encoding='utf-8').read()
api = {'yandex': "''", 'android': "'https://pirogovlab.ru/api/mari-filword/'", 'web': "'/api/mari-filword/'"}[target]
c = re.sub(r"lbApi: '[^']*'", 'lbApi: ' + api, c); open(cfg, 'w', encoding='utf-8').write(c)
if target == 'yandex':
    p = f'{out}/js/platform.js'; t = open(p, encoding='utf-8').read(); open(p, 'w', encoding='utf-8').write(t.replace("'https://pirogovlab.ru/mari-filword/'", 'null'))
bad = []
for dp, _, fs in os.walk(out):
    for f in fs:
        if not f.endswith(('.html', '.js', '.css')): continue
        p = os.path.join(dp, f); t = open(p, encoding='utf-8', errors='ignore').read()
        if re.search(r'marlamuter|марламутер', t, re.I): bad.append(p + ': forbidden mention')
        if target != 'web' and ('mc.yandex' in t or '108319724' in t): bad.append(p + ': Metrika outside web')
        if target != 'web' and ('adapters/rsya' in t or 'ads/system/context' in t or 'AdvManager' in t): bad.append(p + ': RSYA web ads outside web')
        if f.endswith('.html') and ('testBadge' in t or 'noindex' in t): bad.append(p + ': test marker')
        if target == 'yandex' and '/data/' not in p:
            for m in re.finditer(r'https?://[^\s"\'`<>)]+', t):
                if 'w3.org' not in m.group(0): bad.append(f'{p}: external ref {m.group(0)}')
if 'window.RELEASE=true' not in open(out + '/index.html').read(): bad.append('RELEASE flag missing')
if bad: print('\n'.join(bad)); sys.exit('build_release: ABORT')
size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(out) for f in fs)
print(f'build_release {target}: {out} v={V} {size/1e6:.1f} MB')
if target == 'yandex':
    z = 'release/mari-filword-yandex.zip'
    if os.path.exists(z): os.remove(z)
    with zipfile.ZipFile(z, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for dp, _, fs in os.walk(out):
            for f in sorted(fs): p = os.path.join(dp, f); zf.write(p, os.path.relpath(p, out))
    print(f'zip: {z} {os.path.getsize(z)/1e6:.2f} MB')
