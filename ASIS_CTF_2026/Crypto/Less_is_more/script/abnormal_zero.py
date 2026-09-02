import json, importlib.util, struct, numpy as np
import check_infosets as ci
c=ci.c; d=ci.d
C=np.zeros((c.n,c.k),dtype=np.int16)
for j in range(c.k): C[j,j]=1
C[c.k:]=np.array(d['G0'],dtype=np.int16).T

def leaves(path):
    out={}; stack=[(int(v),bytes.fromhex(h)) for v,h in path]
    while stack:
        v,s=stack.pop()
        if v>=c.lvs:
            if v-c.lvs<c.t: out[v-c.lvs]=s
        else:
            a,b=c.kid(s); stack += [(2*v,a),(2*v+1,b)]
    return out
for ti,tx in enumerate(d['tx']):
    b=c.sch(bytes.fromhex(tx['cmt'])); z=leaves(tx['path']); salt=bytes.fromhex(tx['salt']); bad=[]
    for i,s in z.items():
        p=c.spm(c.st_of(s,salt,struct.pack('<I',i)),c.n)[0]
        if not ci.full_rank(C[np.array(p[:c.k],dtype=np.int64)],ci.INV): bad.append(i)
    print(ti,bad)
