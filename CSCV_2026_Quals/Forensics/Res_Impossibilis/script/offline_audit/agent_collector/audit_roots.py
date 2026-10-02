import kernel_walk as k,json,struct,hashlib
from pathlib import Path
OUT=Path('script/offline_audit/agent_collector');rows=[]
for root in json.loads((OUT/'kernel_roots.json').read_text())['roots']:
 pages={}
 for va in [0x400000,0x401000,0x402000,0x403000,0x404000,0x405000]:
  pa=k.walk(root,va)
  if pa is None:continue
  fo=k.p2f(pa)
  if fo is None:continue
  b=k.m[fo:fo+4096];pages[hex(va)]={'phys':hex(pa),'file':hex(fo),'head':b[:64].hex(),'sha256':hashlib.sha256(b).hexdigest()}
 if pages:rows.append({'root':hex(root),'pages':pages})
(OUT/'low_userspace_pages.json').write_text(json.dumps(rows,indent=2))
print('rootcount',len(json.loads((OUT/'kernel_roots.json').read_text())['roots']),'mappedlow',len(rows))
for r in rows:print(r['root'],{v:p['head'][:32] for v,p in r['pages'].items()})
