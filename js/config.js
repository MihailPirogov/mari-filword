/* Game config. Leaderboard:
 *  lbYandex — leaderboard technical name in the Yandex Games console (create it there: «Мари филворд — очки», numeric, desc)
 *  lbApi    — URL of server/leaderboard.php for web/Android ('' = local mode: only own score is shown) */
window.FW_CONFIG = { lbYandex: 'mfscore', lbApi: '/api/mari-filword/',
  photos: ['animals','birds','body','clothes','colors','culture','family','food','home','main','mixed','nature','numbers','plants','time','tools'] };   // theme ids that have img/bg/<id>.webp (tools/make_bgs.sh fills this)
/* Web ads (Рекламная сеть Яндекса, сайт 20255381) — ONLY the public web build (tools/build_release.py web) loads the RSYA ads adapter (js/adapters/ + rsya.js).
 *  Empty ID = that ad is off. Fill in the IDs and run: bash tools/deploy_public.sh
 *  floorTouch / floorDesktop — «Floor Ad» banner (touch / desktop blocks), shown after the tutorial
 *  fullscreenTouch / fullscreenDesktop — «Полноэкранный» block: interstitial (every 3rd win, ≥150 s) and «🎬 Бесплатно» hint (reward after close)
 *  If a desktop ID is empty the touch ID is NOT reused (RSYA blocks are platform-specific). */
window.FW_CONFIG.rsya = { floorTouch: '', floorDesktop: '', fullscreenTouch: '', fullscreenDesktop: '' };
if (!window.RELEASE) { const m = /[?&]lbapi=([^&]+)/.exec(location.search); if (m) window.FW_CONFIG.lbApi = decodeURIComponent(m[1]); }
