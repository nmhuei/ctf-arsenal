import z3,json
from pathlib import Path
from hash_model import hkey
OUT=Path('script/offline_audit/agent_collector/alt_reconstruction')
lines=Path('script/offline_audit/root_files/37_AlternateServices.partial.txt').read_text().splitlines()[1:]
N=3;cap=64;slots=[z3.Int(f'slot{i}') for i in range(N+len(lines))];s=z3.Solver()
for i,x in enumerate(slots):
 s.add(x>=0,x<cap)
 if i:s.add(slots[i-1]<x)
occ=[z3.Or(*[x==j for x in slots]) for j in range(cap)]
for i,line in enumerate(lines):
 h=hkey(line.split('\t')[0]);p=h>>26;step=(h&63)|1;probe=[(p-j*step)&63 for j in range(64)]
 for depth,j in enumerate(probe):s.add(z3.Implies(slots[i+N]==j,z3.And(*[occ[k] for k in probe[:depth]])))
results=[]
while s.check()==z3.sat and len(results)<10:
 m=s.model();v=[m.eval(x).as_long() for x in slots];results.append(v);s.add(z3.Or(*[x!=y for x,y in zip(slots,v)]))
(OUT/'order_solutions64.json').write_text(json.dumps(results,indent=2));print('solutions',len(results));print(results[:8])
