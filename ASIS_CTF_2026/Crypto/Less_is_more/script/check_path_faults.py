#!/usr/bin/env python3
import json, importlib.util
base='/home/light/Workspace/CTF/ASIS_CTF_2026/Crypto/Less_is_more/challenge/less_is_more_c21e39cc296efe86ee76902cae855a705bd74214/less_is_more'
spec=importlib.util.spec_from_file_location('chall',base+'/challenge.py')
c=importlib.util.module_from_spec(spec); spec.loader.exec_module(c)
d=json.load(open(base+'/output.txt'))
for ti,tx in enumerate(d['tx']):
    b=c.sch(bytes.fromhex(tx['cmt']))
    covered={}
    for v,h in tx['path']:
        lo,hi=c.srg(v)
        for i in range(lo,min(hi,c.t)):
            covered.setdefault(i,[]).append((v,h))
    challenged={i for i,x in enumerate(b) if x}
    zero={i for i,x in enumerate(b) if not x}
    leaked=sorted(challenged & set(covered))
    missing=sorted(zero-set(covered))
    print('tx',ti,'path_nodes',len(tx['path']),'covered',len(covered),'leaked_nonzero',len(leaked),'missing_zero',len(missing))
    for i in leaked:
        print('  LEAK pos=%d challenge=%d via=%s' % (i,b[i],[(v,c.srg(v)) for v,_ in covered[i]]))
    if missing: print('  missing zero positions',missing[:30])
