#!/usr/bin/env python3
import json, importlib.util
base='/home/light/Workspace/CTF/ASIS_CTF_2026/Crypto/Less_is_more/challenge/less_is_more_c21e39cc296efe86ee76902cae855a705bd74214/less_is_more'
spec=importlib.util.spec_from_file_location('chall',base+'/challenge.py')
c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
d=json.load(open(base+'/output.txt'))

def expected_nodes(P):
    Ps=set(P); out=[]
    def ok(v):
        lo,hi=c.srg(v)
        real=[i for i in range(lo,hi) if i<c.t]
        return bool(real) and all(i in Ps for i in real)
    def walk(v):
        if ok(v): out.append(v); return
        if v<c.lvs:
            walk(2*v); walk(2*v+1)
    walk(1)
    return out

for ti,tx in enumerate(d['tx']):
    b=c.sch(bytes.fromhex(tx['cmt']))
    P=[i for i,x in enumerate(b) if not x]
    exp=expected_nodes(P)
    got=[v for v,_ in tx['path']]
    print('tx',ti,'same_ids',got==exp,'got',len(got),'exp',len(exp))
    if got!=exp:
        print(' missing',sorted(set(exp)-set(got)))
        print(' extra',sorted(set(got)-set(exp)))
        print(' got_order',got)
        print(' exp_order',exp)
