# Gameplay video for Yandex Games: real play in the dev build (no ads, no browser UI) → release/store/yandex/gameplay_1920x1080.mp4 (≤28 s, H.264 + silent AAC)
import asyncio, os, glob, subprocess, shutil
from playwright.async_api import async_playwright
ROOT = 'file://' + os.path.abspath('index.html'); V = '/tmp/fwvid'; shutil.rmtree(V, ignore_errors=True)
async def swipe(pg, path, step=6):
    bx = [await (await pg.query_selector(f'.cell[data-i="{i}"]')).bounding_box() for i in path]
    c = lambda b: (b['x'] + b['width'] / 2, b['y'] + b['height'] / 2)
    await pg.mouse.move(*c(bx[0]), steps=8); await pg.mouse.down()
    for b in bx[1:]: await pg.mouse.move(*c(b), steps=step)
    await pg.mouse.up(); await pg.wait_for_timeout(450)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'])
        ctx = await b.new_context(viewport={'width': 1920, 'height': 1080}, record_video_dir=V, record_video_size={'width': 1920, 'height': 1080})
        pg = await ctx.new_page()
        await pg.goto(ROOT); await pg.evaluate('localStorage.setItem("mariFilword.v1",JSON.stringify({tut:true,mode:"mid",coins:120,m:{mid:{level:47}}}))')
        await pg.reload(); await pg.wait_for_timeout(2200)
        await pg.mouse.wheel(0, 500); await pg.wait_for_timeout(1300); await pg.mouse.wheel(0, -500); await pg.wait_for_timeout(700)
        await pg.click('#bPlay'); await pg.wait_for_timeout(1500)
        n = await pg.evaluate('fw.L.words.length')
        for k in range(n): await swipe(pg, await pg.evaluate(f'fw.L.words[{k}].path'))
        await pg.wait_for_timeout(3000)
        await pg.click('#bNext'); await pg.wait_for_timeout(1500)
        for k in range(2): await swipe(pg, await pg.evaluate(f'fw.L.words[{k}].path'))
        await pg.click('#bHint'); await pg.wait_for_timeout(1500)
        await ctx.close(); await b.close()
asyncio.run(main())
src = glob.glob(V + '/*.webm')[0]; out = 'release/store/yandex/gameplay_1920x1080.mp4'; os.makedirs(os.path.dirname(out), exist_ok=True)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '0.6', '-i', src, '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=stereo', '-t', '27.5',
                '-c:v', 'libx264', '-preset', 'slow', '-crf', '20', '-pix_fmt', 'yuv420p', '-r', '30', '-c:a', 'aac', '-shortest', '-movflags', '+faststart', out], check=True)
print(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size:stream=codec_name,width,height', '-of', 'compact', out], capture_output=True, text=True).stdout)
