# Мари филворд — ответы для форм Google Play Console (и коротко для RuStore / Яндекс Игр)

Приложение `ru.pirogovlab.marifilword`, 1.0.0 (versionCode 1), файл `release/mari-filword.aab`. Подпись — собственный ключ «Мари филворд»
(SHA-256 `A3:C4:A7:22:33:A8:16:2D:46:6A:7C:98:CC:B6:21:14:DE:EE:19:37:41:8E:79:5B:01:F9:57:A4:F0:6B:49:88`; в Play это ключ загрузки, Play App Signing).
Политика: **https://pirogovlab.ru/mari-filword/privacy/**

Что приложение реально отправляет с устройства:
1. **Yandex Mobile Ads SDK 8.6.0** (баннер, межстраничная, за вознаграждение; сейчас демо-блоки, см. ANDROID_CHECKLIST.md): рекламный ID (`AD_ID`) и технические данные для показа рекламы. Геолокацию не отправляет.
2. **Общая таблица лидеров — только если игрок сам ввёл ник:** ник, случайный ID игрока и ключ (на сервере — хеш), очки и число уровней → https://pirogovlab.ru/api/mari-filword/ (сервер PirogovLab, Россия). Удаление — кнопка «Удалить меня из таблицы».
3. Больше ничего: нет аккаунтов, аналитики разработчика, Firebase, покупок.

(Шаблон — «Марий мут», ru.pirogovlab.mariwordle, в том же аккаунте; у него тоже есть таблица лидеров с ником.)

## 1. Privacy policy — `https://pirogovlab.ru/mari-filword/privacy/`
## 2. Ads — **Contains ads: Yes**
## 3. App access — **All functionality is available without special access**
## 4. Advertising ID — **Yes** → **Advertising or marketing** (Yandex Mobile Ads SDK)
## 5. Target audience — **13–15, 16–17, 18+** (не отмечать младше 13: Yandex Mobile Ads не в программе Families). «Unintentionally appeal to children?» → **No**.

## 6. Data safety
| Вопрос | Ответ |
|---|---|
| Collect or share required user data? | **Yes** |
| Encrypted in transit? | **Yes** (HTTPS) |
| Account creation | **My app does not allow users to create an account** (ник без пароля — не аккаунт) |
| Users can request deletion? | **Yes** — кнопка «Удалить меня из таблицы» в игре или запрос через https://pirogovlab.ru/contacts/ |

Типы данных:
| Категория → тип | Collected | Shared | Ephemeral | Required/Optional | Цели |
|---|---|---|---|---|---|
| Device or other IDs (рекламный ID, Yandex Mobile Ads) | Yes | **Yes** (Яндекс) | No | Optional | Advertising or marketing |
| Personal info → **Other info** (игровой ник) | Yes | No | No | **Optional** | **App functionality** |
| App activity → **Other user-generated content / In-app actions** (очки и уровни в таблице) | Yes | No | No | **Optional** | **App functionality** |
Не отмечать: Location, Financial, Health, Messages, Photos/Videos, Audio, Files, Calendar, Contacts, Web browsing, App info and performance.
Перед отправкой сверить с тем, как заполнено у «Марий мут» в этом же аккаунте, и с таблицей Яндекса для Mobile Ads SDK 8 (ads.yandex.com/helpcenter/en/dev/android/app-privacy-android).

## 7. Content rating (IARC) — email mihail.pirogov@gmail.com · Game (Puzzle/Word)
Violence/Fear/Sexuality/Nudity — No · Profanity — No (бранные слова исключены, фильтр ников) · Controlled substances — No · Gambling — No ·
**Users interact / exchange content — Yes, limited:** только ник в таблице лидеров (без чата и сообщений; ники фильтруются, игрок может удалить себя) ·
Shares location — No · Digital purchases — No · Unrestricted internet — No · Ads — Yes. Ожидаемо: PEGI 3 / IARC 3+ (возможна пометка «Users Interact»).

## 8. Прочее — News/Government/Financial/Health/COVID: No · foreground services/exact alarms: не используются.
## 9. Store settings — Game · **Word** · теги Word, Puzzle, Casual, Offline, Educational · email mihail.pirogov@gmail.com · сайт **https://pirogovlab.ru** (app-ads.txt уже есть) · Free · все страны.

## RuStore — коротко
Тип **Игра** · **Словесные игры** + **Головоломки** · **0+** · реклама **есть** (РСЯ) · платного контента нет · политика как выше · `release/mari-filword.apk`.

## Яндекс Игры
0+. Реклама и лидерборд — платформенные (SDK), внешних ссылок и запросов в сборке нет (проверено test/release.py).
