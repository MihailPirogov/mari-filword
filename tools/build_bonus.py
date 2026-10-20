#!/usr/bin/env python3
"""data/bonus.js: bonus-word dictionary = words present in BOTH «Мут тӱня» list and «Марий йылме мутер» index, 3–9 letters."""
import json, re
D = json.load(open('/workspace/mari-wow/src/uchaev/dict_index.json', encoding='utf-8'))
MARI = re.compile(r'^[а-яёӧӱҥ]{3,9}$'); out = {}
for l in open('/workspace/mari-wow/wordlist_mhr.txt', encoding='utf-8'):
    p = l.rstrip('\n').split('\t'); w = p[0]
    if not MARI.match(w) or w not in D: continue
    g = p[3] if len(p) > 3 and p[3] and not p[3].startswith(('Курык', 'сокр')) and re.match('[а-яё]', p[3]) else (D[w].get('g') or '')
    g = re.split(r'[;(]', g)[0].strip()
    t = g.split(' ')
    if len(t) > 1 and (w.startswith(t[0]) or t[0].startswith(w[:3])) and re.fullmatch('[а-яёӧӱҥ]+', t[0]) and t[0] not in ('а',): g = ' '.join(t[1:])  # drop echoed headword
    g = ', '.join(g.split(', ')[:2])[:32].rstrip(' ,')
    if g and re.match('[а-яё]', g): out[w] = g
open('data/bonus.js', 'w', encoding='utf-8').write('window.FW_BONUS=' + json.dumps(out, ensure_ascii=False, separators=(',', ':')) + ';\n')
print(len(out))
