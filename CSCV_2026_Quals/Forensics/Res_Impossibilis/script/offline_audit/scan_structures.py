from pathlib import Path
import mmap,struct,json,re
root=Path(__file__).resolve().parents[2];out={}
needles={'plt0':bytes.fromhex('ff35e23f0000ff25e43f0000'),'init':bytes.fromhex('4883ec08488b05d53f0000'),'vault':b'IMGV','vault_backup':b'vault_backup.key','triage':b'incident_triage_confirmed.txt'}
with (root/'script/evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 for name,needle in needles.items():
  rows=[];p=0
  while True:
   p=m.find(needle,p)
   if p<0:break
   if name=='vault':
    length=struct.unpack_from('>I',m,p+4)[0]
    if not (32<=length<=20000000 and length%16==0):p+=4;continue
   row={'offset':hex(p),'hex':m[p:p+128].hex(),'context':repr(m[max(p-96,0):p+1000])};rows.append(row)
   if name in ('plt0','init'):
    base=p-(0x20 if name=='plt0' else 0)
    (root/f'script/offline_audit/collector_code_{base:x}.bin').write_bytes(m[base:base+0x12f5])
   print(name,row if name in ('plt0','init','vault') else hex(p),flush=True)
   p+=len(needle)
  out[name]=rows
(root/'script/offline_audit/structure_markers.json').write_text(json.dumps(out,indent=2))
