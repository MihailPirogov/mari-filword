# Alternative paths: a planned word swiped over other cells is accepted (re-solve) or given as bonus — never «нет такого слова».
import asyncio, os
from playwright.async_api import async_playwright
ROOT = 'file://' + os.path.abspath('index.html')
ALT = '''(k)=>{const L=fw.L,n=L.n,o=L.words[k],a=[...o.w],orig=o.path.join(),rev=o.path.slice().reverse().join();let res=null;
 const nb=i=>{const r=Math.floor(i/n),c=i%n,q=[];if(r)q.push(i-n);if(r<n-1)q.push(i+n);if(c)q.push(i-1);if(c<n-1)q.push(i+1);return q};
 const dfs=p=>{if(res)return;if(p.length===a.length){const j=p.join();if(j!==orig&&j!==rev)res=p.slice();return}
  for(const y of nb(p[p.length-1]))if(!p.includes(y)&&L.cells[y]===a[p.length]){p.push(y);dfs(p);p.pop()}};
 for(let s=0;s<n*n&&!res;s++)if(L.cells[s]===a[0])dfs([s]);return res}'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'])
        pg = await (await b.new_context(viewport={'width': 390, 'height': 844})).new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(ROOT); await pg.wait_for_timeout(500); await pg.evaluate('fw.S.tut=true;document.getElementById("tSkip").click()')
        async def attempt(mode, g, k, path):
            await pg.evaluate(f'fw.setMode("{mode}");fw.M.found[{g}]=[];fw.M.bonus[{g}]=[];if(fw.M.paths)delete fw.M.paths[{g}];fw.start({g})')
            await pg.evaluate(f'fw.trySel({path})'); await pg.wait_for_timeout(30)
            tr = await pg.evaluate('document.getElementById("tr").textContent')
            found = await pg.evaluate(f'fw.M.found[{g}].includes({k})')
            bonus = await pg.evaluate(f'(fw.M.bonus[{g}]||[]).includes(fw.L.words[{k}].w)')
            assert 'нет' not in tr.lower() or 'спрятано' in tr, (mode, g, tr)
            assert found or (bonus and 'спрятано по-другому' in tr), (mode, g, k, tr)
            if found:   # grid must still be fully coverable: remaining words' paths spell them and tile the free cells
                ok = await pg.evaluate('''(()=>{const L=fw.L,c=new Set();for(const o of L.words){if(o.path.map(x=>L.cells[x]).join('')!==o.w)return false;o.path.forEach(x=>c.add(x))}return c.size===L.cells.length})()''')
                assert ok, ('broken tiling', mode, g)
            return 'found' if found else 'bonus'
        # 1) the reported case: «веҥе»
        case = None
        for mode in ('mid', 'easy', 'hard'):
            tot = await pg.evaluate(f'fw.MODES.{mode}.total')
            for g in range(tot):
                r = await pg.evaluate(f'fw.setMode("{mode}");fw.start({g});const k=fw.L.words.findIndex(o=>o.w==="веҥе");k<0?null:{{k,alt:({ALT})(k)}}')
                if r and r['alt']: case = (mode, g, r['k'], r['alt']); break
            if case: break
        assert case, 'no level with an alternative path for веҥе'
        res = await attempt(*case); await pg.screenshot(path='shots/alt_vene.png'); print('веҥе:', case[0], 'level', case[1] + 1, '→', res)
        # 2) general: every mode, every 3rd level, every planned word with an alternative path
        stats = {}
        for mode in ('easy', 'mid', 'hard'):
            tot = await pg.evaluate(f'fw.MODES.{mode}.total'); st = stats[mode] = {'found': 0, 'bonus': 0}
            for g in range(0, tot, 3):
                await pg.evaluate(f'fw.setMode("{mode}");fw.M.found[{g}]=[];if(fw.M.paths)delete fw.M.paths[{g}];fw.start({g})')
                alts = await pg.evaluate(f'fw.L.words.map((o,k)=>({ALT})(k))')
                for k, a in enumerate(alts):
                    if a: st[await attempt(mode, g, k, a)] += 1
        print('alt paths:', stats, 'errors', errs); assert not errs
        await b.close()
asyncio.run(main())
