from pathlib import Path
import mmap,struct,json
from Crypto.Cipher import AES
root=Path(__file__).resolve().parents[2]
words=[x&0xffffffff for x in [2032387434,2144802918,1612300407,-1744597057,376328228,-333502917,137095450,-350496053]]
key=struct.pack('>4I',*(words[i]^words[i+4] for i in range(4)));iv=int.from_bytes(struct.pack('>4I',words[4],words[5],0,0),'big')
def cipher(off):
 c=AES.new(key,AES.MODE_CTR,nonce=b'',initial_value=iv+off//16);c.encrypt(b'\0'*(off%16));return c
pages={};records=[];basealign=0x14
with (root/'script/evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 segments=[];pos=0
 while pos<len(m):
  _,_,start,end,_=struct.unpack_from('<IIQQQ',m,pos);segments.append((start,end+1,pos+32));pos+=32+end-start+1
 def f2p(p):
  for s,e,o in segments:
   if o<=p<o+e-s:return s+p-o
 def savepage(hit,logical):
  p=f2p(hit);r=p%4096;base=hit-r;vbase=logical-r
  pages[vbase]=m[base:base+4096];return base,vbase
 logical=0
 for index in range(40):
  magic=b'PK\x03\x04\x14\0' if index<39 else b'PK\x01\x02'
  sig=cipher(logical).encrypt(magic);hit=m.find(sig)
  if hit<0:print('missing header',index,hex(logical),flush=True);break
  base,vbase=savepage(hit,logical)
  block=cipher(logical).encrypt(m[hit:hit+1024])
  if index==39:
   print('CENTRAL',hex(logical),hex(hit),flush=True)
   # Try physical adjacency until EOCD; entries all fit in a small number of pages.
   for n in range(1,4):savepage(base+4096*n,vbase+4096*n)
   break
  h=struct.unpack_from('<4s5H3I2H',block);name=block[30:30+h[9]]
  row={'index':index,'logical':hex(logical),'memory':hex(hit),'page_logical':vbase,'page_file':hex(base),'name':name.decode(errors='replace'),'compressed_size':h[7],'plain_size':h[8],'crc32':hex(h[6])};records.append(row);print(row,flush=True)
  logical+=30+h[9]+h[10]+h[7]
 end=max(pages)+4096;raw=bytearray(end);known=bytearray(end)
 for p,data in pages.items():
  start=max(p,0);data=data[start-p:];raw[start:start+len(data)]=data;known[start:start+len(data)]=b'\1'*len(data)
 plain=cipher(0).encrypt(raw);eocd=plain.find(b'PK\x05\x06');print('EOCD',eocd,'holes',known.count(0),flush=True)
 if eocd>=0:plain=plain[:eocd+22+struct.unpack_from('<H',plain,eocd+20)[0]];known=known[:len(plain)]
 (root/'script/offline_audit/documents_reassembled.zip').write_bytes(plain)
 (root/'script/offline_audit/archive_known.bin').write_bytes(known)
(root/'script/offline_audit/archive_records.json').write_text(json.dumps(records,indent=2))
