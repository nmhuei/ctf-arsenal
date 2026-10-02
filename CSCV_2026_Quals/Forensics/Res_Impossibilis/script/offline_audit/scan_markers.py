from pathlib import Path
import mmap,re,json
root=Path(__file__).resolve().parents[2]
patterns=[b'mega-login',b'mega-put',b'@gmail.com',b'@proton',b'collector',b'surveillance',b'DISPLAY_FRAME_PNG',b'g_resident_vault',b'.cpython-39.pyc',b'.pyc',b'archive_password',b'zip -P',b'7z a']
results={}
with (root/'script/evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 for pat in patterns:
  hits=[];start=0
  for _ in range(30):
   i=m.find(pat,start)
   if i<0:break
   region=m[max(0,i-120):i+220]
   printable=re.sub(rb'[^\x20-\x7e\n\t]',b'.',region).decode('ascii')
   hits.append({'offset':hex(i),'context':printable});start=i+len(pat)
  results[pat.decode()]=hits
  print(pat.decode(),'first offsets',[h['offset'] for h in hits[:4]],flush=True)
  for h in hits[:2]:print(h['context'],flush=True)
 (root/'script/offline_audit/markers.json').write_text(json.dumps(results,indent=2))
