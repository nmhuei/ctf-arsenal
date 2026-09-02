#!/usr/bin/env python3
import json, random, subprocess, time, sys
from pathlib import Path
from solve_remote_fast_exact import build_universe, base, jq_accept_set
raw=json.loads(Path('chains_225.json').read_text())
ops_pool=sorted({op for ops in raw.values() for op in ops})
# add known safe jq numeric filters from existing pool only
length=142; charset=base.DEFAULT_CHARSET; feature_count=124
universe=build_universe(length, charset, feature_count)

def exact_map(raw):
    m={}
    for k,ops in raw.items():
        try: acc=jq_accept_set('jq', universe, ops)
        except Exception: continue
        if len(acc)==1:
            v=next(iter(acc))
            if v not in m or len(ops)<len(m[v]): m[v]=ops
    return m

m=exact_map(raw)
missing=sorted(universe-set(m))
print('[+] universe',len(universe),'exact',len(m),'missing',len(missing),missing[:80], flush=True)
rng=random.Random(0xC0FFEE)
start=time.time(); trials=0; added=0
while missing and time.time()-start < 120:
    trials+=1
    L=rng.randint(1,12)
    ops=[rng.choice(ops_pool) for _ in range(L)]
    t=tuple(ops)
    if any(tuple(v)==t for v in raw.values()):
        continue
    try:
        acc=jq_accept_set('jq', universe, ops)
    except Exception:
        continue
    if len(acc)==1:
        v=next(iter(acc))
        if v in missing:
            raw[str(v)]=ops
            m[v]=ops
            missing=sorted(universe-set(m))
            added+=1
            print(f'[+] added exact {v}: {ops}; remaining {len(missing)}', flush=True)
            Path('chains_augmented.json').write_text(json.dumps(raw, indent=2))
print('[+] done trials',trials,'added',added,'exact',len(m),'missing',len(missing), flush=True)
Path('chains_augmented.json').write_text(json.dumps(raw, indent=2))
