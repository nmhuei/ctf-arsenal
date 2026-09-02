#!/usr/bin/env python3
import json, importlib.util, struct
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
def greedy_positions(C,perm,INV):
    n,k=C.shape; basis=np.zeros((k,k),dtype=np.int16); has=np.zeros(k,dtype=np.uint8)
    pos=np.empty(k,dtype=np.int16); rnk=0
    for idx in range(n):
        v=C[perm[idx]].copy()
        for r in range(k):
            if has[r] and v[r]!=0:
                f=v[r]
                for z in range(r,k): v[z]=(v[z]-f*basis[r,z])%127
        pr=-1
        for r in range(k):
            if v[r]!=0: pr=r; break
        if pr>=0:
            iv=INV[v[pr]]
            for z in range(pr,k): basis[pr,z]=(v[z]*iv)%127
            has[pr]=1; pos[rnk]=idx; rnk+=1
            if rnk==k: break
    return pos

def expand(path):
    leaves={}; stack=[(int(v),bytes.fromhex(h)) for v,h in path]
    while stack:
        v,sd=stack.pop()
        if v>=c.lvs:
            i=v-c.lvs
            if i<c.t: leaves[i]=sd
        else:
            l,r=c.kid(sd); stack.append((2*v,l)); stack.append((2*v+1,r))
    return leaves
_ = greedy_positions(C,np.arange(n,dtype=np.int16),INV)
for ti,tx in enumerate(d['tx']):
    b=c.sch(bytes.fromhex(tx['cmt'])); leaves=expand(tx['path']); salt=bytes.fromhex(tx['salt'])
    bad=[]
    for pos,sd in sorted(leaves.items()):
        Qt=c.spm(c.st_of(sd,salt,struct.pack('<I',pos)),n)
        piv=greedy_positions(C,np.array(Qt[0],dtype=np.int16),INV)
        if not np.array_equal(piv,np.arange(k,dtype=np.int16)):
            bad.append((pos,list(map(int,piv[-6:])), int(piv[-1]-k)))
    print('tx',ti,'known_zero_rounds',len(leaves),'abnormal',len(bad),bad)
