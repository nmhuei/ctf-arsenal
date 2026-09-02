#!/usr/bin/env python3
import json, importlib.util, hashlib
from collections import defaultdict
base='/home/light/Workspace/CTF/ASIS_CTF_2026/Crypto/Less_is_more/challenge/less_is_more_c21e39cc296efe86ee76902cae855a705bd74214/less_is_more'
spec=importlib.util.spec_from_file_location('chall',base+'/challenge.py')
c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
d=json.load(open(base+'/output.txt'))
records=[]
for ti,tx in enumerate(d['tx']):
    b=c.sch(bytes.fromhex(tx['cmt'])); ri=0
    for pos,bi in enumerate(b):
        if not bi: continue
        S=tuple(tx['rsp'][ri]); ri+=1
        records.append((S,ti,pos,bi,ri-1))
by=defaultdict(list)
for rec in records: by[rec[0]].append(rec[1:])
print('exact response duplicates:',[(v) for v in by.values() if len(v)>1])
# complement equality
set_to_meta={frozenset(S):(ti,pos,bi,ri) for S,ti,pos,bi,ri in records}
seen=[]
U=set(range(548))
for S,ti,pos,bi,ri in records:
    comp=frozenset(U-set(S))
    if comp in set_to_meta:
        a=(ti,pos,bi,ri); bmeta=set_to_meta[comp]
        if a < bmeta: seen.append((a,bmeta))
print('complement pairs:',seen)
# node seed reuse
nodes=defaultdict(list)
for ti,tx in enumerate(d['tx']):
    for v,h in tx['path']: nodes[(v,h)].append(ti)
print('exact node-record reuse:',[(k,v) for k,v in nodes.items() if len(set(v))>1][:20])
seedvals=defaultdict(list)
for ti,tx in enumerate(d['tx']):
    for v,h in tx['path']: seedvals[h].append((ti,v))
print('seed value reused across tx:',[(h,locs) for h,locs in seedvals.items() if len({x[0] for x in locs})>1][:20])
print('salt duplicate?',len({tx['salt'] for tx in d['tx']})<len(d['tx']))
print('msg duplicate?',len({tx['msg'] for tx in d['tx']})<len(d['tx']))
