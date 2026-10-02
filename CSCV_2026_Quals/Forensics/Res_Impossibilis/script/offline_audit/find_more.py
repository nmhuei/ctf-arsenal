from pathlib import Path
import mmap,re,json,struct
from Crypto.Cipher import AES
root=Path(__file__).resolve().parents[2];out={}
words=[x&0xffffffff for x in [2032387434,2144802918,1612300407,-1744597057,376328228,-1744597057,137095450,-350496053]]
words[5]=(-333502917)&0xffffffff
key=struct.pack('>4I',*(words[i]^words[i+4] for i in range(4)));iv=int.from_bytes(struct.pack('>4I',words[4],words[5],0,0),'big')
def cipher_at(off):
 c=AES.new(key,AES.MODE_CTR,nonce=b'',initial_value=iv+off//16);c.encrypt(b'\0'*(off%16));return c
with (root/'script/evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 for needle in [b'zip_password',b'archive_password',b'ZIP_PASSWORD',b'ARCHIVE_PASSWORD',b'incident_triage_confirmed',b'3e91fa12',b'g_resident_vault',cipher_at(0x1215).encrypt(b'PK\x03\x04\x14\0\x01\0\0\0')]:
  p=0;rows=[];seen=set()
  while True:
   p=m.find(needle,p)
   if p<0:break
   context=m[max(0,p-150):p+1500];h=context.hex()
   if h not in seen:
    seen.add(h);rows.append({'offset':hex(p),'text':''.join(chr(c) if 32<=c<127 or c==10 else '.' for c in context)})
   p+=len(needle)
   if len(rows)>200:break
  out[needle.hex()]=rows;print(repr(needle),len(rows),flush=True)
  if len(rows)<10:
   for row in rows:print(row,flush=True)
(root/'script/offline_audit/more_markers.json').write_text(json.dumps(out,indent=2))
