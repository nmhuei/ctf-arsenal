#!/usr/bin/env python3
import json, importlib.util
import numpy as np
from numba import njit
base='/home/light/Workspace/CTF/ASIS_CTF_2026/Crypto/Less_is_more/challenge/less_is_more_c21e39cc296efe86ee76902cae855a705bd74214/less_is_more'
spec=importlib.util.spec_from_file_location('chall',base+'/challenge.py')
c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
d=json.load(open(base+'/output.txt'))
q=127; k=274; n=548
INV=np.zeros(q,dtype=np.int16)
for a in range(1,q): INV[a]=pow(a,-1,q)
@njit
def full_rank(rows, inv):
    A=rows.copy(); r=0
    for col in range(k):
        piv=-1
        for i in range(r,k):
            if A[i,col]!=0:
                piv=i; break
        if piv<0: continue
        if piv!=r:
            tmp=A[r].copy(); A[r]=A[piv]; A[piv]=tmp
        iv=inv[A[r,col]]
        for j in range(col,k): A[r,j]=(A[r,j]*iv)%q
        for i in range(r+1,k):
            if A[i,col]!=0:
                f=A[i,col]
                for j in range(col,k): A[i,j]=(A[i,j]-f*A[r,j])%q
        r+=1
        if r==k: return True
    return False

def cols_as_rows(P):
    C=np.zeros((n,k),dtype=np.int16)
    for i in range(k): C[i,i]=1
    C[k:]=np.array(P,dtype=np.int16).T
    return C
pub=[cols_as_rows(P) for P in d['PK']]
# compile
full_rank(pub[0][np.arange(k,dtype=np.int64)],INV)
for ti,tx in enumerate(d['tx']):
    b=c.sch(bytes.fromhex(tx['cmt'])); ri=0; bad=[]
    for pos,bi in enumerate(b):
        if not bi: continue
        S=np.array(tx['rsp'][ri],dtype=np.int64); ri+=1
        if not full_rank(pub[bi-1][S],INV): bad.append((pos,bi,ri-1))
    print('tx',ti,'non_infosets',len(bad),bad[:30])
