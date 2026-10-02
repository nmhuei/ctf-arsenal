from pathlib import Path
import mmap,struct,json,subprocess,collections
OUT=Path('script/offline_audit/agent_collector')
targets={'mapping':0xffff978f68ecd198,'firstpage':0xffffe18300d02040,'damagedpage':0xffffe18300000000+((0x2f71a000>>12)*64),'inode':0xffff978f68ecd020}
patterns={k:''.join('\\x%02x'%x for x in struct.pack('<Q',v)) for k,v in targets.items()}
patterns['damaged_pte']=r'[\x01-\xff][\xa0-\xaf]\x71\x2f\x00\x00\x00[\x00\x80]'
p=subprocess.run(['rg','-aob','--no-unicode','|'.join(patterns.values()),'script/evidence/mem.clean'],capture_output=True)
import re
with open('script/evidence/mem.clean','rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 rows=[]
 for l in p.stdout.splitlines():
  if b':' not in l:continue
  off,b=l.split(b':',1); o=int(off)
  tags=[k for k,p in patterns.items() if re.fullmatch(p.encode(),b)]
  rows.append({'offset':hex(o),'tags':tags,'near':m[o-64:o+96].hex()})
(OUT/'refs.json').write_text(json.dumps(rows,indent=2))
print('targets',{k:hex(v) for k,v in targets.items()});print(collections.Counter(t for r in rows for t in r['tags']))
for r in rows[:30]: print(r)
