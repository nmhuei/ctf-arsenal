#!/usr/bin/env python3
"""Read-only passive code-signature scan; saved artifacts stay in this branch."""
from pathlib import Path
import subprocess,json,mmap,struct,re,base64,collections
HERE=Path(__file__).resolve().parent;BASE=HERE.parents[1];MEM=BASE.parent/'evidence/mem.clean'
values={'crc_polynomial':0xedb88320,'initial_key0':0x12345678,'initial_key1':0x23456789,'initial_key2':0x34567890,'fnv32_basis':0x811c9dc5,'fnv32_prime':0x01000193,'fnv64_basis':0xcbf29ce484222325,'fnv64_legacy_basis':0x14650fb0739d0383,'fnv64_prime':0x100000001b3,'djb2_basis':5381,'sdbm_multiplier':65599}
patterns={name:v.to_bytes(8 if v>0xffffffff else 4,'little') for name,v in values.items()}
regex='|'.join(''.join(r'\x%02x'%x for x in pat) for pat in patterns.values())
proc=subprocess.run(['rg','--json','-a','-o','--no-unicode',regex,str(MEM)],capture_output=True,check=False)
assert proc.returncode in (0,1)
hits=[]
for line in proc.stdout.splitlines():
 r=json.loads(line)
 if r['type']!='match':continue
 d=r['data']
 for sm in d['submatches']:
  content=sm['match']; b=content['text'].encode() if 'text'in content else base64.b64decode(content['bytes'])
  hits.append({'offset':d['absolute_offset']+sm['start'],'names':[name for name,pat in patterns.items() if pat==b]})
for row in json.loads((BASE/'zipcrypto_constant_hits.json').read_text()):
 hits.append({'offset':int(row['offset'],16),'names':['zipcrypto_multiplier'],'prior_artifact':True})
with MEM.open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 report=[]
 for hit in hits:
  off=hit['offset']; names=hit['names'];expected=(0x08088405).to_bytes(4,'little') if names==['zipcrypto_multiplier'] else patterns[names[0]]
  assert m[off:off+len(expected)]==expected,(off,names)
  lo=max(0,off-1024);data=m[lo:min(len(m),off+1024)]
  absolute_refs=[]
  for q in re.finditer(rb'[\x00-\xff][\x30-\x31]\x40\x00',data):
   value=struct.unpack_from('<I',data,q.start())[0]
   if 0x403000<=value<=0x403190:absolute_refs.append({'offset':hex(lo+q.start()),'value':hex(value)})
  # Infer a file-to-VA translation from direct CALL rel32 landing on expected PLT slots.
  votes=collections.defaultdict(list)
  for q in re.finditer(b'\xe8',data):
   at=lo+q.start()
   if q.start()+5>len(data):continue
   displacement=struct.unpack_from('<i',data,q.start()+1)[0]
   for target in range(0x401030,0x4011e0,0x10):
    bias=target-at-5-displacement;constant_va=off+bias
    if 0x401000<=constant_va<0x4022f5:votes[bias].append({'offset':hex(at),'target':hex(target)})
  supported=[]
  for bias,calls in votes.items():
   if len(calls)>=2:
    supported.append({'constant_va':hex(off+bias),'bias':bias,'calls':calls})
  near_constants={name:hex(lo+data.find(pat)) for name,pat in patterns.items() if data.find(pat)>=0}
  report.append({**hit,'offset':hex(off),'context_hex':m[max(0,off-32):off+64].hex(),'absolute_collector_rodata_refs':absolute_refs,'coherent_plt_mappings':supported,'near_constants':near_constants})
(HERE/'constant_neighborhoods.json').write_text(json.dumps(report,indent=2)+'\n')
summary={'new_scan_patterns':{k:v.hex() for k,v in patterns.items()},'reused_multiplier_hits':11,'counts':dict(collections.Counter(name for row in hits for name in row['names'])),'total_hits':len(hits),'absolute_ref_rows':sum(bool(r['absolute_collector_rodata_refs']) for r in report),'coherent_plt_rows':sum(bool(r['coherent_plt_mappings']) for r in report),'candidate_offsets':[r['offset'] for r in report if r['absolute_collector_rodata_refs'] or r['coherent_plt_mappings']]}
(HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
