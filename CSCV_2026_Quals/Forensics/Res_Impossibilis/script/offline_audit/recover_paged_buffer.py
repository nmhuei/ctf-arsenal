from pathlib import Path
import mmap,struct,json,hashlib
from Crypto.Cipher import AES
ROOT=Path(__file__).resolve().parents[2]
results=[]
with (ROOT/'script/evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 segs=[];off=0
 while off<len(m):
  magic,version,start,end,res=struct.unpack_from('<IIQQQ',m,off)
  assert magic==0x4c694d45
  segs.append((start,end+1,off+32));off+=32+end-start+1
 def p2f(p):
  for s,e,o in segs:
   if s<=p<e:return o+p-s
 def f2p(p):
  for s,e,o in segs:
   if o<=p<o+e-s:return s+p-o
 def read(p,n=4096):
  o=p2f(p)
  return m[o:o+n] if o is not None else b''
 origin=0x2f3e054;physical=f2p(origin);page=physical&~4095;prefix=struct.pack('<Q',page)[2:6]
 print('physical',hex(physical),'page',hex(page),flush=True)
 words=[x&0xffffffff for x in [2032387434,2144802918,1612300407,-1744597057,376328228,-333502917,137095450,-350496053]]
 key=struct.pack('>4I',*(words[i]^words[i+4] for i in range(4)));iv=int.from_bytes(struct.pack('>4I',words[4],words[5],0,0),'big')
 off=0
 while True:
  hit=m.find(prefix,off)
  if hit<0:break
  off=hit+1;pos=hit-2;pp=f2p(pos)
  if pp%8:continue
  entry=struct.unpack_from('<Q',m,pos)[0]
  if entry&0x000ffffffffff000 !=page or not entry&1:continue

  chunks=[];entries=[]
  for i in range(64):
   ent=struct.unpack_from('<Q',m,pos+8*i)[0];p=ent&0x000ffffffffff000
   if not ent&1:break
   data=read(p)
   if len(data)!=4096:break
   entries.append(hex(p));chunks.append(data)
  raw=b''.join(chunks)[physical%4096:]
  plain=AES.new(key,AES.MODE_CTR,nonce=b'',initial_value=iv).decrypt(raw)
  eocd=plain.find(b'PK\x05\x06');central=plain.find(b'PK\x01\x02');headers=plain.count(b'PK\x03\x04')
  row={'pte_file':hex(pos),'pte_phys':hex(pp),'pages':len(chunks),'local_headers':headers,'central':central,'eocd':eocd,'entries':entries}
  print(row,flush=True);results.append(row)
  if headers>4:
   if eocd>=0:plain=plain[:eocd+22+struct.unpack_from('<H',plain,eocd+20)[0]]
   target=ROOT/f'script/offline_audit/archive_pte_{pos:x}.zip';target.write_bytes(plain);row['output']=str(target)
(ROOT/'script/offline_audit/zip_page_results.json').write_text(json.dumps(results,indent=2))
