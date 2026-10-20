#!/usr/bin/env python3
"""data/words.js: themed meadow-Mari words (tools/themes_manual.py). Every word is checked against
«Марий йылме мутер» index (../mari-wow/src/uchaev/dict_index.json) AND the «Мут тӱня» list (../mari-wow/wordlist_mhr.txt).
Filler pool (rarely used on big grids): frequent nouns of «Мут тӱня»."""
import json, re, sys, os
sys.path.insert(0, os.path.dirname(__file__)); from themes_manual import THEMES
D = json.load(open('/workspace/mari-wow/src/uchaev/dict_index.json', encoding='utf-8'))
WL = {}
for l in open('/workspace/mari-wow/wordlist_mhr.txt', encoding='utf-8'):
    p = l.rstrip('\n').split('\t'); WL[p[0]] = p
MARI = re.compile(r'^[а-яёӧӱҥ]{3,9}$')
# Mari (meadow) theme names; every word checked in «Марий йылме мутер» index and/or «Мут тӱня» list (see README)
MHR = {'family': 'Еш', 'animals': 'Янлык', 'birds': 'Кайык', 'food': 'Кочкыш', 'nature': 'Пӱртӱс', 'plants': 'Пушеҥге да кушкыл',
       'body': 'Кап', 'clothes': 'Вургем', 'colors': 'Тӱс', 'numbers': 'Шотлымаш', 'home': 'Сурт да ял', 'tools': 'Паша да ӱзгар',
       'culture': 'Пайрем да культур', 'time': 'Жап'}
for k, v in MHR.items():
    for t in v.lower().split():
        assert t in D, (k, t)
out = {'themes': [], 'filler': []}; seen = set(); drop = []; uniq = set()
for key, name, icon, col, ws in THEMES:
    lst, here = [], set()
    for w, g in ws:
        if not MARI.match(w) or w in here: continue
        if w not in D or w not in WL: drop.append(w); continue
        lst.append([w, g]); here.add(w)
    out['themes'].append({'id': key, 'mhr': MHR[key], 'name': name, 'icon': icon, 'color': col, 'words': lst}); seen |= here; uniq |= here
for w, p in WL.items():
    if len(p) < 4 or p[2] != 'grid' or not p[3] or w in seen or w not in D: continue
    g = p[3].split(';')[0].strip()
    if not MARI.match(w) or len(w) > 8 or not re.fullmatch(r'[а-яё ,\-]+', g) or len(g) > 24: continue
    if re.search(r'(ый|ий|ой|ть|ться|ся)$', g.split(',')[0]) or w in ('мый','тый','тудо','нуно'): continue
    out['filler'].append([w, g]); seen.add(w)
    if len(out['filler']) >= 300: break
# mixed pool «Всё подряд»: all «Мут тӱня» words with a Russian gloss that are in the index, by frequency
mixed = []
for w, p in WL.items():
    if len(p) < 4 or not re.fullmatch(r'[а-яёӧӱҥ]{3,9}', w) or w not in D: continue
    g = p[3]
    if not g or g.startswith(('Курык', 'сокр')) or not re.match('[а-яё]', g): continue
    g = re.split(r'[;(]', g)[0].strip(); g = ', '.join(g.split(', ')[:2])[:30].rstrip(' ,')
    g = re.sub(r'^(?:[а-яё]{2,7}\.\s*)+', '', g) or g   # drop labels like «ткац.», «лингв.»
    t = g.split(' ')
    if len(t) == 2 and re.search(r'(ский|ный|ний|ий|ой|ый)$', t[1]): g = t[0]   # «мать материнский» → «мать»
    mixed.append((int(p[1]), w, g))
mixed.sort(key=lambda x: -x[0]); out['mixed'] = [[w, g] for _, w, g in mixed]
open('data/words.js', 'w', encoding='utf-8').write('window.FW_WORDS=' + json.dumps(out, ensure_ascii=False) + ';\n')
print('mixed', len(out['mixed']));print('themes', len(out['themes']), 'unique themed words', len(uniq), 'filler', len(out['filler']))
print('dropped (not in both dictionaries):', ' '.join(drop))
for t in out['themes']: print(t['id'], len(t['words']))
