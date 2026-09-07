from random import sample
from hashlib import shake_256

N,q,df,dg = 251,128,73,71
R.<x> = ZZ[]
Q.<y> = QQ[]
K.<z> = Q.quotient(y^N-1)
phi = x^N-1

def keygen():
    while True:
        f,g = [sum(x^i for i in sample(range(N),d)) for d in (df,dg)]
        rf,a,_ = f.xgcd(phi)
        rg,b,_ = g.xgcd(phi)
        if gcd(ZZ(rf),q) != 1:
            continue
        d,u,v = xgcd(ZZ(rf),ZZ(rg))
        if abs(d) != 1:
            continue
        u = u/d
        v = v/d
        F = (-q*v*b) % phi
        G = (q*u*a) % phi
        k = R([round(c) for c in K(Q(F))/K(Q(f))])
        F = (F-k*f) % phi
        G = (G-k*g) % phi
        h = (g*a*inverse_mod(ZZ(rf),q))
        return f,g,F,G,h

f,g,F,G,h = keygen()
print('f', f.list())
print('g', g.list())
print('F range', min(F.list()), max(F.list()), 'norm', sqrt(sum(c*c for c in F.list())))
print('f norm', sqrt(sum(c*c for c in f.list())))

def sign(msg):
    m = R([c&127 for c in shake_256(msg).digest(N)])
    aa = (-m*F) % phi
    bb = ( m*f) % phi
    a = R([(QQ(aa[i])/q).round('away') for i in range(N)])
    b = R([(QQ(bb[i])/q).round('away') for i in range(N)])
    return (a*f+b*F) % phi, m

ss=[]; ms=[]
for i in range(500):
    s,m=sign(('msg-%d' % i).encode())
    ss.append(vector(ZZ, s.list() + [0] * (N - len(s.list()))))
    ms.append(vector(ZZ, m.list() + [0] * (N - len(m.list()))))

import numpy as np
S=np.array(ss, dtype=float)
M=np.array(ms, dtype=float)
for center in ['raw','diff']:
    X=S if center=='raw' else S-M
    X=X-np.mean(X, axis=0)
    C=(X.T@X)/500
    print(center, 'trace', np.trace(C), 'minmax', np.min(np.diag(C)), np.max(np.diag(C)))
    ev=np.linalg.eigvalsh(C)
    print('eigs', ev[:5], ev[-5:])

print('sig max', max(abs(v) for s in ss for v in s), 'sig norm', float(max(s.norm() for s in ss)))
print('diff max', max(abs(v) for i,s in enumerate(ss) for v in s-ms[i]), 'diff norm', float(max((s-ms[i]).norm() for i,s in enumerate(ss))))

import json
with open('/tmp/downhill_sim.json', 'w') as out:
    to_ints = lambda vals: [int(v) for v in vals]
    json.dump({'f': to_ints(f.list()), 'g': to_ints(g.list()),
               'F': to_ints(F.list()), 'G': to_ints(G.list()),
               'h': to_ints(h.list()), 'sigs': [to_ints(s) for s in ss],
               'msgs': [to_ints(m) for m in ms]}, out)
