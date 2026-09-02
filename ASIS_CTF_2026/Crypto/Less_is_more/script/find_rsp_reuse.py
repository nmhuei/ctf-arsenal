#!/usr/bin/env python3
import importlib.util, json, os, time
from collections import defaultdict
import galois, numpy as np

HERE=os.path.dirname(os.path.abspath(__file__))
ROOT=os.path.dirname(HERE)
BASE=os.path.join(ROOT,"challenge","less_is_more_c21e39cc296efe86ee76902cae855a705bd74214","less_is_more")
spec=importlib.util.spec_from_file_location("c",os.path.join(BASE,"challenge.py"))
c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
d=json.load(open(os.path.join(BASE,"output.txt"),encoding="utf-8"))
GF=galois.GF(c.q); k,n=c.k,c.n

def full(right):
    G=np.zeros((k,n),dtype=np.int64); G[:,:k]=np.eye(k,dtype=np.int64); G[:,k:]=np.asarray(right,dtype=np.int64); return G
PUB=[full(P) for P in d["PK"]]

def sysright(G,J):
    J=np.asarray(sorted(map(int,J)),dtype=np.int64)
    mask=np.ones(n,dtype=bool); mask[J]=False; K=np.arange(n,dtype=np.int64)[mask]
    return np.asarray(np.linalg.inv(GF(G[:,J])) @ GF(G[:,K]),dtype=np.int64)

def fp(B):
    Z=B==0
    rd=Z.sum(1).astype(np.int16); cd=Z.sum(0).astype(np.int16)
    # Stronger than degree multiset: degree-neighbor profiles on zero bipartite graph.
    r2=tuple(sorted(tuple(sorted(map(int,cd[np.flatnonzero(Z[i])])) ) for i in range(k)))
    c2=tuple(sorted(tuple(sorted(map(int,rd[np.flatnonzero(Z[:,j])])) ) for j in range(k)))
    return (tuple(sorted(map(int,rd))),tuple(sorted(map(int,cd))),r2,c2)

records=[]
for ti,tx in enumerate(d["tx"]):
    b=c.sch(bytes.fromhex(tx["cmt"])); ri=0
    for pos,bi in enumerate(b):
        if bi:
            records.append((ti,pos,bi,ri,tuple(tx["rsp"][ri]))); ri+=1

m=defaultdict(list); start=time.time()
for idx,r in enumerate(records,1):
    ti,pos,bi,ri,J=r
    F=fp(sysright(PUB[bi-1],J))
    m[F].append(r)
    if idx%25==0: print("progress",idx,"/",len(records),"elapsed",round(time.time()-start,1),flush=True)
dups=[v for v in m.values() if len(v)>1]
print("duplicate_fingerprints",len(dups))
for group in dups:
    print("GROUP",[(x[0],x[1],x[2],x[3]) for x in group])
print("elapsed",round(time.time()-start,1))
