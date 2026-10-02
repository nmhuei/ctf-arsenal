from pathlib import Path
import sys,json,hashlib
P=Path(__file__).resolve().parent;sys.path.insert(0,str(P.parent/'agent_collector'));import kernel_walk as k;from dump_cache import xarray_lookup
phys=[0x20de1d000,0x20de1e000,0x20de1b000,0x20de19000,0x20de18000,0x20de17000,0x20de16000,0x20dcd1000,0x20dcce000,0x20dcc9000]
phys +=[k.f2p(fo) for fo in (0x2f3e040,0x2f41040,0x1cd8040,0x1de2040)]
rows=[]
for p in phys:
 fo=k.p2f(p);src=fo
 for level in range(8):
  cp,trace=xarray_lookup(src//4096)
  row={'target_phys':hex(p),'target_file':hex(fo),'level':level,'source_file':hex(src),'cache_phys':hex(cp) if cp is not None else None,'trace':trace}
  if cp is None:rows.append(row);break
  co=k.p2f(cp);data=k.m[co+src%4096:co+src%4096+4096];row.update(cache_file=hex(co+src%4096),nonzero=sum(c!=0 for c in data),head=data[:32].hex(),sha256=hashlib.sha256(data).hexdigest());rows.append(row)
  (P/f'cache_{p:x}_{level}.bin').write_bytes(data)
  if co+src%4096==src:break
  src=co+src%4096
(P/'cache_archive.json').write_text(json.dumps(rows,indent=2))
for r in rows:print({kk:v for kk,v in r.items() if kk!='trace'})
