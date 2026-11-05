import json, sys
tpl, seed, out = sys.argv[1:4]
d = json.load(open(seed, encoding='utf-8'))
for r in d['rows'] + d['done']:
    if r.get('d') and ' ' in r['d']: r['d'] = r['d'].split(' ')[0]
s = json.dumps(d, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
t = open(tpl, encoding='utf-8').read()
assert t.count('__SEED__') == 1
open(out, 'w', encoding='utf-8').write(t.replace('__SEED__', s))
print('wrote', out, len(t) + len(s))
