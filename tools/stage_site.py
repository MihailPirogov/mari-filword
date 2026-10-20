#!/usr/bin/env python3
"""Stage the public pages of «Мари филворд» on pirogovlab.ru (ported from finnish-wow/tools/stage_site.py).
Input: read-only copies of the live pages in site_stage/live/ (the Sanamaailma landing/blog post are templates only).
Output: site_stage/out/ — mari-filword-igra/, en/mari-filword-igra/, blog/DATE-mari-filword/, en/blog/…, + patched
index.html, en/index.html, blog/index.html, en/blog/index.html, blog/rss.xml, en/blog/rss.xml, sitemap.xml."""
import re, os, html, sys, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
L = ROOT + '/site_stage/live/'; O = ROOT + '/site_stage/out/'
DATE = sys.argv[1] if len(sys.argv) > 1 else '2026-10-20'
Y, M, D = DATE.split('-'); MRU = ['января','февраля','марта','апреля','мая','июня','июля','августа','сентября','октября','ноября','декабря'][int(M)-1]
MEN = ['January','February','March','April','May','June','July','August','September','October','November','December'][int(M)-1]
DRU = f'{int(D)} {MRU} {Y}'; DEN = f'{MEN} {int(D)}, {Y}'
dt = datetime.date(int(Y), int(M), int(D)); RFC = dt.strftime('%a, %d %b %Y') + ' 15:00:00 +0300'
SLUG = f'{DATE}-mari-filword'; VER = '1.0.0'; TSLUG = '2026-10-19-sanamaailma'
APK = '/mari-filword/mari-filword.apk'; SIZE_MB = round(os.path.getsize(ROOT + '/release/mari-filword.apk') / 1e6)
SIZE_RU = f'{SIZE_MB} МБ'; SIZE_EN = f'{SIZE_MB} MB'
GAME = '/mari-filword/'; PRIV = '/mari-filword/privacy/'
RU_P = 'https://pirogovlab.ru/mari-filword-igra/'; EN_P = 'https://pirogovlab.ru/en/mari-filword-igra/'
OG = 'https://pirogovlab.ru/mari-filword-igra/img/og-mari-filword.jpg'
IMG = '/mari-filword-igra/img/'
e = html.escape
def rd(p): return open(L + p, encoding='utf-8').read()
def wr(p, s):
    os.makedirs(os.path.dirname(O + p), exist_ok=True); open(O + p, 'w', encoding='utf-8').write(s)
def sub1(pat, rep, s, flags=0):
    n, k = re.subn(pat, lambda m: rep, s, count=1, flags=flags); assert k == 1, pat; return n
