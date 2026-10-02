"""Test whether a memory block is a per-byte operand inside the VM loop."""
from pathlib import Path
from itertools import product
import importlib.util,json
root=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('ops',root/'solver/math_workspace/solve_system.py')
ops=importlib.util.module_from_spec(spec);spec.loader.exec_module(ops)
data=(root/'challenge/ctf_super_agent_can_solve_this.challage').read_bytes()
blocks=(data[16:40],data[88:112]);prefix=b'CSCV2026{'
# Include AND/OR and noninvertible multiplication; only local puzzle arithmetic.
operators=ops.candidate_operators()+[
 ops.Operator('and',lambda v,c:v&c),ops.Operator('or',lambda v,c:v|c)]
found=[];tested=0;best=0
for direction,(key,target) in enumerate((blocks,blocks[::-1])):
 for chosen in product(operators,repeat=4):
  tested+=1
  def run(x,i):
   for op,c in zip(chosen,(key[i],255,67,4)):x=ops.apply_one(x,op,c)
   return x
  matched=0
  for i,x in enumerate(prefix):
   if run(x,i)!=target[i]:break
   matched+=1
  best=max(best,matched)
  if matched!=len(prefix):continue
  possible=[[x for x in range(256) if run(x,i)==y] for i,y in enumerate(target)]
  found.append({'direction':direction,'ops':[op.name for op in chosen],'preimages':possible})
out={'models':tested,'best_prefix_bytes':best,'prefix_matches':found,'hypothesis':'First binary operation uses a byte from the other block at the index, rather than the index itself.'}
(root/'script/keyed_vm_checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
