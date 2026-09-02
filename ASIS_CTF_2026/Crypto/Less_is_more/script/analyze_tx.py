#!/usr/bin/env python3
import json, importlib.util
base='/home/light/Workspace/CTF/ASIS_CTF_2026/Crypto/Less_is_more/challenge/less_is_more_c21e39cc296efe86ee76902cae855a705bd74214/less_is_more'
spec=importlib.util.spec_from_file_location('chall',base+'/challenge.py')
c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
d=json.load(open(base+'/output.txt'))
for ti,tx in enumerate(d['tx']):
    b=c.sch(bytes.fromhex(tx['cmt']))
    ri=0; bad=[]
    for pos,bi in enumerate(b):
        if not bi: continue
        a=tx['rsp'][ri]; ri+=1
        issues=[]
        if len(a)!=274: issues.append('len='+str(len(a)))
        if a!=sorted(a): issues.append('unsorted')
        if len(set(a))!=len(a): issues.append('dups')
        if min(a)<0 or max(a)>=548: issues.append('range')
        if issues: bad.append((pos,bi,ri-1,issues))
    print('tx',ti,'structural_bad',bad,'responses',ri)
