# Images for the site pages → site_stage/out/mari-filword-igra/img/ and site_stage/out/blog/media/
import asyncio, os
from PIL import Image
from playwright.async_api import async_playwright
R = 'release/store/raw'; I = 'site_stage/out/mari-filword-igra/img/'; B = 'site_stage/out/blog/media/'
os.makedirs(I, exist_ok=True); os.makedirs(B, exist_ok=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'])
        for w, h, out in ((1200, 630, '/tmp/og.png'), (960, 640, '/tmp/card.png')):
            pg = await b.new_page(viewport={'width': w, 'height': h}); await pg.goto('file://' + os.path.abspath('tools/art/promo.html')); await pg.wait_for_timeout(600); await pg.screenshot(path=out); await pg.close()
        await b.close()
asyncio.run(main())
og = Image.open('/tmp/og.png').convert('RGB')
og.save(I + 'og-mari-filword.jpg', quality=86, optimize=True); og.save(B + 'mari-filword.jpg', quality=86, optimize=True)
og.resize((960, 504), Image.LANCZOS).crop((0, 0, 960, 504)).resize((960, 540)).save(B + 'mari-filword-thumb.webp', quality=82)
Image.open('/tmp/og.png').convert('RGB').resize((960, 540), Image.LANCZOS).save(B + 'mari-filword-thumb.webp', quality=82)
Image.open('/tmp/card.png').convert('RGB').resize((480, 320), Image.LANCZOS).save(I + 'kartochka-mari-filword.webp', quality=85)
Image.open(R + '/icon_512.png').resize((256, 256), Image.LANCZOS).save(I + 'logo.webp', quality=90)
Image.open(R + '/fg_1024x500.png').convert('RGB').save(I + 'feature-graphic.webp', quality=82)
for k in ('game', 'home', 'hard', 'win', 'leaderboard', 'tutorial'):
    f = [x for x in os.listdir(R) if x.startswith('mobile_') and x.endswith(f'_{k}.png')][0]
    Image.open(f'{R}/{f}').convert('RGB').resize((540, 960), Image.LANCZOS).save(f'{I}screen-{k}.webp', quality=80)
for k in ('game', 'home'):
    f = [x for x in os.listdir(R) if x.startswith('desktop_') and x.endswith(f'_{k}.png')][0]
    Image.open(f'{R}/{f}').convert('RGB').resize((1280, 720), Image.LANCZOS).save(f'{I}desktop-{k}.webp', quality=80)
for d in (I, B):
    for f in sorted(os.listdir(d)): print(d + f, os.path.getsize(d + f) // 1024, 'KB')
