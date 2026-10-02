from pathlib import Path
import mmap,struct,json
from Crypto.Cipher import AES
root=Path(__file__).resolve().parents[2];key=bytes.fromhex('3e91fa1288cd04b2715a90ef234761d8');out=[]
with (root/'script/evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 for off in range(8,len(m)-16,32*1024*1024):
  end=min(len(m),off+32*1024*1024);end=off+((end-off)//16)*16
  b=AES.new(key,AES.MODE_CBC,b'\0'*16).decrypt(m[off:end]);pos=0
  while True:
   hit=b.find(b'IDAT',pos)
   if hit<0:break
   pos=hit+4
   if hit<4:continue
   size=struct.unpack_from('>I',b,hit-4)[0]
   if not 1<=size<=65536:continue
   row={'offset':hex(off+hit-4),'size':size,'head':b[hit-4:hit+40].hex()};print(row,flush=True);out.append(row)
(root/'script/offline_audit/cbc_idat_results.json').write_text(json.dumps(out,indent=2))
