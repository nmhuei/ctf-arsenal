import kernel_walk as k,profile_inodes as pi,struct,json,subprocess,re
from pathlib import Path
OUT=Path('script/offline_audit/agent_collector');pat=r'libxul\.so|nsSiteSecurityService|AltSvcMapping|mozLz4|addonStartup\.json\.lz4|search\.json\.mozlz4|sessionstore\.jsonlz4'
p=subprocess.run(['rg','-aob','--no-unicode',pat,'script/evidence/mem.clean'],capture_output=True);rows=[];dent=[]
for l in p.stdout.splitlines():
 if b':' not in l:continue
 off,b=l.split(b':',1);fo=int(off);row={'file':hex(fo),'term':b.decode()};rows.append(row)
 dfo=fo-56;pa=k.f2p(dfo)
 if pa is None:continue
 va=k.DM+pa
 if pi.q(va,0x28)!=va+56 or struct.unpack_from('<I',k.m,dfo+36)[0]!=len(b):continue
 ino=pi.q(va,48);r={**row,'path':pi.path(va),'inode':hex(ino)}
 if ino:r.update(size=pi.q(ino,80),mapping=hex(pi.q(ino,48)),head=hex(pi.q(pi.q(ino,48),16)),nrpages=pi.q(pi.q(ino,48),88))
 dent.append(r)
(OUT/'firefox_presence_hits.json').write_text(json.dumps(rows,indent=2));(OUT/'firefox_cache_dentries.json').write_text(json.dumps(dent,indent=2))
from collections import Counter
print(Counter(r['term'] for r in rows));print(json.dumps(dent,indent=2))
