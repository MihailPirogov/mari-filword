# Rules test: bonus words, palindromes (both directions), planned word on other cells → bonus. Shot: shots/bonus_word.png
import asyncio, os
from playwright.async_api import async_playwright
ROOT = 'file://' + os.path.abspath('index.html')
FIND = '''(mode)=>{ // DFS for a path spelling a dictionary word that is not a planned path
 for(let g=0;g<fw.TOTAL;g++){ fw.start(g); const L=fw.L,n=L.n,planned=new Set(L.words.map(o=>o.path.join())),pw=new Set(L.words.map(o=>o.w));
  const nb=i=>{const r=Math.floor(i/n),c=i%n,a=[];if(r)a.push(i-n);if(r<n-1)a.push(i+n);if(c)a.push(i-1);if(c<n-1)a.push(i+1);return a};
  let res=null; const dfs=(p)=>{ if(res)return; const w=p.map(i=>L.cells[i]).join('');
   if(p.length>=3){ const ok = mode==='planned' ? pw.has(w) : (fw.BONUS[w] && !pw.has(w));
     if(ok && !planned.has(p.join()) && !planned.has(p.slice().reverse().join())) {res=p.slice();return;} }
   if(p.length>=6)return; for(const y of nb(p[p.length-1])) if(!p.includes(y)){p.push(y);dfs(p);p.pop()} };
  for(let s=0;s<n*n&&!res;s++)dfs([s]); if(res) return {g,path:res,word:res.map(i=>L.cells[i]).join('')}; }
 return null }'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome', args=['--allow-file-access-from-files'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(ROOT); await pg.wait_for_timeout(500)
        await pg.evaluate('fw.S.tut=true;document.getElementById("tSkip").click()')
        # 1) bonus word
        r = await pg.evaluate(f'({FIND})("bonus")'); assert r, 'no bonus candidate'
        await pg.evaluate(f'fw.start({r["g"]})'); c0 = await pg.evaluate('fw.S.coins')
        await pg.evaluate(f'fw.trySel({r["path"]})'); await pg.wait_for_timeout(300)
        assert await pg.evaluate('fw.S.coins') == c0 + 5, 'bonus coins'
        assert await pg.evaluate(f'(fw.M.bonus[{r["g"]}]||[]).includes("{r["word"]}")')
        assert await pg.evaluate('document.querySelectorAll(".cell.done").length') == 0, 'bonus must not colour cells'
        txt = await pg.evaluate('document.getElementById("tr").textContent'); assert 'Бонусное слово' in txt, txt
        assert '★ бонус: 1' in await pg.evaluate('document.getElementById("bonusCnt").textContent')
        await pg.screenshot(path='shots/bonus_word.png')
        await pg.evaluate(f'fw.trySel({r["path"]})'); assert await pg.evaluate('fw.S.coins') == c0 + 5, 'bonus counted twice'
        print('bonus OK:', r['word'], 'level', r['g'] + 1)
        # 2) palindrome planned word in reverse
        pal = await pg.evaluate('''(()=>{for(let g=0;g<fw.TOTAL;g++){fw.start(g);const k=fw.L.words.findIndex(o=>{const a=[...o.w];return a.length>=3&&a.join('')===a.reverse().join('')});if(k>=0)return {g,k,w:fw.L.words[k].w}}return null})()''')
        assert pal, 'no palindrome in levels'
        await pg.evaluate(f'fw.start({pal["g"]});fw.M.found[{pal["g"]}]=[];fw.start({pal["g"]})')
        await pg.evaluate(f'fw.trySel(fw.L.words[{pal["k"]}].path.slice().reverse())')
        assert await pg.evaluate(f'fw.M.found[{pal["g"]}].includes({pal["k"]})'), 'palindrome reverse not accepted'
        print('palindrome OK:', pal['w'], 'level', pal['g'] + 1)
        # 3) non-palindrome planned word reversed must NOT count as planned
        np_ = await pg.evaluate('''(()=>{fw.start(0);fw.M.found[0]=[];fw.start(0);const k=fw.L.words.findIndex(o=>{const a=[...o.w];return a.join('')!==a.slice().reverse().join('')});fw.trySel(fw.L.words[k].path.slice().reverse());return fw.M.found[0].includes(k)})()''')
        assert not np_, 'reversed non-palindrome accepted'
        # 4) planned letters on other cells → bonus
        r2 = await pg.evaluate(f'({FIND})("planned")')
        if r2:
            await pg.evaluate(f'fw.start({r2["g"]})'); c1 = await pg.evaluate('fw.S.coins'); f1 = await pg.evaluate(f'fw.M.found[{r2["g"]}].length')
            await pg.evaluate(f'fw.trySel({r2["path"]})')
            assert await pg.evaluate('fw.S.coins') == c1 + 5 and await pg.evaluate(f'fw.M.found[{r2["g"]}].length') == f1, 'planned-elsewhere not bonus'
            print('planned-on-other-cells → bonus OK:', r2['word'], 'level', r2['g'] + 1)
        else: print('planned-on-other-cells: no such case in 168 levels (rule still in code)')
        # 5) win dialog shows bonus counter
        await pg.evaluate(f'fw.start({r["g"]});fw.solveAll()'); await pg.wait_for_timeout(1200)
        wb = await pg.evaluate('document.getElementById("winBonus").textContent'); assert 'Бонусных слов:' in wb and 'аше' in wb or r['word'] in wb, wb
        print('win bonus OK; errors:', errs); assert not errs
        await b.close()
asyncio.run(main())
