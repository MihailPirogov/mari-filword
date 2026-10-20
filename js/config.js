/* Game config. Leaderboard:
 *  lbYandex — leaderboard technical name in the Yandex Games console (create it there: «Мари филворд — очки», numeric, desc)
 *  lbApi    — URL of server/leaderboard.php for web/Android ('' = local mode: only own score is shown) */
window.FW_CONFIG = { lbYandex: 'mfscore', lbApi: '/api/mari-filword/',
  photos: ['animals','birds','body','clothes','colors','culture','family','food','home','main','mixed','nature','numbers','plants','time','tools'] };   // theme ids that have img/bg/<id>.webp (tools/make_bgs.sh fills this)
if (!window.RELEASE) { const m = /[?&]lbapi=([^&]+)/.exec(location.search); if (m) window.FW_CONFIG.lbApi = decodeURIComponent(m[1]); }
