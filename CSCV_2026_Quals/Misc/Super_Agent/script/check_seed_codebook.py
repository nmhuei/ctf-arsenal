"""Check a bounded seed-derived opcode-table hypothesis for the local file."""
from pathlib import Path
import random,hashlib,json
root=Path(__file__).resolve().parents[1]
b=(root/'challenge/ctf_super_agent_can_solve_this.challage').read_bytes()
a=b[16:40];code=b[40:88];observed=sorted(set(code[::4]))
seeds=[]
for label,value in [('a',a),('a_first8',a[:8]),('a_last8',a[-8:]),('a_first16',a[:16]),('a_last16',a[-16:]),('sha256_a',hashlib.sha256(a).digest())]:
 for kind,seed in [('bytes',value),('hex',value.hex()),('big',int.from_bytes(value,'big')),('little',int.from_bytes(value,'little'))]:seeds.append((label+':'+kind,seed))
rows=[]
for label,seed in seeds:
 for method in ['shuffle','sample','unique_getrandbits','unique_randrange']:
  rng=random.Random(seed)
  if method=='shuffle':table=list(range(256));rng.shuffle(table)
  elif method=='sample':table=rng.sample(range(256),256)
  else:
   table=[];seen=set()
   while len(table)<256:
    value=rng.getrandbits(8) if method=='unique_getrandbits' else rng.randrange(256)
    if value not in seen:seen.add(value);table.append(value)
  inverse={v:i for i,v in enumerate(table)}
  for direction,mapping in [('forward',inverse),('inverse',dict(enumerate(table)))]:
   ids=[mapping[x] for x in observed]
   rows.append({'seed':label,'method':method,'direction':direction,'max_id':max(ids),'ids':ids})
rows.sort(key=lambda r:r['max_id'])
out={'distinct_opcodes':observed,'models_tested':len(rows),'hypothesis':'Python Random seed-derived opcode permutation; small semantic opcode IDs','matches_under_32':[r for r in rows if r['max_id']<32],'best_five':rows[:5]}
(root/'script/seed_codebook_checks.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
