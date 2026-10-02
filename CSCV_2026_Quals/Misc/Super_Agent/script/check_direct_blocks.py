"""Bounded offline checks; operation assignments remain hypotheses."""
from pathlib import Path
from itertools import product
import importlib.util,json
root=Path(__file__).resolve().parents[1]
p=root/'solver/math_workspace/solve_system.py'
spec=importlib.util.spec_from_file_location('ops',p);ops=importlib.util.module_from_spec(spec);spec.loader.exec_module(ops)
data=(root/'challenge/ctf_super_agent_can_solve_this.challage').read_bytes()
blocks=[data[16:40],data[88:112]]
stages=[ops.operators_for_stage(k) for k in ('phi1','phi2','phi3','phi4')]
results=[];total=0
for blockid,block in enumerate(blocks):
 for chosen in product(*stages):
  names=[op.name for op in chosen]
  result=bytes(ops.apply_mapping(names,list(block)));total+=1
  if result.startswith(b'CSCV') or (all(32<=b<127 for b in result) and len(set(result))>=8):
   results.append({'block':blockid,'operators':names,'direction':'forward','result':repr(result)})
  # Invert the hypothesized byte transformation independently at each position.
  inverse=[]
  for i,target in enumerate(block):
   possible=[]
   for start in range(256):
    value=start
    for op,c in zip(chosen,(i,255,67,4)):value=ops.apply_one(value,op,c)
    if value==target:possible.append(start)
   if len(possible)!=1:break
   inverse.append(possible[0])
   # Reject an inverse as soon as it contradicts the known event prefix.
   if i<9 and possible[0]!=b'CSCV2026{'[i]:break
  if len(inverse)==24:
   results.append({'block':blockid,'operators':names,'direction':'inverse','result':repr(bytes(inverse))})
summary={'forward_models':total,'results':results}
(root/'script/direct_block_checks.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
