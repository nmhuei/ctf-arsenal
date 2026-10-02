from pathlib import Path
import mmap,struct,zlib,json,hashlib
from Crypto.Cipher import AES
root=Path(__file__).resolve().parents[2];key=bytes.fromhex('3e91fa1288cd04b2715a90ef234761d8');out=[]
with (root/'script/evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 for row in json.loads((root/'script/offline_audit/structure_markers.json').read_text())['vault']:
  off=int(row['offset'],16);size=struct.unpack_from('>I',m,off+4)[0];iv=m[off+8:off+24];plain=AES.new(key,AES.MODE_CBC,iv).decrypt(m[off+24:off+8+size]);pos=8;chunks=[]
  if plain[:8]!=b'\x89PNG\r\n\x1a\n':print('bad magic',hex(off),plain[:32].hex());continue
  while pos+12<len(plain):
   n=struct.unpack_from('>I',plain,pos)[0];kind=plain[pos+4:pos+8]
   if pos+12+n>len(plain):break
   good=(zlib.crc32(plain[pos+4:pos+8+n])&0xffffffff)==struct.unpack_from('>I',plain,pos+8+n)[0]
   chunks.append([pos,n,kind.decode(errors='replace'),good]);pos+=12+n
   if kind==b'IEND':break
  result={'offset':hex(off),'plain_sha256':hashlib.sha256(plain).hexdigest(),'chunks':chunks,'tail':plain[-16:].hex()};out.append(result);print(result,flush=True)
  path=root/f'script/offline_audit/vault_{off:x}.png';path.write_bytes(plain[:pos] if chunks and chunks[-1][2]=='IEND' else plain)
(root/'script/offline_audit/vault_results.json').write_text(json.dumps(out,indent=2))
