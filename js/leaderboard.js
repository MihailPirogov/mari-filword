/* Leaderboard: score = words / bonus words / won levels × mode factor (Куштылго ×1, Кокла ×2, Неле ×3).
 * Yandex Games → ysdk leaderboards (Platform.leaderboard, name FW_CONFIG.lbYandex, all-time only);
 * web / Android → FW_CONFIG.lbApi (server/leaderboard.php: week + all time, own place); otherwise local mode. */
(function () {
  const CFG = window.FW_CONFIG || {}, P = window.Platform;
  const MULT = { easy: 1, mid: 2, hard: 3 }, PTS = { word: 2, bonus: 1, win: 20 };
  const BAD = ['хуй', 'хуе', 'хуя', 'пизд', 'бля', 'ебат', 'ебан', 'сука', 'мудак', 'пидор', 'жоп', 'говн', 'fuck', 'shit', 'bitch', 'admin', 'pirogovlab'];
  function weekId(t) { const d = new Date((t || Date.now()) + 3 * 3600e3); d.setUTCHours(0, 0, 0, 0); d.setUTCDate(d.getUTCDate() + 3 - (d.getUTCDay() + 6) % 7);
    const w1 = new Date(Date.UTC(d.getUTCFullYear(), 0, 4)); const n = 1 + Math.round(((d - w1) / 864e5 - 3 + (w1.getUTCDay() + 6) % 7) / 7); return d.getUTCFullYear() + '-W' + String(n).padStart(2, '0'); }
  const hex = () => Array.from(crypto.getRandomValues(new Uint8Array(16)), b => b.toString(16).padStart(2, '0')).join('');
  function nickProblem(n) {
    n = (n || '').trim().replace(/\s+/g, ' ');
    if (n.length < 2 || n.length > 16) return 'Ник: от 2 до 16 символов';
    if (!/^[\p{Script=Cyrillic}A-Za-z0-9 _.\-]+$/u.test(n)) return 'Можно буквы, цифры, пробел, _ . -';
    const low = n.toLowerCase().replace(/[^a-zа-яёӧӱҥ]/g, '');
    if (BAD.some(b => low.includes(b))) return 'Этот ник нельзя использовать';
    return null;
  }
  let S = null, save = null, mode = () => 'mid';
  const LB = {
    MULT, PTS, weekId, nickProblem,
    attach(state, saveFn, modeFn) {
      S = state; save = saveFn; mode = modeFn;
      S.lb = Object.assign({ total: 0, week: 0, wk: weekId(), lv: 0, name: '', pid: hex(), key: hex(), sent: 0 }, S.lb || {});
    },
    get kind() { return P.name === 'yandex' ? 'yandex' : CFG.lbApi ? 'server' : 'local'; },
    add(what) {   // returns points added
      const lb = S.lb; if (lb.wk !== weekId()) { lb.wk = weekId(); lb.week = 0; }
      const p = PTS[what] * (MULT[mode()] || 1); lb.total += p; lb.week += p; if (what === 'win') lb.lv++; save(); return p;
    },
    async api(method, body, qs) {
      const r = await fetch(CFG.lbApi + (qs || ''), method === 'GET' ? {} : { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });
      return r.json();
    },
    async setName(name) {
      const pr = nickProblem(name); if (pr) return { ok: false, msg: pr };
      if (LB.kind === 'server') { const j = await LB.api('POST', { a: 'name', pid: S.lb.pid, key: S.lb.key, name }); if (!j.ok) return j; }
      S.lb.name = name.trim(); save(); LB.submit(); return { ok: true };
    },
    async remove() {   // forget me on the server; local points stay, nickname cleared
      try { if (LB.kind === 'server') { const j = await LB.api('POST', { a: 'delete', pid: S.lb.pid, key: S.lb.key }); if (!j.ok && j.err !== 'no_player') return j; } } catch (e) { return { ok: false, msg: 'Нет связи с сервером' }; }
      S.lb.name = ''; S.lb.sent = 0; save(); return { ok: true };
    },
    async submit() {
      const lb = S.lb;
      try {
        if (LB.kind === 'yandex') return await P.leaderboard.submit(CFG.lbYandex, lb.total);
        if (LB.kind === 'server' && lb.name) { const j = await LB.api('POST', { a: 'submit', pid: lb.pid, key: lb.key, total: lb.total, week: lb.week, wk: lb.wk, lv: lb.lv }); if (j.ok) { lb.sent = lb.total; save(); } return j; }
      } catch (e) {}
    },
    async board(period) {   // → {top:[{r,n,s,me}], me, note}
      const lb = S.lb, mine = { r: null, n: lb.name || 'Вы', s: period === 'week' ? lb.week : lb.total, me: true };
      try {
        if (LB.kind === 'yandex') {
          const e = await P.leaderboard.top(CFG.lbYandex);
          return { top: (e || []).map(x => ({ r: x.rank, n: (x.player && x.player.publicName) || 'Игрок', s: x.score })), me: mine, note: period === 'week' ? 'На Яндекс Играх — только общий зачёт' : '' };
        }
        if (LB.kind === 'server') {
          if (lb.total > lb.sent) await LB.submit();
          const j = await LB.api('GET', null, '?a=board&period=' + period + '&pid=' + lb.pid);
          if (j.ok) return { top: j.top, me: j.me || mine, total: j.total, note: lb.name ? '' : 'Укажите ник, чтобы попасть в таблицу' };
        }
      } catch (e) {}
      return { top: [Object.assign({}, mine, { r: 1 })], me: Object.assign({}, mine, { r: 1 }), note: 'Общая таблица пока не подключена — показан ваш результат' };
    },
  };
  window.FW_LB = LB;
})();
