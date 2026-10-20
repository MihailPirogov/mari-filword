// node test/levels_node.js — every level of every mode fills the grid; no duplicate word sets within a mode; timing
global.window = {}; const fs = require('fs');
for (const f of ['data/words.js', 'js/gen.js', 'js/levels.js']) eval(fs.readFileSync(f, 'utf8'));
const { MODES, make, info } = window.FW_LEVELS; let all = 0, bad = [];
for (const m in MODES) {
  const seen = new Map(); let themedWords = 0, worst = 0, sum = 0, theme = 0, words = 0, dups = [], wordsUsed = new Set(), straightBad = 0, sizes = {};
  for (let g = 0; g < MODES[m].total; g++) {
    const t0 = process.hrtime.bigint(), L = make(m, g), ms = Number(process.hrtime.bigint() - t0) / 1e6; worst = Math.max(worst, ms); sum += ms;
    if (!L || L.cells.some(x => !x)) { bad.push(m + g); continue; }
    const key = L.words.map(o => o.w).sort().join(); if (seen.has(key)) dups.push(g + '=' + seen.get(key)); seen.set(key, g);
    if (!info(m, g).mixed) themedWords += L.words.length; L.words.forEach(o => { words++; if (o.theme && !info(m, g).mixed) theme++; wordsUsed.add(o.w); });
    if (m === 'easy') L.words.forEach(o => { const d = o.path[1] - o.path[0]; if (!o.path.every((x, i) => !i || x - o.path[i - 1] === d) || (Math.abs(d) === 1 && Math.floor(o.path[0] / L.n) !== Math.floor(o.path[o.path.length - 1] / L.n))) straightBad++; });
    sizes[L.n] = (sizes[L.n] || 0) + 1;
  }
  all += MODES[m].total;
  console.log(m, 'levels', MODES[m].total, '(themed', MODES[m].themed + ', mixed', MODES[m].mixed + ')', 'sizes', JSON.stringify(sizes), 'unique words', wordsUsed.size, 'own-theme words in themed levels', (theme / Math.max(1, themedWords) * 100).toFixed(1) + '%', 'dups', dups.length, dups.slice(0, 5).join(' '), 'straightBad', straightBad, 'gen avg', (sum / MODES[m].total).toFixed(1), 'ms worst', worst.toFixed(0), 'ms');
  if (dups.length || straightBad) bad.push(m + ' dups/straight');
}
console.log('TOTAL', all, bad.length ? 'FAIL ' + bad.slice(0, 10) : 'OK'); process.exit(bad.length ? 1 : 0);
