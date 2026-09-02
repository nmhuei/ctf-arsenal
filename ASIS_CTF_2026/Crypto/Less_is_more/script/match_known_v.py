#!/usr/bin/env python3
import json, importlib.util, struct
from collections import defaultdict
import numpy as np
from numba import njit
base='/home/light/Workspace/CTF/ASIS_CTF_2026/Crypto/Less_is_more/challenge/less_is_more_c21e39cc296efe86ee76902cae855a705bd74214/less_is_more'
spec=importlib.util.spec_from_file_location('chall',base+'/challenge.py')
c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
d=json.load(open(base+'/output.txt'))
q,k,n=c.q,c.k,c.n
M=np.array(d['G0'],dtype=np.int16)
C=np.zeros((n,k),dtype=np.int16)
for i in range(k): C[i,i]=1
C[k:]=M.T
INV=np.zeros(q,dtype=np.int16)
for a in range(1,q): INV[a]=pow(int(a),-1,q)
@njit
def greedy_basis(C,perm,INV):
    n,k=C.shape
    basis=np.zeros((k,k),dtype=np.int16)
    has=np.zeros(k,dtype=np.uint8)
    selected=np.empty(k,dtype=np.int16)
    rnk=0
    for idx in range(n):
        ci=perm[idx]
        v=C[ci].copy()
        for r in range(k):
            if has[r] and v[r]!=0:
                f=v[r]
                for cc in range(r,k): v[cc]=(v[cc]-f*basis[r,cc])%127
        pr=-1
        for r in range(k):
            if v[r]!=0: pr=r; break
        if pr>=0:
            iv=INV[v[pr]]
            for cc in range(pr,k): basis[pr,cc]=(v[cc]*iv)%127
            has[pr]=1; selected[rnk]=ci; rnk+=1
            if rnk==k: break
    return selected

def expand_path(path):
    leaves={}; stack=[(int(v),bytes.fromhex(h)) for v,h in path]
    while stack:
        v,sd=stack.pop()
        if v>=c.lvs:
            idx=v-c.lvs
            if idx<c.t: leaves[idx]=sd
            continue
        ls,rs=c.kid(sd); stack.append((2*v,ls)); stack.append((2*v+1,rs))
    return leaves

# compile
_ = greedy_basis(C,np.arange(n,dtype=np.int16),INV)
known=[]
for ti,tx in enumerate(d['tx']):
    b=c.sch(bytes.fromhex(tx['cmt'])); leaves=expand_path(tx['path'])
    assert set(leaves)=={i for i,x in enumerate(b) if not x}
    salt=bytes.fromhex(tx['salt'])
    for pos,sd in leaves.items():
        Qt=c.spm(c.st_of(sd,salt,struct.pack('<I',pos)),n)
        V=tuple(sorted(map(int,greedy_basis(C,np.array(Qt[0],dtype=np.int16),INV))))
        known.append((V,ti,pos))
rsp=[]
for ti,tx in enumerate(d['tx']):
    b=c.sch(bytes.fromhex(tx['cmt'])); ri=0
    for pos,bi in enumerate(b):
        if not bi: continue
        rsp.append((tuple(tx['rsp'][ri]),ti,pos,bi,ri)); ri+=1
km=defaultdict(list)
for V,ti,pos in known: km[V].append((ti,pos))
exact=[]
for R,ti,pos,bi,ri in rsp:
    if R in km: exact.append(((ti,pos,bi,ri),km[R]))
print('known_V',len(known),'rsp',len(rsp),'exact_matches',len(exact))
for x in exact: print(x)
# nearest symmetric difference using bitsets encoded as bool vectors
KV=np.zeros((len(known),n),dtype=np.uint8)
for z,(V,_,__) in enumerate(known): KV[z,list(V)]=1
best=[]
for R,ti,pos,bi,ri in rsp:
    x=np.zeros(n,dtype=np.uint8); x[list(R)]=1
    dist=np.count_nonzero(KV != x,axis=1)
    j=int(np.argmin(dist))
    best.append((int(dist[j]),ti,pos,bi,ri,(known[j][1],known[j][2])))
print('best nearest distances:',sorted(best)[:20])