def head(s, title, desc, canon, ogt, ogd, ogimg, ru, en):
    s = sub1(r'<title>.*?</title>', f'<title>{e(title)}</title>', s)
    s = sub1(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{e(desc)}">', s)
    s = sub1(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{canon}">', s)
    s = sub1(r'<link rel="alternate" hreflang="ru" href="[^"]*">', f'<link rel="alternate" hreflang="ru" href="{ru}">', s)
    s = sub1(r'<link rel="alternate" hreflang="en" href="[^"]*">', f'<link rel="alternate" hreflang="en" href="{en}">', s)
    s = sub1(r'<link rel="alternate" hreflang="x-default" href="[^"]*">', f'<link rel="alternate" hreflang="x-default" href="{ru}">', s)
    s = sub1(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{e(ogt)}">', s)
    s = sub1(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{e(ogd)}">', s)
    s = sub1(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{canon}">', s)
    s = sub1(r'<meta property="og:image" content="[^"]*">', f'<meta property="og:image" content="{ogimg}">', s)
    s = sub1(r'<meta name="twitter:image" content="[^"]*">', f'<meta name="twitter:image" content="{ogimg}">', s)
    return s
def fix(s):   # leftovers of the template
    s = s.replace('/sanamaailma-igra/', '/mari-filword-igra/').replace('/sanamaailma/privacy/', PRIV).replace(f'/blog/{TSLUG}/', f'/blog/{SLUG}/')
    s = s.replace('<span class="crumb">Sanamaailma</span>', '<span class="crumb">Мари филворд</span>')
    return s
GP_SVG = '<svg viewBox="0 0 24 26" aria-hidden="true" width="26" height="28"><path fill="#00d7fe" d="M1 .6 13.4 13 1 25.4C.6 25.2.4 24.7.4 24.1V1.9C.4 1.3.6.8 1 .6z"/><path fill="#ffce00" d="m17.5 8.9 4.3 2.4c1.3.8 1.3 2 0 2.8l-4.3 2.4L13.4 13z"/><path fill="#ff3a44" d="M17.5 17.1 13.4 13 1 25.4c.5.4 1.2.4 2 0z"/><path fill="#00f076" d="M17.5 8.9 3 .6C2.2.2 1.5.2 1 .6L13.4 13z"/></svg>'
def stores(lang):
    t = (lambda ru, en: ru if lang == 'ru' else en)
    return ('<!-- PLACEHOLDER stores: set href and remove "hidden" when each listing is live -->\n      <div class="stores-row">'
      f'<a class="store rs" href="#rustore" rel="noopener" hidden><i>R</i><span><small>{t("Скачать в","Get it on")}</small><b>RuStore</b></span></a>'
      f'<a class="store gp" href="#google-play" rel="noopener" hidden>{GP_SVG}<span><small>{t("Доступно в","Get it on")}</small><b>Google Play</b></span></a>'
      f'<a class="store yg" href="#yandex-games" rel="noopener" hidden><i>Я</i><span><small>{t("Играть в","Play on")}</small><b>{t("Яндекс Играх","Yandex Games")}</b></span></a></div>')
SH = {'ru': [('game','Уровень: слова змейкой'),('home','Главный экран и карта тем'),('hard','Сложный режим 7×7'),('win','Победа и перевод слов'),('leaderboard','Общая таблица лидеров'),('tutorial','Обучение при первом запуске')],
      'en': [('game','A level: words snake through the grid'),('home','Home screen and the theme map'),('hard','Hard mode 7×7'),('win','Win screen with translations'),('leaderboard','Common leaderboard'),('tutorial','First-launch tutorial')]}
def gal(lang): return '<div class="gal">' + ''.join(f'<figure class="shot"><img src="{IMG}screen-{k}.webp" width="540" height="960" loading="lazy" alt="{c}"><figcaption>{c}</figcaption></figure>' for k, c in SH[lang]) + '</div>'
FEAT_RU = '''<li><b>1300+ уровней, 14 тем</b>: Семья, Животные, Птицы, Еда, Природа, Деревья и растения, Тело, Одежда, Цвета, Числа, Дом и село, Работа, Праздники и культура, Время — и «Всё подряд»</li>
    <li><b>Три сложности</b>: Куштылго (лёгкий, прямые слова), Кокла (средний, змейкой), Неле (сложный, до 7×7)</li>
    <li><b>Перевод каждого слова</b> на русский — сразу под сеткой и на экране победы</li>
    <li><b>Бонусные слова</b>: нашли другое марийское слово — получите монеты; палиндромы читаются в обе стороны</li>
    <li>Фотографии природы Марий Эл — свой фон у каждой темы; <b>общая таблица лидеров</b> по желанию</li>
    <li>Подсказки, короткое обучение при первом запуске; уровни работают <b>без интернета</b></li>'''
FEAT_EN = '''<li><b>1300+ levels, 14 themes</b>: family, animals, birds, food, nature, plants, body, clothes, colours, numbers, home and village, work, holidays and culture, time — plus a mixed mode</li>
    <li><b>Three difficulties</b>: Kushtylgo (easy, straight words), Kokla (medium, snake words), Nele (hard, up to 7×7)</li>
    <li><b>A Russian translation for every word</b>, right below the grid and on the win screen</li>
    <li><b>Bonus words</b>: find another Mari word and get coins; palindromes count both ways</li>
    <li>Photos of Mari El nature, one per theme; an optional <b>common leaderboard</b></li>
    <li>Hints and a short tutorial; levels work <b>offline</b>; the interface is in Russian</li>'''
def landing(lang):
    s = rd(('en/' if lang == 'en' else '') + 'sanamaailma-igra/index.html')
    pre, post = s[:s.index('<main')], s[s.index('</main>') + len('</main>'):]
    if lang == 'ru':
        pre = head(pre, 'Мари филворд — игра на марийском языке | Pirogov Lab',
          'Мари филворд — бесплатная игра на луговомарийском языке: ищите марийские слова змейкой на сетке и узнавайте перевод. 1300+ уровней, 14 тем, три сложности. В браузере и на Android, скоро в RuStore, Google Play и Яндекс Играх.',
          RU_P, 'Мари филворд — марийские слова змейкой', 'Ищите марийские слова на сетке букв и узнавайте их перевод: 1300+ уровней, 14 тем, три сложности, фото природы Марий Эл.', OG, RU_P, EN_P)
        main = f'''<main class="wrap">
  <header>
    <div>
      <img class="applogo" src="{IMG}logo.webp" width="256" height="256" alt="Мари филворд">
      <p class="eyebrow"><span>Марий йылме · Android · Браузер</span></p>
      <h1>Мари филворд — марийские слова змейкой</h1>
      <p class="lead">Филворд на <b>луговомарийском языке</b>: проводите пальцем по буквам, находите спрятанные слова и сразу узнавайте их перевод на русский. <b>1300+ уровней</b> в 14 темах и три сложности.</p>
      <div class="dl"><a class="btn" href="{GAME}">▶ Играть в браузере</a><a class="btn ghost" href="{APK}" download>⬇ Скачать APK ({VER}, {SIZE_RU})</a></div>
      {stores('ru')}
      <div class="meta"><span class="pill">Версия {VER}</span><span class="pill">{DRU}</span><span class="pill">Android 7.0+</span><span class="pill">Бесплатно</span></div>
    </div>
    <figure class="hero-app"><div class="tilt"><img src="{IMG}screen-game.webp" width="540" height="960" alt="Мари филворд — уровень с найденными словами" fetchpriority="high"></div></figure>
  </header>
  <hr class="rule" style="margin-top:1rem">
  <section aria-labelledby="f"><h2 id="f">Возможности</h2><div class="card"><ul style="padding-left:1.2rem;margin:0">
    {FEAT_RU}
  </ul></div></section>
  <section aria-labelledby="s"><h2 id="s">Скриншоты</h2><figure class="shot" style="margin-bottom:1.5rem"><img src="{IMG}feature-graphic.webp" width="1024" height="500" loading="lazy" alt="Мари филворд"></figure>
  {gal('ru')}
  <div class="wide"><figure class="shot"><img src="{IMG}desktop-game.webp" width="1280" height="720" loading="lazy" alt="Версия для компьютера"><figcaption>В браузере на компьютере</figcaption></figure><figure class="shot"><img src="{IMG}desktop-home.webp" width="1280" height="720" loading="lazy" alt="Главный экран на компьютере"><figcaption>Главный экран</figcaption></figure></div></section>
  <section aria-labelledby="i"><h2 id="i">Где играть</h2><div class="card"><p style="margin:0">Прямо сейчас — <a href="{GAME}">в браузере</a> на телефоне или компьютере (прогресс сохраняется на устройстве) или на Android: скачайте <a href="{APK}" download>mari-filword.apk</a> ({VER}, {SIZE_RU}), откройте файл и разрешите установку из этого источника. Скоро «Мари филворд» появится в RuStore, Google Play и Яндекс Играх.</p></div></section>
  <section aria-labelledby="src"><h2 id="src">Словарь</h2><div class="card"><ul class="src" style="padding-left:1.2rem;margin:0"><li>«Марий йылме мутер» / «Словарь марийского языка» в 10 томах (МарНИИЯЛИ, 1990–2005), электронная версия — <a href="https://dict.fu-lab.ru" target="_blank" rel="noopener">dict.fu-lab.ru</a></li><li>В. М. Васильев, З. В. Учаев «Марийско-русский словарь» (2003)</li><li>Список слов игры «Мут тӱня» (PirogovLab); каждое слово уровня проверено по словарю</li></ul>
  <p class="note">В мобильных версиях есть ненавязчивая реклама (баннер после обучения, иногда между уровнями и по желанию — за бесплатную подсказку). В веб-версии рекламы нет. <a href="{PRIV}">Политика конфиденциальности</a>.</p></div></section>
  <aside class="callout" role="note" style="margin-top:3rem"><div class="callout-ico" aria-hidden="true">✦</div><p><b>Тау!</b> · Проект лаборатории <a href="https://pirogovlab.ru">PirogovLab</a>. Нашли ошибку в слове или переводе? Напишите в <a href="/contacts/">Telegram</a>.</p></aside>
</main>'''
        wr('mari-filword-igra/index.html', fix(pre + main + post))
    else:
        pre = head(pre, 'Mari Word Search — a word game in the Mari language | Pirogov Lab',
          'Mari Word Search (Мари филворд) is a free word-search game in Meadow Mari: find Mari words snaking through the grid and learn their translation. 1300+ levels, 14 themes, three difficulties.',
          EN_P, 'Mari Word Search — Mari words in a grid', 'Find Mari words in a letter grid and learn their translation: 1300+ levels, 14 themes, three difficulties.', OG, RU_P, EN_P)
        main = f'''<main class="wrap">
  <header>
    <div>
      <img class="applogo" src="{IMG}logo.webp" width="256" height="256" alt="Mari Word Search">
      <p class="eyebrow"><span>Mari language · Android · Browser</span></p>
      <h1>Mari Word Search — Mari words in a grid</h1>
      <p class="lead">A word-search game in <b>Meadow Mari</b>: swipe across letters, find hidden words that snake through the grid and see each word's Russian translation. <b>1300+ levels</b> in 14 themes and three difficulties.</p>
      <div class="dl"><a class="btn" href="{GAME}" hreflang="ru">▶ Play in the browser</a><a class="btn ghost" href="{APK}" download>⬇ Download APK ({VER}, {SIZE_EN})</a></div>
      {stores('en')}
      <div class="meta"><span class="pill">Version {VER}</span><span class="pill">{DEN}</span><span class="pill">Android 7.0+</span><span class="pill">Free</span></div>
    </div>
    <figure class="hero-app"><div class="tilt"><img src="{IMG}screen-game.webp" width="540" height="960" alt="Mari Word Search — a level with found words" fetchpriority="high"></div></figure>
  </header>
  <hr class="rule" style="margin-top:1rem">
  <section aria-labelledby="f"><h2 id="f">Features</h2><div class="card"><ul style="padding-left:1.2rem;margin:0">
    {FEAT_EN}
  </ul></div></section>
  <section aria-labelledby="s"><h2 id="s">Screenshots</h2><figure class="shot" style="margin-bottom:1.5rem"><img src="{IMG}feature-graphic.webp" width="1024" height="500" loading="lazy" alt="Mari Word Search"></figure>
  {gal('en')}
  <div class="wide"><figure class="shot"><img src="{IMG}desktop-game.webp" width="1280" height="720" loading="lazy" alt="Desktop browser version"><figcaption>In a desktop browser</figcaption></figure><figure class="shot"><img src="{IMG}desktop-home.webp" width="1280" height="720" loading="lazy" alt="Home screen on desktop"><figcaption>Home screen</figcaption></figure></div></section>
  <section aria-labelledby="i"><h2 id="i">Where to play</h2><div class="card"><p style="margin:0">Right now: <a href="{GAME}" hreflang="ru">in the browser</a> on a phone or computer, or on Android: download <a href="{APK}" download>mari-filword.apk</a> ({VER}, {SIZE_EN}), open it and allow installs from this source. RuStore, Google Play and Yandex Games are coming soon.</p></div></section>
  <section aria-labelledby="src"><h2 id="src">Dictionary</h2><div class="card"><ul class="src" style="padding-left:1.2rem;margin:0"><li>“Марий йылме мутер” / Dictionary of the Mari language in 10 volumes (MarNIIYaLI, 1990–2005), online at <a href="https://dict.fu-lab.ru" target="_blank" rel="noopener">dict.fu-lab.ru</a></li><li>V. M. Vasilyev, Z. V. Uchaev, Mari–Russian Dictionary (2003)</li><li>The word list of PirogovLab’s “Мут тӱня”; every level word is checked against the dictionary</li></ul>
  <p class="note">The mobile versions show unobtrusive ads (a banner after the tutorial, sometimes between levels and, if you choose, for a free hint). The web version has no ads. <a href="{PRIV}en/">Privacy policy</a>.</p></div></section>
  <aside class="callout" role="note" style="margin-top:3rem"><div class="callout-ico" aria-hidden="true">✦</div><p>A <a href="https://pirogovlab.ru/en/">PirogovLab</a> project. Found a mistake in a word or translation? Message me on <a href="/en/contacts/">Telegram</a>.</p></aside>
</main>'''
        wr('en/mari-filword-igra/index.html', fix(pre + main + post).replace(PRIV + '"', PRIV + 'en/"'))
def blogpost(lang):
    s = rd(('en/' if lang == 'en' else '') + f'blog/{TSLUG}/index.html')
    pre, post = s[:s.index('<main')], s[s.index('</main>') + len('</main>'):]
    ru_u = f'https://pirogovlab.ru/blog/{SLUG}/'; en_u = f'https://pirogovlab.ru/en/blog/{SLUG}/'; img = 'https://pirogovlab.ru/blog/media/mari-filword.jpg'
    if lang == 'ru':
        T = '«Мари филворд»: марийские слова змейкой'
        DS = 'Сделал «Мари филворд» — филворд на луговомарийском: 1300+ уровней в 14 темах, три сложности и перевод каждого слова. Играть можно в браузере и на Android, скоро — RuStore, Google Play и Яндекс Игры.'
        pre = head(pre, T + ' | Pirogov Lab', DS, ru_u, T, DS, img, ru_u, en_u)
        main = f'''<main class="wrap">
<article class="full">
  <p class="eyebrow"><a href="/blog/">Микроблог</a></p>
  <h1>{T}</h1>
  <time class="date" datetime="{DATE}T15:00:00+03:00">{DRU}</time>
  <figure class="media"><img src="/blog/media/mari-filword.jpg" width="1200" height="630" alt="{T}"></figure>
  <div class="body">
<p>Новая игра на <b>марийском языке</b> — <b>«Мари филворд»</b>. На сетке спрятаны марийские слова: проводите пальцем по буквам, собирайте слово змейкой — и сразу видите перевод на русский.</p>
<h2>Что внутри</h2>
<ul>
{FEAT_RU.replace('    <li>', '<li>')}
</ul>
<p>Слова и переводы — из «Марий йылме мутер» (МарНИИЯЛИ) и словаря Васильева и Учаева, все слова уровней проверены по словарю, а если вы нашли на сетке другое настоящее марийское слово — оно засчитается как бонусное. Играть можно <b>прямо в браузере</b> на телефоне и компьютере или на Android (APK), скоро игра появится в RuStore, Google Play и Яндекс Играх.</p>
<p>Нашли ошибку в слове или переводе? Напишите мне в <a href="/contacts/">Telegram</a> — буду исправлять. Тау!</p>
  </div>
  <div class="stores"><a class="btn" href="{GAME}">▶ Играть в браузере</a></div>
  <div class="meta"><span class="pill">Версия {VER}</span><a class="pill" href="https://pirogovlab.ru{APK}" download>⬇ Android: скачать APK ({SIZE_RU})</a><a class="pill" href="/mari-filword-igra/">Страница игры</a><span class="pill">Бесплатно</span></div>
  <a class="proj" href="/mari-filword-igra/"><img src="{IMG}kartochka-mari-filword.webp" width="480" height="320" alt=""><div><b>Мари филворд</b><span>Страница игры: возможности, скриншоты, где играть</span></div><span class="go" aria-hidden="true">→</span></a>
  <a class="backlink" href="/blog/">← Все записи</a>
</article>
</main>'''
        wr(f'blog/{SLUG}/index.html', fix(pre + main + post))
    else:
        T = 'Mari Word Search: Mari words snaking through a grid'
        DS = 'I made Mari Word Search (Мари филворд), a word-search game in Meadow Mari: 1300+ levels in 14 themes, three difficulties and a translation for every word. Browser and Android; stores coming soon.'
        pre = head(pre, T + ' | Pirogov Lab', DS, en_u, T, DS, img, ru_u, en_u)
        main = f'''<main class="wrap">
<article class="full">
  <p class="eyebrow"><a href="/en/blog/">Microblog</a></p>
  <h1>{T}</h1>
  <time class="date" datetime="{DATE}T15:00:00+03:00">{DEN}</time>
  <figure class="media"><img src="/blog/media/mari-filword.jpg" width="1200" height="630" alt="{T}"></figure>
  <div class="body">
<p>A new game in the <b>Mari language</b>: <b>Mari Word Search</b> («Мари филворд»). Mari words are hidden in a letter grid: swipe across the letters, collect a word as it snakes through the grid and see its Russian translation right away.</p>
<h2>What's inside</h2>
<ul>
{FEAT_EN.replace('    <li>', '<li>')}
</ul>
<p>Words and translations come from the MarNIIYaLI dictionary and the Vasilyev–Uchaev Mari–Russian dictionary; every level word is checked, and any other real Mari word you find in the grid counts as a bonus. Play <b>right in the browser</b> or on Android (APK); RuStore, Google Play and Yandex Games are coming soon.</p>
<p>Found a mistake in a word or translation? Message me on <a href="/en/contacts/">Telegram</a>. Tau!</p>
  </div>
  <div class="stores"><a class="btn" href="{GAME}" hreflang="ru">▶ Play in the browser</a></div>
  <div class="meta"><span class="pill">Version {VER}</span><a class="pill" href="https://pirogovlab.ru{APK}" download>⬇ Android: download APK ({SIZE_EN})</a><a class="pill" href="/en/mari-filword-igra/">Game page</a><span class="pill">Free</span></div>
  <a class="proj" href="/en/mari-filword-igra/"><img src="{IMG}kartochka-mari-filword.webp" width="480" height="320" alt=""><div><b>Mari Word Search</b><span>Game page: features, screenshots, where to play</span></div><span class="go" aria-hidden="true">→</span></a>
  <a class="backlink" href="/en/blog/">← All posts</a>
</article>
</main>'''
        wr(f'en/blog/{SLUG}/index.html', fix(pre + main + post))
def patch(rel, fn):
    s = rd(rel); assert 'mari-filword-igra' not in s and SLUG not in s, rel + ' already has the filword'; n = fn(s); assert n != s, rel; wr(rel, n)
def feed_add(s, mb, cap):
    i = s.index('<a class="mbf"'); s = s[:i] + mb + s[i:]
    items = list(re.finditer(r'      <a class="mbf" href="[^"]*".*?</a>\n', s, re.S))
    if len(items) > cap: last = items[-1]; s = s[:last.start()] + s[last.end():]
    return s
def home_ru(s):
    n0 = len(re.findall(r'<a class="mbf"', s))
    s = feed_add(s, f'<a class="mbf" href="/blog/{SLUG}/"><img src="/blog/media/mari-filword-thumb.webp" width="960" height="540" alt=""><div><time datetime="{DATE}">{DRU}</time><b>«Мари филворд»: марийские слова змейкой</b><span>Филворд на марийском: 1300+ уровней, 14 тем и перевод каждого слова — играть в браузере</span></div></a>\n      ', n0)
    pj = f'<a class="proj" href="/mari-filword-igra/"><img src="{IMG}kartochka-mari-filword.webp" width="480" height="320" alt="Мари филворд — игра на марийском языке"><div><b>Мари филворд — марийские слова змейкой</b><span>Филворд на луговомарийском: 1300+ уровней, 14 тем, перевод каждого слова — в браузере и на Android</span></div><span class="go" aria-hidden="true">→</span></a>\n  '
    i = s.index('<a class="proj"'); return s[:i] + pj + s[i:]
def home_en(s):
    n0 = len(re.findall(r'<a class="mbf"', s))
    s = feed_add(s, f'<a class="mbf" href="/en/blog/{SLUG}/"><img src="/blog/media/mari-filword-thumb.webp" width="960" height="540" alt=""><div><time datetime="{DATE}">{DEN}</time><b>Mari Word Search: Mari words in a grid</b><span>A word search in Mari: 1300+ levels, 14 themes and a translation for every word — play in the browser</span></div></a>\n      ', n0)
    pj = f'<a class="proj" href="/en/mari-filword-igra/"><img src="{IMG}kartochka-mari-filword.webp" width="480" height="320" alt="Mari Word Search — a game in the Mari language"><div><b>Mari Word Search — Mari words in a grid</b><span>A word search in Meadow Mari: 1300+ levels, 14 themes, a translation for every word — browser and Android</span></div><span class="go" aria-hidden="true">→</span></a>\n  '
    i = s.index('<a class="proj"'); return s[:i] + pj + s[i:]
def blog_idx(lang):
    def f(s):
        if lang == 'ru':
            a = f'''  <article class="card post">
    <time class="date" datetime="{DATE}T15:00:00+03:00">{DRU}</time>
    <h2><a href="/blog/{SLUG}/">«Мари филворд»: марийские слова змейкой</a></h2>
    <figure class="media"><img src="/blog/media/mari-filword.jpg" width="1200" height="630" alt="Мари филворд" loading="lazy"></figure>
    <p>Филворд на луговомарийском: ищите слова змейкой на сетке и узнавайте перевод. 1300+ уровней в 14 темах, три сложности, бонусные слова и общая таблица лидеров. Играть можно в браузере и на Android, скоро — RuStore, Google Play и Яндекс Игры.</p>
    <a class="more" href="/blog/{SLUG}/">Читать полностью →</a>
  </article>
'''
        else:
            a = f'''  <article class="card post">
    <time class="date" datetime="{DATE}T15:00:00+03:00">{DEN}</time>
    <h2><a href="/en/blog/{SLUG}/">Mari Word Search: Mari words snaking through a grid</a></h2>
    <figure class="media"><img src="/blog/media/mari-filword.jpg" width="1200" height="630" alt="Mari Word Search" loading="lazy"></figure>
    <p>A word search in Meadow Mari: find words snaking through the grid and learn their translation. 1300+ levels in 14 themes, three difficulties, bonus words and a common leaderboard. Browser and Android; stores coming soon.</p>
    <a class="more" href="/en/blog/{SLUG}/">Read more →</a>
  </article>
'''
        assert '  <div class="feed">\n' in s
        return s.replace('  <div class="feed">\n', '  <div class="feed">\n' + a, 1)
    return f
def rss(lang):
    def f(s):
        base = f'https://pirogovlab.ru/blog/{SLUG}/' if lang == 'ru' else f'https://pirogovlab.ru/en/blog/{SLUG}/'
        t = '«Мари филворд»: марийские слова змейкой' if lang == 'ru' else 'Mari Word Search: Mari words snaking through a grid'
        d = ('Филворд на марийском: 1300+ уровней, 14 тем, три сложности и перевод каждого слова. Игра в браузере и на Android.' if lang == 'ru'
             else 'A word search in Mari: 1300+ levels, 14 themes, three difficulties and a translation for every word. Browser and Android.')
        item = f'    <item>\n      <title>{e(t)}</title>\n      <link>{base}</link>\n      <guid isPermaLink="true">{base}</guid>\n      <pubDate>{RFC}</pubDate>\n      <description>{e(d)}</description>\n    </item>\n'
        s = re.sub(r'<lastBuildDate>.*?</lastBuildDate>', f'<lastBuildDate>{RFC}</lastBuildDate>', s, count=1)
        i = s.index('    <item>'); return s[:i] + item + s[i:]
    return f
def sitemap(s):
    add = ''.join(f'  <url><loc>https://pirogovlab.ru/{u}</loc><lastmod>{DATE}</lastmod></url>\n' for u in
        ['mari-filword-igra/', 'en/mari-filword-igra/', f'blog/{SLUG}/', f'en/blog/{SLUG}/', 'mari-filword/'])
    for u in ['', 'en/', 'blog/', 'en/blog/']:
        s = re.sub(rf'(<url><loc>https://pirogovlab.ru/{re.escape(u)}</loc><lastmod>)[^<]*', rf'\g<1>{DATE}', s)
    return s.replace('</urlset>', add + '</urlset>')
if __name__ == '__main__':
    import shutil; shutil.rmtree(O, ignore_errors=True)
    landing('ru'); landing('en'); blogpost('ru'); blogpost('en')
    patch('index.html', home_ru); patch('en/index.html', home_en)
    patch('blog/index.html', blog_idx('ru')); patch('en/blog/index.html', blog_idx('en'))
    patch('blog/rss.xml', rss('ru')); patch('en/blog/rss.xml', rss('en')); patch('sitemap.xml', sitemap)
    print('staged ->', O, 'slug', SLUG)
