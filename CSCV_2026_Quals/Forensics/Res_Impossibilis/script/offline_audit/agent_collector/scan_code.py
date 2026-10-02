from pathlib import Path
import subprocess,json,mmap,struct
ROOT=Path.cwd(); OUT=ROOT/'script/offline_audit/agent_collector'
patterns={'gmon_init':r'\x48\x8b\x05\xe5\x3f\x00\x00','legacy_plt26':r'\xff\x25\x12\x3f\x00\x00\x68\x1a\x00\x00\x00','cet_push26':r'\xf3\x0f\x1e\xfa\x68\x1a\x00\x00\x00','push26':r'\x68\x1a\x00\x00\x00\xe9','start_main_indirect':r'\xff\x15\x69\x3c\x00\x00','legacy_start':r'\x31\xed\x49\x89\xd1\x5e\x48\x89\xe2\x48\x83\xe4\xf0\x50\x54','collector_comm':'sys_audit_colle','build_id':r'\x73\x12\x07\xed\xc0\xca\xdd\x34\xcf\x5e\x5f\xc1\x1a\xa5\xea\x55\x63\x0b\xf3\x90'}
p=subprocess.run(['rg','-aob','--no-unicode','|'.join(patterns.values()),'script/evidence/mem.clean'],capture_output=True)
with open('script/evidence/mem.clean','rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 rows=[]
 for line in p.stdout.splitlines():
  if not b':' in line:continue
  o=int(line.split(b':',1)[0]); b=line.split(b':',1)[1]
  # matched binary strings can contain LF; every pattern avoids this.
  import re
  tags=[k for k,pat in patterns.items() if re.fullmatch(pat.encode(),b)]
  rows.append({'offset':hex(o),'tags':tags,'near':m[max(0,o-32):o+128].hex()})
(OUT/'code_scan.json').write_text(json.dumps(rows,indent=2))
from collections import Counter
print(Counter(t for r in rows for t in r['tags']))
