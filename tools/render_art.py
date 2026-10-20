# Render tools/art/*.html with Chrome → release/store/raw/ + Android mipmaps + img/icon.png
import asyncio, os, sys
from PIL import Image
from playwright.async_api import async_playwright
R = 'release/store/raw'; os.makedirs(R, exist_ok=True)
def url(f, q=''): return 'file://' + os.path.abspath('tools/art/' + f) + q
async def shot(b, f, w, h, out, q='', transparent=False):
    pg = await b.new_page(viewport={'width': w, 'height': h}); await pg.goto(url(f, q)); await pg.wait_for_timeout(600)
    await pg.screenshot(path=out, omit_background=transparent); await pg.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'])
        await shot(b, 'icon.html', 1024, 1024, '/tmp/icon_full.png')
        await shot(b, 'icon.html', 1024, 1024, '/tmp/icon_fg.png', '?fg=1&s=.6', True)
        await shot(b, 'icon.html', 1024, 1024, '/tmp/icon_bg.png', '?s=0.001')
        await b.close()
    full = Image.open('/tmp/icon_full.png').convert('RGB'); full.resize((512, 512), Image.LANCZOS).save(f'{R}/icon_512.png')
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'])
        for n, w, h in (('fg', 1024, 500), ('cover', 800, 470), ('showcase', 1560, 520), ('banner', 1920, 1080)):
            await shot(b, 'promo.html', w, h, f'{R}/{n}_{w}x{h}.png')
        await b.close()
asyncio.run(main())
full = Image.open('/tmp/icon_full.png').convert('RGB')
full.resize((512, 512), Image.LANCZOS).save(f'{R}/icon_512.png'); full.resize((192, 192), Image.LANCZOS).save('img/icon.png')
# rounded/round legacy icons + adaptive layers
mask_sq = Image.new('L', (1024, 1024), 0); from PIL import ImageDraw
ImageDraw.Draw(mask_sq).rounded_rectangle((0, 0, 1023, 1023), 180, fill=255)
mask_rd = Image.new('L', (1024, 1024), 0); ImageDraw.Draw(mask_rd).ellipse((0, 0, 1023, 1023), fill=255)
fg = Image.open('/tmp/icon_fg.png').convert('RGBA'); bg = Image.open('/tmp/icon_bg.png').convert('RGB')
small = Image.open('/tmp/icon_full.png').convert('RGBA')
for d, s in (('mdpi', 48), ('hdpi', 72), ('xhdpi', 96), ('xxhdpi', 144), ('xxxhdpi', 192)):
    o = f'android/app/src/main/res/mipmap-{d}/'
    sq = small.copy(); sq.putalpha(mask_sq); sq.resize((s, s), Image.LANCZOS).save(o + 'ic_launcher.png')
    rd = small.copy(); rd.putalpha(mask_rd); rd.resize((s, s), Image.LANCZOS).save(o + 'ic_launcher_round.png')
    a = int(s * 108 / 48); fg.resize((a, a), Image.LANCZOS).save(o + 'ic_launcher_foreground.png'); bg.resize((a, a), Image.LANCZOS).save(o + 'ic_launcher_background.png')
print('icons OK')
