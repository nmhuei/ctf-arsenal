import json,struct,zlib,hashlib
from pathlib import Path
import kernel_walk as k
import dump_cache as dc
OUT=Path('script/offline_audit/agent_collector');(OUT/'recovered_files').mkdir(exist_ok=True)
expected={'extensions.json':0x20a2f078,'AlternateServices.txt':0x25489b76,'handlers.json':0x6df5e5fd,'SiteSecurityServiceState.txt':0xe16206f5};rows=[]
for row in json.loads((OUT/'profile_inodes.json').read_text()):
 name=row['path'].rsplit('/',1)[-1];parts=[];pages=[]
 for i in range((row['size']+4095)//4096):
  pa,trace=dc.xarray_lookup(i,int(row['head'],16));fo=k.p2f(pa) if pa else None
  b=k.m[fo:fo+4096] if fo else bytes(4096);parts.append(b)
  pages.append({'index':i,'phys':hex(pa) if pa else None,'file':hex(fo) if fo else None,'nonzero':sum(c!=0 for c in b),'head':b[:32].hex(),'trace':trace})
 blob=b''.join(parts)[:row['size']];crc=zlib.crc32(blob);okay=crc==expected[name]
 (OUT/f'candidate_{name}').write_bytes(blob)
 if okay:(OUT/'recovered_files'/name).write_bytes(blob)
 record={'name':name,'size':len(blob),'crc32':f'{crc:08x}','expected':f'{expected[name]:08x}','verified':okay,'pages':pages};rows.append(record)
 print(name,len(blob),hex(crc),'verified',okay)
 for p in pages:print({k:v for k,v in p.items() if k!='trace'})
(OUT/'profile_recovery.json').write_text(json.dumps(rows,indent=2))
