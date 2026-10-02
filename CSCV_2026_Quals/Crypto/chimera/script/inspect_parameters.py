from sage.all import *
import json
from pathlib import Path
N=ZZ(json.loads(Path('script/modulus.json').read_text())['N'])
M=ZZ(31721752939659896617792337171084495768312741523809821454149295955199893657462682088273)
print('N square gap bits',(isqrt(N)**2-N).nbits(),flush=True)
print('gcd(N,M)',gcd(N,M),flush=True)
for ell,_ in factor(M):
 g=Mod(17,ell); order=g.multiplicative_order()
 print('prime',ell,'order',order,'N in subgroup',pow(int(N),int(order),int(ell))==1,flush=True)
try: print('log N',discrete_log(Mod(N,M),Mod(17,M),ord=21621600),flush=True)
except ValueError as e: print('N has no discrete log in group',flush=True)
# Find smallest exponent orders reachable using a large divisor of M.
opts=[]
for d in divisors(21621600):
 modulus=prod([ell for ell,_ in factor(M) if pow(17,int(d),int(ell))==1])
 if modulus.nbits()>195: opts.append((d,modulus.nbits()))
print('small orders',opts[:20],flush=True)
