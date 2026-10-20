/* Filword level generator: tiles an N×N grid completely with snake paths (orthogonal neighbours),
 * then fills each path with a word of that length (theme first, then filler pool). Deterministic per seed. */
(function () {
  function rng(seed) { let s = seed >>> 0 || 1; return () => { s ^= s << 13; s >>>= 0; s ^= s >> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; }; }
  const letters = w => Array.from(w);
  function nb(i, n) { const r = Math.floor(i / n), c = i % n, a = []; if (r) a.push(i - n); if (r < n - 1) a.push(i + n); if (c) a.push(i - 1); if (c < n - 1) a.push(i + 1); return a; }
  function compsOk(free, n, min) {  // every free region must be ≥ min cells
    const seen = new Set();
    for (const s of free) { if (seen.has(s)) continue; let sz = 0; const st = [s]; seen.add(s);
      while (st.length) { const x = st.pop(); sz++; for (const y of nb(x, n)) if (free.has(y) && !seen.has(y)) { seen.add(y); st.push(y); } }
      if (sz < min) return false; }
    return true;
  }
  function tile(n, lens, R) {  // lens: allowed lengths with weights {len: weight}
    for (let attempt = 0; attempt < 400; attempt++) {
      const free = new Set([...Array(n * n).keys()]), paths = []; let ok = true;
      while (free.size && ok) {
        // start at the free cell with fewest free neighbours (avoid stranding corners)
        let start = -1, best = 9; for (const x of free) { const k = nb(x, n).filter(y => free.has(y)).length + R() * 0.5; if (k < best) { best = k; start = x; } }
        const pool = []; for (const L in lens) if (+L <= free.size && (free.size - L === 0 || free.size - L >= 3)) for (let k = 0; k < lens[L]; k++) pool.push(+L);
        if (!pool.length) { ok = false; break; }
        let placed = null;
        for (let t = 0; t < 12 && !placed; t++) {
          const L = pool[Math.floor(R() * pool.length)], p = [start], used = new Set(p);
          while (p.length < L) { const c = nb(p[p.length - 1], n).filter(y => free.has(y) && !used.has(y)); if (!c.length) break; const y = c[Math.floor(R() * c.length)]; p.push(y); used.add(y); }
          if (p.length !== L) continue;
          const rest = new Set([...free].filter(x => !used.has(x)));
          if (compsOk(rest, n, 3)) placed = p;
        }
        if (!placed) { ok = false; break; }
        placed.forEach(x => free.delete(x)); paths.push(placed);
      }
      if (ok) return paths;
    }
    return null;
  }
  function generate(theme, filler, n, seed) {
    const R = rng(seed), byLen = {}, fillLen = {};
    theme.words.forEach(([w, g]) => { const L = letters(w).length; if (L <= n * 2) (byLen[L] = byLen[L] || []).push([w, g]); });
    filler.forEach(([w, g]) => { const L = letters(w).length; (fillLen[L] = fillLen[L] || []).push([w, g]); });
    const lens = {}; for (const L in byLen) lens[L] = byLen[L].length * 3;
    if (n >= 6) for (const L of [5, 6, 7]) if (fillLen[L]) lens[L] = (lens[L] || 0) + 2;   // longer words on big grids
    if (n <= 4) for (const L in lens) if (+L > 5) delete lens[L];
    for (let a = 0; a < 30; a++) {
      const paths = tile(n, lens, R); if (!paths) continue;
      const usedW = new Set(), words = []; let ok = true;
      for (const p of paths) {
        const pick = (arr) => { const c = (arr || []).filter(x => !usedW.has(x[0])); return c.length ? c[Math.floor(R() * c.length)] : null; };
        let w = pick(byLen[p.length]), th = true; if (!w) { w = pick(fillLen[p.length]); th = false; }
        if (!w) { ok = false; break; }
        usedW.add(w[0]); words.push({ w: w[0], g: w[1], path: R() < 0.5 ? p : p.slice().reverse(), theme: th });
      }
      if (!ok) continue;
      const cells = Array(n * n); words.forEach(o => { const ls = letters(o.w); o.path.forEach((x, i) => cells[x] = ls[i]); });
      return { n, cells, words };
    }
    return null;
  }
  /* generate2: modes «Лёгкий» (straight lines) and «Сложный» (long words, many bends).
   * o = {primary, secondary, n, seed, straight, minL, maxL, turn (0..1 bend preference), lenBias (prefer long)} */
  function tileStraight(n, lens, R) {
    const cells = new Array(n * n).fill(-1), paths = []; let steps = 0;
    const order = Object.keys(lens).map(Number);
    function rec() {
      if (++steps > 20000) return false;
      const s = cells.indexOf(-1); if (s < 0) return true;
      const r = Math.floor(s / n), c = s % n, opts = [];
      for (const L of order) for (const d of [1, n]) {
        if (d === 1 && c + L > n) continue; if (d === n && r + L > n) continue;
        let ok = true; for (let k = 0; k < L; k++) if (cells[s + k * d] !== -1) { ok = false; break; }
        if (ok) opts.push([L, d, lens[L] * (0.5 + R())]);
      }
      opts.sort((a, b) => b[2] - a[2]);
      for (const [L, d] of opts) {
        const p = []; for (let k = 0; k < L; k++) { p.push(s + k * d); cells[s + k * d] = paths.length; }
        paths.push(p); if (rec()) return true;
        paths.pop(); p.forEach(x => cells[x] = -1);
      }
      return false;
    }
    return rec() ? paths : null;
  }
  function tileSnake(n, lens, R, turn) {
    for (let attempt = 0; attempt < 300; attempt++) {
      const free = new Set([...Array(n * n).keys()]), paths = []; let ok = true;
      while (free.size && ok) {
        let start = -1, best = 9; for (const x of free) { const k = nb(x, n).filter(y => free.has(y)).length + R() * 0.5; if (k < best) { best = k; start = x; } }
        const pool = []; for (const L in lens) if (+L <= free.size && (free.size - L === 0 || free.size - L >= 3)) for (let k = 0; k < lens[L]; k++) pool.push(+L);
        if (!pool.length) { ok = false; break; }
        let placed = null;
        for (let t = 0; t < 14 && !placed; t++) {
          const L = pool[Math.floor(R() * pool.length)], p = [start], used = new Set(p);
          while (p.length < L) {
            const last = p[p.length - 1], c = nb(last, n).filter(y => free.has(y) && !used.has(y)); if (!c.length) break;
            let y;
            if (p.length >= 2 && c.length > 1) { const d = last - p[p.length - 2], bend = c.filter(z => z - last !== d), str = c.filter(z => z - last === d);
              const pickFrom = (R() < turn ? bend : str).length ? (R() < turn ? bend : str) : c; y = (pickFrom.length ? pickFrom : c)[Math.floor(R() * (pickFrom.length || c.length))]; }
            else y = c[Math.floor(R() * c.length)];
            p.push(y); used.add(y);
          }
          if (p.length !== L) continue;
          const rest = new Set([...free].filter(x => !used.has(x)));
          if (compsOk(rest, n, 3)) placed = p;
        }
        if (!placed) { ok = false; break; }
        placed.forEach(x => free.delete(x)); paths.push(placed);
      }
      if (ok) return paths;
    }
    return null;
  }
  function generate2(o) {
    const R = rng(o.seed), by = (arr) => { const m = {}; arr.forEach(([w, g]) => { const L = letters(w).length; if (L >= o.minL && L <= o.maxL) (m[L] = m[L] || []).push([w, g]); }); return m; };
    const P1 = by(o.primary), P2 = by(o.secondary || []), lens = {};
    for (let L = o.minL; L <= o.maxL; L++) { const c = (P1[L] || []).length * 3 + Math.min(20, (P2[L] || []).length); if (c) lens[L] = Math.max(1, Math.round(c * (o.lenBias ? Math.pow(L / o.minL, o.lenBias) : 1))); }
    for (let a = 0; a < 40; a++) {
      const paths = o.straight ? tileStraight(o.n, lens, R) : tileSnake(o.n, lens, R, o.turn || 0.4); if (!paths) continue;
      const usedW = new Set(), words = []; let ok = true;
      const pick = arr => { const c = (arr || []).filter(x => !usedW.has(x[0])); return c.length ? c[Math.floor(R() * Math.min(c.length, o.top || 1e9))] : null; };
      for (const p of paths) {
        let w = pick(P1[p.length]), th = true; if (!w) { w = pick(P2[p.length]); th = false; }
        if (!w) { ok = false; break; }
        usedW.add(w[0]); words.push({ w: w[0], g: w[1], path: R() < (o.straight ? 0.8 : 0.5) ? p : p.slice().reverse(), theme: th });
      }
      if (!ok) continue;
      const cells = Array(o.n * o.n); words.forEach(w => { const ls = letters(w.w); w.path.forEach((x, i) => cells[x] = ls[i]); });
      return { n: o.n, cells, words };
    }
    return null;
  }
  window.FW_GEN = { generate, generate2, nb };
})();
