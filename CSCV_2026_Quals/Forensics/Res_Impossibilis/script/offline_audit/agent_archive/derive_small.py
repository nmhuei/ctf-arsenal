from pathlib import Path
import sys,json,struct,ctypes,zlib,mmap,subprocess
P=Path(__file__).resolve().parent;H=P.parent;sys.path.insert(0,str(H));from verify_zip_evidence import INITIAL,TABLE;from recover_archive_central import crypt
raw=bytearray((P/'32_entries_archive.zip').read_bytes());known=bytearray((P/'32_entries_known.bin').read_bytes());records=json.loads((H/'archive_central_records.json').read_text());libc=ctypes.CDLL('libc.so.6');libc.srand(1788885121);rng=bytes(libc.rand()&255 for _ in range(429));sigmap={};derived=[]
for i in range(32,37):
 r=records[i];matches=list((H/'agent_password/recovered_files').glob(f'{i:02d}_*'))
 if not matches:continue
 plain=matches[0].read_bytes();assert len(plain)==r['plain_size'] and zlib.crc32(plain)==int(r['crc32'],16)
 header=struct.pack('<4s5H3I2H',b'PK\x03\x04',20,1,0,0x6800,0x5521,int(r['crc32'],16),r['compressed_size'],r['plain_size'],len(r['name']),0)+r['name'].encode();a,b,c=INITIAL;out=bytearray()
 for p in rng[i*11:i*11+11]+bytes([int(r['crc32'],16)>>24])+plain:
  t=(c&65535)|2;out.append(p^((t*(t^1)>>8)&255));a=(a>>8)^TABLE[(a^p)&255];b=((b+(a&255))*134775813+1)&0xffffffff;c=(c>>8)^TABLE[(c^(b>>24))&255]
 data=header+out;start=r['local_offset'];assert all(not known[j] or raw[j]==v for j,v in enumerate(data,start));raw[start:start+len(data)]=data;known[start:start+len(data)]=b'\x01'*len(data);derived.append(i)
 for offset in range(start,start+len(data)-16,8):
  for layer in ('zip','mega'):
   sig=bytes(raw[offset:offset+16]);sig=sig if layer=='zip' else crypt(sig,offset)
   if b'\n' not in sig:sigmap[sig]=(offset,layer)
pat='|'.join(''.join(f'\\x{x:02x}' for x in s) for s in sigmap)
if not pat:raise SystemExit('No new plaintext candidates')
r=subprocess.run(['rg','--text','--byte-offset','--only-matching','--no-unicode','--replace','X'*16,'--regexp',pat,str(H.parent/'evidence/mem.clean')],capture_output=True);assert r.returncode in(0,1),r.stderr
results=[]
with (H.parent/'evidence/mem.clean').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as m:
 for line in r.stdout.splitlines():
  pos=int(line.split(b':')[0]);offset,layer=sigmap[m[pos:pos+16]];results.append({'memory':hex(pos),'logical':offset,'layer':layer})
(P/'small_derived_archive.zip').write_bytes(raw);(P/'small_derived_known.bin').write_bytes(known);(P/'small_signature_hits.json').write_text(json.dumps({'derived_members':derived,'hits':results},indent=2));print('Derived',derived,'known',sum(known),'hits',results)
