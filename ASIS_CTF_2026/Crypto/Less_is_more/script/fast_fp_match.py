#!/usr/bin/env python3
import importlib.util, json, os, struct, time
from collections import defaultdict

import numpy as np
from numba import njit

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(HERE)
BASE=os.path.join(ROOT,"challenge","less_is_more_c21e39cc296efe86ee76902cae855a705bd74214","less_is_more")
spec=importlib.util.spec_from_file_location("c",os.path.join(BASE,"challenge.py"))
c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
d=json.load(open(os.path.join(BASE,"output.txt"),encoding="utf-8"))
q,k,n=c.q,c.k,c.n

M0=np.asarray(d["G0"],dtype=np.int64)
PUB=[np.asarray(P,dtype=np.int64) for P in d["PK"]]

C=np.zeros((n,k),dtype=np.int16)
for i in range(k): C[i,i]=1
C[k:]=M0.T.astype(np.int16)
INV=np.zeros(q,dtype=np.int16)
for a in range(1,q): INV[a]=pow(int(a),-1,q)

@njit(cache=True)
def greedy_basis(C,perm,INV):
    nn,kk=C.shape
    basis=np.zeros((kk,kk),dtype=np.int16)
    has=np.zeros(kk,dtype=np.uint8)
    selected=np.empty(kk,dtype=np.int16)
    rnk=0
    for idx in range(nn):
        ci=perm[idx]
        v=C[ci].copy()
        for r in range(kk):
            if has[r] and v[r]!=0:
                f=v[r]
                for cc in range(r,kk):
                    v[cc]=(v[cc]-f*basis[r,cc])%127
        pr=-1
        for r in range(kk):
            if v[r]!=0:
                pr=r; break
        if pr>=0:
            iv=INV[v[pr]]
            for cc in range(pr,kk):
                basis[pr,cc]=(v[cc]*iv)%127
            has[pr]=1
            selected[rnk]=ci
            rnk+=1
            if rnk==kk: break
    return selected

@njit(cache=True)
def inv_mod(A, invtab):
    m=A.shape[0]
    aug=np.zeros((m,2*m),dtype=np.int16)
    for i in range(m):
        for j in range(m):
            aug[i,j]=A[i,j]%127
        aug[i,m+i]=1
    for col in range(m):
        piv=-1
        for r in range(col,m):
            if aug[r,col]!=0:
                piv=r; break
        if piv<0:
            return np.empty((0,0),dtype=np.int16)
        if piv!=col:
            tmp=aug[col].copy(); aug[col]=aug[piv]; aug[piv]=tmp
        iv=invtab[aug[col,col]]
        for j in range(col,2*m):
            aug[col,j]=(aug[col,j]*iv)%127
        for r in range(m):
            if r==col: continue
            f=aug[r,col]
            if f:
                for j in range(col,2*m):
                    aug[r,j]=(aug[r,j]-f*aug[col,j])%127
    return aug[:,m:]

def fp_for(right,V):
    V=np.asarray(sorted(map(int,V)),dtype=np.int64)
    S=V[V<k]
    T=V[V>=k]-k
    sm=np.ones(k,dtype=bool); sm[S]=False; R=np.arange(k,dtype=np.int64)[sm]
    tm=np.ones(k,dtype=bool); tm[T]=False; U=np.arange(k,dtype=np.int64)[tm]
    # D is |T| x |T| and invertible exactly when V is an information set.
    if len(T)==0:
        X=np.asarray(right[:,U],dtype=np.int64)%q
    elif len(S)==0:
        Di=np.asarray(inv_mod(np.asarray(right[:,T],dtype=np.int16),INV),dtype=np.int64)
        if Di.size==0: return None
        X=(Di @ np.asarray(right[:,U],dtype=np.int64))%q if len(U) else np.empty((k,0),dtype=np.int64)
    else:
        B=np.asarray(right[np.ix_(S,T)],dtype=np.int64)
        D=np.asarray(right[np.ix_(R,T)],dtype=np.int16)
        Di=np.asarray(inv_mod(D,INV),dtype=np.int64)
        if Di.size==0: return None
        left_top=(-B @ Di)%q
        left_bot=Di
        if len(U):
            MRU=np.asarray(right[np.ix_(R,U)],dtype=np.int64)
            Y=(Di @ MRU)%q
            right_top=(np.asarray(right[np.ix_(S,U)],dtype=np.int64)-B@Y)%q
            right_bot=Y
            X=np.block([[left_top,right_top],[left_bot,right_bot]])
        else:
            X=np.vstack([left_top,left_bot])
    Z=(X==0)
    # Cheap but strong invariant under independent row/column permutations/scalings.
    return (tuple(np.bincount(Z.sum(1),minlength=16)),
            tuple(np.bincount(Z.sum(0),minlength=16)))

def expand_path(path):
    leaves={}
    stack=[(int(v),bytes.fromhex(h)) for v,h in path]
    while stack:
        v,sd=stack.pop()
        if v>=c.lvs:
            idx=v-c.lvs
            if idx<c.t: leaves[idx]=sd
        else:
            ls,rs=c.kid(sd); stack.append((2*v,ls)); stack.append((2*v+1,rs))
    return leaves

# warmup numba
_ = greedy_basis(C,np.arange(n,dtype=np.int16),INV)
_ = inv_mod(np.eye(2,dtype=np.int16),INV)

known=[]
for ti,tx in enumerate(d["tx"]):
    b=c.sch(bytes.fromhex(tx["cmt"]))
    leaves=expand_path(tx["path"])
    salt=bytes.fromhex(tx["salt"])
    for pos,sd in leaves.items():
        Qt=c.spm(c.st_of(sd,salt,struct.pack("<I",pos)),n)
        V=tuple(sorted(map(int,greedy_basis(C,np.asarray(Qt[0],dtype=np.int16),INV))))
        known.append((V,ti,pos))

responses=[]
for ti,tx in enumerate(d["tx"]):
    b=c.sch(bytes.fromhex(tx["cmt"])); ri=0
    for pos,bi in enumerate(b):
        if bi:
            responses.append((tuple(tx["rsp"][ri]),ti,pos,bi,ri)); ri+=1

start=time.time()
src=defaultdict(list)
for i,(V,ti,pos) in enumerate(known,1):
    f=fp_for(M0,V)
    src[f].append((V,ti,pos))
    if i%25==0: print("src",i,"/",len(known),"elapsed",round(time.time()-start,2),flush=True)

hits=[]
for i,(R,ti,pos,bi,ri) in enumerate(responses,1):
    f=fp_for(PUB[bi-1],R)
    if f in src:
        for rec in src[f]:
            hits.append(((ti,pos,bi,ri,R),rec))
            print("FP_HIT","rsp",(ti,pos,bi,ri),"src",(rec[1],rec[2]),flush=True)
    if i%25==0: print("rsp",i,"/",len(responses),"elapsed",round(time.time()-start,2),"hits",len(hits),flush=True)

print("FINAL",len(hits),"elapsed",round(time.time()-start,2))
for a,b in hits:
    print("HIT",a[:4],b[1:3])
