# Мари филворд — марийские слова змейкой

**Мари филворд** (EN: *Mari Word Search*) — бесплатный филворд (поиск слов) на луговомарийском языке от [PirogovLab](https://pirogovlab.ru). На сетке букв спрятаны марийские слова: проведите пальцем по соседним буквам, соберите слово змейкой и сразу узнайте перевод на русский.

- **Страница игры:** https://pirogovlab.ru/mari-filword-igra/ (EN: https://pirogovlab.ru/en/mari-filword-igra/)
- **Играть в браузере:** https://pirogovlab.ru/mari-filword/
- **Политика конфиденциальности:** https://pirogovlab.ru/mari-filword/privacy/
- Android-пакет: `ru.pirogovlab.marifilword` — APK на странице игры; <!-- PLACEHOLDER store badges --> скоро в RuStore, Google Play и Яндекс Играх

## Возможности
- 1300+ уровней в 14 темах (Семья, Животные, Птицы, Еда, Природа, Растения, Тело, Одежда, Цвета, Числа, Дом и село, Работа, Праздники и культура, Время) и «Всё подряд».
- Три сложности: Куштылго (прямые слова), Кокла (змейкой), Неле (до 7×7). Уровни генерируются детерминированно.
- Перевод каждого слова; бонусные слова (любое настоящее марийское слово на сетке), палиндромы в обе стороны, альтернативные пути решения.
- Фотофоны природы Марий Эл, обучение со spotlight, подсказки, звуки (WebAudio-синтез), работа без интернета.
- Общая таблица лидеров (сайт и Android: PHP-API; Яндекс Игры: лидерборд платформы `mfscore`), участие по нику, удаление одной кнопкой.

## Устройство репозитория
| Путь | Что это |
|---|---|
| `index.html`, `css/`, `js/app.js`, `js/gen.js`, `js/levels.js`, `js/sound.js` | игра (HTML5, без фреймворков) |
| `js/platform.js`, `js/adapters/{yandex,android}.js` | платформенный слой: Яндекс Игры SDK (реклама, облачные сохранения, лидерборд) и Android-мост |
| `js/leaderboard.js`, `server/leaderboard.php` | таблица лидеров: клиент и PHP-API (JSON + flock, лимиты частоты, ключ игрока хранится как хеш, фильтр ников) |
| `android/` | Android-оболочка (WebView + Yandex Mobile Ads: баннер, межстраничная, за вознаграждение) |
| `tools/` | данные (`build_words.py`, `build_bonus.py`), сборки (`build_release.py yandex\|android\|web`, `build_android.sh`), графика и ассеты магазинов |
| `test/` | Playwright-тесты (уровни, правила, лидерборд, раскладка 320–1920 px, попапы, обучение, звук, Яндекс- и Android-сборки) |
| `site/privacy/` | политика конфиденциальности (RU/EN) |

## Сборка
```bash
python3 tools/build_words.py && python3 tools/build_bonus.py   # data/words.js, data/bonus.js (нужны исходные словари, см. ниже)
node test/levels_node.js                                      # проверка всех 1308 уровней
python3 tools/build_release.py web|yandex|android             # release/build/web, release/mari-filword-yandex.zip, android/…/assets/www
bash tools/build_android.sh                                   # подписанные APK + AAB (нужен свой keystore.properties)
```

**Словарные данные в репозиторий не входят.** Слова и переводы получены из «Марий йылме мутер» / «Словаря марийского языка» в 10 т. (МарНИИЯЛИ, 1990–2005; электронная версия — [dict.fu-lab.ru](https://dict.fu-lab.ru)) и «Марийско-русского словаря» В. М. Васильева и З. В. Учаева (2003); у этих источников нет открытой лицензии. Ключи подписи, пароли и скрипты выкладки тоже не публикуются. Фотофоны (`img/bg/`) сгенерированы ИИ.

Лицензия кода — MIT (см. `LICENSE`).
