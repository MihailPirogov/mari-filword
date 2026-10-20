/* Мари филворд — Mari filword. State: localStorage 'mariFilword.v1'. */
(function () {
  'use strict';
  const W = window.FW_WORDS, G = window.FW_GEN, P = window.Platform, $ = id => document.getElementById(id);
  const BONUS = window.FW_BONUS || {}, BONUS_COINS = 5, THEMEW = {};
  window.FW_WORDS.themes.forEach(t => t.words.forEach(([w, g]) => THEMEW[w] = g)); (window.FW_WORDS.mixed || []).forEach(([w, g]) => { if (!THEMEW[w]) THEMEW[w] = g; });
  const KEY = 'mariFilword.v1', HINT_COST = 30, LV = window.FW_LEVELS, MODES = LV.MODES;
  const COLORS = ['#ef6f6c', '#4fa3e0', '#5cbf72', '#f5a623', '#a97bd8', '#2fbfb3', '#ec6aa0', '#8cc152', '#f0c419', '#7b8ce0', '#e8833a', '#3fb0d9', '#c46fbf', '#58b88a', '#d9a53f', '#6c9bd2'];
  let S = Object.assign({ coins: 60, wins: 0, lastAd: 0, learned: {}, tut: false, mode: 'mid', m: null }, P.storage.load(KEY) || {});
  if (!S.m) {   // migration: old single progress → «Средний» (level number kept; per-level found lists reset, levels were regenerated)
    S.m = { easy: { level: 0 }, mid: { level: S.level || 0 }, hard: { level: 0 } };
    if (S.level) S.mode = 'mid';
    delete S.level; delete S.found; delete S.hints; delete S.bonus;
  }
  for (const k in MODES) S.m[k] = Object.assign({ level: 0, found: {}, hints: {}, bonus: {} }, S.m[k]);
  if (!MODES[S.mode]) S.mode = 'mid';
  const M = () => S.m[S.mode];
  const LB = window.FW_LB; let lvlPts = 0;
  let cloudT = 0;
  const progress = o => { try { return Object.values(o.m || {}).reduce((a, m) => a + (m.level || 0), 0) * 1000 + ((o.lb && o.lb.total) || 0); } catch (e) { return 0; } };
  // sounds (js/sound.js); S.sound = false → muted by the 🔊 toggle
  const snd = (k, a) => { try { if (window.Sound) Sound[k](a); } catch (e) {} };
  const sndBtn = () => { const b = $('bSnd'); if (b) { b.textContent = S.sound === false ? '🔇' : '🔊'; b.setAttribute('aria-label', S.sound === false ? 'Включить звук' : 'Выключить звук'); } };
  if (window.Sound) Sound.enabled = S.sound !== false;
  const save = () => { S.t = Date.now(); P.storage.save(KEY, S);
    if (P.cloud && P.cloud.available) { clearTimeout(cloudT); cloudT = setTimeout(() => { try { P.cloud.push(S); } catch (e) {} }, 3000); } };   // cloud save (Yandex Games), debounced
  LB.attach(S, save, () => S.mode);
  const levelInfo = g => LV.info(S.mode, g);
  let L = null, lvl = null, sel = [], dragging = false, cellEls = [], centers = [];
  const BG_IDS = new Set((window.FW_CONFIG && window.FW_CONFIG.photos) || []);
  function setBg(i, mixed) {
    const t = W.themes[Math.max(0, i - 1)] || W.themes[0], id = mixed ? 'mixed' : i ? t.id : 'main';
    document.body.style.setProperty('--accent', i ? t.color : '#d8573c'); document.body.dataset.theme = id;
    const bg = $('bg');
    if (!BG_IDS.has(id)) { bg.style.backgroundImage = ''; return; }          // illustrated scene (css) until a photo exists
    const url = 'img/bg/' + id + '.webp', im = new Image();                   // lazy: only the current screen's photo is loaded
    im.onload = () => { if (document.body.dataset.theme === id) bg.style.backgroundImage = `url(${url})`; }; im.src = url;
  }
  function coins(bump) { document.querySelectorAll('.coins b').forEach(b => b.textContent = S.coins); if (bump) document.querySelectorAll('.coins').forEach(c => { c.classList.remove('bump'); void c.offsetWidth; c.classList.add('bump'); }); }
  function show(id) { document.querySelectorAll('.screen').forEach(s => s.classList.toggle('on', s.id === id)); try { id === 'scrGame' ? P.gameplay.start() : P.gameplay.stop(); } catch (e) {} }
  let trT = 0;
  function tr(html, color, info) { const e = $('tr'); clearTimeout(trT); e.innerHTML = html ? `<div class="tc${info ? ' info' : ''}" style="--wc:${color || '#f0a530'}">${html}</div>` : ''; if (html && info) trT = setTimeout(() => tr(''), 2200); }

  /* ---------- HOME ---------- */
  function home() {
    setBg(0); coins(); show('scrHome'); tr('');
    const md = MODES[S.mode], lv = M().level, cur = levelInfo(lv), per = md.per;
    $('modes').innerHTML = Object.keys(MODES).map(k => `<button class="md ${k === S.mode ? 'on' : ''}" data-m="${k}"><b>${MODES[k].mhr}</b><i>${MODES[k].name}</i><small>${Math.min(S.m[k].level, MODES[k].total)} / ${MODES[k].total}</small></button>`).join('');
    $('modeSub').textContent = md.sub; $('hScore').textContent = '🏆 ' + S.lb.total;
    $('modes').querySelectorAll('.md').forEach(b => b.onclick = () => { S.mode = b.dataset.m; save(); home(); });
    $('playLvl').textContent = cur.idx ? cur.theme.mhr + ' (' + cur.theme.name + ')' + ' · уровень ' + cur.idx + '/' + cur.per : 'Бесконечный режим · ' + (lv + 1);
    $('pcIcon').textContent = cur.theme.icon;
    const cards = W.themes.map((t, i) => ({ t, start: i * per, len: per, words: t.words.length + ' слов' }));
    cards.push({ t: { mhr: 'Тӱрлӧ мут', name: 'Всё подряд', icon: '🎲', color: '#8a7c6c' }, start: md.themed, len: md.mixed, words: md.mixed + ' уровней' });
    $('themes').innerHTML = cards.map((c, i) => {
      const done = Math.max(0, Math.min(c.len, lv - c.start)), open = lv >= c.start, isCur = lv >= c.start && lv < c.start + c.len;
      return `<button class="th ${open ? '' : 'lock'} ${isCur ? 'now' : ''}" data-i="${i}" style="--tc:${c.t.color}"><span class="ic">${c.t.icon}</span><span class="tn"><b>${c.t.mhr}</b><i>${c.t.name}</i></span><small>${open ? (done === c.len ? '✓ пройдено' : done + ' из ' + c.len) : c.words}</small><span class="bar"><i style="width:${done / c.len * 100}%"></i></span></button>`;
    }).join('');
    renderMap(cards, lv);
    $('themes').querySelectorAll('.th').forEach(b => b.onclick = () => { const c = cards[+b.dataset.i]; if (lv < c.start) return toastHome('Сначала пройди предыдущие темы'); start(Math.min(lv, c.start + c.len - 1)); });
  }
  // «new» design: themes are stops on a winding road through the Mari land
  function renderMap(cards, lv) {
    const H = 112, W = 340, pts = cards.map((c, i) => [i % 2 ? W - 45 : 45, 60 + i * H]);
    let d = `M${pts[0][0]} ${pts[0][1]}`; for (let i = 1; i < pts.length; i++) { const a = pts[i - 1], b = pts[i]; d += ` C${a[0]} ${a[1] + H * .6} ${b[0]} ${b[1] - H * .6} ${b[0]} ${b[1]}`; }
    const done = cards.findIndex(c => lv < c.start + c.len); const k = done < 0 ? cards.length - 1 : done;
    let dd = `M${pts[0][0]} ${pts[0][1]}`; for (let i = 1; i <= k; i++) { const a = pts[i - 1], b = pts[i]; dd += ` C${a[0]} ${a[1] + H * .6} ${b[0]} ${b[1] - H * .6} ${b[0]} ${b[1]}`; }
    const svg = `<svg class="road" viewBox="0 0 ${W} ${60 + cards.length * H}" preserveAspectRatio="xMidYMin meet"><path d="${d}" class="r1"/><path d="${d}" class="r2"/><path d="${dd}" class="r3"/></svg>`;
    const th = $('themes'); th.classList.add('map'); th.style.height = (60 + cards.length * H) + 'px';
    th.insertAdjacentHTML('afterbegin', svg);
    th.querySelectorAll('.th').forEach((b, i) => { b.style.left = (pts[i][0] / W * 100) + '%'; b.style.top = pts[i][1] + 'px'; b.classList.toggle('right', i % 2 === 1); });
  }
  function toastHome(t) { const b = $('playLvl'), o = b.textContent; b.textContent = t; setTimeout(() => b.textContent = o, 1600); }

  /* ---------- GAME ---------- */
  function start(g) {
    lvl = levelInfo(g); L = LV.make(S.mode, g);
    const sp = (M().paths || {})[g]; if (sp && sp.length === L.words.length) sp.forEach((p, k) => { if (p.every(x => x < L.cells.length) && p.map(x => L.cells[x]).join('') === L.words[k].w) L.words[k].path = p; });
    lvlPts = 0; M().found[g] = M().found[g] || []; setBg(lvl.ti + 1, lvl.mixed); tr(''); sel = []; $('win').classList.remove('on');
    $('gTheme').textContent = lvl.theme.mhr; $('gRu').textContent = lvl.theme.name; $('gIcon').textContent = lvl.theme.icon;
    $('gLvl').textContent = MODES[S.mode].name + ' · ' + (lvl.idx ? lvl.idx + ' из ' + lvl.per : 'уровень ' + (g + 1)) + ' · ' + lvl.n + '×' + lvl.n;
    document.body.dataset.mode = S.mode;
    const grid = $('grid'); grid.style.setProperty('--n', lvl.n); grid.style.setProperty('--gap', (lvl.n > 6 ? 5 : 7) + 'px'); grid.innerHTML = '';
    cellEls = L.cells.map((ch, i) => { const d = document.createElement('div'); d.className = 'cell'; d.textContent = ch.toUpperCase(); d.dataset.i = i; grid.appendChild(d); return d; });
    show('scrGame'); measure();
    M().found[g].forEach(wi => markFound(wi, false)); (M().hints[g] || []).forEach(hintMark);
    drawLines(); renderFound(); coins(); paintSel();
    if (!S.tut && g === 0) setTimeout(() => Tut.start(), 400);
  }
  function measure() { const b = $('board').getBoundingClientRect(); centers = cellEls.map(c => { const r = c.getBoundingClientRect(); return [r.left - b.left + r.width / 2, r.top - b.top + r.height / 2, r.width]; }); }
  window.addEventListener('resize', () => { if (L) { measure(); drawLines(); } });
  const color = wi => COLORS[wi % COLORS.length];
  function markFound(wi, anim) {
    L.words[wi].path.forEach((x, k) => { const c = cellEls[x]; c.classList.add('done'); c.style.setProperty('--wc', color(wi)); if (anim) { c.style.animationDelay = k * 55 + 'ms'; c.classList.remove('pop'); void c.offsetWidth; c.classList.add('pop'); } });
  }
  function hintMark(wi) { if (!M().found[lvl.g].includes(wi)) cellEls[L.words[wi].path[0]].classList.add('hint'); }
  const pts = path => path.map(i => centers[i][0].toFixed(1) + ',' + centers[i][1].toFixed(1)).join(' ');
  function drawLines() {
    if (!centers.length) return; const w = centers[0][2], f = M().found[lvl.g];
    let s = f.map(wi => `<polyline class="wl" points="${pts(L.words[wi].path)}" stroke-width="${(w * 0.16).toFixed(1)}"/>`).join('');
    if (sel.length) s += `<polyline class="selline" points="${pts(sel)}" stroke-width="${(w * 0.42).toFixed(1)}"/><circle class="dot" cx="${centers[sel[sel.length - 1]][0]}" cy="${centers[sel[sel.length - 1]][1]}" r="${(w * 0.09).toFixed(1)}"/>`;
    $('lines').innerHTML = s;
  }
  function renderFound() {
    const f = M().found[lvl.g], n = L.words.length;
    $('found').innerHTML = L.words.map((o, i) => f.includes(i)
      ? `<span class="w ok" style="--wc:${color(i)}"><i></i><b>${o.w}</b><em>${o.g}</em></span>`
      : S.mode === 'easy' ? `<span class="w hintw">${'•'.repeat(Array.from(o.w).length)} <em>${o.g}</em></span>` : S.mode === 'hard' ? `<span class="w">?</span>` : `<span class="w">${'•'.repeat(Array.from(o.w).length)}</span>`).join('');
    const nb = (M().bonus[lvl.g] || []).length; $('bonusCnt').textContent = '★ бонус: ' + nb; $('bonusCnt').classList.toggle('has', nb > 0);
    $('progBar').style.width = (f.length / n * 100) + '%'; $('progTxt').textContent = f.length + ' / ' + n;
  }
  /* swipe (pointer events: finger + mouse); swipe back over the previous cell = undo */
  const cellAt = (x, y) => { const e = document.elementFromPoint(x, y); return e && e.classList && e.classList.contains('cell') ? +e.dataset.i : -1; };
  function paintSel(state) {
    cellEls.forEach(c => c.classList.remove('sel')); sel.forEach(i => cellEls[i].classList.add('sel'));
    const c = $('cur'); c.textContent = sel.map(i => L.cells[i]).join('').toUpperCase(); c.className = 'cur' + (sel.length || state ? ' on' : '') + (state ? ' ' + state : '');
    drawLines();
  }
  function addCell(i) {
    if (i < 0) return;   // found (coloured) cells may be crossed too: the word is then checked as a bonus word
    if (sel.length > 1 && sel[sel.length - 2] === i) { sel.pop(); return paintSel(); }
    if (sel.includes(i) || (sel.length && !G.nb(sel[sel.length - 1], lvl.n).includes(i))) return;
    sel.push(i); paintSel(); snd('letter', sel.length - 1); try { P.haptic(8); } catch (e) {}
  }
  const grid = $('grid');
  grid.addEventListener('pointerdown', e => { e.preventDefault(); try { Sound.unlock(); } catch (x) {} dragging = true; sel = []; measure(); addCell(cellAt(e.clientX, e.clientY)); });
  window.addEventListener('pointermove', e => { if (dragging) addCell(cellAt(e.clientX, e.clientY)); });
  window.addEventListener('pointerup', () => { if (!dragging) return; dragging = false; check(); });
  grid.addEventListener('touchmove', e => e.preventDefault(), { passive: false });
  function check() {
    const word = sel.map(i => L.cells[i]).join(''), f = M().found[lvl.g];
    const same = (a, b) => a.length === b.length && a.every((x, j) => x === b[j]);
    const isPal = w => { const a = Array.from(w); return a.join('') === a.slice().reverse().join(''); };
    // planned word: exact cells in order; palindromes also in reverse order
    const wi = L.words.findIndex((o, k) => !f.includes(k) && (same(o.path, sel) || (isPal(o.w) && same(o.path.slice().reverse(), sel))));
    if (wi >= 0) {
      const o = L.words[wi]; f.push(wi); markFound(wi, true); S.learned[o.w] = o.g; lvlPts += LB.add('word'); save();
      sel = []; paintSel('good'); $('cur').textContent = o.w.toUpperCase(); setTimeout(() => { if (!sel.length) $('cur').className = 'cur'; }, 700);
      renderFound(); tr(`<b>${o.w}</b><span>— ${o.g}</span>`, color(wi)); if (f.length < L.words.length) snd('word');
      Tut.event('found');
      if (f.length === L.words.length) setTimeout(win, 800);
      return;
    }
    const B = M().bonus[lvl.g] = M().bonus[lvl.g] || [];
    const ki = L.words.findIndex((o, k) => !f.includes(k) && o.w === word);
    if (ki >= 0 && !sel.some(i => cellEls[i].classList.contains('done'))) {
      // unfound planned word on other cells: accept it if the remaining cells can be re-split into the remaining words
      const sol = resolve(ki, sel);
      if (sol) {
        sol.forEach((p, k) => { if (p) L.words[k].path = p; });
        (M().paths = M().paths || {})[lvl.g] = L.words.map(o => o.path); save();
        cellEls.forEach(c => c.classList.remove('hint')); (M().hints[lvl.g] || []).forEach(hintMark);
        sel = L.words[ki].path.slice(); return check();
      }
    }
    const planned = L.words.find(o => o.w === word);
    const bg = planned ? planned.g : (BONUS[word] || THEMEW[word]);
    if (sel.length >= 3 && bg) {   // real dictionary word (bonus): cells stay uncoloured
      const keep = sel; sel = []; paintSel('good'); $('cur').textContent = keep.map(i => L.cells[i]).join('').toUpperCase(); setTimeout(() => { if (!sel.length) $('cur').className = 'cur'; }, 700);
      const elsewhere = planned && !f.includes(L.words.indexOf(planned));
      if (B.includes(word)) { tr(elsewhere ? `Слово <b>${word}</b> есть, но здесь оно спрятано по-другому` : `Бонусное слово <b>${word}</b> уже найдено`, '', true); return; }
      snd('bonus'); setTimeout(() => snd('coin'), 260); B.push(word); S.coins += BONUS_COINS; S.learned[word] = bg; lvlPts += LB.add('bonus'); save(); coins(true); renderFound();
      tr(elsewhere
        ? `<span class="bw"><small>★ Слово есть, но здесь оно спрятано по-другому · +${BONUS_COINS}</small><span><b>${word}</b> — ${bg}</span></span>`
        : `<span class="bw"><small>★ Бонусное слово · +${BONUS_COINS}</small><span><b>${word}</b> — ${bg}</span></span>`, '#f0c419', true);
      return;
    }
    if (sel.length > 1) {
      tr('Такого слова здесь нет', '', true); snd('wrong');
      $('board').classList.add('shake'); setTimeout(() => $('board').classList.remove('shake'), 350);
      const keep = sel; sel = []; paintSel('bad'); $('cur').textContent = keep.map(i => L.cells[i]).join('').toUpperCase(); setTimeout(() => { if (!sel.length) $('cur').className = 'cur'; }, 600);
      return;
    }
    sel = []; paintSel();
  }
  // solver: can the unfound cells (minus `path`) be split into the other unfound words? returns new paths or null
  function resolve(ki, path) {
    const f = M().found[lvl.g], n = lvl.n, free = new Set();
    L.words.forEach((o, k) => { if (!f.includes(k)) o.path.forEach(x => free.add(x)); });
    if (!path.every(x => free.has(x))) return null;
    path.forEach(x => free.delete(x));
    const rest = L.words.map((o, k) => k).filter(k => k !== ki && !f.includes(k)).sort((a, b) => Array.from(L.words[b].w).length - Array.from(L.words[a].w).length);
    const out = []; out[ki] = path.slice(); let steps = 0;
    const paths = (w) => { const a = Array.from(w), res = [];
      const dfs = p => { if (steps++ > 300000) return; if (p.length === a.length) { res.push(p.slice()); return; }
        for (const y of G.nb(p[p.length - 1], n)) if (free.has(y) && !p.includes(y) && L.cells[y] === a[p.length]) { p.push(y); dfs(p); p.pop(); } };
      for (const x of free) if (L.cells[x] === a[0]) dfs([x]); return res; };
    const rec = i => {
      if (i === rest.length) return free.size === 0;
      const k = rest[i];
      for (const p of paths(L.words[k].w)) { p.forEach(x => free.delete(x)); out[k] = p; if (rec(i + 1)) return true; p.forEach(x => free.add(x)); }
      return false;
    };
    return rec(0) && steps <= 300000 ? out : null;
  }
  function useHint() {
    const f = M().found[lvl.g], h = M().hints[lvl.g] = M().hints[lvl.g] || [];
    const wi = L.words.findIndex((o, k) => !f.includes(k) && !h.includes(k));
    if (wi < 0) { const r = L.words.findIndex((o, k) => !f.includes(k)); if (r < 0) return false; sel = L.words[r].path.slice(); check(); return true; }
    h.push(wi); hintMark(wi); save(); tr(`Первая буква: <b>${L.words[wi].w[0].toUpperCase()}</b><span>· ${L.words[wi].g}</span>`, color(wi)); return true;
  }
  $('bHint').onclick = () => { if (S.coins < HINT_COST) return tr('Мало монет — посмотри рекламу 🎬', '', true); if (useHint()) { snd('hint'); S.coins -= HINT_COST; save(); coins(true); Tut.event('hint'); } };
  $('bAdHint').onclick = async () => {
    if (!P.ads.rewardedAvailable()) return tr('Реклама сейчас недоступна', '', true);
    P.gameplay.stop(); const ok = await P.ads.showRewarded(); P.gameplay.start(); if (ok) useHint();
  };
  function confetti() { const b = $('burst'); b.innerHTML = ''; for (let i = 0; i < 40; i++) { const e = document.createElement('i'); const a = Math.random() * Math.PI * 2, d = 120 + Math.random() * 160; e.style.cssText = `background:${COLORS[i % COLORS.length]};--x:${Math.cos(a) * d}px;--y:${Math.sin(a) * d + 80}px;--r:${Math.random() * 720}deg;animation-delay:${Math.random() * .2}s`; b.appendChild(e); } }
  function win() {
    const g = lvl.g, prize = 10 + lvl.n * 2; lvlPts += LB.add('win'); $('winScore').textContent = '🏆 +' + lvlPts + ' очков · всего ' + S.lb.total; LB.submit(); S.coins += prize; S.wins++; if (M().level === g) M().level = g + 1; save(); coins(true);
    $('winTheme').innerHTML = `<b>${lvl.theme.mhr}</b><i>${lvl.theme.name}</i>`;
    $('winTxt').textContent = `Найдено слов: ${L.words.length} · +${prize} монет`;
    const bw = M().bonus[g] || []; $('winBonus').innerHTML = bw.length ? '★ Бонусных слов: ' + bw.length + ' (' + bw.join(', ') + ')' : '';
    $('winWords').innerHTML = L.words.map((o, i) => `<div style="--wc:${color(i)}"><b>${o.w}</b>${o.g}</div>`).join('');
    $('win').classList.add('on'); snd('win'); setTimeout(() => snd('coin'), 900); confetti(); tr(''); P.gameplay.stop();
  }
  $('bNext').onclick = async () => {
    $('win').classList.remove('on');
    if (S.wins % 3 === 0 && Date.now() - S.lastAd > 150000 && P.ads.interstitialAvailable()) { S.lastAd = Date.now(); save(); await P.ads.showInterstitial(); }  // every 3rd win, ≥150 s
    start(lvl.g + 1);
  };

  /* ---------- TUTORIAL (first launch; replay: «Как играть») ---------- */
  const Tut = (function () {
    let step = -1, anim = null, spot = null;
    const STEPS = [
      { txt: 'Проведи пальцем по буквам, чтобы собрать слово. Буквы идут <b>змейкой</b> — вверх, вниз, вбок, но не по диагонали.', wait: 'found', finger: true, at: 'bottom' },
      { txt: 'Отлично! Под сеткой — <b>перевод</b> найденного слова на русский. Все найденные слова собираются в список.', spot: 'tr', at: 'top' },
      { txt: 'Каждая клетка — часть какого-то слова. Найди все слова, и уровень пройден!', spot: 'board', at: 'bottom' },
      { txt: 'Застрял? <b>Подсказка</b> покажет первую букву слова и его перевод.', spot: 'bHint', at: 'top', last: true },
    ];
    let hole = null, follow = null;
    function clear() { cancelAnimationFrame(anim); anim = null; cancelAnimationFrame(follow); follow = null; $('finger').style.opacity = 0; if (spot) spot.classList.remove('spot'); spot = null; }
    // spotlight: a fixed «hole» over the target (dims everything else via huge box-shadow), bubble placed above/below the target
    function place(el) {
      if (!hole) { hole = document.createElement('div'); hole.id = 'spotHole'; $('tut').prepend(hole); }
      const card = $('tcard'), vh = innerHeight, pad = 8;
      const r = el ? el.getBoundingClientRect() : null;
      if (r) Object.assign(hole.style, { display: 'block', left: r.left - pad + 'px', top: r.top - pad + 'px', width: r.width + 2 * pad + 'px', height: r.height + 2 * pad + 'px' });
      else hole.style.display = 'none';
      const ch = card.offsetHeight, gap = 14;
      let top;
      if (!r) top = vh - ch - 24;
      else if (r.bottom + pad + gap + ch <= vh - 8) top = r.bottom + pad + gap;              // below the target
      else if (r.top - pad - gap - ch >= 8) top = r.top - pad - gap - ch;                    // above the target
      else top = (r.top + r.height / 2 > vh / 2) ? 8 : vh - ch - 8;                          // target is huge: farthest edge
      card.style.bottom = ''; card.style.top = Math.round(top) + 'px';
    }
    function fingerLoop() {
      const o = L.words.find((w, k) => !M().found[lvl.g].includes(k)); if (!o) return;
      const f = $('finger'), b = $('board').getBoundingClientRect(), p = o.path.map(i => [b.left + centers[i][0], b.top + centers[i][1]]);
      const T0 = performance.now(), seg = 450, total = seg * (p.length - 1) + 1200;
      const tick = t => {
        const e = Math.max(0, t - T0) % total, k = Math.min(p.length - 1, e / seg), i = Math.floor(k), fr = k - i;
        const a = p[i], c = p[Math.min(i + 1, p.length - 1)];
        f.style.left = (a[0] + (c[0] - a[0]) * fr) + 'px'; f.style.top = (a[1] + (c[1] - a[1]) * fr) + 'px';
        f.style.opacity = e > seg * (p.length - 1) + 700 ? 0 : 1; anim = requestAnimationFrame(tick);
      };
      anim = requestAnimationFrame(tick);
    }
    function render() {
      clear(); const s = STEPS[step]; $('tut').classList.add('on'); $('tTxt').innerHTML = s.txt;
      $('tNext').style.display = s.wait ? 'none' : ''; $('tNext').textContent = s.last ? 'Играть!' : 'Дальше';
      if (s.finger) fingerLoop();
      const tgt = $(s.spot || 'board'); if (s.spot) { spot = tgt; spot.classList.add('spot'); }
      const loop = () => { place(tgt); follow = requestAnimationFrame(loop); }; loop();
    }
    function next() { step++; if (step >= STEPS.length) return end(); render(); }
    function end() { setTimeout(updBanner, 0); clear(); if (hole) hole.style.display = 'none'; step = -1; $('tut').classList.remove('on'); S.tut = true; save(); }
    $('tNext').onclick = next; $('tSkip').onclick = end;
    return {
      start() { step = -1; next(); },
      event(name) { if (step >= 0 && STEPS[step].wait === name) setTimeout(next, 500); },
      get step() { return step; },
    };
  })();
  function howTo() { M().found[0] = []; M().hints[0] = []; S.tut = true; start(0); Tut.start(); }  // replay on level 1 (overall progress kept)
  $('bHow').onclick = $('bHow2').onclick = howTo;

  /* leaderboard modal */
  let lbPeriod = 'week';
  async function lbShow() {
    $('lbm').classList.add('on'); $('lbName').value = S.lb.name || ''; $('lbDel').hidden = !S.lb.name || LB.kind !== 'server'; $('lbErr').textContent = ''; $('lbNick').hidden = LB.kind === 'yandex';
    document.querySelectorAll('#lbm .tab').forEach(t => t.classList.toggle('on', t.dataset.p === lbPeriod));
    $('lbList').innerHTML = '<li class="load">Загрузка…</li>';
    const b = await LB.board(lbPeriod);
    $('lbList').innerHTML = b.top.map(e => `<li class="${e.me ? 'me' : ''}"><span class="r">${e.r}</span><span class="n">${esc(e.n)}</span><span class="s">${e.s}</span></li>`).join('') || '<li class="load">Пока пусто</li>';
    $('lbMe').innerHTML = b.me ? `Ваше место: <b>${b.me.r || '—'}</b> · ${b.me.s} очков` : '';
    $('lbNote').textContent = b.note || '';
  }
  const esc = t => String(t).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' })[c]);
  $('bLb').onclick = lbShow; $('lbClose').onclick = () => $('lbm').classList.remove('on');
  document.querySelectorAll('#lbm .tab').forEach(t => t.onclick = () => { lbPeriod = t.dataset.p; lbShow(); });
  $('bSnd').onclick = () => { S.sound = S.sound === false; if (window.Sound) Sound.enabled = S.sound; save(); sndBtn(); snd('click'); };
  document.addEventListener('click', e => { if (e.target.closest('button') && e.target.closest('button').id !== 'bSnd') snd('click'); }, true);
  sndBtn();
  $('lbDel').onclick = async () => { if (!S.lb.name) return; const r = await LB.remove(); if (r.ok) await lbShow(); $('lbErr').textContent = r.ok ? 'Вы удалены из общей таблицы' : (r.msg || 'Ошибка'); };
  $('lbNick').onsubmit = async e => { e.preventDefault(); const r = await LB.setName($('lbName').value); if (r.ok) await lbShow(); $('lbErr').textContent = r.ok ? 'Ник сохранён' : (r.msg || 'Ошибка'); };
  $('bPlay').onclick = () => start(M().level);
  $('bBack').onclick = () => { if (Tut.step >= 0) $('tSkip').onclick(); home(); };
  window.__appBack = () => { if ($('scrGame').classList.contains('on')) { $('bBack').onclick(); return true; } return false; };
  if (!window.RELEASE) window.fw = { snd, get L() { return L; }, get S() { return S; }, get tut() { return Tut.step; }, start, levelInfo, get TOTAL() { return MODES[S.mode].total; }, get M() { return M(); }, LB, lbShow, setMode(m) { S.mode = m; save(); }, MODES, BONUS, trySel(p) { sel = p.slice(); check(); },
    solveAll() { L.words.forEach((o, k) => { if (!M().found[lvl.g].includes(k)) { sel = o.path.slice(); check(); } }); } };
  function updBanner() { try { if (S.tut && P.ads.bannerAvailable()) P.ads.showBanner(); else P.ads.hideBanner(); } catch (e) {} }
  (async () => { try { await P.init(); } catch (e) {}
    try { if (P.cloud && P.cloud.available) { const c = await P.cloud.pull(); if (c && c.m && progress(c) > progress(S)) { S = Object.assign(S, c); P.storage.save(KEY, S); } } } catch (e) {}
    updBanner(); if (!S.tut && M().level === 0) start(0); else home(); try { P.gameReady(); } catch (e) {} })();
})();
