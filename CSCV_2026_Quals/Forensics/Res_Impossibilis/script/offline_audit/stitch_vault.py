from pathlib import Path
from Crypto.Cipher import AES
import mmap,struct,zlib,json,hashlib
root=Path(__file__).resolve().parents[2];key=bytes.fromhex('3e91fa1288cd04b2715a90ef234761d8');origin=0x7fb6bc0;trace=[]
with (root/'script/evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 def pageend(off):return ((off-0x40)//4096+1)*4096+0x40
 size=struct.unpack_from('>I',m,origin+4)[0]-16;iv=m[origin+8:origin+24]
 raw=m[origin+24:pageend(origin)];raw=raw[:len(raw)//16*16];plain=AES.new(key,AES.MODE_CBC,iv).decrypt(raw)
 def extend(data,kind):
  anchorlen=64
  anchoroff=len(data)-anchorlen
  sig=data[anchoroff:];pos=0x7000000;best=data;src=None
  while True:
   hit=m.find(sig,pos,0x9000000)
   if hit<0:break
   pos=hit+1;end=pageend(hit+anchorlen-1);extra=m[hit: min(end,hit+size-anchoroff)]
   if anchoroff+len(extra)>len(best):best=data[:anchoroff]+extra;src=hex(hit)
  if len(best)>len(data):
   row={'kind':kind,'before':len(data),'after':len(best),'signature_offset':anchoroff,'memory':src};trace.append(row);print(row,flush=True)
  return best
 for iteration in range(100):
  old=len(plain);safe_raw=raw
  plain=extend(plain,'plaintext')
  raw=AES.new(key,AES.MODE_CBC,iv).encrypt(plain[:len(plain)//16*16])
  raw=extend(raw,'ciphertext');raw=raw[:len(raw)//16*16]
  plain=AES.new(key,AES.MODE_CBC,iv).decrypt(raw)
  if len(plain)>=size or len(plain)<=old:break
 if len(plain)>=size:
  final_raw=extend(safe_raw,'ciphertext-final')
  if len(final_raw)>=size:plain=AES.new(key,AES.MODE_CBC,iv).decrypt(final_raw[:size])
 print('Recovered',len(plain),'of',size,flush=True)
 (root/'script/offline_audit/vault_stitched.bin').write_bytes(plain)
 pos=8;checks=[]
 while pos+12<=len(plain):
  n=struct.unpack_from('>I',plain,pos)[0];kind=plain[pos+4:pos+8]
  if pos+12+n>len(plain):break
  good=zlib.crc32(plain[pos+4:pos+8+n])&0xffffffff==struct.unpack_from('>I',plain,pos+8+n)[0]
  checks.append([pos,n,kind.decode(errors='replace'),good]);pos+=12+n
  if kind==b'IEND':break
 print(checks,flush=True)
 if checks and checks[-1][2]=='IEND' and all(x[3] for x in checks):
  png=plain[:pos];(root/'script/offline_audit/surveillance.png').write_bytes(png);print('VERIFIED PNG',len(png),hashlib.sha256(png).hexdigest(),flush=True)
(root/'script/offline_audit/vault_stitch_trace.json').write_text(json.dumps({'trace':trace,'checks':checks},indent=2))
