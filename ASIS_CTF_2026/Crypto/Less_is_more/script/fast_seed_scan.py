#!/usr/bin/env python3
import os, sys, struct, time
import numpy as np

HERE=os.path.dirname(os.path.abspath(__file__))
# Reuse the optimized finite-field primitives without executing its scan body.
src=open(os.path.join(HERE,"fast_fp_match.py"),encoding="utf-8").read()
src=src.replace("@njit(cache=True)", "@njit(cache=False)")
prefix=src.split("\nknown=[]",1)[0]
ns={"__file__":os.path.join(HERE,"fast_fp_match.py")}
exec(compile(prefix,"fast_fp_match.py","exec"),ns)

c,d,n=ns["c"],ns["d"],ns["n"]
C,INV=ns["C"],ns["INV"]
greedy_basis,fp_for=ns["greedy_basis"],ns["fp_for"]
PUB=ns["PUB"]
KEY=int(sys.argv[1])

def expand_all(path):
    out=[]
    for source_v,h in path:
        stack=[(int(source_v),bytes.fromhex(h))]
        while stack:
            v,sd=stack.pop()
            if v>=c.lvs:
                idx=v-c.lvs
                if idx<c.t: out.append((int(source_v),idx,sd))
            else:
                l,r=c.kid(sd); stack.append((2*v,l)); stack.append((2*v+1,r))
    return out

start=time.time(); tests=0; hits=[]
for ti,tx in enumerate(d["tx"]):
    leaves=expand_all(tx["path"])
    salt=bytes.fromhex(tx["salt"])
    b=c.sch(bytes.fromhex(tx["cmt"]))
    ri=0
    for pos,bi in enumerate(b):
        if not bi: continue
        R=tuple(tx["rsp"][ri]); cur_ri=ri; ri+=1
        if bi!=KEY: continue
        target=fp_for(PUB[bi-1],R)
        for source_v,source_pos,sd in leaves:
            Qt=c.spm(c.st_of(sd,salt,struct.pack("<I",pos)),n)
            V=tuple(sorted(map(int,greedy_basis(C,np.asarray(Qt[0],dtype=np.int16),INV))))
            f=fp_for(ns["M0"],V)
            tests+=1
            if f==target:
                rec=(ti,pos,bi,cur_ri,source_v,source_pos,V,R)
                hits.append(rec)
                print("SEED_HIT","tx",ti,"pos",pos,"key",bi,"ri",cur_ri,
                      "source_node",source_v,"source_leaf_pos",source_pos,flush=True)
print("KEY",KEY,"tests",tests,"hits",len(hits),"elapsed",round(time.time()-start,2))
for h in hits:
    print("HIT_DETAIL",h[:6])
