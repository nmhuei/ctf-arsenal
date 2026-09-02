#!/usr/bin/env python3
import json, itertools, time, random
from pathlib import Path
from solve_remote_fast_exact import build_universe, base, jq_accept_set
raw=json.loads(Path('chains_augmented.json').read_text() if Path('chains_augmented.json').exists() else Path('chains_225.json').read_text())
ops_pool=sorted({op for ops in raw.values() for op in ops})
# prioritize domain-cutting ops
priority=['acos','asin','atanh','acosh','log','sqrt','lgamma','gamma','tan','sin','cos','erf','erfc','logb','frexp|first','frexp|last','modf|first','modf|last','trunc','floor','ceil','round','rint','nearbyint','cbrt','asinh','atan','tanh','sinh','cosh','exp','significand','abs']
ops_pool=[x for x in priority if x in ops_pool]+[x for x in ops_pool if x not in priority]
universe=build_universe(142, base.DEFAULT_CHARSET, 124)

def exact_map(raw):
    m={}; accs={}
    for k,ops in list(raw.items()):
        try: acc=jq_accept_set('jq', universe, ops)
        except Exception: continue
        accs[k]=acc
        if len(acc)==1:
            v=next(iter(acc))
            if v not in m or len(ops)<len(m[v]): m[v]=ops
    return m,accs

m,accs=exact_map(raw)
missing=sorted(universe-set(m))
print('[+] start exact',len(m),'missing',len(missing),missing, flush=True)
start=time.time(); added=0; tests=0
# Try extending existing chain keyed by missing value first
for v in list(missing):
    if str(v) not in raw: continue
    baseops=raw[str(v)]
    candidates=[]
    # breadth suffix lengths 1,2,3 over prioritized first 20 to keep quick
    for L in [1,2,3]:
        for suf in itertools.product(ops_pool[:24], repeat=L):
            candidates.append(baseops+list(suf))
    random.Random(v).shuffle(candidates)
    for ops in candidates[:8000]:
        tests+=1
        try: acc=jq_accept_set('jq', universe, ops)
        except Exception: continue
        if len(acc)==1 and v in acc:
            raw[str(v)]=ops; m[v]=ops; added+=1
            print(f'[+] refined {v}: len={len(ops)} ops={ops}', flush=True)
            Path('chains_refined.json').write_text(json.dumps(raw,indent=2))
            break
    missing=sorted(universe-set(m))
    print(f'    after {v}: missing {len(missing)}', flush=True)
    if time.time()-start>240: break
print('[+] done added',added,'tests',tests,'exact',len(m),'missing',len(sorted(universe-set(m))), sorted(universe-set(m)), flush=True)
Path('chains_refined.json').write_text(json.dumps(raw,indent=2))
