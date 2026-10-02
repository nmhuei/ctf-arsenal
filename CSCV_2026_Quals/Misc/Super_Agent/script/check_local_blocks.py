"""Test explicitly hypothetical byte transforms of the local puzzle blocks."""
from pathlib import Path
from itertools import product
import importlib.util,json,hashlib,struct
root=Path(__file__).resolve().parents[1]
p=root/'solver/math_workspace/solve_system.py'
spec=importlib.util.spec_from_file_location('operators',p)
ops=importlib.util.module_from_spec(spec);spec.loader.exec_module(ops)
b=(root/'challenge/ctf_super_agent_can_solve_this.challage').read_bytes()
assert b[:8]==b'CHALLAGE'
a,tail=b[16:40],b[88:112]
stages=[ops.operators_for_stage(k) for k in ('phi1','phi2','phi3','phi4')]
found=[];tested=0;ranked=[]
for direction,(x,y) in enumerate(((a,tail),(tail,a))):
 for chosen in product(*stages):
  names=[o.name for o in chosen]
  z=bytes(ops.apply_mapping(names,list(x)))
  for combine in ('xor','add','sub','rsub'):
   result=bytes((u^v) if combine=='xor' else ((u+v)&255) if combine=='add' else ((u-v)&255) if combine=='sub' else ((v-u)&255) for u,v in zip(z,y))
   tested+=1
   score=sum(32<=c<127 for c in result)
   if b'CSCV' in result or score>=22:
    candidate={'direction':direction,'operators':names,'combine':combine,'printable':score,'hex':result.hex(),'text':repr(result)}
    ranked.append(candidate)
    if b'CSCV2026{' in result and result.endswith(b'}'):found.append(candidate)
summary={'sha256':hashlib.sha256(b).hexdigest(),'size':len(b),'header_bytes':b[:16].hex(),'header_after_magic':list(struct.unpack('<BBHHH',b[8:16])),'hypothesis':'Four byte operations followed by combining the second block; VM semantics unknown','tested':tested,'flag_candidates':found,'printable_candidates':sorted(ranked,key=lambda x:-x['printable'])[:10]}
(root/'script/local_block_checks.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
