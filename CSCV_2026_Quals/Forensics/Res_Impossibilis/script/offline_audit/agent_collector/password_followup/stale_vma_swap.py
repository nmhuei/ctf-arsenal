from pathlib import Path
import sys,struct,subprocess,re,json,collections
sys.path.insert(0,'script/offline_audit/agent_collector');import kernel_walk as k
OUT=Path('script/offline_audit/agent_collector/password_followup')
pairs=[(0x400000,0x401000),(0x401000,0x403000),(0x403000,0x404000),(0x404000,0x405000),(0x405000,0x406000)]
patterns={f'vma_{a:x}_{b:x}':''.join('\\x%02x'%c for c in struct.pack('<QQ',a,b)) for a,b in pairs}
for s in ['zswap.enabled','zswap:','zram0','/dev/zram','/proc/swaps','Filename\t\t\t\tType','Adding ','swapfile','resume=']:
 patterns['text_'+s]=re.escape(s).replace('\\\t',r'\x09')
p=subprocess.run(['rg','-aob','--no-unicode','|'.join(patterns.values()),'script/evidence/mem.clean'],capture_output=True);rows=[]
for line in p.stdout.splitlines():
 if b':' not in line:continue
 a,b=line.split(b':',1);off=int(a);tags=[n for n,pat in patterns.items() if re.fullmatch(pat.encode(),b)];row={'file':hex(off),'phys':hex(k.f2p(off)),'tags':tags,'context':k.m[off-64:off+320].hex()}
 if any(t.startswith('vma_') for t in tags):row['words']=[hex(x) for x in struct.unpack_from('<32Q',k.m,off)]
 rows.append(row)
(OUT/'stale_vma_swap_hits.json').write_text(json.dumps(rows,indent=2));print('counts',collections.Counter(t for x in rows for t in x['tags']),flush=True)
