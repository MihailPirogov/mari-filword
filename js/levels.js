/* Level catalogue: 3 difficulty modes, deterministic by (mode, number). Old saves: level number migrates to «Средний». */
(function () {
  const W = window.FW_WORDS, G = window.FW_GEN, NT = W.themes.length;
  const MIX = W.mixed, mixTop = k => MIX.slice(0, k);
  const MIXED_THEME = { id: 'mixed', mhr: 'Тӱрлӧ мут', name: 'Всё подряд', icon: '🎲', color: '#8a7c6c' };
  const MODES = {
    easy: { mhr: 'Куштылго', name: 'Лёгкий', sub: '4×4–5×5 · прямые слова · переводы видны', per: 20, mixed: 150, icon: '🌱' },
    mid:  { mhr: 'Кокла', name: 'Средний', sub: '5×5–7×7 · слова змейкой', per: 12, mixed: 250, icon: '🌿' },
    hard: { mhr: 'Неле', name: 'Сложный', sub: '7×7–10×10 · длинные слова, изломы', per: 15, mixed: 250, icon: '🌳' },
  };
  const MID_SIZES = [5, 5, 5, 5, 6, 6, 6, 6, 7, 7, 7, 7];
  const cap = W.themes.map(t => { const L = t.words.reduce((a, [w]) => a + Array.from(w).length, 0); return Math.max(5, Math.min(8, Math.floor(Math.sqrt(L * 0.8)))); });
  for (const k in MODES) { const m = MODES[k]; m.themed = NT * m.per; m.total = m.themed + m.mixed; }
  function info(mode, g) {
    const m = MODES[mode];
    if (g < m.themed) { const ti = Math.floor(g / m.per), k = g % m.per; return { mode, g, ti, theme: W.themes[ti], k, idx: k + 1, per: m.per, n: size(mode, k, ti) }; }
    const j = g - m.themed, n = mode === 'easy' ? (j % 3 === 2 ? 4 : 5) : mode === 'mid' ? 5 + (j % 3) : 8 + (j % 3);
    return { mode, g, ti: -1, theme: MIXED_THEME, k: j, idx: j < m.mixed ? j + 1 : null, per: m.mixed, n, mixed: true };
  }
  function size(mode, k, ti) {
    if (mode === 'easy') return k < 10 ? 4 : 5;
    if (mode === 'mid') return MID_SIZES[k];
    return k < 5 ? 7 : k < 11 ? 8 : 9;
  }
  // easy themes are small: generate the theme's levels in order and re-seed on a repeated word set (deterministic, ~2 ms per theme)
  const easyCache = {};
  function easyThemed(I) {
    const key = I.ti, c = easyCache[key] = easyCache[key] || { list: [], seen: new Set() };
    while (c.list.length <= I.k) {
      const k = c.list.length, n = size('easy', k, I.ti);
      for (let t = 0; ; t++) {
        const L = G.generate2({ primary: I.theme.words, secondary: mixTop(600), n, seed: (I.ti * 20 + k) * 7919 + 114 + t * 104729, straight: true, minL: 3, maxL: 5 });
        const sig = L && L.words.map(o => o.w).sort().join();
        if (L && (!c.seen.has(sig) || t > 30)) { c.seen.add(sig); c.list.push(L); break; }
      }
    }
    const L = c.list[I.k]; return { n: L.n, cells: L.cells.slice(), words: L.words.map(o => Object.assign({}, o, { path: o.path.slice() })) };
  }
  function make(mode, g) {
    const I = info(mode, g), seed = g * 7919 + 13 + (mode === 'easy' ? 101 : mode === 'hard' ? 202 : 0);
    if (mode === 'mid' && !I.mixed) return G.generate2({ primary: I.theme.words, secondary: W.filler, n: I.n, seed, minL: 3, maxL: 7, turn: 0.45 });
    if (mode === 'easy') return I.mixed
      ? G.generate2({ primary: MIX.slice((I.k * 37) % 400, (I.k * 37) % 400 + 500), secondary: mixTop(1200), n: I.n, seed, straight: true, minL: 3, maxL: 5 })
      : easyThemed(I);
    if (mode === 'mid') return G.generate2({ primary: MIX.slice((I.k * 53) % 1200, (I.k * 53) % 1200 + 900), secondary: MIX, n: I.n, seed, minL: 3, maxL: 7, turn: 0.45 });
    return I.mixed
      ? G.generate2({ primary: MIX.slice((I.k * 61) % 1500, (I.k * 61) % 1500 + 1300), secondary: MIX, n: I.n, seed, minL: 5, maxL: 9, turn: 0.85, lenBias: 2 })
      : G.generate2({ primary: I.theme.words.filter(([w]) => Array.from(w).length >= 4), secondary: MIX, n: I.n, seed, minL: 4, maxL: 9, turn: 0.85, lenBias: 2.5 });
  }
  window.FW_LEVELS = { MODES, info, make };
})();
